from django.shortcuts import render
from django.db.models import Q
from .models import Equipment, Studio

def home(request):
    """
    หน้าแรกของเว็บไซต์ (Home Page)
    """
    return render(request, 'rentals/public/home.html')

def equipment_catalog(request):
    """
    หน้าแสดงรายการอุปกรณ์ทั้งหมด (Equipment Catalog)
    รองรับการค้นหา (q) และกรองตามหมวดหมู่ (category)
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    # เริ่มต้นดึงข้อมูลทั้งหมด
    equipment_list = Equipment.objects.all().order_by('-id')
    
    # กรองตามคำค้นหา
    if query:
        equipment_list = equipment_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        
    # กรองตามหมวดหมู่
    if category:
        equipment_list = equipment_list.filter(category=category)
        
    context = {
        'equipment_list': equipment_list,
        'categories': Equipment.CATEGORY_CHOICES,
        'current_category': category,
        'query': query,
    }
    return render(request, 'rentals/public/catalog.html', context)

def studios(request):
    """
    หน้าแสดงรายการสตูดิโอ (Studio List)
    """
    studios = Studio.objects.all()
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

def faq(request):
    """
    หน้าคำถามที่พบบ่อย (FAQ)
    """
    return render(request, 'rentals/public/faq.html')

def contact(request):
    """
    หน้าติดต่อเรา (Contact Us)
    """
    return render(request, 'rentals/public/contact.html')
