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
from rentals import views_public as public_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Website (Customer Facing)
    path('', public_views.public_home, name='public_home'),
    path('catalog/', public_views.public_catalog, name='public_catalog'),
    path('studios/', public_views.public_studios, name='public_studios'),
    path('packages/', public_views.public_packages, name='public_packages'),
    path('about/', public_views.public_about, name='public_about'),
    path('portfolio/', public_views.public_portfolio, name='public_portfolio'),
    path('faq/', public_views.public_faq, name='public_faq'),
    path('contact/', public_views.public_contact, name='public_contact'),
    
    # Staff/Admin Dashboard
    path('staff/dashboard/', rentals_views.dashboard, name='dashboard'),
    
    # Rentals App
    path('rentals/', include('rentals.urls')),
]
