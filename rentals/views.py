from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Equipment, Studio, Staff


@staff_member_required
def dashboard(request):
    """
    Dashboard หน้าหลักของ MCOT Rental System
    แสดงภาพรวม สถิติ และ Quick Actions
    """
    today = timezone.now().date()
    
    # สถิติการจอง
    bookings_today = Booking.objects.filter(
        start_time__date=today
    ).count()
    
    bookings_pending = Booking.objects.filter(
        status='draft'
    ).count()
    
    bookings_this_month = Booking.objects.filter(
        start_time__year=today.year,
        start_time__month=today.month
    ).count()
    
    # สถิติอุปกรณ์
    equipment_total = Equipment.objects.count()
    equipment_available = Equipment.objects.filter(
        status='available'
    ).count()
    equipment_maintenance = Equipment.objects.filter(
        status='maintenance'
    ).count()
    
    # สถิติสตูดิโอ
    studio_total = Studio.objects.count()
    
    # สถิติพนักงาน
    staff_active = Staff.objects.filter(is_active=True).count()
    
    # รายการจองล่าสุด (5 รายการ)
    recent_bookings = Booking.objects.select_related().prefetch_related(
        'equipment', 'studios', 'staff'
    ).order_by('-id')[:5]
    
    # Alerts: อุปกรณ์ที่ต้องคืนวันนี้
    ending_today = Booking.objects.filter(
        end_time__date=today,
        status='approved'
    ).prefetch_related('equipment').order_by('end_time')
    
    # Alerts: การจองที่รอการอนุมัติ  
    pending_bookings = Booking.objects.filter(
        status='draft'
    ).prefetch_related('equipment', 'studios').order_by('-id')[:5]
    
    # คำนวณรายได้เดือนนี้ (ประมาณการ)
    revenue_this_month = 0
    for booking in Booking.objects.filter(
        start_time__year=today.year,
        start_time__month=today.month,
        status__in=['approved', 'completed']
    ):
        revenue_this_month += booking.calculate_total_price()
    
    context = {
        'today': today,
        'stats': {
            'bookings_today': bookings_today,
            'bookings_pending': bookings_pending,
            'bookings_this_month': bookings_this_month,
            'equipment_available': equipment_available,
            'equipment_total': equipment_total,
            'equipment_maintenance': equipment_maintenance,
            'studio_total': studio_total,
            'staff_active': staff_active,
            'revenue_this_month': revenue_this_month,
        },
        'recent_bookings': recent_bookings,
        'ending_today': ending_today,
        'pending_bookings': pending_bookings,
        'equipment_total': equipment_total, # Pass directly to debug
        'equipment_available': equipment_available,
    }
    
    return render(request, 'rentals/dashboard.html', context)

@staff_member_required
def calendar_view(request):
    """
    หน้าปฏิทินแสดงรายการจองทั้งหมด
    """
    return render(request, 'rentals/calendar.html')

@staff_member_required
def booking_api(request):
    """
    API สำหรับส่งข้อมูลการจองให้ FullCalendar
    """
    from django.http import JsonResponse
    
    events = []
    bookings = Booking.objects.all()
    
    for booking in bookings:
        # Determine color based on status
        color = '#3788d8' # Default blue
        if booking.status == 'approved':
            color = '#28a745' # Green
        elif booking.status == 'draft':
            color = '#ffc107' # Yellow/Orange for draft
        elif booking.status == 'completed':
            color = '#6c757d' # Gray
            
        # Get creator name (fallback to username if first_name is empty)
        creator_name = 'Unknown'
        if booking.created_by:
            creator_name = booking.created_by.first_name or booking.created_by.username
            
        title = f"{booking.customer_name} ({booking.equipment.count()} รายการ)"
        if booking.created_by:
             title += f" [โดย: {creator_name}]"
            
        events.append({
            'title': title,
            'start': booking.start_time.isoformat(),
            'end': booking.end_time.isoformat(),
            'url': f"/admin/rentals/booking/{booking.id}/change/",
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'creator': creator_name
            }
        })
        
    return JsonResponse(events, safe=False, json_dumps_params={'ensure_ascii': False})


@staff_member_required
def staff_quotation(request, booking_id):
    """
    สร้างใบเสนอราคาสำหรับ Booking ที่ระบุ
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # คำนวณวัน
    duration = booking.end_time - booking.start_time
    days = duration.total_seconds() / (24 * 3600)
    if days < 1:
        days = 1
    else:
        days = int(days) + (1 if days % 1 > 0 else 0)
    
    # รวบรวมรายการ
    items = []
    
    # Equipment
    for eq in booking.equipment.all():
        items.append({
            'name': eq.name,
            'details': f"S/N: {eq.serial_number}",
            'price': eq.daily_rate,
            'total': eq.daily_rate * days,
            'type': 'Equipment'
        })
        
    # Studios
    for st in booking.studios.all():
        items.append({
            'name': st.name,
            'details': "Studio rental",
            'price': st.daily_rate,
            'total': st.daily_rate * days,
            'type': 'Studio'
        })

    # คำนวณยอดรวม
    from decimal import Decimal
    subtotal = sum(item['total'] for item in items)
    vat = subtotal * Decimal('0.07')
    grand_total = subtotal + vat
    
    context = {
        'booking': booking,
        'items': items,
        'days': int(days),
        'subtotal': subtotal,
        'vat': vat,
        'grand_total': grand_total,
    }
    
    return render(request, 'rentals/staff/quotation.html', context)

@staff_member_required
def staff_work_order(request, booking_id):
    """
    สร้างใบเบิกของ/ใบงาน (Work Order) สำหรับ Booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # คำนวณวัน
    duration = booking.end_time - booking.start_time
    days = duration.total_seconds() / (24 * 3600)
    if days < 1:
        days = 1
    else:
        days = int(days) + (1 if days % 1 > 0 else 0)
    
    # รวบรวมรายการ (เน้น Serial Number)
    items = []
    
    # Equipment
    for eq in booking.equipment.all():
        items.append({
            'name': eq.name,
            'details': f"S/N: {eq.serial_number}",
            'type': 'Equipment',
            'qty': 1, # สมมติ 1 ชิ้นต่อ record
            'unit': 'ชุด/ชิ้น'
        })
        
    # Studios (ถ้าต้องเตรียมห้อง)
    for st in booking.studios.all():
        items.append({
            'name': st.name,
            'details': "Studio Set",
            'type': 'Studio',
            'qty': 1,
            'unit': 'ห้อง'
        })

    context = {
        'booking': booking,
        'items': items,
        'days': int(days),
    }
    
    return render(request, 'rentals/staff/work_order.html', context)
