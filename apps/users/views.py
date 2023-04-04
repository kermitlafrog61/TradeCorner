from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from knox.models import AuthToken

from .serializers import (RegistrationSerializer, ActivationSerializer,
                          LoginSerializer, PasswordUpdateSerializer,
                          PasswordRestoreSerializer, UserSerializer)
from .utils import create_activation_code

User = get_user_model()


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


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# class Logout(generics.DestroyAPIView):
#     permission_classes = (permissions.IsAuthenticated,)

#     def delete(self, request: Request) -> Response:
#         Token.objects.get(user=request.user).delete()
#         return Response(
#             {'message': 'Loged out'},
#             status.HTTP_200_OK)


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


class PasswordRestore(generics.GenericAPIView):
    serializer_class = PasswordRestoreSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        create_activation_code(request.user)
        # TODO
        # send_activation_code(request.user, message="""
        # Here's your password restore code""", subject='Password restore')
        # return Response(
        #     {'message': 'Your restore code was sent to your email'},
        #     status=status.HTTP_200_OK)

    def put(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {'message': 'Password updated succesfully'},
            status=status.HTTP_200_OK)
