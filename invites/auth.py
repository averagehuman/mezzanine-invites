
from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from mezzanine.conf import settings
from mezzanine.core.auth_backends import MezzanineBackend

from .models import InvitationCode

class InviteAuthBackend(MezzanineBackend):
    """A custom authentication backend that checks validity of an 'invite key'

    Designed to give quick access to a site to known potential users. An
    administrator will create an Invite Code with at least the invitee's email
    address and possibly also a full name and phone number. This code's key (a
    short alphanumeric token) is sent to the invitee and, if they choose to use
    it, the first login with the code will create a new site user.

    An Invite Code must be used to register within the number of days given by
    the `INVITE_CODE_USAGE_WINDOW` setting (default 14 days), and once
    registered, the code is valid for the number of days given by
    `INVITE_CODE_EXPIRY_DAYS` (default 30 days).
    """

    @staticmethod
    def get_or_create_user_from_code(code, timestamp):
        """Given an InvitationCode object get or create an associated User

        We try to be generic here with regard to potential `AUTH_USER_MODEL`s,
        but the basic modus is to create an instance of that model with the
        `USERNAME_FIELD` set to the invitee's email as given in the Invite
        Code's `registered_to` property. This is compatible with Django's
        `auth.User` at least; you might subclass the backend and override this
        method if it does not suffice.
        """
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        email = code.registered_to
        created = True
        try:
            user = User.objects.get(**{username_field:email})
        except User.DoesNotExist:
            name = (code.registered_name or '').partition(' ')
            possible_kwargs = {
                'email': email,
                'username': email,
                'first_name': name[0],
                'last_name': name[2],
                'name': code.registered_name,
                'phone': code.registered_phone,
                'phone_number': code.registered_phone,
                'date_joined': timestamp,
                'last_login': timestamp,
            }
            kwargs = {username_field: email}
            for field in User._meta.fields:
                try:
                    kwargs[field.name] = possible_kwargs[field.name]
                except KeyError:
                    pass
            user = User(**kwargs)
            user.set_unusable_password()
            user.save()
        else:
            created = False
        return user, created

    def authenticate(self, **kwargs):
        invite_key = kwargs.pop("invite_key", None)
        invite_key = invite_key or kwargs.get("password", None)
        email = kwargs.get("email", None)
        email = email or kwargs.get("username", None)
        code = None
        if invite_key:
            code = InvitationCode.objects.get_code_from_key_if_valid(
                invite_key, email
            )
        if not code:
            # try regular login
            return super(InviteAuthBackend, self).authenticate(**kwargs)
        # It is a valid code but although "code.expired == False", it might
        # be lying and may actually be expired (for example, on the first login
        # after the expiry date). If it is lying we set "code.expired = True"
        # below and eventually refuse to authenticate.
        short_key = code.short_key
        now = timezone.now()
        expiry_days = getattr(settings, 'INVITE_CODE_EXPIRY_DAYS', 30)
        try:
            expiry_days = int(expiry_days)
        except (ValueError, TypeError):
            expiry_days = 0
        try:
            usage_window = int(settings.INVITE_CODE_USAGE_WINDOW)
        except (AttributeError, ValueError, TypeError):
            usage_window = 14
        delta = timedelta(usage_window)
        update_fields = None
        if not code.registered_date and (now - code.created_date) > delta:
            # never used and now out of date code
            code.expired = True
            update_fields = ['expired']
        else:
            # may or may not have been registered
            user, created = self.get_or_create_user_from_code(code, now)
            if not code.registered_date:
                # first use of the code
                code.registered_date = now
                update_fields = ['registered_date']
            else:
                # is registered but check expiry
                delta = timedelta(days=expiry_days)
                if not delta or (now - code.registered_date) > delta:
                    # code is expired
                    code.expired = True
                    update_fields = ['expired']
        if update_fields:
            code.save(update_fields=update_fields)
        if not code.expired:
            return user

