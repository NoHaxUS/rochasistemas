from django import template
from django.template import Library
from django.conf import settings

register = template.Library()

@register.filter(name='standard_cotations_order_by')
def standard_cotations_order_by(queryset):

    standard_cotations = queryset.filter(is_standard=True)
    if standard_cotations:
        cote = [standard_cotations.get('1'), standard_cotations.get('X'), standard_cotations.get('2')]
        return cote
    else:
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
