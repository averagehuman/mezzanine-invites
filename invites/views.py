
from __future__ import unicode_literals

from django.contrib.messages import info, error
from django.contrib.auth import login as auth_login
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.template import loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from mezzanine.conf import settings
from mezzanine.utils.views import render
from mezzanine.utils.email import send_verification_mail
from mezzanine.utils.urls import login_redirect

from .models import InvitationCode
from .forms import LoginForm, PasswordResetForm, QuickLoginForm, InviteForm
from .utils import send_invite_code_mail

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

@login_required
@staff_member_required
def send_invite(request, template="invites/send_invite.html"):
    form = InviteForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        dummy = form.save(commit=False)
        code = InvitationCode.objects.create_invite_code(
            dummy.registered_to,
            name=dummy.registered_name,
            phone=dummy.registered_phone,
            creator=request.user,
        )
        site_url = request.build_absolute_uri(reverse("home"))
        login_url = request.build_absolute_uri(reverse("login"))
        try:
            send_invite_code_mail(code, site_url, login_url)
        except Exception as e:
            if settings.DEBUG:
                raise
            error(request, "There was an error sending mail to %s. [%s]" % (
                code.registered_to, e
            ))
        else:
            info(request, "An Invite has been sent to %s." % code.registered_to)
        return redirect(reverse("send-invite"))
    context = {'form': form, 'title': 'Send Invitation'}
    return render(request, template, context)


