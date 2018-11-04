from django import template
from django.template import Library
from django.conf import settings
import os, re

register = template.Library()

@register.filter(name='standard_cotations_order_by')
def standard_cotations_order_by(queryset):

    standard = queryset.filter(market__name="1X2", market__isnull=False)

    home = standard.filter(name='Casa').first()
    away = standard.filter(name='Fora').first()
    draw = standard.filter(name='Empate').first()
    
    return [home, draw, away]


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key,key)

@register.simple_tag
def app_name():
    return settings.APP_VERBOSE_NAME

