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
from rest_framework import generics, viewsets, status
from templated_email import send_templated_mail

from api.permissions import IsOwner
from api.utils import Util
from api.models import Profile
from api.serializers import CustomTokenObtainPairSerializer, UserSerializer, \
    RegisterSerializer, RegisterUserSerializer, ProfileSerializer


class APIRootView(APIView):
    """
    Root of backed api
    This is the actual api endpoint for all api calls
    """

    def get(self, request, format=None):
        return Response({
            'email/verify': reverse('email_verify', request=request, format=format),
            'email/verify-send': reverse('email_verify_send', request=request, format=format),
            'register': reverse('register_user', request=request, format=format),
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token/refresh': reverse('token_refresh', request=request, format=format),
            'token/verify': reverse('token_verify', request=request, format=format),
            'users': reverse('user_list', request=request, format=format),
            'users/password-reset': reverse('user_password_reset', request=request, format=format),
            'users/password-reset/confirm': reverse('user_password_reset_confirm', request=request, format=format),
            'users/password-reset/validate': reverse('user_password_reset_validate', request=request, format=format),
            'users/profiles': reverse('user_profile', request=request, format=format),
        })


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Creates JWT token pair with email authantication
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    list, create, retreive, update and destroy actoins for users

    for user details:
    users/<pk>/
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    List, retreive, update actions for user profiles
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


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
        relative_link = reverse('email_verify')
        verify_url = 'https://' + current_site + relative_link + "?token=" + token

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


class EmailVerifySendViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args,**kwargs):
        user_email = request.GET.get('email')

        if not user_email:
            return Response({"error": 'Verification Email NOT Sent'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            # get user by email parameter
            user = User.objects.get(email=user_email)

            # check if user email verified
            if not user.profile.is_email_verified:
                token = str(RefreshToken.for_user(user).access_token)

                current_site = get_current_site(request).domain
                relative_link = reverse('email_verify')
                absurl = 'http://' + current_site + relative_link + "?token=" + token

                email_body = '''Hello {first_name} {last_name}\n
                Please verify your email address with following link:\n
                {absurl}''' \
                    .format(absurl=absurl,
                            first_name=user.first_name,
                            last_name=user.last_name)

                data = {
                    'email_body': email_body,
                    'email_subject': 'Verify Your Email',
                    'email_receiver': user.email
                }

                Util.send_email(data=data)
            return Response({"info": 'Verification Email Sent'},
                            status=status.HTTP_200_OK)


class EmailVerifyViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def update(self, request):
        token = request.GET.get('token')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(email=payload['user_id'])
            if not user.profile.is_email_verified:
                user.profile.is_email_verified = True
                user.save()
            return Response({'info': 'Verified'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Link Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid / Missing Token'}, status=status.HTTP_400_BAD_REQUEST)

