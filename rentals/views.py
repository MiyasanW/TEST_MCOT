from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from simple_history.models import HistoricalRecords  # สำหรับ Audit Trailt
from .models import Booking, Equipment, Studio, Staff, Notification, Product, BookingItem, PackageItem
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince



def dashboard_callback(request, context):
    """
    Callback function for Unfold admin index page.
    Adds dashboard stats and recent bookings to the admin index context.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("🎯 Dashboard callback called!")
    
    today = timezone.now().date()
    logger.warning(f"Today's date: {today}")
    
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
    
    # สถิติอุปกรณ์ (ใช้ Product model)
    equipment_total = Product.objects.count()
    equipment_available = Product.objects.filter(
        is_active=True,
        quantity__gt=0
    ).count()
    
    # สถิติพนักงาน (ใช้ User model)
    staff_active = User.objects.filter(is_staff=True, is_active=True).count()
    
    # รายการจองล่าสุด (5 รายการ)
    recent_bookings = Booking.objects.select_related(
        'created_by'
    ).order_by('-created_at')[:5]
    
    # คำนวณรายได้เดือนนี้
    revenue_this_month = 0
    for booking in Booking.objects.filter(
        start_time__year=today.year,
        start_time__month=today.month,
        status__in=['approved', 'completed']
    ):
        revenue_this_month += booking.calculate_total_price()
    
    stats = {
        'bookings_today': bookings_today,
        'bookings_pending': bookings_pending,
        'bookings_this_month': bookings_this_month,
        'equipment_available': equipment_available,
        'equipment_total': equipment_total,
        'staff_active': staff_active,
        'revenue_this_month': revenue_this_month,
    }

    # --- Chart Data Calculation (New) ---
    # 1. 7-Day Revenue Trend
    days = []
    revenue_trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        days.append(d.strftime('%d %b')) # e.g. "16 Jan"
        daily_rev = 0
        # Naive calculation: sum of bookings starting on that day
        for b in Booking.objects.filter(start_time__date=d, status__in=['approved', 'completed']):
             daily_rev += float(b.calculate_total_price())
        revenue_trend.append(daily_rev)
    
    # 2. Status Distribution
    status_counts = {
        'draft': Booking.objects.filter(status='draft').count(),
        'approved': Booking.objects.filter(status='approved').count(),
        'completed': Booking.objects.filter(status='completed').count(),
        'active': Booking.objects.filter(status='active').count(),
        'problem': Booking.objects.filter(status='problem').count(),
    }
    
    # Thai Date for Header
    thai_full_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    today_thai = f"วัน{today.strftime('%A')}ที่ {today.day} {thai_full_months[today.month-1]} {today.year + 543}"

    stats.update({
        'chart_labels': days,
        'chart_revenue': revenue_trend,
        'status_counts': status_counts,
        'today_thai': today_thai,
    })
    # ------------------------------------
    
    logger.warning(f"📊 Stats: {stats}")
    logger.warning(f"📅 Recent bookings count: {len(list(recent_bookings))}")
    
    # Add data to context
    context.update({
        'stats': stats,
        'recent_bookings': recent_bookings,
    })
    
    logger.warning(f"✅ Context updated. Keys: {context.keys()}")
    return context


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
            
        # ใช้ items.count() ถ้ามี หรือ equipment.count() ถ้ายังไม่ได้ใช้ BookingItem
        item_count = booking.items.count() or booking.equipment.count()
        title = f"{booking.customer_name} ({item_count} รายการ)"
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
    # Equipment (จากที่ Assign แล้ว)
    for eq in booking.equipment.all():
        product_name = eq.product.name if eq.product else "Unknown Item"
        product_price = eq.product.price if eq.product else 0
        items.append({
            'name': product_name,
            'details': f"S/N: {eq.serial_number}",
            'price': product_price,
            'total': product_price * days,
            'type': 'Equipment'
        })
        
    # Booking Items (จากที่ลูกค้าเลือก แต่ยังไม่ได้ Assign Serial)
    # เฉพาะกรณีที่ยังไม่ได้ Assign equipment (เพื่อไม่ให้ซ้ำ)
    # หรือถ้าเราเปลี่ยน Logic การคิดเงิน 
    if not booking.equipment.exists():
        for item in booking.items.all():
            items.append({
                'name': item.product.name,
                'details': f"Quantity: {item.quantity}",
                'price': item.price_at_booking or item.product.price,
                'total': item.total_price() * days,
                'type': 'Product'
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
        product_name = eq.product.name if eq.product else "Unknown Item"
        items.append({
            'name': product_name,
            'details': f"S/N: {eq.serial_number}",
            'type': 'Equipment',
            'qty': 1, # สมมติ 1 ชิ้นต่อ record
            'unit': 'ชุด/ชิ้น'
        })

    # ถ้ายังไม่ได้ assign serial ให้แสดงรายการที่จองแทน
    if not booking.equipment.exists():
        for item in booking.items.all():
            items.append({
                'name': item.product.name,
                'details': "Waiting for assignment",
                'type': 'Product',
                'qty': item.quantity,
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

# --- Notification API ---

def get_notifications(request):
    """
    API สำหรับดึงข้อมูลการแจ้งเตือน (Polling)
    """
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0, 'items': []})
        
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    items = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'message': item.message,
            'link': item.link,
            'is_read': item.is_read,
            'type': item.notification_type,
            'created_at': item.created_at.strftime('%d/%m %H:%M'),
            'time_ago': timesince(item.created_at)
        })
        
    return JsonResponse({'count': unread_count, 'items': data})

@require_POST
def mark_notification_read(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True})
    
@require_POST
def mark_all_notifications_read(request):
    if not request.user.is_authenticated:
         return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@staff_member_required
def inventory_dashboard(request):
    # 1. Determine Selected Date
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.localtime().date()
    else:
        target_date = timezone.localtime().date()

    # Create time range for the selected date (Start of day to End of day)
    target_start = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
    target_end = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))

    products = Product.objects.filter(is_active=True).order_by('category', 'name')
    inventory_data = []

    for product in products:
        # Calculate Ledger (Keep showing all future/recent active logs for context, or filter? 
        # Requirement implies "check stock for that day", so ledger can remain "recent view" or be filtered.
        # For now, let's keep ledger showing *relevant* activity around that time?)
        # Actually, let's keep the ledger as a general "what is going on" view, 
        # but the AVAILABLE COUNT must be specific to the date.
        
        ledger = []
        
        # Find bookings relevant to this product (for Ledger)
        booking_items = BookingItem.objects.filter(
            product=product,
            booking__status__in=['approved', 'active', 'pending_deposit', 'quotation_sent'], 
            booking__start_time__lte=target_end,
            booking__end_time__gte=target_start
        ).select_related('booking')

        for bi in booking_items:
            # Check assigned equipment (Serial Numbers)
            assigned_equipment = bi.booking.equipment.filter(product=product)
            if assigned_equipment.exists():
                detail_text = f"Assigned: {', '.join([e.serial_number for e in assigned_equipment])}"
                qty = assigned_equipment.count()
            else:
                detail_text = "Requested (Pending Assignment)"
                qty = bi.quantity

            # Format Date Range to show temporary usage (Thai)
            thai_months = [
                "", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
            ]
            
            def to_thai_date(dt):
                return f"{dt.day} {thai_months[dt.month]}"

            start_str = to_thai_date(bi.booking.start_time)
            end_str = to_thai_date(bi.booking.end_time)
            date_display = f"{start_str} - {end_str}" if start_str != end_str else start_str

            ledger.append({
                'date': bi.booking.start_time,
                'booking': bi.booking,
                'date': bi.booking.start_time,
                'booking': bi.booking,
                'date_display': date_display, # Renamed to fix rendering
                # Combined string to avoid template parsing issues
                'entry_title': f"{bi.booking.customer_name}",
                'change': -qty,
                'detail': detail_text,
                'package_name': None 
            })

        # Sort ledger by date
        ledger.sort(key=lambda x: x['date'])

        # --- KEY CHANGE: Calculate Available Stock for TARGET DATE ---
        from django.db.models import Sum
        booked_qty_result = BookingItem.objects.filter(
             product=product,
             booking__status__in=['approved', 'active', 'pending_deposit', 'quotation_sent'], # Include pending to be safe
             # Overlap Logic: Booking Start <= Target End AND Booking End >= Target Start
             booking__start_time__lte=target_end,
             booking__end_time__gte=target_start
        ).aggregate(Sum('quantity'))
        
        booked_qty = booked_qty_result['quantity__sum'] or 0
        available_stock = max(0, product.quantity - booked_qty)

        inventory_data.append({
            'product': product,
            'total_stock': product.quantity,
            'available_stock': available_stock, 
            'ledger': ledger
        })

    return render(request, 'admin/inventory_dashboard.html', {
        'inventory': inventory_data,
        'title': 'Inventory Dashboard',
        'selected_date': target_date.strftime('%Y-%m-%d'),
        'pretty_date': target_date.strftime('%d %B %Y')
    })

