from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import User

from api.views import Profile
from api.models import Organization, BlockChain, BlockChainBuildDeploy, DroneCIServer


class OwnerPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.model = kwargs.pop('model')
        assert hasattr(self.model, 'owner')
        super().__init__(**kwargs)

    def get_queryset(self):
        return self.model.objects.filter(owner=self.context['request'].user)


class BlockChainBuildDeploySerializer(serializers.ModelSerializer):
    """
    Serializer for BolockChainDeploy model
    """

    class Meta:
        model = BlockChainBuildDeploy
        fields = '__all__'


class BlockChainSerializer(serializers.ModelSerializer):
    """
    Serializer for BolockChain model
    """
    # disabled for now for simplicity
    # build_deploy = BlockChainBuildDeploySerializer(many=True, read_only=True)

    class Meta:
        model = BlockChain
        fields = '__all__'


class BlockChainUserSerializer(serializers.ModelSerializer):
    """
    Serializer for BolockChain model
    """
    organization = OwnerPrimaryKeyRelatedField(model=Organization)

    class Meta:
        model = BlockChain
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
            'organization': {'read_only': False},
            'owner': {'read_only': True}
        }


class BlockChainUserUpdatePatchSerializer(serializers.ModelSerializer):
    """
    Serializer for BlockChain model with readonly fields
    Applies to update and patch actions
    """
    organization = OwnerPrimaryKeyRelatedField(model=Organization)

    class Meta:
        model = BlockChain
        fields = [
            'id',
            'organization',
            'name',
            'description',
            'enable_custom_domain',
            'custom_domain',
            'binary_public',
            'number_of_peers',
            'debug',
            'logging',
        ]
        extra_kwargs = {
            'created_by': {'read_only': True},
            'organization': {'read_only': False},
            'owner': {'read_only': True}
        }


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


class DroneCIServerSerializer(serializers.ModelSerializer):
    """
    Serializer for DroneCIServer model
    """
    class Meta:
        model = DroneCIServer
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model
    """
    class Meta:
        model = Organization
        fields = '__all__'


class OrganizationUserSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model
    """

    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
            'owner': {'read_only': True}
        }


class ProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer for user profile detail
    """

    class Meta:
        model = Profile
        fields = '__all__'

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of user
        :return: returns a successfully created student record
        """
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        profile, created = Profile.objects.update_or_create(user=user)

        return profile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Profile serializer for current user
    """
    organization = OwnerPrimaryKeyRelatedField(model=Organization)

    class Meta:
        model = Profile
        fields = ['id', 'is_email_verified', 'organization']
        read_only_fields = ['id', 'is_email_verified']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class UserUserSerializer(serializers.ModelSerializer):
    """
    User serializer for current user
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'profile', 'last_login', 'first_name', 'last_name',
                  'email', 'date_joined']
        read_only_fields = ['id', 'profile', 'last_login', 'email', 'date_joined']


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'email',
                  'password',
                  'first_name',
                  'last_name',
                  'is_active',
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
            password=validated_data['password'],
        )
        return user
