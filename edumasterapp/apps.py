from django.apps import AppConfig


class EdumasterappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "edumasterapp"
    verbose_name = "EDUMASTER"

    def ready(self):
        from . import signals
