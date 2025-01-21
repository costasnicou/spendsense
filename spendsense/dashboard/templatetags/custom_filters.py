from django import template
from django.utils.translation import gettext as _
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom template filter to get a dictionary value by key.
    """
    return dictionary.get(key)

@register.filter(name='translate')
def translate(value):
    return _(value)