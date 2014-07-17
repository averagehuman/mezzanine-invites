from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mezzanine.conf import settings


LOGIN_URL = settings.LOGIN_URL
ACCOUNT_URL = getattr(settings, "ACCOUNT_URL", "/accounts/")
PASSWORD_RESET_URL = getattr(
    settings, "PASSWORD_RESET_URL", "/%s/password/reset/" % ACCOUNT_URL.strip("/")
)

_slash = "/" if settings.APPEND_SLASH else ""

urlpatterns = patterns("invites.views",
    url("^%s%s$" % (LOGIN_URL.strip("/"), _slash),
        "login", name="login"),
    url("^%s/pending%s$" % (PASSWORD_RESET_URL.strip("/"), _slash),
        "password_reset_sent", name="mezzanine_password_reset_sent"),
    url("^%s%s$" % (PASSWORD_RESET_URL.strip("/"), _slash),
        "password_reset", name="mezzanine_password_reset"),
)

