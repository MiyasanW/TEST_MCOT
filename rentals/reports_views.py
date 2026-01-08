from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from .models import Booking, Equipment, Studio, IssueReport

@staff_member_required
def reports_dashboard(request):
    """
    หน้าหลักสำหรับดูรายงานและสถิติต่างๆ
    """
    # 1. จัดการ Date Filter
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    today = timezone.now().date()
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today - timedelta(days=365)
            end_date = today
    else:
        # Default 1 ปี
        start_date = today - timedelta(days=365)
        end_date = today

    # 2. จัดการ Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="revenue_report_{today}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Month', 'Revenue (THB)', 'Bookings Count'])
        
        # Calculate data for export
        current = start_date.replace(day=1)
        while current <= end_date:
            next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            bookings = Booking.objects.filter(
                start_time__year=current.year,
                start_time__month=current.month,
                status__in=['approved', 'completed']
            )
            
            total_revenue = sum(b.calculate_total_price() for b in bookings)
            writer.writerow([current.strftime('%B %Y'), total_revenue, bookings.count()])
            
            current = next_month
            
        return response

    # 3. คำนวณข้อมูลสำหรับแสดงผล
    
    # กราฟรายเดือน
    monthly_data = []
    
    # Create distinct months list from start_date to end_date
    current = start_date.replace(day=1)
    chart_end_date = end_date
    
    while current <= chart_end_date:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        bookings = Booking.objects.filter(
            start_time__year=current.year,
            start_time__month=current.month,
            status__in=['approved', 'completed']
        )
        
        total_revenue = sum(b.calculate_total_price() for b in bookings)
        monthly_data.append({
            'month': current.strftime('%B %Y'),
            'revenue': total_revenue,
            'count': bookings.count()
        })
        
        current = next_month

    # อุปกรณ์ยอดนิยม (Top 5) ในช่วงเวลาที่เลือก
    top_equipment = Equipment.objects.filter(
        bookings__start_time__date__range=[start_date, end_date]
    ).annotate(
        usage_count=Count('bookings')
    ).order_by('-usage_count').distinct()[:5]
    
    # สัดส่วนสถานะการจอง ในช่วงเวลาที่เลือก
    status_counts = Booking.objects.filter(
        start_time__date__range=[start_date, end_date]
    ).values('status').annotate(total=Count('id'))
    
    context = {
        'monthly_data': monthly_data,
        'top_equipment': top_equipment,
        'status_counts': status_counts,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'rentals/reports.html', context)

@staff_member_required
def reports_maintenance(request):
    """
    หน้าแสดงรายงานการแจ้งปัญหา/ซ่อมบำรุง (Issue/Maintenance Report)
    """
    # 1. รับค่า Filter
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    # 2. Query ข้อมูล
    issues = IssueReport.objects.all().select_related('equipment', 'studio', 'booking', 'reporter').order_by('-created_at')
    
    if status_filter:
        issues = issues.filter(status=status_filter)
        
    if priority_filter:
        issues = issues.filter(priority=priority_filter)
        
    # 3. สรุปข้อมูล (Summary Stats)
    total_issues = IssueReport.objects.count()
    open_issues = IssueReport.objects.exclude(status='closed').count()
    critical_issues = IssueReport.objects.filter(priority='critical').exclude(status='closed').count()
    
    # 4. Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="maintenance_report_{timezone.now().date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Priority', 'Status', 'Equipment', 'Studio', 'Booking', 'Reporter', 'Date'])
        
        for issue in issues:
            equip_name = issue.equipment.name if issue.equipment else '-'
            studio_name = issue.studio.name if issue.studio else '-'
            booking_info = f"{issue.booking.customer_name} ({issue.booking.id})" if issue.booking else '-'
            reporter_name = issue.reporter.username if issue.reporter else '-'
            
            writer.writerow([
                issue.id, 
                issue.title, 
                issue.get_priority_display(), 
                issue.get_status_display(),
                equip_name,
                studio_name,
                booking_info,
                reporter_name,
                issue.created_at.strftime('%Y-%m-%d %H:%M')
            ])
            
        return response

    context = {
        'issues': issues,
        'total_issues': total_issues,
        'open_issues': open_issues,
        'critical_issues': critical_issues,
        'current_status': status_filter,
        'current_priority': priority_filter,
    }
    
    return render(request, 'rentals/reports_issues.html', context)
