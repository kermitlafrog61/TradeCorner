from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from knox.models import AuthToken
from knox.settings import knox_settings
import logging

from .serializers import (RegistrationSerializer, ActivationSerializer,
                          LoginSerializer, PasswordUpdateSerializer,
                          PasswordRestoreSerializer, UserSerializer)
from .utils import create_activation_code
from .tasks import send_password_restore

User = get_user_model()

logger = logging.getLogger('main')


class Registration(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'message': 'Thanks for the registration! Check your email for the activation code'},
            status.HTTP_201_CREATED)


class Activation(generics.RetrieveAPIView):
    serializer_class = ActivationSerializer

    def get(self, request, activation_code):
        serializer = self.get_serializer(
            data={'activation_code': activation_code})
        serializer.is_valid(raise_exception=True)
        serializer.activate()
        return Response({'message': 'Account succesfully activated!'})


class LoginAPI(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def post(self, request, *args, **kwargs):
        token_limit_per_user = self.get_token_limit_per_user()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordUpdate(generics.UpdateAPIView):
    serializer_class = PasswordUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {'message': 'Password was updated succesfully'},
            status=status.HTTP_200_OK)


class PasswordRestore(generics.RetrieveUpdateAPIView):
    serializer_class = PasswordRestoreSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        create_activation_code(request.user)
        send_password_restore.delay(request.user.id)
        return Response(
            {'message': 'Your restore code was sent to your email'},
            status=status.HTTP_200_OK)

    def put(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {'message': 'Password updated succesfully'},
            status=status.HTTP_200_OK)