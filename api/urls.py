from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from django_rest_passwordreset import views as drp_views
from api import views

#
# admin
#
blockchain_list = views.BlockChainViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
blockchain_detail = views.BlockChainViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
blockchain_build_deploy = views.BlockChainBuildDeployViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
blockchain_build_deploy_detail = views.BlockChainBuildDeployViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
blockchain_build = views.BlockChainBuildViewSet.as_view({
    'get': 'list',
})
blockchain_build_list = views.BlockChainBuildViewSet.as_view({
    'get': 'blockchain_build_list',
})
blockchain_build_build = views.BlockChainBuildViewSet.as_view({
    'post': 'create',
})
blockchain_build_detail = views.BlockChainBuildViewSet.as_view({
    'get': 'retrieve',
})
blockchain_build_restart = views.BlockChainBuildViewSet.as_view({
    'post': 'restart',
})
blockchain_deploy = views.BlockChainDeployViewSet.as_view({
    'get': 'list',
})
blockchain_deploy_list = views.BlockChainDeployViewSet.as_view({
    'get': 'blockchain_deploy_list',
})
blockchain_deploy_deploy = views.BlockChainDeployViewSet.as_view({
    'post': 'create',
})
blockchain_deploy_detail = views.BlockChainDeployViewSet.as_view({
    'get': 'retrieve',
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
user_password_reset = drp_views.ResetPasswordRequestTokenViewSet.as_view({
    'get': 'create',
})
user_password_reset_confirm = drp_views.ResetPasswordConfirmViewSet.as_view({
    'get': 'create',
})
user_password_reset_validate = drp_views.ResetPasswordValidateTokenViewSet.as_view({
    'get': 'create',
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
organization_list = views.OrganizationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
organization_detail = views.OrganizationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

#
# user - start
#
email_verify = views.EmailVerifyViewSet.as_view({
    'get': 'update',
})
email_verify_send = views.EmailVerifySendViewSet.as_view({
    'get': 'create',
})
register_user = views.RegisterUserViewSet.as_view({
    'post': 'create',
})
user_blockchain_list = views.BlockChainUserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
user_blockchain_detail = views.BlockChainUserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
user_organization_list = views.OrganizationUserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
user_organization_detail = views.OrganizationUserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
user_user_detail = views.UserUserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
user_user_profile_detail = views.UserProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
user_geo_location = views.GeoLocationUserViewSet.as_view({
    'get': 'retrieve',
})
# user - end

#
# public - start
#

# public - end

urlpatterns = [
    # root
    path('', views.APIRootView.as_view()),
    # admin
    path('admin/blockchains/', blockchain_list, name='blockchain_list'),
    path('admin/blockchains/<int:pk>', blockchain_detail, name='blockchain_detail'),
    path('admin/blockchains/builds/', blockchain_build, name='blockchain_build'),
    path('admin/blockchains/builds/<int:pk>', blockchain_build_list, name='blockchain_build_list'),
    path('admin/blockchains/builds/build/<int:pk>', blockchain_build_build, name='blockchain_build_build'),
    path('admin/blockchains/builds/detail/<int:pk>', blockchain_build_detail, name='blockchain_build_detail'),
    path('admin/blockchains/builds/restart/<int:pk>', blockchain_build_restart, name='blockchain_build_restart'),
    path('admin/blockchains/builds-deploys/', blockchain_build_deploy, name='blockchain_build_deploy'),
    path('admin/blockchains/builds-deploys/<int:pk>', blockchain_build_deploy_detail, name='blockchain_build_deploy_detail'),
    path('admin/blockchains/deploys/', blockchain_deploy, name='blockchain_deploy'),
    path('admin/blockchains/deploys/<int:pk>', blockchain_deploy_list, name='blockchain_deploy_list'),
    path('admin/blockchains/deploys/deploy/<int:pk>', blockchain_deploy_deploy, name='blockchain_deploy_deploy'),
    path('admin/blockchains/deploys/detail/<int:pk>', blockchain_deploy_detail, name='blockchain_deploy_detail'),
    path('admin/organizations/', organization_list, name='organization_list'),
    path('admin/organizations/<int:pk>', organization_detail, name='organization_detail'),
    path('admin/users/', user_list, name='user_list'),
    path('admin/users/<int:pk>/', user_detail, name='user_detail'),
    path('admin/users/password-reset/', user_password_reset, name='user_password_reset'),
    path('admin/users/password-reset/confirm', user_password_reset_confirm, name='user_password_reset_confirm'),
    path('admin/users/password-reset/validate', user_password_reset_validate, name='user_password_reset_validate'),
    path('admin/users/profiles/', user_profiles, name='user_profile'),
    path('admin/users/profiles/<int:pk>', user_profile_detail, name='user_profile_detail'),
    # user
    path('user/blockchains/', user_blockchain_list, name='user_blockchain_list'),
    path('user/blockchains/<int:pk>', user_blockchain_detail, name='user_blockchain_detail'),
    path('user/geolocation/', user_geo_location, name='user_geo_location'),
    path('user/email/verify/', email_verify, name='email_verify'),
    path('user/email/verify-send/', email_verify_send, name='email_verify_send'),
    path('user/organizations/', user_organization_list, name='user_organization_list'),
    path('user/organizations/<int:pk>', user_organization_detail, name='user_organization_detail'),
    path('user/profile/', user_user_profile_detail, name='user_user_profile_detail'),
    path('user/user/', user_user_detail, name='user_user_detail'),
    # public
    path('register/', register_user, name='register_user'),
    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
]

