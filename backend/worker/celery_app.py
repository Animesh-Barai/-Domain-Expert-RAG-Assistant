from celery import Celery

celery_app = Celery('rag_worker', broker='redis://localhost:6379/0')