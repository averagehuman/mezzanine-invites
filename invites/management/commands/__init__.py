
import os
from optparse import make_option
from ConfigParser import ConfigParser

from django.core.management.base import BaseCommand, CommandError

pathjoin = os.path.join
pathexists = os.path.exists
dirname = os.path.dirname
basename = os.path.basename

class SiteConfigureCommand(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--config', dest='config',
            help="The path to a 'site.cfg' file"),
    )

    def handle(self, *args, **options):
        inifile = options.get('config')
        if not inifile:
            cwd = os.getcwd()
            inifile = pathjoin(cwd, '.site.cfg')
        if not pathexists(inifile):
            raise CommandError("can't find config file - '%s'" % inifile)
        cfg = ConfigParser()
        cfg.read(inifile)
        self.configure(cfg)

