from django.apps import AppConfig
from django.db.models.signals import post_migrate

def define_country_priority(sender, **kwargs):
    print("Definindo prioridades de países")
    from core.models import Location
    Location.objects.filter(pk=183).update(priority=150)
    Location.objects.filter(pk__in=[203,142,221,195,230,197,138,76,215,218,176,147,243])\
    .update(priority=100)
    

class UserConfig(AppConfig):
    name = 'user'
    verbose_name = "Usuários"
    
    def ready(self):
        post_migrate.connect(define_country_priority, sender=self)
