
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _ 
from django.contrib.auth import authenticate

from captcha.fields import CaptchaField
from mezzanine.core.forms import Html5Mixin
from mezzanine.accounts import forms as base

def captcha():
    return CaptchaField(
        label="Enter the letters you see below",
        help_text="Confirm that you are human",
    )

def ProfileForm(*args, **kwargs):
    user = kwargs.get("instance")
    if user and user.is_authenticated():
        cls = base.ProfileForm
    else:
        cls = SignupForm
    return cls(*args, **kwargs)

class SignupForm(base.ProfileForm):
    check = captcha()

class LoginForm(base.LoginForm):
    check = captcha()

class PasswordResetForm(base.PasswordResetForm):
    check = captcha()

class QuickLoginForm(Html5Mixin, forms.Form):
    key = forms.CharField(label="Code", max_length=12)

    def clean_key(self):
        key = self.cleaned_data["key"]
        self._user = authenticate(invite_key=key)
        if self._user is None:
            raise forms.ValidationError(ugettext("Invalid key"))
        elif not self._user.is_active:
            raise forms.ValidationError(ugettext("Your account is inactive"))
        return self.cleaned_data

    def save(self):
        """
        Just return the authenticated user - used for logging in.
        """
        return getattr(self, "_user", None)

