from django.apps import AppConfig


class FoncierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foncier'
    default_app_config = 'foncier.apps.FoncierConfig'

    def ready(self):
        import foncier.audit  # noqa: F401 — connecte les signaux du journal d'audit