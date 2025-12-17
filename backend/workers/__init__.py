from workers.celery_config import celery_app
from typing import Dict

@celery_app.task(bind=True)
def get_task_status(self, task_id: str) -> Dict:
    """Get the status of a Celery task"""
    
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        response = {
            'state': task_result.state,
            'status': 'Pending...'
        }
    elif task_result.state != 'FAILURE':
        response = {
            'state': task_result.state,
            'status': task_result.info.get('status', ''),
            'result': task_result.info
        }
    else:
        response = {
            'state': task_result.state,
            'status': str(task_result.info),
        }
    
    return response
