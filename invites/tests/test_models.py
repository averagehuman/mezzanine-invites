
import pytest

from django.conf import settings

from invites.models import InvitationCode

@pytest.mark.django_db
def test_invite_code_creation():
    code = InvitationCode.objects.create_invite_code()
    assert code
    assert len(code.short_key) == settings.INVITE_CODE_LENGTH

