from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, \
    IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, viewsets

from api.permissions import IsOwner
from api.serializers import CustomTokenObtainPairSerializer, UserSerializer


class APIRootView(APIView):
    """
    Root of backed api
    This is the actual api endpoint for all api calls
    """
    def get(self, request, format=None):
        return Response({
            'hello': reverse('hello', request=request, format=format),
            'users': reverse('user_list', request=request, format=format),
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token/refresh': reverse('token_refresh', request=request, format=format),
            'token/verify': reverse('token_verify', request=request, format=format),
        })


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Creates JWT token pair with email authantication
    """
    serializer_class = CustomTokenObtainPairSerializer


class HelloView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        content = {
            'message': 'Hello, World!',
            'owner': 'kelepirci',
        }
        return Response(content)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    """
    list, create, retreive, update and destroy actoins for users

    for user details:
    users/<pk>/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]