from django.contrib import admin
from utils.models  import GeneralConfigurations

@admin.register(GeneralConfigurations)
class ConfigurationsAdmin(admin.ModelAdmin):
    pass