
from django.conf import settings
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save, post_syncdb
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.contrib.auth.hashers import (
    check_password, make_password, is_password_usable
)


from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField, AutoSlugField,
    UUIDField,
)

AUTH_USER_MODEL = settings.AUTH_USER_MODEL

def get_code_length():
    try:
        n = int(settings.INVITE_CODE_LENGTH)
    except (AttributeError, ValueError, TypeError):
        n = 9
    if n < 6:
        raise Exception("INVITE_CODE_LENGTH must be at least 3")
    if n > 30:
        raise Exception("INVITE_CODE_LENGTH must be at most 30")
    return n

class InvitationCodeManager(models.Manager):

    def create_invite_code(
        self, email, site=None, name=None, phone=None, creator=None
    ):
        chars = 'ABCDEFGHJKMPQRSTUVWXYZ'
        nums = '23456789'
        site = site or Site.objects.get_current()
        N = get_code_length()
        while True:
            key = str(site.id) + '-'
            key += get_random_string(N-3, chars) + get_random_string(3, nums)
            if not self.filter(site=site, key=key).exists():
                break
        code = self.model(
            key=key, site=site, registered_to=email, registered_name=name,
            registered_phone=phone, created_by=creator
        )
        code.save()
        return code

    def get_code_from_key_if_valid(self, key, email=None, site=None):
        N = get_code_length()
        # no point in hitting the database if the code is the wrong format
        if not key or len(key) != N:
            return
        top, tail = key[:-3], key[-3:]
        if (set('01') & set(tail)) | (set('ILN1234567890') & set(top)):
            return
        try:
            int(tail)
        except ValueError:
            return
        site = site or Site.objects.get_current()
        key = str(site.id) + '-' + key
        try:
            code = self.get(site=site, key=key)
        except:
            return
        # *IF* an email is given then ensure that it matches, but at least for
        # the "quick login" use case we don't want to insist on an email
        if email and email != code.registered_to:
            return
        if not code.expired:
            return code
    
class InvitationCode(models.Model):
    site = models.ForeignKey(Site, related_name="invite_codes")
    uuid = UUIDField(version=4, auto=True, unique=True)
    created_date = CreationDateTimeField(_('created date'))
    created_by = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True)
    registered_to = models.EmailField('email', blank=False)
    registered_name = models.CharField(
        'name', max_length=70, blank=True, null=True
    )
    registered_phone = models.CharField(
        'phone', max_length=20, blank=True, null=True
    )
    registered_date = models.DateTimeField(
        _('registered date'), blank=True, null=True, editable=False
    )
    key = models.CharField(
        max_length=30, blank=True, null=True, editable=False
    )
    expired = models.BooleanField(default=False)
    objects = InvitationCodeManager()

    class Meta:
        unique_together = ('site', 'key')

    def __repr__(self):
        return "<InvitationCode: %s>" % self.key

    @property
    def short_key(self):
        if self.key:
            return self.key.rpartition('-')[2]

    def save(self, *args, **kwargs):
        if not hasattr(self, 'site') or not self.site:
            self.site_id = settings.SITE_ID
        super(InvitationCode, self).save(*args, **kwargs)

