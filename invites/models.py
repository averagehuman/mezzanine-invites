
from datetime import datetime
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


from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField, AutoSlugField,
)

User = get_user_model()

def get_code_length():
    try:
        n = int(settings.INVITE_CODE_LENGTH)
    except (AttributeError, ValueError):
        n = 9
    if n < 3:
        raise Exception("INVITE_CODE_LENGTH must be at least 3")
    return n

class InvitationCodeManager(models.Manager):

    def create_invite_code(self, site=None, email=None, creator=None):
        chars = 'ABCDEFGHJKMPQRSTUVWXYZ'
        nums = '23456789'
        site = site or Site.objects.get_current()
        N = get_code_length()
        while True:
            key = str(site.id) + '-'
            key += get_random_string(N-3, chars) + get_random_string(3, nums)
            if not self.filter(site=site, key=key).exists():
                break
        code = self.model(key=key, site=site, registered_to=email, created_by=creator)
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
        # key as saved is prefixed with the site id
        key = str(site.id) + '-' + key
        try:
            code = self.get(site=site, key=key)
        except:
            return
        if code.registered_to and code.registered_to != email:
            return
        if code.registered_by and getattr(settings, 'INVITE_CODES_ARE_REUSABLE', True) is False:
            # the code has already been used to login to the site
            return
        if not code.expired:
            return code
    
class InvitationCode(models.Model):
    """
    registered_to - an email address associated with a given code
    registered_by - the site user who used the code to register
    """
    site = models.ForeignKey(Site, related_name="invite_codes")
    created_date = CreationDateTimeField(_('created date'))
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("created by"),
        related_name="created_invites",
    )
    registered_to = models.EmailField(blank=True, null=True)
    registered_by = models.OneToOneField(
        User,
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("registered by"),
    )
    registered_date = models.DateTimeField(blank=True, null=True, editable=False)
    expired = models.BooleanField(default=False)
    key = models.CharField(max_length=12, editable=False)
    objects = InvitationCodeManager()

    class Meta:
        unique_together = ('site', 'key')

    def __unicode__(self):
        return self.key

    @property
    def short_key(self):
        if self.key:
            return self.key.rpartition('-')[2]

