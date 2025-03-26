from celery import Celery
from emailocr import EmailProcessor

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_email_task(email_content):
    processor = EmailProcessor()
    processor.process_email(email_content)
