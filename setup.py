# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = '0.0.2'

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)



setup(
    name="invites",
    version=__version__,
    description="Extensions for Mezzanine Drum.",
    download_url="",
    packages = find_packages(),
    tests_require=['tox'],
    cmdclass = {'test': Tox},
)
    

