"""
Management utility to create invitation codes

Eg. python manage.py invite --domain=mysite.com

"""

import os
import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.utils.encoding import force_str, force_text
from django.contrib.sites.models import Site
from django.utils.six.moves import input

from invites.models import InvitationCode
from invites.utils import send_invite_code_mail

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--email', dest='email',
            help="The email address of the invitee"),
        make_option('--domain', dest='domain',
            help="The site's url root domain"),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".'),
    )
    help = 'Create an Invite Code'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        database = options.get('database')
        email = options.get('email')
        domain = options.get('domain')
        sites = Site.objects.all()
        site_items = dict((str(obj.id), obj) for obj in sites)
        site = None
        if not site_items:
            raise CommandError("No site available.")
        while not email:
            email = (input(
                force_str('Enter the email address of the recipient: ')
            ) or '').strip()
        if domain:
            for site in sites:
                if site.domain == domain:
                    break
            else:
                raise CommandError("A site with domain '%s' does not exist" % domain)
        else:
            if len(site_items) == 1:
                site = sites[0]
            while site is None:
                for obj in sites:
                    self.stdout.write("[%s] %s" % (obj.id, obj.domain))
                site_id = input(force_str('Select a site: '))
                try:
                    site = site_items[site_id]
                except KeyError:
                    continue
        code = InvitationCode.objects.create_invite_code(email, site=site)
        do_send = None
        while do_send is None:
            do_send = (input(
                force_str('Send the code now? [y/N]')
            ) or '').strip().lower()
            do_send = do_send or 'n'
            if do_send not in 'yn':
                do_send = None
        if do_send == 'y':
            secure = None
            while secure is None:
                secure = (input(
                    force_str('Use https for site urls in the email? [y/N]')
                ) or '').strip().lower()
                secure = secure or 'n'
                if secure not in 'yn':
                    secure = None
            protocol = 'http'
            if secure == 'y':
                protocol += 's'
            site_url = '%s://%s%s' % (protocol, site.domain, reverse("home"))
            login_url = '%s://%s%s' % (protocol, site.domain, reverse("login"))
            try:
                send_invite_code_mail(code, site_url, login_url)
            except Exception as e:
                self.stdout.write("Mail send error - %s" % e)
                sys.exit("FAIL")
                return
            else:
                self.stdout.write("Mail sent to %s." code.registered_to)
        else:
            self.stdout.write(code.short_key)


