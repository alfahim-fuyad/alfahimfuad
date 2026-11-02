"""Signal handlers for the home app.

`ensure_superuser` runs after every `python manage.py migrate` and makes
sure a superuser exists so the admin login at /admin/ always works.

It reads credentials from the DJANGO_SUPERUSER_* environment variables
(and falls back to the hardcoded defaults below when those are not set).

The logic is deliberately identical to the
`home/management/commands/create_superuser.py` command, so whether the
deploy runs `migrate` only, `create_superuser` only, or both, the result
is the same: exactly one superuser exists and you can log in.

If a superuser with the chosen username already exists, it is LEFT
UNTOUCHED — the password is NOT reset. This protects you if you've
already changed the password inside /admin/.
"""
import os

from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver


DEFAULT_USERNAME = "fuad"
DEFAULT_EMAIL = "fuad@email.com"
DEFAULT_PASSWORD = "fuad1234"


@receiver(post_migrate)
def ensure_superuser(sender, **kwargs):
    # Only run for the home app's own migrations (and the very first
    # migrate that creates the auth tables). The sender is the AppConfig
    # of the app whose migrations just finished.
    app_label = getattr(sender, "label", None) or getattr(sender, "name", None)
    if app_label not in (None, "home", "auth", "contenttypes"):
        return

    # Need the auth tables to exist before we can create a user.
    try:
        User._meta.get_field("username")
    except Exception:
        return  # auth tables not ready yet

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", DEFAULT_USERNAME).strip()
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", DEFAULT_EMAIL).strip()
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", DEFAULT_PASSWORD)

    if not username or not password:
        return

    # If the superuser already exists, leave it alone — don't reset the
    # password (the owner may have changed it inside /admin/).
    if User.objects.filter(username=username).exists():
        return

    try:
        User.objects.create_superuser(username, email, password)
    except Exception:
        # Never let a signal crash the migrate command.
        pass
