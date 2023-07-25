# bar/__init__.py

from django import template
from .custom_filters import inttimes, get_item

# Register the custom filters
register = template.Library()
register.filter('inttimes', inttimes)
register.filter('get_item', get_item)
