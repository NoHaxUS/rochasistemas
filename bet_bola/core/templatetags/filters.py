from django import template
from django.template import Library

register = template.Library()

@register.filter(name='standard_cotations_order_by')
def standard_cotations_order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.filter(is_standard=True).order_by(*args)
