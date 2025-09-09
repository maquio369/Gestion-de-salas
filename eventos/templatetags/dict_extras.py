from django import template

register = template.Library()

@register.filter
def dictkey(d, key):
    """Permite obtener un valor por clave en un diccionario dentro del template."""
    try:
        return d.get(key)
    except Exception:
        return None
