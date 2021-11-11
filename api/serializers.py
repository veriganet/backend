from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import User

from api.views import Profile
from api.models import Organization, BlockChain


class BlockChainSerializer(serializers.ModelSerializer):
    """
    Serializer for BolockChain model
    """
    class Meta:
        model = BlockChain
        fields = '__all__'


class BlockChainUserSerializer(serializers.ModelSerializer):
    """
    Serializer for BolockChain model
    """
    class Meta:
        model = BlockChain
        read_only_fields = ['id', 'created']
        fields = [
            'id',
            'abbreviation',
            'name',
            'description',
            'created',
            'enable_custom_domain',
            'custom_domain',
            'faucet_public_key',
            'landing_public_key',
            'canary_beta_public_key',
            'canary_live_public_key',
            'canary_test_public_key',
            'genesis_beta_account',
            'genesis_beta_work',
            'genesis_beta_signature',
            'genesis_dev_public_key',
            'genesis_dev_private_key',
            'genesis_dev_account',
            'genesis_dev_work',
            'genesis_dev_signature',
            'genesis_live_public_key',
            'genesis_live_account',
            'genesis_live_work',
            'genesis_live_signature',
            'genesis_test_public_key',
            'genesis_test_account',
            'genesis_test_work',
            'genesis_test_signature',
            'beta_pre_conf_rep_public_key_0',
            'beta_pre_conf_rep_public_key_1',
            'beta_pre_conf_rep_private_key_0',
            'beta_pre_conf_rep_private_key_1',
            'live_pre_conf_rep_public_key_0',
            'live_pre_conf_rep_public_key_1',
            'live_pre_conf_rep_public_key_2',
            'live_pre_conf_rep_public_key_3',
            'live_pre_conf_rep_public_key_4',
            'live_pre_conf_rep_public_key_5',
            'live_pre_conf_rep_public_key_6',
            'live_pre_conf_rep_public_key_7',
            'live_pre_conf_rep_private_key_0',
            'live_pre_conf_rep_private_key_1',
            'live_pre_conf_rep_private_key_2',
            'live_pre_conf_rep_private_key_3',
            'live_pre_conf_rep_private_key_4',
            'live_pre_conf_rep_private_key_5',
            'live_pre_conf_rep_private_key_6',
            'live_pre_conf_rep_private_key_7',
            'live_node_peering_port',
            'beta_node_peering_port',
            'test_node_peering_port',
            'live_rpc_port',
            'beta_rpc_port',
            'test_rpc_port',
            'binary_public',
            's3_bucket_name',
            'number_of_peers',
            'created_by',
            'organization',
            'owner',
        ]



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
    class Meta:
        model = Profile
        fields = ['id', 'is_email_verified', 'organization']
        read_only_fields = ['id', 'is_email_verified']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

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
