from django.shortcuts import render
from django.db.models import Q
from .models import Equipment, Studio

def public_home(request):
    """
    หน้าแรกเว็บไซต์ (Public Home)
    แสดงอุปกรณ์แนะนำและข้อมูลทั่วไป
    """
    # ดึงอุปกรณ์ที่สถานะ 'available' มาแสดง 4 ชิ้นล่าสุด
    featured_items = Equipment.objects.filter(status='available').order_by('-id')[:4]
    
    return render(request, 'rentals/public/home.html', {
        'featured_items': featured_items
    })

def public_catalog(request):
    """
    หน้าแสดงรายการอุปกรณ์ทั้งหมด (Public Catalog)
    รองรับการค้นหา (q) และกรองตามหมวดหมู่ (category)
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    equipment_list = Equipment.objects.all().order_by('-id')
    
    if query:
        equipment_list = equipment_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        
    if category:
        equipment_list = equipment_list.filter(category=category)
        
    context = {
        'equipment_list': equipment_list,
        'categories': Equipment.CATEGORY_CHOICES,
        'current_category': category,
        'query': query,
    }
    
    return render(request, 'rentals/public/catalog.html', context)

def public_studios(request):
    """
    หน้าแสดงสตูดิโอทั้งหมด (Public Studio Showcase)
    """
    studios = Studio.objects.all().order_by('name')
    return render(request, 'rentals/public/studios.html', {'studios': studios})

def public_packages(request):
    """
    หน้าแสดงโปรโมชั่น (Public Packages)
    """
    return render(request, 'rentals/public/packages.html')

def public_about(request):
    """
    หน้าเกี่ยวกับเรา (Public About Us)
    """
    return render(request, 'rentals/public/about.html')

def public_portfolio(request):
    """
    หน้าผลงาน (Public Portfolio)
    """
    return render(request, 'rentals/public/portfolio.html')

def public_faq(request):
    """
    หน้าคำถามยอดฮิต (Public FAQ)
    """
    return render(request, 'rentals/public/faq.html')

def public_contact(request):
    """
    หน้าติดต่อเรา (Public Contact)
    """
    return render(request, 'rentals/public/contact.html')
