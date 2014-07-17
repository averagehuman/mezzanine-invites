from __future__ import unicode_literals

from django.contrib.auth import (authenticate, login as auth_login,
                                               logout as auth_logout)
from django.contrib.messages import info, error
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.conf import settings

from mezzanine.accounts import get_profile_form
from mezzanine.utils.email import send_verification_mail
from mezzanine.utils.urls import login_redirect
from mezzanine.utils.views import render

from .forms import LoginForm, PasswordResetForm, QuickLoginForm

def login(request, template="accounts/account_login.html"):
    """
    Login form.
    """
    form = LoginForm(request.POST or None)
    quick_form = QuickLoginForm(request.POST or None)
    if request.method == "POST":
        if request.POST.get("login_type") == "quick":
            f = quick_form
        else:
            f = form
        if f.is_valid():
            authenticated_user = f.save()
            info(request, _("Successfully logged in"))
            auth_login(request, authenticated_user)
            request.logged_in = True
            response = login_redirect(request)
            response.set_cookie(NGINX_CACHE_COOKIE, '')
            return response
    context = {"form": form, "quick_form": quick_form, "title": _("Log in")}
    return render(request, template, context)


def password_reset(request, template="accounts/account_password_reset.html"):
    form = PasswordResetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        send_verification_mail(request, user, "password_reset_verify")
        info(request, _("A verification email has been sent with "
                        "a link for resetting your password."))
        return redirect(reverse("mezzanine_password_reset_sent"))
    context = {"form": form, "title": _("Password Reset")}
    return render(request, template, context)

def password_reset_sent(request, template="accounts/account_password_reset_sent.html"):
    context = {"title": _("Password Reset Pending")}
    return render(request, template, context)

