import jwt
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, status
from templated_email import send_templated_mail

from api.permissions import IsOwner, IsUserOwner
from api.models import Profile, Organization, BlockChain
from api.serializers import CustomTokenObtainPairSerializer, UserSerializer, \
    RegisterSerializer, RegisterUserSerializer, ProfileSerializer, \
    OrganizationSerializer, BlockChainSerializer, UserUserSerializer, \
    UserProfileSerializer, BlockChainUserSerializer, OrganizationUserSerializer


class APIRootView(APIView):
    """
    Root of backed api
    This is the actual api endpoint for all api calls
    """

    def get(self, request, format=None):
        return Response({
            # admin
            'admin/blockchains': reverse('blockchain_list', request=request, format=format),
            'admin/organizations': reverse('organization_list', request=request, format=format),
            'admin/users': reverse('user_list', request=request, format=format),
            'admin/users/profiles': reverse('user_profile', request=request, format=format),
            # user
            'user/blockchains': reverse('user_blockchain_list', request=request, format=format),
            'user/email/verify': reverse('email_verify', request=request, format=format),
            'user/email/verify-send': reverse('email_verify_send', request=request, format=format),
            'user/password-reset': reverse('user_password_reset', request=request, format=format),
            'user/password-reset/confirm': reverse('user_password_reset_confirm', request=request,
                                                          format=format),
            'user/password-reset/validate': reverse('user_password_reset_validate', request=request,
                                                           format=format),
            'user/organizations': reverse('user_organization_list', request=request, format=format),
            'user/profile': reverse('user_user_profile_detail', request=request, format=format),
            'user/user': reverse('user_user_detail', request=request, format=format),
            # public
            'register': reverse('register_user', request=request, format=format),
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token/refresh': reverse('token_refresh', request=request, format=format),
            'token/verify': reverse('token_verify', request=request, format=format),
        })


#
# admin views - start
#
class BlockChainViewSet(viewsets.ModelViewSet):
    """
    List, retrieve, update, partial update and delete actions for blockchains

    blockchain details:
    blockchains/<pk>/
    """
    queryset = BlockChain.objects.all()
    serializer_class = BlockChainSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    """
    list, create, retrieve, update and destroy actions for users

    for user details:
    users/<pk>/
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    List, retrieve, update, partial update and delete actions for organizations

    for organization details:
    organizations/<pk>/
    """
    queryset = Organization.objects.all().order_by('id')
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    List, retrieve, update actions for user profiles
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
# admin views - end


#
# user views - start
#
class BlockChainUserViewSet(viewsets.ModelViewSet):
    """
    List, retrieve, update, partial update and delete actions for blockchains

    blockchain details:
    user/blockchains/<pk>/
    """
    model = BlockChain
    serializer_class = BlockChainUserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user

        return BlockChain.objects.filter(owner=user)


class EmailVerifySendViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args,**kwargs):
        user_email = request.GET.get('email')

        if not user_email:
            return Response({"error": 'Verification email NOT sent'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            # get user by email parameter
            user = User.objects.get(email=user_email)

            # check if user email verified
            if not user.profile.is_email_verified:
                token = str(RefreshToken.for_user(user).access_token)

                current_site = get_current_site(request).domain
                verify_url = request.build_absolute_uri(reverse('email_verify')) + "?token=" + token

                send_templated_mail(
                    template_name='email_verify',
                    from_email='verify@' + current_site,
                    recipient_list=[user.email],
                    context={
                        'full_name': user.get_full_name(),
                        'verify_url': verify_url,
                    }
                )

            return Response({"status": 'Verification email sent'},
                            status=status.HTTP_200_OK)


class EmailVerifyViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def update(self, request):
        token = request.GET.get('token')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(email=payload['user_id'])
            if not user.profile.is_email_verified:
                user.profile.is_email_verified = True
                user.save()
            return Response({'status': 'Verified'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Link Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid / Missing Token'}, status=status.HTTP_400_BAD_REQUEST)


class OrganizationUserViewSet(viewsets.ModelViewSet):
    """
    List, retrieve, update, partial update and delete actions for organizations

    for organization details:
    organizations/<pk>/
    """
    model = Organization
    serializer_class = OrganizationUserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user

        return Organization.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        serializer = OrganizationUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUserViewSet(viewsets.ModelViewSet):
    """
    Retrieve, update, partial update and delete actions for user
    """
    queryset = User.objects.all()
    serializer_class = UserUserSerializer
    permission_classes = [IsAuthenticated, IsUserOwner]

    def get_object(self):
        return self.request.user


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    Retrieve, update, partial update and delete actions for profile
    """
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsUserOwner]

    def get_object(self):
        return self.request.user.profile

# user views - end


#
# public views
#

class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Creates JWT token pair with email authantication
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class RegisterUserViewSet(viewsets.ModelViewSet):
    """
    Register new user

    :email
    :password
    :first_name
    :last_name
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user = User.objects.get(email=user.email)
        token = str(RefreshToken.for_user(user).access_token)

        current_site = get_current_site(request).domain
        verify_url = request.build_absolute_uri(reverse('user_password_reset_confirm'))+"?token=" + token

        send_templated_mail(
            template_name='welcome',
            from_email='welcome@'+current_site,
            recipient_list=[user.email],
            context={
                'full_name': user.get_full_name(),
                'verify_url': verify_url,
            }
        )

        return Response({
            "user": RegisterUserSerializer(
                user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)
# public views - end
