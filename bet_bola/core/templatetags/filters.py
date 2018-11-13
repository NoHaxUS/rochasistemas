from django import template
from django.template import Library
from django.conf import settings
import os, re

register = template.Library()

@register.filter(name='standard_cotations_order_by')
def standard_cotations_order_by(my_cotations):
    home, draw, away = None, None, None
    for cotation in my_cotations:

        if cotation.name == 'Casa':
            home = cotation
        elif cotation.name == 'Fora':
            away = cotation
        elif cotation.name == 'Empate':
            draw = cotation

    return [home, draw, away]


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key,key)

@register.simple_tag
def app_name():
    return settings.APP_VERBOSE_NAME

