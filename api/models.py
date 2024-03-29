from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from encrypted_model_fields.fields import EncryptedCharField

from django.db.models.signals import post_save
from django.dispatch import receiver


# make email unique field
User._meta.get_field('email')._unique = True
# make username field None
User.username = None
# make USERNAME_FIELD email
User.USERNAME_FIELD = 'email'
# remove REQUIRED_FIELDS
User.REQUIRED_FIELDS = ['username']


class Organization(models.Model):
    name = models.CharField(max_length=128, blank=False)
    description = models.TextField(max_length=2048, blank=True, default='')
    email = models.EmailField(max_length=254, blank=True, default='')
    address = models.TextField(max_length=2048, blank=True, default='')
    url = models.URLField(max_length=254, blank=True, default='')
    coincapmarket_url = models.URLField(max_length=254, blank=True, default='')
    discord_url = models.URLField(max_length=254, blank=True, default='')
    facebook_url = models.URLField(max_length=254, blank=True, default='')
    linkedin_url = models.URLField(max_length=254, blank=True, default='')
    twitter_url = models.URLField(max_length=254, blank=True, default='')
    github_url = models.URLField(max_length=254, blank=True, default='')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    created_by = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='organization_created_by')
    deleted = models.BooleanField(null=False, default=False)
    deleted_at = models.DateTimeField(auto_now=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_delete_by', null=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='organization_owner')

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        ordering = ['id']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    is_email_verified = models.BooleanField(default=False, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['id']


class BlockChain(models.Model):
    CREATED = 1
    DEPLOYING = 2
    DEPLOYED = 3
    PENDING = 4
    SUSPENDED = 4
    ERROR = 5
    STATUS = (
        (CREATED, 'Created'),
        (DEPLOYING, 'Deploying'),
        (DEPLOYED, 'Deployed'),
        (PENDING, 'Pending'),
        (SUSPENDED, 'Suspended'),
        (ERROR, 'Error'),
    )

    # [epoch1],[epoch2],[receive]
    BANANO = 'fffffe0000000000,fffffff000000000,0000000000000000'
    NANO = 'ffffffc000000000,fffffff800000000,fffffe0000000000'
    WORK_THRESHOLD = (
        (BANANO, 'BANANO'),
        (NANO, 'NANO')
    )

    MILLION = '1000000000000000000000000000000'
    BILLION = '100000000000000000000000000000'
    TEN_BILLION = '10000000000000000000000000000'
    HUNDRED_BILLION = '1000000000000000000000000000'
    SUPPLY_MULTIPLIER = (
        (MILLION,         'MILLIONs'),
        (BILLION,         'BILLIONs'),
        (TEN_BILLION,     'TEN_BILLIONs'),
        (HUNDRED_BILLION, 'HUNDRED_BILLIONs'),
    )

    abbreviation = models.CharField(max_length=4, blank=False, unique=True)
    boompow_version = models.CharField(max_length=64, default='v3.0.1')
    boompow_payout_address = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=128, blank=True, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    debug = models.CharField(max_length=100, blank=False, default='INFO')
    domain_svc = models.CharField(max_length=256, blank=False, default='verigasvc.com')
    enable_custom_domain = models.BooleanField(blank=False, default=False)
    custom_domain = models.CharField(max_length=256, blank=True, default='')
    faucet_public_key = models.CharField(max_length=64, blank=False)
    landing_public_key = models.CharField(max_length=64, blank=False)
    canary_beta_public_key = models.CharField(max_length=64, blank=False)
    canary_live_public_key = models.CharField(max_length=64, blank=False)
    canary_test_public_key = models.CharField(max_length=64, blank=False)
    genesis_beta_public_key = models.CharField(max_length=64, blank=False)
    genesis_beta_account = models.CharField(max_length=65, blank=False)
    genesis_beta_work = models.CharField(max_length=16, blank=False)
    genesis_beta_signature = models.CharField(max_length=128, blank=False)
    genesis_dev_public_key = models.CharField(max_length=64, blank=False)
    genesis_dev_private_key = models.CharField(max_length=64, blank=False)
    genesis_dev_account = models.CharField(max_length=65, blank=False)
    genesis_dev_work = models.CharField(max_length=16, blank=False)
    genesis_dev_signature = models.CharField(max_length=128, blank=False)
    genesis_live_public_key = models.CharField(max_length=64, blank=False)
    genesis_live_account = models.CharField(max_length=65, blank=False)
    genesis_live_work = models.CharField(max_length=16, blank=False)
    genesis_live_signature = models.CharField(max_length=128, blank=False)
    genesis_test_public_key = models.CharField(max_length=64, blank=False)
    genesis_test_account = models.CharField(max_length=65, blank=False)
    genesis_test_work = models.CharField(max_length=16, blank=False)
    genesis_test_signature = models.CharField(max_length=128, blank=False)
    beta_pre_conf_rep_account_0 = models.CharField(max_length=65, blank=False)
    beta_pre_conf_rep_account_1 = models.CharField(max_length=65, blank=False)
    beta_pre_conf_rep_public_key_0 = models.CharField(max_length=64, blank=False)
    beta_pre_conf_rep_public_key_1 = models.CharField(max_length=64, blank=False)
    beta_pre_conf_rep_private_key_0 = models.CharField(max_length=64, blank=False)
    beta_pre_conf_rep_private_key_1 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_account_0 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_1 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_2 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_3 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_4 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_5 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_6 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_account_7 = models.CharField(max_length=65, blank=False)
    live_pre_conf_rep_public_key_0 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_1 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_2 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_3 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_4 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_5 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_6 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_public_key_7 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_0 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_1 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_2 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_3 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_4 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_5 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_6 = models.CharField(max_length=64, blank=False)
    live_pre_conf_rep_private_key_7 = models.CharField(max_length=64, blank=False)
    k8s_cluster = models.CharField(max_length=64, blank=False, default='k8s0')
    nano_network = models.CharField(max_length=64, blank=False, default='live')
    nault_version = models.CharField(max_length=64, blank=False, default='v1.15.0')
    nault_price_url = models.CharField(max_length=1024, blank=False, default='None')
    nault_store_key = models.CharField(max_length=128, blank=True, default='None')
    nault_hid_rep_help = models.BooleanField(default=True)
    ninja_version = models.CharField(max_length=64, blank=False, default='663a5b24e2a8e1d423fc3311a6945cc0d234953e')
    proxy_version = models.CharField(max_length=64, blank=False, default='v1.4.4')
    proxy_price_url = models.CharField(max_length=1024, blank=False, default='None')
    supply_multiplier = models.CharField(max_length=128, choices=SUPPLY_MULTIPLIER, default=BILLION)
    work_threshold = models.CharField(max_length=128, choices=WORK_THRESHOLD,default=NANO)
    work_threshold_default = models.CharField(max_length=64, blank=False, default='fffffff800000000')
    work_receive_threshold_default = models.CharField(max_length=64, blank=False, default='fffffe0000000000')
    live_node_peering_port = models.CharField(max_length=5, blank=False, default='7075')
    beta_node_peering_port = models.CharField(max_length=5, blank=False, default='54000')
    test_node_peering_port = models.CharField(max_length=5, blank=False, default='44000')
    live_rpc_port = models.CharField(max_length=5, blank=False, default='7076')
    beta_rpc_port = models.CharField(max_length=5, blank=False, default='55000')
    test_rpc_port = models.CharField(max_length=5, blank=False, default='45000')
    logging = models.CharField(max_length=100, blank=True, default='INFO')
    node_version = models.CharField(max_length=100, blank=False)
    binary_public = models.BooleanField(blank=False, default=False)
    s3_bucket_name = models.CharField(max_length=256, blank=True, default='')
    number_of_peers = models.IntegerField(blank=False, default=2)
    status = models.PositiveIntegerField(choices=STATUS, default=CREATED)
    deleted = models.BooleanField(null=False, default=False)
    deleted_at = models.DateTimeField(null=True, default=None)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockchain_delete_by', null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    created_by = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='blockchain_created_by')
    updated_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='blockchain_owner')

    def __str__(self):
        return "%s - %s" % (self.id, self.abbreviation)

    def __int__(self):
        return self.id

    class Meta:
        ordering = ['id']


class DroneCIServer(models.Model):
    name = models.CharField(max_length=128, blank=False)
    description = models.TextField(max_length=2048, blank=True, default='')
    server = models.URLField(max_length=254, blank=True, default='')
    token = EncryptedCharField(max_length=254)

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    def __int__(self):
        return self.id

    class Meta:
        ordering = ['id']


class BlockChainBuildDeploy(models.Model):
    BUILD = 1
    DEPLOY = 2
    UPDATE = 3
    TERMINATE = 4
    TYPES = (
        (BUILD, 'Build'),
        (DEPLOY, 'Deploy'),
        (UPDATE, 'Update'),
        (TERMINATE, 'Terminate'),
    )
    block_chain = models.ForeignKey(BlockChain, on_delete=models.CASCADE, related_name='block_chain')
    build_id = models.IntegerField(null=False)
    build_no = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    created_by = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name='block_chain_build_deploy_created_by',
                                   default=1)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='block_chain_build_deploy_owner')
    # BlockChainBuildDeploy id
    parent_build_id = models.IntegerField(null=True, default=None)
    parent_build_number = models.IntegerField(null=True, default=None)
    status = models.CharField(max_length=128, null=True, default=None)
    type = models.PositiveIntegerField(
        choices=TYPES,
        default=BUILD
    )
    droneci_server = models.ForeignKey(DroneCIServer, on_delete=models.CASCADE,
                                       related_name='droneci_server', default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class Contact(models.Model):
    name = models.CharField(max_length=512)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=64)
    message = models.CharField(max_length=2048)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['id']
