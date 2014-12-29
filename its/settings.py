import os
import sys
from fnmatch import fnmatch
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages import constants as messages
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP, AUTHENTICATION_BACKENDS
from varlet import variable


PROJECT_DIR = lambda *path: os.path.normpath(os.path.join(os.path.dirname(__file__), *path))
ROOT = lambda *path: PROJECT_DIR("../", *path)
FIXTURE_DIRS = '/vagrant/its/its/its/fixtures'

#FIXTURE_DIRS = lambda *path: os.path.join(PROJECT_DIR, 'fixtures'),


# SECURITY WARNING: don't run with debug turned on in production!
# make this True in dev
DEBUG = variable("DEBUG", default=False)
TEMPLATE_DEBUG = DEBUG

IN_TEST_MODE = 'test' in sys.argv

ALLOWED_HOSTS = variable("ALLOWED_HOSTS", default="*")

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'no-reply@pdx.edu'

# List of two-tuples containing your name, and an email [("Joe", "joe@example.com")]
ADMINS = variable("ADMINS", [])

# the hostname of the site, which will be used to construct absolute URLs
HOSTNAME = variable("HOSTNAME", default="10.0.0.10:8000")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'its',
        # the default is fine for dev
        'USER': variable("DB_USER", default='root'),
        # the default is fine for dev
        'PASSWORD': variable("DB_PASSWORD", default=''),
        # the default is fine for dev
        'HOST': variable("DB_HOST", default=''),
        'PORT': '',
    },
}

LOGGING_CONFIG = 'arcutils.logging.basic'

LOGIN_URL = reverse_lazy("home")
#LOGIN_REDIRECT_URL = reverse_lazy("users-home")
LOGOUT_URL = reverse_lazy("home")

# uncomment to use celery, also update celery.py, and requirements.txt
#BROKER_URL = 'amqp://guest:guest@localhost//'
#CELERY_ACKS_LATE = True
#CELERY_RESULT_BACKEND = 'amqp'

# uncomment to use CAS. You need to update requirements.txt too
CAS_SERVER_URL = 'https://sso.pdx.edu/cas/'
AUTHENTICATION_BACKENDS += ('djangocas.backends.CASBackend',)


AUTH_USER_MODEL = 'users.User'

# In dev: django.core.mail.backends.console.EmailBackend
# In prod: django.core.mail.backends.smtp.EmailBackend
EMAIL_BACKEND = variable("EMAIL_BACKEND", default='django.core.mail.backends.console.EmailBackend')

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}


# allow the use of wildcards in the INTERAL_IPS setting
class IPList(list):
    # do a unix-like glob match
    # E.g. '192.168.1.100' would match '192.*'
    def __contains__(self, ip):  # pragma: no cover
        for ip_pattern in self:
            if fnmatch(ip, ip_pattern):
                return True
        return False

INTERNAL_IPS = IPList(['10.*', '192.168.*'])


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'arcutils',
    'its.users',
	'its.items',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'djangocas.middleware.CASMiddleware',
)

ROOT_URLCONF = 'its.urls'

WSGI_APPLICATION = 'its.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = ROOT("static")

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_DIR("static"),
)

MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ROOT("media")

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_DIR("templates"),
	#[os.path.join(BASE_DIR, 'templates')],
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = variable("SECRET_KEY", os.urandom(64).decode("latin1"))

if IN_TEST_MODE:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    CELERY_ALWAYS_EAGER = True
