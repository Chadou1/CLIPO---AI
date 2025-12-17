from workers.celery_config import celery_app
from video.processor import VideoProcessor
from models import SessionLocal, Video, Clip, VideoStatus
from utils.storage import get_file_url, upload_file_path_to_local
from utils.email import send_clip_ready_email
import os
import tempfile

@celery_app.task(bind=True)
def process_video_task(self, video_id: int):
    """
    Celery task to process video and generate clips
    100% FREE - No API costs!
    """
    
    db = SessionLocal()
    
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {"error": "Video not found"}
        
        # Update status
        video.status = VideoStatus.PROCESSING
        db.commit()
        
        # Video is already in local storage (file_path is the local path)
        video_local_path = video.file_path
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # Process video using FREE analysis
        processor = VideoProcessor(video_local_path, temp_dir)
        
        # Update task progress
        self.update_state(state='PROCESSING', meta={'status': 'Analyzing video with FREE AI...'})
        
        identified_clips = processor.process()
        
        # Generate clips
        total_clips = len(identified_clips)
        for idx, clip_data in enumerate(identified_clips):
            self.update_state(
                state='PROCESSING',
                meta={'status': f'Generating clip {idx+1}/{total_clips}...'}
            )
            
            # Output path
            output_filename = f"clip_{video_id}_{idx}.mp4"
            output_local_path = os.path.join(temp_dir, output_filename)
            
            # Generate clip
            processor.generate_clip(
                clip_data,
                output_local_path,
                style="simple",
                add_watermark_flag=(video.user.plan == "free")
            )
            
            # Save to local storage
            final_path = upload_file_path_to_local(output_local_path, output_filename, folder="clips")
            
            # Save clip to database
            clip = Clip(
                video_id=video_id,
                start_time=clip_data['start_time'],
                end_time=clip_data['end_time'],
                viral_score=clip_data.get('viral_score', 50),
                style="simple",
                output_path=final_path,
                transcript_segment=clip_data.get('transcript', ''),
                metadata={
                    'hook_type': clip_data.get('hook_type'),
                    'duration': clip_data.get('duration')
                }
            )
            db.add(clip)
        
        # Update video status
        video.status = VideoStatus.FINISHED
        db.commit()
        
        # Send email notification
        send_clip_ready_email(video.user.email, total_clips)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        return {
            "status": "success",
            "clips_generated": total_clips
        }
    
    except Exception as e:
        # Update video status to error
        video.status = VideoStatus.ERROR
        video.error_message = str(e)
        db.commit()
        
        return {"error": str(e)}
    
    finally:
        db.close()
