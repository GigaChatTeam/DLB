from configparser import ConfigParser

config = ConfigParser()
config.read("settings.ini")

SECRET_KEY = config.get("server", "SECRET_KEY")
DEBUG = config.getboolean("server", "DEBUG")
ALLOWED_HOSTS = tuple(h.strip() for h in config.get("server", "ALLOWED_HOSTS").split(","))

APPEND_SLASH = False

ROOT_URLCONF = "server.urls"

SERVER_ID = config.get("server", "SERVER_ID")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django.db'
    },
    "SQL": {
        "NAME": config.get("db-sql", "DB_NAME"),
        "USER": config.get("db-sql", "DB_USER"),
        "PASSWORD": config.get("db-sql", "DB_PASSWORD"),
        "HOST": config.get("db-sql", "DB_HOST"),
        "PORT": config.get("db-sql", "DB_PORT"),
        "APPLICATION": config.get("db-sql", "DB_APPLICATION").format(id=SERVER_ID),
        "POOL": {
            "MIN CONNECTIONS": config.getint("db-sql", "DB_POOL_MIN_CONNECTIONS"),
            "MAX CONNECTIONS": config.getint("db-sql", "DB_POOL_MAX_CONNECTIONS"),
        }
    },
    "S3": {
        "HOST": config.get("db-s3", "S3_HOST"),
        "ACCESS_KEY": config.get("db-s3", "S3_ACCESS_KEY"),
        "SECRET_KEY": config.get("db-s3", "S3_SECRET_KEY"),
        "SECURE": config.getboolean("db-s3", "S3_SECURE"),
    },
    "CH": {
        "USER": config.get("db-ch", "CH_USER"),
        "PASSWORD": config.get("db-ch", "CH_PASSWORD"),
        "HOST": config.get("db-ch", "CH_HOST"),
        "PORT": config.getint("db-ch", "CH_PORT"),
        "SECURE": config.get("db-ch", "CH_SECURE"),
    }
}

MIDDLEWARE = [
    "server.middleware.access.AccessDeniedMiddleware",
    "server.middleware.access.NotFoundMiddleware",
    "server.middleware.parameters.MissingParametersMiddleware"
]
