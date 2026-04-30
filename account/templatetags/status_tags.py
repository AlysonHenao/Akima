from django import template
import unicodedata

register = template.Library()


def _normalize(s):
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    return s.strip().lower()


def _mapping():
    return {
        'pendiente confirmacion': 'badge-status-pendiente',
        'confirmado': 'badge-status-confirmado',
        'en produccion': 'badge-status-produccion',
        'completado': 'badge-status-completado',
        'enviado': 'badge-status-enviado',
        'entregado': 'badge-status-entregado',
        'cancelado': 'badge-status-cancelado',
        'pendiente': 'badge-status-pendiente',
        'en progreso': 'badge-status-en-progreso',
        'completada': 'badge-status-completada',
        'cancelada': 'badge-status-cancelada',
    }


def _status_to_class(status):
    key = _normalize(status)
    return _mapping().get(key, 'badge-status-pendiente')


@register.filter(name='status_badge_class')
def status_badge_class(status):
    return _status_to_class(status)


@register.filter(name='status_badge')
def status_badge(status):
    return _status_to_class(status)