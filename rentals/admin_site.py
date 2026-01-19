from django.contrib import admin as django_admin
from django.utils import timezone
from rentals.models import Booking, Equipment, Staff

class CustomAdminSite(django_admin.AdminSite):
    """
    Custom Admin Site with dashboard as index
    """
    site_header = "MCOT Enterprise"
    site_title = "MCOT Rental System"
    index_title = "Dashboard"
    
    def index(self, request, extra_context=None):
        """
        Override index to show custom dashboard with stats
        """
        from rentals.models import Booking, Equipment, Staff, Studio
        from django.utils import timezone
        
        today = timezone.now().date()
        
        # Stats
        stats = {
            'bookings_today': Booking.objects.filter(start_time__date=today).count(),
            'bookings_pending': Booking.objects.filter(status='draft').count(),
            'bookings_this_month': Booking.objects.filter(
                start_time__year=today.year,
                start_time__month=today.month
            ).count(),
            'equipment_total': Equipment.objects.count(),
            'equipment_available': Equipment.objects.filter(status='available').count(),
            'equipment_maintenance': Equipment.objects.filter(status='maintenance').count(),
            'studio_total': Studio.objects.count(),
            'staff_active': Staff.objects.filter(is_active=True).count(),
            'revenue_this_month': sum(
                booking.calculate_total_price()
                for booking in Booking.objects.filter(
                    start_time__year=today.year,
                    start_time__month=today.month,
                    status__in=['approved', 'completed']
                )
            ),
        }
        
        # Recent bookings
        recent_bookings = Booking.objects.select_related().prefetch_related(
            'equipment', 'studios', 'staff'
        ).order_by('-id')[:5]
        
        context = {
            'title': 'Dashboard',
            'stats': stats,
            'recent_bookings': recent_bookings,
            **(extra_context or {}),
        }
        
        return super().index(request, extra_context=context)

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')
