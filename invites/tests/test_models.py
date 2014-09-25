
import pytest

from django.conf import settings

from invites.models import InvitationCode

@pytest.mark.django_db
def test_invite_code_creation():
    email = 'tester@test.com'
    code = InvitationCode.objects.create_invite_code(email)
    assert code
    assert code.registered_to == email
    assert not code.created_by
    assert len(code.short_key) == settings.INVITE_CODE_LENGTH

