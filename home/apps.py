from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        # Wire up the post_migrate signal so a superuser is auto-created
        # (or ensured) after every `python manage.py migrate` run.
        # This makes the admin login work out-of-the-box on every deploy
        # without anyone having to remember to run a separate command.
        from django.db.models.signals import post_migrate
        from .signals import ensure_superuser

        post_migrate.connect(ensure_superuser, sender=self)
