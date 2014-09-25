
from django.utils import timezone
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from mezzanine.conf import settings

from .models import InvitationCode

class InviteAuthBackend(object):

    def authenticate(self, **kwargs):
        if kwargs:
            invite_key = kwargs.pop("invite_key", None)
            email = kwargs.pop("email", None)
            if invite_key:
                code = InvitationCode.objects.get_code_from_key_if_valid(
                    invite_key, email
                )
                if code:
                    User = get_user_model()
                    email = code.registered_to
                    try:
                        user = User.objects.get(username=email)
                    except User.DoesNotExist:
                        name = (code.registered_name or '').partition(' ')
                        user= User.objects.create_user(
                            email, email, first_name=name[0], last_name=name[1],
                            phone=code.registered_phone,
                        )
                    if not code.registered_date:
                        code.registered_date = timezone.now()
                        if getattr(settings, 'INVITE_CODES_ARE_REUSABLE', True) is False:
                            code.expired = True
                        code.save()
                    return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None

