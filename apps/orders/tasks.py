from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from celery import shared_task

from .models import Order
from .utils import create_activation_code
from core.celery import LogErrorsTask
from apps.products.models import Product

User = get_user_model()


@shared_task(base=LogErrorsTask)
def send_updated_status(order_id):
    order = Order.objects.get(pk=order_id)
    user = order.user
    subject = 'Order status update'
    message = f"""
    Hello {user.username},
    There's status update on your {order.product.title} it is now {order.get_status_display()}"""
    if order.status == 'DELIVER':
        create_activation_code(order)
        activation_code = order.activation_code
        complete_link = f"{settings.BASE_URL}{reverse('complete', args=[activation_code])}"
        message += f"""
    Proceed this link to complete your order {complete_link}"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )


@shared_task(base=LogErrorsTask)
def send_cancel_status(order_id, user_id):
    order = Order.objects.get(pk=order_id)
    user = User.objects.get(pk=user_id)
    subject = 'Order was canceled'
    if user == order.user:
        """ Check if user is Author """
        message = f"""
    Hello {order.product.user.username},
    {user.username} have canceled your order on {order.product.title}
    """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.product.user.email],
            fail_silently=False
        )

    elif user == order.product.user:
        """ Checks if user is Owner """
        message = f"""
    Hello {order.user.username},
    The owner of the {order.product.title} have cancelled your order
    """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.user.email],
            fail_silently=False
        )


@shared_task(base=LogErrorsTask)
def send_order_created(order_id):
    order = Order.objects.get(pk=order_id)
    activation_code = order.activation_code
    user = order.product.user
    confirmation_link = f"{settings.BASE_URL}{reverse('confirm', args=[activation_code])}"
    subject = f'New order for {order.product.title}'
    message = f"""
    Hello {user.username},
    User {order.user.username} have ordered your {order.product.title}
    Proceed this link to confirm {confirmation_link}"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )
