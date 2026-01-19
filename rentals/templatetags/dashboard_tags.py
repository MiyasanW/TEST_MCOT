from django import template
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from rentals.models import Booking, Product

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    """
    Returns a dictionary of dashboard statistics for the admin dashboard.
    Usage: {% get_dashboard_stats as stats %}
    """
    today = timezone.now().date()
    
    # 1. Booking Stats
    bookings_today = Booking.objects.filter(start_time__date=today).count()
    bookings_pending = Booking.objects.filter(status='draft').count()
    bookings_this_month = Booking.objects.filter(
        start_time__year=today.year, 
        start_time__month=today.month
    ).count()
    
    # Booking Growth (vs Last Month)
    last_month = today.replace(day=1) - timezone.timedelta(days=1)
    bookings_last_month = Booking.objects.filter(
        start_time__year=last_month.year,
        start_time__month=last_month.month
    ).count()
    
    if bookings_last_month > 0:
        bookings_growth = ((bookings_this_month - bookings_last_month) / bookings_last_month) * 100
    else:
        bookings_growth = 100 if bookings_this_month > 0 else 0

    # 2. Revenue Calculation (This Month vs Last Month)
    revenue_this_month = 0
    monthly_bookings = Booking.objects.filter(
        start_time__year=today.year,
        start_time__month=today.month,
        status__in=['approved', 'completed']
    )
    for booking in monthly_bookings:
        revenue_this_month += booking.calculate_total_price()

    revenue_last_month = 0
    last_month_bookings = Booking.objects.filter(
        start_time__year=last_month.year,
        start_time__month=last_month.month,
        status__in=['approved', 'completed']
    )
    for booking in last_month_bookings:
        revenue_last_month += booking.calculate_total_price()
        
    if revenue_last_month > 0:
        revenue_growth = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
    else:
        revenue_growth = 100 if revenue_this_month > 0 else 0
        
    # 3. Staff & User Stats
    staff_active = User.objects.filter(is_staff=True, is_active=True).count()
    total_users = User.objects.count()
    
    # 4. Equipment Stats & Alerts
    equipment_total = Product.objects.count()
    equipment_available = Product.objects.filter(is_active=True, quantity__gt=0).count()
    
    # Notifications (Unread) - Fetching logic for alerts
    from rentals.models import Notification
    unread_notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    # 5. Activity Logs
    from django.contrib.admin.models import LogEntry
    import json
    
    raw_logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:100]
    recent_logs = []
    
    for log in raw_logs:
        message = ""
        try:
            data = json.loads(log.change_message)
            if isinstance(data, list) and data:
                actions = []
                for item in data:
                    if 'added' in item:
                        actions.append("Created")
                    elif 'changed' in item:
                        fields = item['changed'].get('fields', [])
                        actions.append(f"Changed: {', '.join(fields)}")
                    elif 'deleted' in item:
                        actions.append("Deleted")
                message = "; ".join(actions)
        except:
            message = log.change_message or "Changed"
            
        recent_logs.append({
            'user': log.user,
            'object_repr': log.object_repr,
            'action_time': log.action_time,
            'is_addition': log.is_addition(),
            'is_change': log.is_change(),
            'is_deletion': log.is_deletion(),
            'message': message
        })

    bookings_growth = round(bookings_growth, 1)

    # Thai Date Definitions (Moved to top for scope)
    thai_full_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    thai_days = {
        'Monday': 'จันทร์', 'Tuesday': 'อังคาร', 'Wednesday': 'พุธ',
        'Thursday': 'พฤหัสบดี', 'Friday': 'ศุกร์', 'Saturday': 'เสาร์',
        'Sunday': 'อาทิตย์'
    }

    # 6. Chart Data (Refactored for Table View)
    daily_stats = []
    from datetime import timedelta
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        # Thai Date for Row
        day_thai_short = thai_days.get(d.strftime('%A'), '')
        date_str = f"{d.day} {thai_full_months[d.month-1]}"
        
        daily_rev = 0
        for b in Booking.objects.filter(start_time__date=d, status__in=['approved', 'completed']):
             daily_rev += float(b.calculate_total_price())
        
        daily_stats.append({
            'date': f"{day_thai_short} {date_str}",
            'revenue': daily_rev
        })
    
    status_counts = {
        'draft': Booking.objects.filter(status='draft').count(),
        'approved': Booking.objects.filter(status='approved').count(),
        'completed': Booking.objects.filter(status='completed').count(),
        'active': Booking.objects.filter(status='active').count(),
        'problem': Booking.objects.filter(status='problem').count(),
    }

    # Header Date
    weekday_eng = today.strftime('%A')
    day_thai = thai_days.get(weekday_eng, weekday_eng)
    today_thai = f"วัน{day_thai}ที่ {today.day} {thai_full_months[today.month-1]} {today.year + 543}"

    return {
        'bookings_today': bookings_today,
        'bookings_pending': bookings_pending,
        'bookings_this_month': bookings_this_month,
        'bookings_growth': bookings_growth,
        'staff_active': staff_active,
        'total_users': total_users,
        'equipment_total': equipment_total,
        'equipment_available': equipment_available,
        'revenue_this_month': revenue_this_month,
        'revenue_last_month': revenue_last_month,
        'revenue_growth': round(revenue_growth, 1),
        'unread_notifications': unread_notifications,
        'recent_logs': recent_logs,
        'today_thai': today_thai,
        # Table Data
        'daily_stats': daily_stats,
        'status_counts': status_counts,
        'has_charts': False,
    }

@register.simple_tag
def get_recent_bookings(limit=7):
    """
    Returns the most recent bookings.
    Usage: {% get_recent_bookings 5 as recent_bookings %}
    """
    from django.db.models import Count
    return Booking.objects.select_related('created_by').annotate(items_count=Count('items')).order_by('-created_at')[:limit]
