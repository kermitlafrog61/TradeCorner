import os
import logging

from celery import Task
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


logger = logging.getLogger('main')

class LogErrorsTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception('Celery task failed: %s', str(exc), exc_info=False)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)
