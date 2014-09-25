
from mezzanine.utils.email import send_mail_template
from mezzanine.conf import settings


def send_invite_code_mail(code, site_url, login_url):
    context = {
        'code': code,
        'site_name': settings.SITE_TITLE,
        'site_url': site_url,
        'login_url': login_url,
    }
    send_mail_template(
        "Your Invitation to %s" % settings.SITE_TITLE,
        "invites/send_invite_email",
        settings.DEFAULT_FROM_EMAIL,
        code.registered_to,
        context=context,
        fail_silently=False,
    )

