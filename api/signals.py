from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.reverse import reverse
from templated_email import send_templated_mail

from api.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token,
                                 *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender:
    :param instance:
    :param reset_password_token:
    :param args:
    :param kwargs:
    :return:
    """
    current_site = get_current_site(instance.request).domain

    send_templated_mail(
        template_name='password_reset',
        from_email='password@' + current_site,
        recipient_list=[reset_password_token.user.email],
        context={
            'reset_password_url': "{}?token={}".format(
                instance.request.build_absolute_uri(reverse('user_password_reset_confirm')),
                reset_password_token.key)
        }
    )
