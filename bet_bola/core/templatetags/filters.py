from django import template
from django.template import Library
from django.conf import settings
import os, re
from utils.choices import COUNTRY_TRANSLATE


register = template.Library()

@register.filter(name='standard_cotations_order_by')
def standard_cotations_order_by(queryset):

    standard_cotations = queryset.filter(is_standard=True, kind__isnull=False).order_by('name')

    if standard_cotations.count() >=3:
        cotations_ordered = []
        cotations_ordered.append(standard_cotations[0])
        cotations_ordered.append(standard_cotations[2])
        cotations_ordered.append(standard_cotations[1])
        return cotations_ordered
  
    return standard_cotations


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key,key)

@register.filter(name='translate_country')
def translate_country(country_name):
    return COUNTRY_TRANSLATE.get(country_name, country_name)


@register.simple_tag
def app_name():
    return settings.APP_VERBOSE_NAME


@register.filter(name='get_verbose_cotation')
def get_verbose_cotation(cotation_name):
    names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
    return names_mapping.get(cotation_name, cotation_name)