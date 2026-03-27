from django import template

register = template.Library()


@register.filter
def first_name(value):
    """Return the first word (assumed first name) from a full name string."""
    try:
        if not value:
            return ''
        return str(value).split()[0]
    except Exception:
        return value
