from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


User = get_user_model()


@shared_task
def send_activation_email(user_id):
    user = User.objects.get(pk=user_id)
    activation_url = reverse('activate', args=[user.activation_code])
    activation_link = f"{settings.BASE_URL}{activation_url}"
    subject = 'Activate Your Account'
    message = f"""
    Hello {user.username},
    please click the following link to activate your account: {activation_link}"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )


@shared_task
def send_password_restore(user_id):
    user = User.objects.get(pk=user_id)
    activation_code = user.activation_code
    subject = 'Restoring password'
    message = f"""
    Hello {user.username},
    here is your activation code for : """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )
