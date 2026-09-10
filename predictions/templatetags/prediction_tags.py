from django import template

register = template.Library()


@register.filter
def get_value(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def abs_value(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
