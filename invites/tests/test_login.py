# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from django.core import mail
from django.core.urlresolvers import reverse
from django.core.management import call_command, CommandError
from django.contrib.auth import get_user_model
import pytest

from invites.models import InvitationCode


@pytest.mark.django_db
def test_login_with_valid_credentials_succeeds_and_creates_user(client):
    name = 'Professor Plum'
    email = 'professor@plum.com'
    User = get_user_model()
    assert User.objects.filter(username=email).count() == 0
    code = InvitationCode.objects.create_invite_code(email, name=name)
    assert client.login(**{'invite_key': code.short_key})
    assert User.objects.filter(username=email).count() ==1
    user = User.objects.get(username=email)
    assert user.email == email
    assert user.first_name == 'Professor'
    assert user.last_name == 'Plum'

@pytest.mark.django_db
def test_login_with_empty_credentials_fails(client):
    assert not client.login(**{'invite_key': ''})

@pytest.mark.django_db
def test_login_with_invalid_credentials_fails(client):
    key = '1-XXX'
    assert InvitationCode.objects.filter(key=key).count() == 0
    assert not client.login(**{'invite_key': 'XXX'})


@pytest.mark.django_db
def test_valid_login_form_post_succeeds_and_creates_user(client):
    name = 'Colonel Charles Arthur Mustard'
    email = 'colonel@mustard.com'
    User = get_user_model()
    assert User.objects.filter(username=email).count() == 0
    code = InvitationCode.objects.create_invite_code(email, name=name)
    response = client.post(
        reverse("login"), {'login_type': 'quick', 'key': code.short_key},
        follow=True,
    )
    assert response.redirect_chain
    redirected_to, status_code = response.redirect_chain[-1]
    assert status_code == 302
    parsed = urlparse(redirected_to)
    assert parsed.path == "/"
    assert User.objects.filter(username=email).count() ==1
    user = User.objects.get(username=email)
    assert user.email == email
    assert user.first_name == 'Colonel'
    assert user.last_name == 'Charles Arthur Mustard'

