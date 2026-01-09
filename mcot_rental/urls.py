"""
URL configuration for mcot_rental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rentals import views as rentals_views
from rentals import public_views as public_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Website (Customer Facing)
    path('', public_views.home, name='public_home'),
    path('about/', public_views.about, name='public_about'),
    path('catalog/', public_views.equipment_catalog, name='public_catalog'),
    path('studios/', public_views.studios, name='public_studios'),
    path('packages/', public_views.packages, name='public_packages'),
    path('portfolio/', public_views.portfolio, name='public_portfolio'),
    path('faq/', public_views.faq, name='public_faq'),
    path('contact/', public_views.contact, name='public_contact'),
    
    # Staff/Admin Dashboard
    path('staff/dashboard/', rentals_views.dashboard, name='dashboard'),
    
    # Rentals App
    path('rentals/', include('rentals.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
