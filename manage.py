#!/usr/bin/env python
"""Django"s command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    if "init-config" == sys.argv[1]:
        from configparser import ConfigParser

        try:
            from django.core.management.utils import get_random_secret_key
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc

        config = ConfigParser()

        config.add_section("server")
        config.set("server", "SECRET_KEY", get_random_secret_key().replace("%", "%%"))
        config.set("server", "ALLOWED_HOSTS", "127.0.0.1")
        config.set("server", "DEBUG", "True")
        config.set("server", "SERVER_ID", "DEFAULT SERVER ID")

        config.add_section("db-sql")
        config.set("db-sql", "DB_NAME", "public")
        config.set("db-sql", "DB_USER", "root")
        config.set("db-sql", "DB_PASSWORD", "password")
        config.set("db-sql", "DB_HOST", "localhost")
        config.set("db-sql", "DB_PORT", "0")
        config.set("db-sql", "DB_APPLICATION", "GigaChat DLB server - default startup")
        config.set("db-sql", "DB_POOL_MIN_CONNECTIONS", "1")
        config.set("db-sql", "DB_POOL_MAX_CONNECTIONS", "10")

        config.add_section("db-s3")
        config.set("db-s3", "S3_HOST", "localhost")
        config.set("db-s3", "S3_SECRET_KEY", "S3-SECRET-KEY")
        config.set("db-s3", "S3_ACCESS_KEY", "S3-ACCESS-KEY")
        config.set("db-s3", "S3_SECURE", "True")

        config.add_section("db-ch")
        config.set("db-ch", "CH_HOST", "localhost")
        config.set("db-ch", "CH_PORT", "8123")
        config.set("db-ch", "CH_USER", "CH-USER")
        config.set("db-ch", "CH_PASSWORD", "CH-PASSWORD")
        config.set("db-ch", "CH_SECURE", "True")

        with open("settings.ini", "w") as config_file:
            config.write(config_file)

        exit(0)

    main()
