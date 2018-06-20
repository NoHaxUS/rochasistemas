from django import template
from django.template import Library
from django.conf import settings
import os, re

register = template.Library()

@register.filter(name='standard_cotations_order_by')
def standard_cotations_order_by(queryset):

    standard_cotations = queryset.filter(is_standard=True).order_by('name')
    
    if standard_cotations.count() >=3:
        cotations_ordered = []
        cotations_ordered.append(standard_cotations[0])
        cotations_ordered.append(standard_cotations[2])
        cotations_ordered.append(standard_cotations[1])
        return cotations_ordered
  
    return standard_cotations

@register.filter(name='order_by')
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key,key)


@register.simple_tag
def app_name():
    return settings.APP_VERBOSE_NAME


@register.filter(name='get_verbose_cotation')
def get_verbose_cotation(cotation_name):
    names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
    return names_mapping.get(cotation_name, cotation_name)



