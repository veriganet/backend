from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from api import views

urlpatterns = [
    path('', views.APIRootView.as_view()),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('users/', views.UserList.as_view(), name='user_list'),
    path('users/<int:pk>', views.UserDetail.as_view(), name='user_detail'),
    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
]

