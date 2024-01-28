from decouple import config

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=list[str])

APPEND_SLASH = False

ROOT_URLCONF = 'server.urls'

SERVER_ID = config("SERVER_ID")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT", cast=int),
        'APPLICATION': config("APPLICATION").format(id=SERVER_ID)
    },
    'S3': {
        'HOST': config("S3_HOST"),
        'ACCESS_KEY': config("S3_ACCESS_KEY"),
        'SECRET_KEY': config("S3_SECRET_KEY"),
        'SECURE': config("S3_SECURE", cast=bool, default=not DEBUG),
    }
}

MIDDLEWARE = [
    'server.middleware.access.AccessDeniedMiddleware',
    'server.middleware.access.NotFoundMiddleware',
    'server.middleware.parameters.MissingParametersMiddleware'
]
