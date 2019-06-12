from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UtilsConfig(AppConfig):
    name = 'utils'
    verbose_name = 'Utilidades'
        