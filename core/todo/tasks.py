from celery import shared_task
from .models import Task


@shared_task
def clear_done_tasks():
    Task.objects.filter(complete=True).delete()
