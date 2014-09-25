
import os
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import reverse
import pytest

@pytest.fixture()
def user(db):
    """A non-admin User"""
    from django.contrib.auth.models import User

    try:
        User.objects.get(username='test')
    except User.DoesNotExist:
        user = User.objects.create_user(
            'test', 'test@example.com', 'password'
        )
        user.is_staff = False
        user.is_superuser = False
        user.save()

    return user

@pytest.fixture()
def auth_client(user):
    """A Django test client logged in as an authenticated user"""
    client = Client()
    client.login(username=user.username, password='password')
    return client

data_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

@pytest.fixture
def File():
    def FileOpener(relpath, mode="rb"):
        return open(os.path.join(data_root, relpath.lstrip('/')), mode)
    return FileOpener



