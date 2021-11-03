from rest_framework.response import Response
from rest_framework.views import APIView


class RootView(APIView):
    """
    Root of beckend
    """

    def get(self, request, *args, **kwargs):
        return Response({
            'admin': request.build_absolute_uri('admin/'),
            'auth': request.build_absolute_uri('auth/'),
            'api': request.build_absolute_uri('api/'),
        })
