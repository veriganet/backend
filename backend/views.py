from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


class RootView(APIView):
    """
    Root of beckend
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return Response({
            'api': request.build_absolute_uri('api/'),
        })
