DEBUG = True

ALLOWED_HOSTS = '*'

# List of two-tuples containing your name, and an email [("Joe", "joe@example.com")]
ADMINS = []

# if you're having trouble connecting to LDAP set this to True so you can login
# to track, bypassing LDAP group checks
LDAP_DISABLED = False

# the hostname of the site, which will be used to construct absolute URLs
HOSTNAME = '10.0.0.10:8000'

# ('Your Name', 'your_email@example.com'),
ADMINS = []

DB_NAME = 'its'

DB_USER = 'postgres'

DB_PASSWORD = ''

DB_HOST = ''

SECRET_KEY = 'foobar'

# In dev: django.core.mail.backends.console.EmailBackend
# In prod: django.core.mail.backends.smtp.EmailBackend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LDAP_HOST = 'ldap://ldap-bulk.oit.pdx.edu'

LDAP_USERNAME = 'uid=rethinkwebsite,ou=service,dc=pdx,dc=edu'

LDAP_PASSWORD = ''

LDAP_SEARCH_DB = 'ou=people,dc=pdx,dc=edu'

LDAP_TLS = True
