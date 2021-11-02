from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from api import views


user_list = views.UserViewSet.as_view({
    'get': 'list',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
user_detail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})


urlpatterns = [
    path('', views.APIRootView.as_view()),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('users/', user_list, name='user_list'),
    path('users/<int:pk>/', user_detail, name='user_detail'),
    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
]

