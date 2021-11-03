from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, viewsets

from api.permissions import IsOwner
from api.serializers import CustomTokenObtainPairSerializer, UserSerializer, \
    RegisterSerializer, RegisterUserSerializer


class APIRootView(APIView):
    """
    Root of backed api
    This is the actual api endpoint for all api calls
    """

    def get(self, request, format=None):
        return Response({
            'register': reverse('register_user', request=request, format=format),
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token/refresh': reverse('token_refresh', request=request, format=format),
            'token/verify': reverse('token_verify', request=request, format=format),
            'users': reverse('user_list', request=request, format=format),
        })


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Creates JWT token pair with email authantication
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    list, create, retreive, update and destroy actoins for users

    for user details:
    users/<pk>/
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class RegisterUserViewSet(viewsets.ModelViewSet):
    """
    Register new user
    :email
    :password
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": RegisterUserSerializer(
                user, context=self.get_serializer_context()).data
        })
