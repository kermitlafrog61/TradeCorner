from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from celery import shared_task

from core.celery import LogErrorsTask