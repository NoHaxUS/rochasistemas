from django.contrib.admin.apps import AdminConfig
from django.contrib.admin.sites import AdminSite
from django.conf import settings


class CustomAdminSite(AdminSite):
    site_header = settings.APP_VERBOSE_NAME
    site_title = settings.APP_VERBOSE_NAME


class MyAdminConfig(AdminConfig):
    default_site = 'config.apps.CustomAdminSite'