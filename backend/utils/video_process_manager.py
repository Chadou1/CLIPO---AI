"""
Multi-Process Video Generation Manager

Gère 2 processus vidéo simultanés avec une file d'attente pour les requêtes supplémentaires.
Chaque processus utilise 2 workers pour la génération de clips.
"""

import threading
import queue
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class VideoTask:
    """Représente une tâche de traitement vidéo"""
    video_id: int
    url: str
    quality_settings: dict
    clip_count: int
    plan: str
    submitted_at: datetime
    callback: Optional[Callable] = None
    
    def to_dict(self) -> dict:
        """Convertit la tâche en dictionnaire pour sérialisation JSON"""
        return {
            "video_id": self.video_id,
            "url": self.url,
            "quality_settings": self.quality_settings,
            "clip_count": self.clip_count,
            "plan": self.plan,
            "submitted_at": self.submitted_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'VideoTask':
        """Crée une tâche depuis un dictionnaire"""
        from datetime import datetime
        return VideoTask(
            video_id=data["video_id"],
            url=data["url"],
            quality_settings=data["quality_settings"],
            clip_count=data["clip_count"],
            plan=data["plan"],
            submitted_at=datetime.fromisoformat(data["submitted_at"]),
            callback=None
        )


@dataclass
class ProcessSlot:
    """Représente un slot de processus"""
    slot_id: int
    is_busy: bool = False
    current_task: Optional[VideoTask] = None
    started_at: Optional[datetime] = None


class ProcessPoolManager:
    """
    Gestionnaire de pool de processus pour le traitement vidéo.
    
    Supporte 2 processus simultanés avec une file d'attente FIFO pour les tâches excédentaires.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern pour garantir une seule instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialise le gestionnaire de processus"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.max_processes = 2  # 2 processus simultanés
        self.slots: Dict[int, ProcessSlot] = {
            0: ProcessSlot(slot_id=0),
            1: ProcessSlot(slot_id=1)
        }
        self.task_queue: queue.Queue = queue.Queue()
        self.queue_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        # Fichier de persistence de la queue
        import os
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        self.queue_file_path = os.path.join(data_dir, "video_queue.json")
        
        # Statistiques
        self.total_submitted = 0
        self.total_completed = 0
        self.total_failed = 0
        
        # Charger la queue depuis le fichier
        self._load_queue_from_file()
        
        # Démarrer le worker thread qui surveille la queue
        self.worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.worker_thread.start()
        
        print(f"✅ ProcessPoolManager initialized: {self.max_processes} concurrent processes")
    
    def submit_video_task(
        self,
        video_id: int,
        url: str,
        quality_settings: dict,
        clip_count: int = 12,
        plan: str = "free"
    ) -> Dict[str, Any]:
        """
        Soumet une tâche de traitement vidéo.
        
        Retourne:
            - status: "processing" si démarré immédiatement, "queued" si mis en file d'attente
            - slot_id: ID du slot si démarré immédiatement, None sinon
            - queue_position: Position dans la queue si en attente, None sinon
        """
        task = VideoTask(
            video_id=video_id,
            url=url,
            quality_settings=quality_settings,
            clip_count=clip_count,
            plan=plan,
            submitted_at=datetime.now()
        )
        
        with self.stats_lock:
            self.total_submitted += 1
        
        # Essayer de trouver un slot libre
        available_slot = self._find_available_slot()
        
        if available_slot is not None:
            # Démarrer immédiatement
            self._start_task_in_slot(available_slot, task)
            return {
                "status": "processing",
                "slot_id": available_slot,
                "queue_position": None,
                "message": f"Processing started in slot {available_slot}"
            }
        else:
            # Mettre en queue
            with self.queue_lock:
                self.task_queue.put(task)
                queue_pos = self.task_queue.qsize()
                # Sauvegarder la queue
                self._save_queue_to_file()
            
            print(f"📋 Video {video_id} added to queue (position: {queue_pos})")
            return {
                "status": "queued",
                "slot_id": None,
                "queue_position": queue_pos,
                "message": f"Added to queue at position {queue_pos}"
            }
    
    def _find_available_slot(self) -> Optional[int]:
        """Trouve un slot de processus disponible"""
        with self.queue_lock:
            for slot_id, slot in self.slots.items():
                if not slot.is_busy:
                    return slot_id
        return None
    
    def _start_task_in_slot(self, slot_id: int, task: VideoTask):
        """Démarre une tâche dans un slot spécifique"""
        slot = self.slots[slot_id]
        slot.is_busy = True
        slot.current_task = task
        slot.started_at = datetime.now()
        
        print(f"🎬 Starting video {task.video_id} in slot {slot_id}")
        
        # Démarrer le traitement dans un thread séparé
        process_thread = threading.Thread(
            target=self._execute_task,
            args=(slot_id, task),
            daemon=True
        )
        process_thread.start()
    
    def _execute_task(self, slot_id: int, task: VideoTask):
        """Exécute une tâche de traitement vidéo"""
        try:
            from utils.video_processor import process_video_groq, download_youtube_video
            from utils.file_storage import get_storage
            import os
            from models.schemas import VideoStatus
            
            storage = get_storage()
            
            print(f"⬇️ [Slot {slot_id}] Downloading video {task.video_id}...")
            
            # Chemins de stockage
            storage_base = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "storage"
            )
            uploads_dir = os.path.join(storage_base, "uploads")
            clips_dir = os.path.join(storage_base, "clips")
            
            os.makedirs(uploads_dir, exist_ok=True)
            os.makedirs(clips_dir, exist_ok=True)
            
            video_filename = f"video_{task.video_id}.mp4"
            video_path = os.path.join(uploads_dir, video_filename)
            
            # Téléchargement
            downloaded_path = download_youtube_video(task.url, video_path)
            
            if not downloaded_path or not os.path.exists(downloaded_path):
                print(f"❌ [Slot {slot_id}] Download failed for video {task.video_id}")
                storage.update_video_status(task.video_id, VideoStatus.ERROR.value)
                with self.stats_lock:
                    self.total_failed += 1
                return
            
            actual_video_path = downloaded_path
            print(f"✅ [Slot {slot_id}] Using video file: {actual_video_path}")
            
            storage.update_video(task.video_id, {"file_path": actual_video_path})
            
            # Traitement avec Groq
            print(f"🎬 [Slot {slot_id}] Processing video {task.video_id}...")
            process_video_groq(
                task.video_id,
                actual_video_path,
                clips_dir,
                task.quality_settings,
                clip_count=task.clip_count,
                plan=task.plan
            )
            
            print(f"✅ [Slot {slot_id}] Video {task.video_id} completed successfully")
            with self.stats_lock:
                self.total_completed += 1
            
        except Exception as e:
            print(f"❌ [Slot {slot_id}] Error processing video {task.video_id}: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                from utils.file_storage import get_storage
                from models.schemas import VideoStatus
                storage = get_storage()
                storage.update_video_status(task.video_id, VideoStatus.ERROR.value)
            except:
                pass
            
            with self.stats_lock:
                self.total_failed += 1
        
        finally:
            # Libérer le slot
            self._release_slot(slot_id)
    
    def _release_slot(self, slot_id: int):
        """Libère un slot de processus"""
        with self.queue_lock:
            slot = self.slots[slot_id]
            slot.is_busy = False
            slot.current_task = None
            slot.started_at = None
            
            # Sauvegarder la queue après libération du slot
            self._save_queue_to_file()
            
            print(f"✅ [Slot {slot_id}] Released and available")
    
    def _worker_thread(self):
        """Thread worker qui surveille la queue et démarre les tâches en attente"""
        print("🔄 Queue worker thread started")
        
        while True:
            try:
                # Attendre un peu avant de vérifier la queue
                time.sleep(2)
                
                # Vérifier s'il y a des tâches en attente et des slots disponibles
                if not self.task_queue.empty():
                    available_slot = self._find_available_slot()
                    
                    if available_slot is not None:
                        # Récupérer la prochaine tâche
                        try:
                            task = self.task_queue.get_nowait()
                            print(f"📤 Dequeuing video {task.video_id} for processing")
                            self._start_task_in_slot(available_slot, task)
                        except queue.Empty:
                            pass
            
            except Exception as e:
                print(f"⚠️ Error in worker thread: {e}")
                time.sleep(5)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel de la queue et des processus"""
        with self.queue_lock:
            active_tasks = []
            for slot_id, slot in self.slots.items():
                if slot.is_busy and slot.current_task:
                    task = slot.current_task
                    elapsed = (datetime.now() - slot.started_at).total_seconds() if slot.started_at else 0
                    active_tasks.append({
                        "slot_id": slot_id,
                        "video_id": task.video_id,
                        "plan": task.plan,
                        "elapsed_seconds": int(elapsed)
                    })
            
            queue_size = self.task_queue.qsize()
        
        with self.stats_lock:
            stats = {
                "total_submitted": self.total_submitted,
                "total_completed": self.total_completed,
                "total_failed": self.total_failed
            }
        
        return {
            "max_processes": self.max_processes,
            "active_processes": len(active_tasks),
            "active_tasks": active_tasks,
            "queued_tasks": queue_size,
            "available_slots": self.max_processes - len(active_tasks),
            "statistics": stats
        }
    
    def _save_queue_to_file(self):
        """Sauvegarde la queue actuelle dans un fichier JSON"""
        import json
        
        try:
            # Extraire toutes les tâches de la queue sans les retirer
            tasks_list = []
            temp_queue = queue.Queue()
            
            while not self.task_queue.empty():
                try:
                    task = self.task_queue.get_nowait()
                    tasks_list.append(task.to_dict())
                    temp_queue.put(task)
                except queue.Empty:
                    break
            
            # Remettre les tâches dans la queue
            self.task_queue = temp_queue
            
            # Sauvegarder dans le fichier
            with open(self.queue_file_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_list, f, indent=2, ensure_ascii=False)
            
            if tasks_list:
                print(f"💾 Queue saved: {len(tasks_list)} tasks in {self.queue_file_path}")
        
        except Exception as e:
            print(f"⚠️ Error saving queue to file: {e}")
    
    def _load_queue_from_file(self):
        """Charge la queue depuis le fichier JSON au démarrage"""
        import json
        import os
        
        if not os.path.exists(self.queue_file_path):
            print("📂 No existing queue file found")
            return
        
        try:
            with open(self.queue_file_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            if not tasks_data:
                print("📂 Queue file is empty")
                return
            
            # Restaurer les tâches dans la queue
            for task_dict in tasks_data:
                task = VideoTask.from_dict(task_dict)
                self.task_queue.put(task)
            
            print(f"📂 Loaded {len(tasks_data)} tasks from queue file")
            
            # Nettoyer le fichier après chargement
            with open(self.queue_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        except Exception as e:
            print(f"⚠️ Error loading queue from file: {e}")
            import traceback
            traceback.print_exc()


# Instance globale singleton
def get_process_manager() -> ProcessPoolManager:
    """Retourne l'instance singleton du gestionnaire de processus"""
    return ProcessPoolManager()
