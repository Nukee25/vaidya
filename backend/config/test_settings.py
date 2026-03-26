import os

os.environ.setdefault("DATABASE_URL", "mysql://root:password@localhost:3306/testdb")

from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
