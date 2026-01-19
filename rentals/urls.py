from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import reports_views
from . import public_views  # Import public views

urlpatterns = [
    # --- Public Customer Pages (หน้าบ้านลูกค้า) ---
    path('', public_views.home, name='home'),
    path('about/', public_views.about, name='about'),
    path('catalog/', public_views.equipment_catalog, name='equipment_catalog'),
    path('catalog/<int:product_id>/', public_views.product_detail, name='product_detail'),
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

    # --- Authentication (Login/Register) ---
    path('login/', auth_views.LoginView.as_view(template_name='rentals/public/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', public_views.register_view, name='register'),
    path('register/', public_views.register_view, name='register'),
    path('terms/', public_views.terms_of_use, name='terms_of_use'),
    path('profile/', public_views.profile_view, name='profile'), # User Profile & History


    # --- Staff & Admin Pages ---
    path('staff/dashboard/', views.dashboard, name='staff_dashboard'),  # Explicitly named staff_dashboard
    path('dashboard/', views.dashboard, name='dashboard'),  # Keep legacy for compatibility
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/bookings/', views.booking_api, name='booking_api'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/read/all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    path('reports/', reports_views.reports_dashboard, name='reports_dashboard'),
    path('reports/maintenance/', reports_views.reports_maintenance, name='reports_maintenance'),
    path('staff/quotation/<int:booking_id>/', views.staff_quotation, name='staff_quotation'),
    path('staff/work_order/<int:booking_id>/', views.staff_work_order, name='staff_work_order'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
]
