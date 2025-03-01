from django import template
from django.utils import timezone
from datetime import timedelta
import locale

register = template.Library()

@register.filter(name='currency_idr')
def currency_idr(value):
    """Format a number as Indonesian Rupiah"""
    try:
        return f"Rp {int(value):,}".replace(',', '.')
    except (ValueError, TypeError):
        return ''

@register.filter(name='duration')
def duration(td):
    """Format a timedelta into a human-readable duration"""
    if not isinstance(td, timedelta):
        return ''
    
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0:
        if minutes > 0:
            return f"{hours} jam {minutes} menit"
        return f"{hours} jam"
    if minutes > 0:
        return f"{minutes} menit"
    return "Kurang dari 1 menit"

@register.filter(name='time_since')
def time_since(value):
    """Returns a human-friendly time difference from now"""
    if not value:
        return ''
    
    now = timezone.now()
    diff = now - value
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} tahun yang lalu"
    if diff.days > 30:
        months = diff.days // 30
        return f"{months} bulan yang lalu"
    if diff.days > 0:
        return f"{diff.days} hari yang lalu"
    if diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} jam yang lalu"
    if diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} menit yang lalu"
    return "Baru saja"

@register.simple_tag
def get_vehicle_status(record):
    """Returns the status and appropriate badge class for a parking record"""
    if not record.exit_time:
        return {
            'text': 'Aktif',
            'class': 'bg-primary'
        }
    if record.is_paid:
        return {
            'text': 'Lunas',
            'class': 'bg-success'
        }
    return {
        'text': 'Belum Lunas',
        'class': 'bg-warning'
    }
