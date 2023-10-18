SECRET_KEY = 'django-insecure-5qgnnfl2^u-@@a2+yu1iq(swstlos4*c7p8_ob3+4$^pva=5am'

ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'server.urls'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# MIDDLEWARE = (
#     'django_ratelimit.middleware.RatelimitMiddleware',
# )
#
# RATELIMIT_VIEW = 'server.views.ratelimited'
