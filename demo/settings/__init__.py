
DEBUG = False
NOCACHE = False
DATABASES = None

from .defaults import *

SECRET_KEY = "123456789!!987654321"
NEVERCACHE_KEY = "abcdefg!!zyxwvu"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_SES_ACCESS_KEY_ID = ''
AWS_SES_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''

GOOGLE_ANALYTICS_PROPERTY_ID = ''
GOOGLE_ANALYTICS_DOMAIN = ''


try:
    from .local_settings import *
except ImportError:
    pass

##########
# CACHES #
##########
if not NOCACHE:

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': ['127.0.0.1:11211'],
            'KEY_PREFIX': 'django-test',
            'TIMEOUT': 0,
        },
    }

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

