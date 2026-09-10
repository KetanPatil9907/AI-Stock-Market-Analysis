from django import template

register = template.Library()


@register.filter(name="get")
def get_value(dictionary, key):
    """Get a value from a dictionary by key in templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
