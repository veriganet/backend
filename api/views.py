import logging
import jwt
import requests
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, \
    IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, status
from templated_email import send_templated_mail

from api.permissions import IsOwner, IsUserOwner
from api.models import Profile, Organization, BlockChain, BlockChainBuildDeploy
from api.serializers import CustomTokenObtainPairSerializer, UserSerializer, \
    RegisterSerializer, RegisterUserSerializer, ProfileSerializer, \
    OrganizationSerializer, BlockChainSerializer, UserUserSerializer, \
    UserProfileSerializer, BlockChainUserSerializer, OrganizationUserSerializer, \
    BlockChainUserUpdatePatchSerializer, BlockChainBuildDeploySerializer
from api.utils import request_to_drone_ci
from backend.settings import env

logger = logging.getLogger(__name__)


class APIRootView(APIView):
    """
    Root of backed api
    This is the actual api endpoint for all api calls
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        admin_urls = {
            'admin/blockchains': reverse('blockchain_list', request=request, format=format),
            'admin/blockchains/builds-deploys': reverse('blockchain_build_deploy', request=request, format=format),
            'admin/blockchains/builds': reverse('blockchain_build', request=request, format=format),
            'admin/blockchains/deploys': reverse('blockchain_deploy', request=request, format=format),
            'admin/blockchains/terminations': reverse('blockchain_terminate', request=request,
                                                                        format=format),
            'admin/organizations': reverse('organization_list', request=request, format=format),
            'admin/users': reverse('user_list', request=request, format=format),
            'admin/users/profiles': reverse('user_profile', request=request, format=format),
        }
        user_urls = {
            'user/blockchains': reverse('user_blockchain_list', request=request, format=format),
            'user/geolocation': reverse('user_geo_location', request=request, format=format),
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
        }
        public_urls = {
            'register': reverse('register_user', request=request, format=format),
            'token': reverse('token_obtain_pair', request=request, format=format),
            'token/refresh': reverse('token_refresh', request=request, format=format),
            'token/verify': reverse('token_verify', request=request, format=format),
        }

        admin_all_urls = {}
        admin_all_urls.update(admin_urls)
        admin_all_urls.update(user_urls)
        admin_all_urls.update(public_urls)

        user_all_urls = {}
        user_all_urls.update(user_urls)
        user_all_urls.update(public_urls)

        if request.user.is_superuser:
            # admin urls
            return Response(admin_all_urls)
        elif request.user.is_authenticated:
            # user urls
            return Response(user_all_urls)
        elif not request.user.is_authenticated:
            # public urls
            return Response(public_urls)


#
# admin views - start
#
class BlockChainViewSet(viewsets.ModelViewSet):
    """
    List, retrieve, update, partial update and delete actions for blockchains

    blockchain details:
    blockchains/<pk>
    """
    queryset = BlockChain.objects.all()
    serializer_class = BlockChainSerializer
    permission_classes = [IsAdminUser]


class BlockChainBuildDeployViewSet(viewsets.ModelViewSet):
    """
    List, create, retrieve, update and destroy actions for BlockChainBuildDeploy

    Deploy details:
    blockchains/deploys/<pk>

    Build details:
    blockchains/builds/<pk>
    """
    queryset = BlockChainBuildDeploy.objects.all().order_by('id')
    serializer_class = BlockChainBuildDeploySerializer
    permission_classes = [IsAdminUser]


class BlockChainBuildViewSet(viewsets.ViewSet):
    """
    Create, List, retrieve blockchain builds

    Create: Starts build for blockchain
    <pk> BlockChain ID
    POST blockchains/builds/build/<pk>

    List: Lists builds for blockchain
    <pk> BlockChain ID
    GET blockchains/builds/<pk>

    Retrieve: Retrieves build details from remote build server
    <pk> BlockChainBuildDeploy ID
    GET blockchains/builds/detail/<pk>
    """

    permission_classes = [IsAdminUser]

    def blockchain_build_list(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        build_deploy = BlockChainBuildDeploy.objects.filter(block_chain=pk, type=1).values()

        return Response(build_deploy)

    def create(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        block_chain = get_object_or_404(BlockChain, id=pk)
        build_deploy = BlockChainBuildDeploy.objects.filter(block_chain=block_chain, type=1).last()

        if block_chain.s3_bucket_name != "None":
            s3_bucket_name = block_chain.s3_bucket_name
        else:
            s3_bucket_name = env('S3_BUCKET_PREFIX')+'-'+block_chain.abbreviation

        # create placeholder BuildDeploy object
        if build_deploy is None:
            build = BlockChainBuildDeploy.objects.create(
                build_id=0,
                build_no=0,
                block_chain_id=pk,
                created_by=request.user,
                status='created',
                type=1,
                owner=request.user
            )
            build.save()
        else:
            if build_deploy.status not in ['success', 'running', 'failure', 'created']:
                build = BlockChainBuildDeploy.objects.create(
                    build_id=0,
                    build_no=0,
                    block_chain_id=pk,
                    created_by=request.user,
                    status='created',
                    type=1,
                    owner=request.user
                )
                build.save()
            else:
                build = BlockChainBuildDeploy.objects.filter(block_chain=block_chain, type=1).last()

        # get remote status of the build with drone api
        url_status = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(build.build_no)
        response_status = request_to_drone_ci(method='GET', url=url_status)
        d_status = response_status.json()
        if 'status' in d_status:
            job_status = d_status['status']
            logger.debug("Found the values: %s" % job_status)
        else:
            job_status = None
            logger.debug("Value of build status not found!")

        # check current status of the job before creating
        if job_status in ['success', 'running', 'pending']:
            return Response({
                "detail": "Can not start a new build! Current status: %s" % job_status
            })

        params = 'ABBREVIATION='+block_chain.abbreviation+'&' \
                 'BOOMPOW_VERSION='+block_chain.boompow_version+'&' \
                 'BOOMPOW_PAYOUT_ADDRESS='+block_chain.boompow_payout_address+'&' \
                 'BLOCK_NAME='+block_chain.name+'&' \
                 'DEBUG='+block_chain.debug+'&' \
                 'ENABLE_CUSTOM_DOMAIN='+str(block_chain.enable_custom_domain)+'&' \
                 'CUSTOM_DOMAIN='+block_chain.custom_domain+'&' \
                 'DOMAINSVC='+block_chain.domain_svc+'&' \
                 'FAUCET_PUBLIC_KEY='+block_chain.faucet_public_key+'&' \
                 'LANDING_PUBLIC_KEY='+block_chain.landing_public_key+'&' \
                 'CANARY_BETA_PUBLIC_KEY='+block_chain.canary_beta_public_key+'&' \
                 'CANARY_LIVE_PUBLIC_KEY='+block_chain.canary_live_public_key+'&' \
                 'CANARY_TEST_PUBLIC_KEY='+block_chain.canary_test_public_key+'&' \
                 'GENESIS_DEV_PUBLIC_KEY='+block_chain.genesis_dev_public_key+'&' \
                 'GENESIS_DEV_PRIVATE_KEY='+block_chain.genesis_dev_private_key+'&' \
                 'GENESIS_DEV_ACCOUNT='+block_chain.genesis_dev_account+'&' \
                 'GENESIS_DEV_WORK='+block_chain.genesis_dev_work+'&' \
                 'GENESIS_DEV_SIGNATURE='+block_chain.genesis_dev_signature+'&' \
                 'GENESIS_BETA_PUBLIC_KEY='+block_chain.genesis_beta_public_key+'&' \
                 'GENESIS_BETA_ACCOUNT='+block_chain.genesis_beta_account+'&' \
                 'GENESIS_BETA_WORK='+block_chain.genesis_beta_work+'&' \
                 'GENESIS_BETA_SIGNATURE='+block_chain.genesis_beta_signature+'&' \
                 'GENESIS_LIVE_PUBLIC_KEY='+block_chain.genesis_live_public_key+'&' \
                 'GENESIS_LIVE_ACCOUNT='+block_chain.genesis_live_account+'&' \
                 'GENESIS_LIVE_WORK='+block_chain.genesis_live_work+'&' \
                 'GENESIS_LIVE_SIGNATURE='+block_chain.genesis_live_signature+'&' \
                 'GENESIS_TEST_PUBLIC_KEY='+block_chain.genesis_test_public_key+'&' \
                 'GENESIS_TEST_ACCOUNT='+block_chain.genesis_test_account+'&' \
                 'GENESIS_TEST_WORK='+block_chain.genesis_test_work+'&' \
                 'GENESIS_TEST_SIGNATURE='+block_chain.genesis_test_signature+'&' \
                 'BETA_PRE_CONFIGURED_REP0='+block_chain.beta_pre_conf_rep_public_key_0+'&' \
                 'BETA_PRE_CONFIGURED_REP1='+block_chain.beta_pre_conf_rep_public_key_1+'&' \
                 'LIVE_PRE_CONFIGURED_REP0='+block_chain.live_pre_conf_rep_public_key_0+'&' \
                 'LIVE_PRE_CONFIGURED_REP1='+block_chain.live_pre_conf_rep_public_key_1+'&' \
                 'LIVE_PRE_CONFIGURED_REP2='+block_chain.live_pre_conf_rep_public_key_2+'&' \
                 'LIVE_PRE_CONFIGURED_REP3='+block_chain.live_pre_conf_rep_public_key_3+'&' \
                 'LIVE_PRE_CONFIGURED_REP4='+block_chain.live_pre_conf_rep_public_key_4+'&' \
                 'LIVE_PRE_CONFIGURED_REP5='+block_chain.live_pre_conf_rep_public_key_5+'&' \
                 'LIVE_PRE_CONFIGURED_REP6='+block_chain.live_pre_conf_rep_public_key_6+'&' \
                 'LIVE_PRE_CONFIGURED_REP7='+block_chain.live_pre_conf_rep_public_key_7+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP0='+block_chain.live_pre_conf_rep_account_0+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP1='+block_chain.live_pre_conf_rep_account_1+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP2='+block_chain.live_pre_conf_rep_account_2+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP3='+block_chain.live_pre_conf_rep_account_3+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP4='+block_chain.live_pre_conf_rep_account_4+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP5='+block_chain.live_pre_conf_rep_account_5+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP6='+block_chain.live_pre_conf_rep_account_6+'&' \
                 'LIVE_PRE_CONFIGURED_ACCOUNT_REP7='+block_chain.live_pre_conf_rep_account_7+'&' \
                 'LOGGING='+block_chain.logging+'&' \
                 'NANO_NETWORK='+block_chain.nano_network+'&' \
                 'NAULT_VERSION='+block_chain.nault_version+'&' \
                 'NINJA_VERSION='+block_chain.ninja_version+'&' \
                 'PROXY_VERSION='+block_chain.ninja_version+'&' \
                 'LIVE_NODE_PEERING_PORT='+block_chain.live_node_peering_port+'&' \
                 'BETA_NODE_PEERING_PORT='+block_chain.beta_node_peering_port+'&' \
                 'TEST_NODE_PEERING_PORT='+block_chain.test_node_peering_port+'&' \
                 'LIVE_RPC_PORT='+block_chain.live_rpc_port+'&' \
                 'BETA_RPC_PORT='+block_chain.beta_rpc_port+'&' \
                 'TEST_RPC_PORT='+block_chain.test_rpc_port+'&' \
                 'NODE_VERSION='+block_chain.node_version+'&' \
                 'BINARY_PUBLIC='+str(block_chain.binary_public)+'&' \
                 'S3_BUCKET_NAME='+s3_bucket_name+'&' \
                 'NUMBER_OF_PEERS='+str(block_chain.number_of_peers)+'&' \
                 'WORK_THRESHOLD_DEFAULT='+str(block_chain.work_threshold_default)+'&' \
                 'WORK_RECEIVE_THRESHOLD_DEFAULT='+str(block_chain.work_receive_threshold_default)+'&' \
                 'VERIGA_BUILD_DEPLOY_ID='+str(build.id)

        url = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds?branch=' + \
                   env('BUILD_DEPLOY_BRANCH') + \
                   '&' + \
                   params

        response = request_to_drone_ci(method='POST', url=url)

        # update placeholder BlockChainBuildDeploy object with real data
        d = response.json()
        if 'id' in d and 'number' in d:
            build.build_id = d['id']
            build.build_no = d['number']
            build.status = 'running'
            build.save()

        return Response(d)

    def list(self, request, *args, **kwargs):
        build_deploy = BlockChainBuildDeploy.objects.filter(type=1).values()

        return Response(build_deploy)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        build = get_object_or_404(BlockChainBuildDeploy, id=pk, type=1)

        url = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(build.build_no)

        response = request_to_drone_ci(method='GET', url=url)

        return Response(response.json())


class BlockChainDeployViewSet(viewsets.ViewSet):
    """
    Create, List, retrieve blockchain deploys

    Create: Deploy blockchain
    <pk> BlockChain ID
    POST blockchains/deploys/deploy/<pk>

    List: Lists blockchain deployments
    <pk> BlockChain ID
    GET blockchains/deploys/<pk>

    Retrieve: Retrieves blockchain deployment details
    <pk> BlockChainBuildDeploy ID
    GET blockchains/deploys/detail/<pk>
    """

    permission_classes = [IsAdminUser]

    def blockchain_deploy_list(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        build_deploy = BlockChainBuildDeploy.objects.filter(block_chain=pk, type=2).values()

        return Response(build_deploy)

    def create(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        block_chain = get_object_or_404(BlockChain, id=pk)
        build = BlockChainBuildDeploy.objects.filter(block_chain=block_chain, type=1).last()
        deploy = BlockChainBuildDeploy.objects.filter(block_chain=block_chain, type=2).last()

        # can be removed if not used
        if block_chain.s3_bucket_name != "None":
            s3_bucket_name = block_chain.s3_bucket_name
        else:
            s3_bucket_name = env('S3_BUCKET_PREFIX')+'-'+block_chain.abbreviation

        # create placeholder object
        # check if object is None
        if deploy is None:
            # create deploy object
            deploy = BlockChainBuildDeploy.objects.create(
                build_id=0,
                build_no=0,
                block_chain_id=pk,
                created_by=request.user,
                status='created',
                type=2,
                owner=request.user,
                parent_build_id=build.id,
                parent_build_number=build.build_no
            )
            # save object object
            deploy.save()
        else:
            # check if current status of object is not in
            if deploy.status not in ['success', 'deploying', 'failure', 'created']:
                # create deploy object
                deploy = BlockChainBuildDeploy.objects.create(
                    build_id=0,
                    build_no=0,
                    block_chain_id=pk,
                    created_by=request.user,
                    status='created',
                    type=2,
                    owner=request.user,
                    parent_build_id=build.id,
                    parent_build_number=build.build_no
                )
                # save object
                deploy.save()

        # get remote status of the deployment with drone api
        url_status = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(deploy.build_no)
        response_status = request_to_drone_ci(method='GET', url=url_status)
        d_status = response_status.json()
        if 'status' in d_status:
            job_status = d_status['status']
            logger.debug("Found the values: %s" % job_status)
        else:
            job_status = None
            logger.debug("Value of build status not found!")

        if job_status in ['success', 'running', 'pending']:
            return Response({
                "detail": "Can not start a new deployment! Current status: %s" % job_status
            })

        params = 'ABBREVIATION=' + block_chain.abbreviation + \
                 '&VERIGA_BUILD_DEPLOY_ID=' + str(deploy.id)
        url = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(build.build_no) + \
                   '/promote?target=live&' + params

        # send the api request
        response = request_to_drone_ci(method='POST', url=url)

        # check if request returns None data
        if 'null' in response.text:
            return Response({"detail": "Request returned %s! I have a bad feeling about this." % response.json()})

        d = response.json()
        # create BlockChainBuildDeploy object if request-response returns valida JSON data
        if 'id' in d and 'number' in d:
            deploy.build_id = d['id']
            deploy.build_no = d['number']
            deploy.status = 'deploying'
            deploy.save()

        return Response(response.json())

    def list(self, request, *args, **kwargs):
        build_deploy = BlockChainBuildDeploy.objects.filter(type=2).values()

        return Response(build_deploy)

    def restart(self, request, *args, **kwargs):
        return Response({"detail": "restart"})

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        build = get_object_or_404(BlockChainBuildDeploy, id=pk, type=2)

        url = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(build.build_no)
        response = request_to_drone_ci(method='GET', url=url)

        return Response(response.json())


class BlockChainTerminateViewset(viewsets.ViewSet):
    """
    =========================
    DANGER ZONE ============
    =========================

    Create, list, retrieve blockchain terminate task

    Create: Terminates blockchain and removes all data
    <pk> BlockChain ID
    POST blockchains/terminations/terminate/<pk>

    List: Lists termination tasks for blockchain
    <pk> BlockChain ID
    GET blockchains/terminations/<pk>

    Retrieve: Retrieves blockchain termination details
    <pk> BlockChainBuildDeploy ID
    GET blockchains/terminations/detail/<pk>
    """
    def blockchain_terminate_list(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        build_deploy = BlockChainBuildDeploy.objects.filter(block_chain=pk, type=4).values()

        return Response(build_deploy)

    def create(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        block_chain = get_object_or_404(BlockChain, id=pk)
        build_deploy = BlockChainBuildDeploy.objects.filter(block_chain=block_chain)
        build = BlockChainBuildDeploy.objects.filter(block_chain=block_chain, type=1).last()
        terminate = BlockChainBuildDeploy.objects.filter(block_chain=block_chain, type=4).last()

        # can be removed if not used
        if block_chain.s3_bucket_name != "None":
            s3_bucket_name = block_chain.s3_bucket_name
        else:
            s3_bucket_name = env('S3_BUCKET_PREFIX')+'-'+block_chain.abbreviation

        # create placeholder object
        # check if object is None
        if terminate is None:
            # create deploy object
            terminate = BlockChainBuildDeploy.objects.create(
                build_id=0,
                build_no=0,
                block_chain_id=pk,
                created_by=request.user,
                status='created',
                type=4,
                owner=request.user,
                parent_build_id=build.id,
                parent_build_number=build.build_no
            )
            # save object object
            terminate.save()
        else:
            # check if current status of object is not in
            if terminate.status not in ['success', 'terminating', 'failure', 'created']:
                # create deploy object
                terminate = BlockChainBuildDeploy.objects.create(
                    build_id=0,
                    build_no=0,
                    block_chain_id=pk,
                    created_by=request.user,
                    status='created',
                    type=4,
                    owner=request.user,
                    parent_build_id=build.id,
                    parent_build_number=build.build_no
                )
                # save object
                terminate.save()

        # get remote status of the deployment with drone api
        url_status = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(terminate.build_no)
        response_status = request_to_drone_ci(method='GET', url=url_status)
        d_status = response_status.json()
        if 'status' in d_status:
            job_status = d_status['status']
            logger.debug("Found the values: %s" % job_status)
        else:
            job_status = None
            logger.debug("Value of build status not found!")

        if job_status in ['success', 'running', 'pending']:
            return Response({
                "detail": "Can not start a new termination job! Current status: %s" % job_status
            })

        params = 'ABBREVIATION=' + block_chain.abbreviation + \
                 '&VERIGA_BUILD_DEPLOY_ID=' + str(terminate.id) + \
                 '&VERIGA_BLOCK_CHAIN_ID=' + str(terminate.block_chain.id)
        url = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(build.build_no) + \
                   '/promote?target=live-terminate&' + params
        response = request_to_drone_ci(method='POST', url=url)

        # check if request returns None data
        if 'null' in response.text:
            return Response({"detail": "Request returned %s! I have a bad feeling about this." % response.json()})

        d = response.json()
        # create BlockChainBuildDeploy object if request-response returns valid JSON
        if 'id' in d and 'number' in d:
            terminate.build_id = d['id']
            terminate.build_no = d['number']
            terminate.status = 'terminating'
            terminate.save()

        return Response(response.json())

    def list(self, request, *args, **kwargs):
        build_deploy = BlockChainBuildDeploy.objects.filter(type=4).values()

        return Response(build_deploy)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        terminate = get_object_or_404(BlockChainBuildDeploy, id=pk, type=4)

        url = env('DRONE_SERVER') + \
                   '/api/repos/' + \
                   env('BUILD_DEPLOY_ORG') + \
                   '/' + \
                   env('BUILD_DEPLOY_REPO') + \
                   '/builds/' + \
                   str(terminate.build_no)
        response = request_to_drone_ci(method='GET', url=url)

        return Response(response.json())


class UserViewSet(viewsets.ModelViewSet):
    """
    list, create, retrieve, update and destroy actions for users

    for user details:
    users/<pk>
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
    permission_classes = [IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'patch':
            return BlockChainUserUpdatePatchSerializer
        return BlockChainUserSerializer

    def get_queryset(self):
        user = self.request.user

        return BlockChain.objects.filter(owner=user)


class GeoLocationUserViewSet(viewsets.GenericViewSet):
    """
    Gets geographic location of client by IP
    """

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        response = requests.get(env('GEO_LOCATION_API_URL') + '?apiKey='
                                + env('GEO_LOCATION_API_KEY'))
        geo_data = response.json()
        return Response(geo_data)


class EmailVerifySendViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
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
        verify_url = request.build_absolute_uri(reverse('user_password_reset_confirm')) + "?token=" + token

        send_templated_mail(
            template_name='welcome',
            from_email='welcome@' + current_site,
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
