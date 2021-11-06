from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from api import views


email_verify = views.EmailVerifyViewSet.as_view({
    'get': 'update',
})
email_verify_send = views.EmailVerifySendViewSet.as_view({
    'get': 'create',
})
user_detail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
user_list = views.UserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
user_profiles = views.ProfileViewSet.as_view({
    'get': 'list',
})
user_profile_detail = views.ProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
register_user = views.RegisterUserViewSet.as_view({
    'post': 'create',
})

urlpatterns = [
    path('', views.APIRootView.as_view()),
    path('register/', register_user, name='register_user'),
    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('users/', user_list, name='user_list'),
    path('users/<int:pk>/', user_detail, name='user_detail'),
    path('users/profiles/', user_profiles, name='user_profile'),
    path('users/profiles/<int:pk>', user_profile_detail, name='user_profile_detail'),
    path('email/verify/', email_verify, name='email_verify'),
    path('email/verify-send/', email_verify_send, name='email_verify_send'),
]

