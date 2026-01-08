from django.shortcuts import render
from .models import Equipment, Studio

def home(request):
    """
    หน้าแรกของเว็บไซต์ (Home Page)
    """
    return render(request, 'rentals/public/home.html')

def equipment_catalog(request):
    """
    หน้าแสดงรายการอุปกรณ์ทั้งหมด (Equipment Catalog)
    """
    # ดึงอุปกรณ์ที่พร้อมใช้งานและแนะนำ
    featured_equipment = Equipment.objects.filter(status='available')[:6]
    return render(request, 'rentals/public/catalog.html', {
        'equipment': featured_equipment
    })

def studios(request):
    """
    หน้าแสดงรายการสตูดิโอ (Studio List)
    """
    studios = Studio.objects.filter(status='available')
    return render(request, 'rentals/public/studios.html', {
        'studios': studios
    })

def packages(request):
    """
    หน้าแสดงแพ็คเกจราคา (Packages)
    """
    # สมมติว่ามี Model Package หรือ Hardcode ไปก่อน
    return render(request, 'rentals/public/packages.html')

def portfolio(request):
    """
    หน้าผลงานที่ผ่านมา (Portfolio)
    """
    return render(request, 'rentals/public/portfolio.html')

def contact(request):
    """
    หน้าติดต่อเรา (Contact Us)
    """
    return render(request, 'rentals/public/contact.html')
