"""Create a superuser from environment variables.

Reads DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL /
DJANGO_SUPERUSER_PASSWORD from the environment. Falls back to the
hardcoded defaults below only when the env vars are not set, so the
command still works out of the box in development.

Run with:  python manage.py create_superuser
"""
import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


DEFAULT_USERNAME = "fuad"
DEFAULT_EMAIL = "fuad@email.com"
DEFAULT_PASSWORD = "fuad1234"


class Command(BaseCommand):
    help = (
        "Create a superuser from DJANGO_SUPERUSER_* env vars "
        "(or sensible defaults if they are not set)."
    )

    def handle(self, *args, **kwargs):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", DEFAULT_USERNAME)
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", DEFAULT_EMAIL)
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", DEFAULT_PASSWORD)

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD not set — skipping."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Superuser '{username}' already exists — leaving it untouched."
            ))
            return

        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{username}' created."
        ))
