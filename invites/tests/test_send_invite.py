# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
import pytest


def _assert_redirect_to(_client, url):
    send_invite_url = reverse("send-invite")
    response = _client.get(send_invite_url, follow=True)
    assert response.redirect_chain
    redirect_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    parsed = urlparse(redirect_url)
    assert parsed.path == url
    assert parsed.query == "next=%s" % send_invite_url

@pytest.mark.django_db
def test_anonymous_users_are_redirected_to_login(client):
    login_url = reverse("login")
    _assert_redirect_to(client, login_url)

@pytest.mark.django_db
def test_non_privileged_users_are_redirected_to_login(auth_client):
    admin_login_url = reverse("admin:login")
    _assert_redirect_to(auth_client, admin_login_url)

@pytest.mark.django_db
def test_staff_are_allowed(admin_client):
    response = admin_client.get(reverse("send-invite"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_send_email(admin_client):
    email = 'tester@test.com'
    User = get_user_model()
    assert User.objects.filter(email=email).count() == 0
    assert len(mail.outbox) == 0
    response = admin_client.post(
        reverse("send-invite"), {'registered_to': 'tester@test.com'},
        follow=True,
    )
    assert response.status_code == 200
    assert len(mail.outbox) == 1


