# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = '0.2.0'

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
    name="mezzanine-invites",
    version=__version__,
    description="Authentication Backend for Mezzanine that allows site registration via"
    " alphanumeric invite codes.",
    author="gmf",
    author_email="gmflanagan@outlook.com",
    license="MIT",
    url="https://pypi.python.org/pypi/mezzanine-invites",
    download_url="https://pypi.python.org/packages/source/m/mezzanine-invites/mezzanine-invites-%s.tar.gz" % __version__ ,
    packages = find_packages(),
    tests_require=['tox'],
    cmdclass = {'test': Tox},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
)
    

