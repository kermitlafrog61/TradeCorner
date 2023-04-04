from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers


def create_activation_code(user):
    user.activation_code = get_random_string(10)
    user.save()


def password_confirmation(pwd, pwd_conf):
    if pwd != pwd_conf:
        raise serializers.ValidationError('Passwords does not match')
    elif not (pwd and pwd_conf):
        raise serializers.ValidationError('Passwords cannot be left empty')
