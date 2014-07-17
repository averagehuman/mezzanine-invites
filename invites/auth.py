
from datetime import datetime
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.exceptions import ImproperlyConfigured, PermissionDenied


from .models import InvitationCode

User = get_user_model()

class InviteAuthBackend(object):

    def authenticate(self, **kwargs):
        if kwargs:
            invite_key = kwargs.pop("invite_key", None)
            email = kwargs.pop("email", None)
            if invite_key:
                code = InvitationCode.objects.get_code_from_key_if_valid(invite_key, email)
                if code:
                    if not code.registered_by:
                        site = Site.objects.get_current().pk
                        user = User.objects.create_user(
                            '%s%05d' % (site, code.pk+40)
                        )
                        code.registered_by = user
                        code.registered_date = datetime.now()
                        if getattr(settings, 'INVITE_CODES_ARE_REUSABLE', True) is False:
                            code.expired = True
                        code.save()
                    return code.registered_by
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None

