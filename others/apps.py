from django.apps import AppConfig


class OthersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "others"
    # The app folder is still `others` for backwards compatibility with
    # the existing migrations, but the user-facing page is "My World".
    verbose_name = "My World (Games & Videos)"
