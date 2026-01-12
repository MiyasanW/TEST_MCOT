from django import template
from datetime import date, datetime

register = template.Library()

THAI_MONTHS = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
]

THAI_FULL_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

@register.filter(name='thai_date')
def thai_date(value, arg=None):
    if not value:
        return ""
    
    # Ensure value is a date or datetime object
    if not isinstance(value, (date, datetime)):
        return value

    year = value.year + 543
    month = value.month - 1
    day = value.day
    
    if arg == 'full':
        return f"{day} {THAI_FULL_MONTHS[month]} {year}"
    
    # Default short format
    return f"{day} {THAI_MONTHS[month]} {year}"

@register.filter(name='thai_datetime')
def thai_datetime(value):
    if not value:
        return ""
    
    if not isinstance(value, (date, datetime)):
        return value
        
    date_part = thai_date(value)
    time_part = value.strftime('%H:%M')
    return f"{date_part} {time_part}"
