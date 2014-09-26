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


def _assert_redirect_to(_client, url):
    send_invite_url = reverse("send-invite")
    response = _client.get(send_invite_url, follow=True)
    assert response.redirect_chain
    redirected_to, status_code = response.redirect_chain[-1]
    assert status_code == 302
    parsed = urlparse(redirected_to)
    assert parsed.path == url
    assert parsed.query == "next=%s" % send_invite_url

@pytest.mark.django_db
def test_anonymous_users_are_redirected_to_site_login(client):
    login_url = reverse("login")
    _assert_redirect_to(client, login_url)

@pytest.mark.django_db
def test_unprivileged_users_are_redirected_to_admin_login(auth_client):
    admin_login_url = reverse("admin:login")
    _assert_redirect_to(auth_client, admin_login_url)

@pytest.mark.django_db
def test_staff_are_allowed(admin_client):
    response = admin_client.get(reverse("send-invite"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_send_invite_view(admin_client):
    email = 'tester@test.com'
    N = len(mail.outbox)
    response = admin_client.post(
        reverse("send-invite"), {'registered_to': 'tester@test.com'},
        follow=True,
    )
    assert response.status_code == 200
    assert len(mail.outbox) == N+1

@pytest.mark.django_db
def test_non_interactive_send_invite_command():
    # email is required
    with pytest.raises(CommandError) as e:
        call_command("invite", interactive=False)
    assert e.value.args[0] == "Missing parameter 'email'"

    # if domain is given, a matching Site must exist
    email = 'tester@test.com'
    with pytest.raises(CommandError) as e:
        call_command("invite", interactive=False, email=email, domain="nope")
    assert e.value.args[0] == "A site with domain 'nope' does not exist"

    # if no domain is given, the default is used, but no mail is sent unless
    # specifically requested
    N = len(mail.outbox)
    call_command("invite", interactive=False, email=email)
    assert len(mail.outbox) == N
    call_command("invite", interactive=False, email=email, send=True)
    assert len(mail.outbox) == N+1

