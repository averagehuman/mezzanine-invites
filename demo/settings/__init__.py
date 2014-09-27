
DEBUG = False
NOCACHE = False
DATABASES = None

from .defaults import *

SECRET_KEY = "123456789!!987654321"
NEVERCACHE_KEY = "abcdefg!!zyxwvu"


try:
    from .local_settings import *
except ImportError:
    pass

##########
# CACHES #
##########

#############
# DATABASES #
#############
if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db',
        }
    }

####################
# DYNAMIC SETTINGS #
####################

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable. We also allow this settings module to be imported
# without Mezzanine installed, as the case may be when using the
# fabfile, where setting the dynamic settings below isn't strictly
# required.
try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())

AUTHENTICATION_BACKENDS = [
    X for X in AUTHENTICATION_BACKENDS if 'mezzanine' not in X
]

