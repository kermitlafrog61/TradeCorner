from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from .utils import create_activation_code, password_confirmation
from .tasks import send_activation_email


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        write_only_fields = ('password', 'password_confirm')

    def validate(self, attrs: dict):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        password_confirmation(password, password_confirm)
        return attrs

    def validate_email(self, email: str):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такая почта уже существует')
        return email

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        create_activation_code(user)
        send_activation_email.delay(user.id)
        return user


class ActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=10)

    def validate_activation_code(self, activation_code: str):
        if not User.objects.filter(activation_code=activation_code).exists():
            raise serializers.ValidationError(
                'The activation code is not correct!')
        return activation_code

    def activate(self):
        code = self.validated_data.get('activation_code')
        user = User.objects.get(activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid Details.")


class PasswordUpdateSerializer(serializers.Serializer):
    old_pwd = serializers.CharField(max_length=128)
    new_pwd = serializers.CharField(max_length=128)
    new_pwd_conf = serializers.CharField(max_length=128)

    def validate(self, attrs):
        old_pwd = attrs.get('old_pwd')
        new_pwd = attrs.get('new_pwd')
        new_pwd_conf = attrs.get('new_pwd_conf')
        user = self.context.get('request').user

        if old_pwd == new_pwd:
            raise serializers.ValidationError(
                'New password cannot remain same')

        password_confirmation(new_pwd, new_pwd_conf)

        if not user.check_password(old_pwd):
            raise serializers.ValidationError('Password is not correct')

        user.set_password(new_pwd)
        user.save()
        return attrs


class PasswordRestoreSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=10)
    new_pwd = serializers.CharField(max_length=128)
    new_pwd_conf = serializers.CharField(max_length=128)

    def validate(self, attrs):
        password_confirmation(attrs.get('new_pwd'),
                              attrs.get('new_pwd_conf'))
        user = self.context.get('request').user
        if user.activation_code != attrs.get('activation_code'):
            raise serializers.ValidationError('Restore code is not correct')
        user.set_password(attrs.get('new_pwd'))
        user.activation_code = ''
        user.save()
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
