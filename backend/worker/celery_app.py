from celery import Celery

celery_app = Celery('rag_worker', broker='redis://localhost:6379/0')

# Task Discovery
celery_app.autodiscover_tasks(['worker'])

# Optional: Import tasks directly to ensure registration
from worker import tasks