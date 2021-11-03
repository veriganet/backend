from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import User


class EmailTokenObtainSerializer(TokenObtainSerializer):
    """
    Use email for username_field
    """
    username_field = User.EMAIL_FIELD


class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    """
    Custom class and methodes to get, refresh and validate token
    """
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'email',
                  'first_name',
                  'last_name',
                  'groups',
                  'user_permissions',
                  'is_staff',
                  'is_active',
                  'is_superuser',
                  'last_login',
                  'date_joined']


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'email',
                  'password',
                  'first_name',
                  'last_name',
                  'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'password',
                  'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['email'],
            password=validated_data['password']
        )
        return user
