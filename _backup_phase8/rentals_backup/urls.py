from django.urls import path
from . import views
from . import reports_views
from . import public_views  # Import public views

urlpatterns = [
    # --- Public Customer Pages (หน้าบ้านลูกค้า) ---
    path('', public_views.home, name='home'),
    path('about/', public_views.about, name='about'),
    path('catalog/', public_views.equipment_catalog, name='equipment_catalog'),
    path('studios/', public_views.studios, name='studios'),
    path('packages/', public_views.packages, name='packages'),
    path('portfolio/', public_views.portfolio, name='portfolio'),
    path('faq/', public_views.faq, name='faq'),
    path('contact/', public_views.contact, name='contact'),
    
    # Cart & Checkout
    path('cart/add/<int:product_id>/', public_views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', public_views.cart_remove, name='cart_remove'),
    path('cart/', public_views.cart_detail, name='cart_detail'),
    path('checkout/', public_views.checkout, name='checkout'),

    # --- Staff & Admin Pages ---
    path('staff/dashboard/', views.dashboard, name='staff_dashboard'),  # Explicitly named staff_dashboard
    path('dashboard/', views.dashboard, name='dashboard'),  # Keep legacy for compatibility
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/bookings/', views.booking_api, name='booking_api'),
    path('reports/', reports_views.reports_dashboard, name='reports_dashboard'),
    path('reports/maintenance/', reports_views.reports_maintenance, name='reports_maintenance'),
    path('staff/quotation/<int:booking_id>/', views.staff_quotation, name='staff_quotation'),
    path('staff/work_order/<int:booking_id>/', views.staff_work_order, name='staff_work_order'),
]
