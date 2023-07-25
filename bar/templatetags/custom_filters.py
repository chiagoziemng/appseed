from django import template

register = template.Library()

@register.filter
def inttimes(value, arg):
    return int(value) * arg

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)

