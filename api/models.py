from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# make email unique field
User._meta.get_field('email')._unique = True
# make username field None
User.username = None
# make USERNAME_FIELD email
User.USERNAME_FIELD = 'email'
# remove REQUIRED_FIELDS
User.REQUIRED_FIELDS = ['username']


class Organization(models.Model):
    address = models.TextField(max_length=2048, blank=True, default='')
    email = models.EmailField(max_length=254, blank=True, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    name = models.CharField(max_length=128, blank=False)
    url = models.URLField(max_length=254, blank=True, default='')
    linkedin_url = models.URLField(max_length=254, blank=True, default='')
    twitter_url = models.URLField(max_length=254, blank=True, default='')
    github_url = models.URLField(max_length=254, blank=True, default='')
    facebook_url = models.URLField(max_length=254, blank=True, default='')
    discord_url = models.URLField(max_length=254, blank=True, default='')
    coincapmarket_url = models.URLField(max_length=254, blank=True, default='')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class BlockChain(models.Model):
    abbreviation = models.CharField(max_length=4, blank=False)
    canary_beta_public_key = models.CharField(max_length=64, blank=False)
    canary_live_public_key = models.CharField(max_length=64, blank=False)
    canary_test_public_key = models.CharField(max_length=64, blank=False)
    custom_domain = models.CharField(max_length=256, blank=True, default='')
    created = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    debug = models.CharField(max_length=100, blank=True, default='INFO')
    domain_svc = models.CharField(max_length=256, blank=True, default='verigasvc.com')
    enable_custom_domain = models.BooleanField(blank=False, default=False)
    faucet_public_key = models.CharField(max_length=64, blank=False)
    landing_public_key = models.CharField(max_length=64, blank=False)
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
    beta_pre_conf_rep_public_key_0 = models.CharField(max_length=64, blank=False)
    beta_pre_conf_rep_public_key_1 = models.CharField(max_length=64, blank=False)
    beta_pre_conf_rep_private_key_0 = models.CharField(max_length=64, blank=False)
    beta_pre_conf_rep_private_key_1 = models.CharField(max_length=64, blank=False)
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
    live_node_peering_port = models.CharField(max_length=5, blank=False)
    beta_node_peering_port = models.CharField(max_length=5, blank=False)
    test_node_peering_port = models.CharField(max_length=5, blank=False)
    live_rpc_port = models.CharField(max_length=5, blank=False)
    beta_rpc_port = models.CharField(max_length=5, blank=False)
    test_rpc_port = models.CharField(max_length=5, blank=False)
    logging = models.CharField(max_length=100, blank=True, default='INFO')
    node_version = models.CharField(max_length=100, blank=False)
    binary_public = models.BooleanField(default=False)
    s3_bucket_name = models.CharField(max_length=256, blank=True)
    number_of_peers = models.IntegerField(blank=False, default=2)
    name = models.CharField(max_length=128, blank=True, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True)

    class Meta:
        ordering = ['abbreviation']
