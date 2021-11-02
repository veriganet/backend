from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from api.permissions import IsOwner
from api.serializers import CustomTokenObtainPairSerializer


class APIRootView(APIView):
    """
    Root of backed api
    This is the actual api endpoint for all api calls
    """
    def get(self, request, format=None):
        return Response({
            'hello': reverse('hello', request=request, format=format),
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token/refresh': reverse('token_refresh', request=request, format=format),
            'token/verify': reverse('token_verify', request=request, format=format),
        })


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class HelloView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        content = {
            'message': 'Hello, World!',
            'owner': 'kelepirci',
        }
        return Response(content)
