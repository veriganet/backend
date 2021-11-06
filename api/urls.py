from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from api import views


register_user = views.RegisterUserViewSet.as_view({
    'post': 'create',
})
user_list = views.UserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
user_detail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
email_verify = views.VerifyEmailViewSet.as_view({
    'get': 'update',
})


urlpatterns = [
    path('', views.APIRootView.as_view()),
    path('register/', register_user, name='register_user'),
    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('users/', user_list, name='user_list'),
    path('users/<int:pk>/', user_detail, name='user_detail'),
    path('email/verify/', email_verify, name='email_verify'),
]

