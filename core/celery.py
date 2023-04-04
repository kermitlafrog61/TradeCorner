import os
from datetime import timedelta

from django.utils import timezone
from celery import Celery
# from knox.models import AuthToken

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):...
    # sender.add_periodic_task(
        # timedelta(seconds=10), delete_expired_tokens.s(), name='delete expired tokens'
    # )


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# @app.task
# def delete_expired_tokens():
#     AuthToken.objects.filter(expires__lte=timezone.now()).delete()
