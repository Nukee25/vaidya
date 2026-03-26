import os

from django.core.exceptions import ImproperlyConfigured


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ImproperlyConfigured("DATABASE_URL is required and must point to MariaDB.")
    if not database_url.startswith("mysql://"):
        raise ImproperlyConfigured("DATABASE_URL must use a MariaDB/MySQL URL (mysql://...).")
    return database_url
