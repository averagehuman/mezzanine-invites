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

from invites.models import InvitationCode

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--domain', dest='domain',
            help="The site's url root domain"),
        make_option('--email', dest='email',
            help="The email address of the invitee"),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Specifies the database to use. Default is "default".'),
    )
    help = 'Create an Invite Code'

    def handle(self, *args, **options):
        domain = options.get('domain')
        if not domain:
            raise CommandError("Missing argument: --domain")
        try:
            site = Site.objects.get(domain=domain)
        except Site.DoesNotExist:
            raise CommandError("A site with domain '%s' does not exist" % domain)
        email = options.get('email')
        verbosity = int(options.get('verbosity', 1))
        database = options.get('database')
        code = InvitationCode.objects.create_invite_code(
            site=site, email=email
        )
        print("%s - <%s>" % (code.short_key, email))


