
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

def get_or_create_user_from_code(code, timestamp):
    User = get_user_model()
    pk_field = User.USERNAME_FIELD
    created = True
    try:
        user = User.objects.get(pk_field=code.email)
    except User.DoesNotExist:
        name = (code.registered_name or '').partition(' ')
        all_kwargs = {
            'email': email,
            'username': email,
            'first_name': name[0],
            'last_name': name[1],
            'name': code.registered_name,
            'fullname': code.registered_name,
            'full_name': code.registered_name,
            'phone': code.phone,
            'phone_number': code.phone,
            'date_joined': timestamp,
            'last_login': timestamp,
        }
        kwargs = {pk_field: email}
        for field in User._meta.fields:
            try:
                kwargs[field.name] = all_kwargs[field.name]
            except KeyError:
                pass
        user = User(**kwargs)
        # WARNING - for convenience we set the user password to be the
        # invite code key itself. This gives an immediate way for the
        # user to login but may be insecure because:
        #    + the code may have been sent in a plain text email
        #    + the code may not be very strong as a password
        # This risk is mitigated by the INVITE_CODE_EXPIRY_DAYS setting
        # and by a 'set_unusable_password' call if the password hasn't
        # been changed within the expiry time.
        user.set_password(code.short_key)
        user.save()
    else:
        created = False
    return user, created

class InviteAuthBackend(object):

    def authenticate(self, **kwargs):
        invite_key = kwargs.pop("invite_key", None)
        email = kwargs.pop("email", None)
        if not invite_key:
            return
        code = InvitationCode.objects.get_code_from_key_if_valid(
            invite_key, email
        )
        if not code:
            return
        # It is a valid code but although "code.expired == False", it might
        # be lying and may actually be expired. If it is lying we set
        # "code.expired = True" below and eventually refuse to authenticate.
        email = code.registered_to
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
        delta = timedelta(expiry_days + usage_window)
        update_fields = None
        if not code.registered_date and (code.creation_date + delta) > now:
            # never used and now expired code
            code.expired = True
            code.key = ''
            update_fields = ['expired', 'key']
        else:
            # may or may not have been registered
            user, created = get_or_create_user_from_code(code, now)
            if created:
                # first use of the code
                code.registered_date = now
                update_fields = ['registered_date']
            else:
                # is registered but check expiry
                delta = timedelta(days=expiry_days)
                if not delta or (code.registered_date + delta) > now:
                    # code is expired
                    code.expired = True
                    code.key = ''
                    update_fields = ['expired', 'key']
                    # may need to update user password
                    if user.check_password(short_key):
                        # it's still the (now invalid) invite code
                        user.set_unusable_password()
                        user.save()
        if update_fields:
            code.save(update_fields=update_fields)
        if not code.expired:
            return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None

