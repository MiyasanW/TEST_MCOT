from django.shortcuts import render
from django.db.models import Q
from .models import Equipment, Studio, Product, Package, Booking, BookingItem, Notification
from .cart import Cart
from .cart import Cart
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import BookingAdminForm
from django.utils import timezone
from datetime import datetime
from .services.notify import send_line_notify
from django.contrib.auth.models import User


def home(request):
    """
    Landing page view.
    """
    # Fetch featured equipment (Top 4 active items, ordered by newest)
    featured_equipment = Product.objects.filter(is_active=True).order_by('-id')[:4]
    
    context = {
        'featured_equipment': featured_equipment,
    }
    return render(request, 'rentals/public/home.html', context)

def about(request):
    """
    หน้าเกี่ยวกับเรา (About Us)
    """
    return render(request, 'rentals/public/about.html')

def equipment_catalog(request):
    """
    หน้าแสดงรายการสินค้า (Products)
    รองรับการค้นหา (q) และกรองตามหมวดหมู่ (category)
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    # เริ่มต้นดึงข้อมูลสินค้าที่เปิดให้เช่า
    product_list = Product.objects.filter(is_active=True).order_by('name')
    
    # กรองตามคำค้นหา
    if query:
        product_list = product_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        
    # กรองตามหมวดหมู่
    if category:
        product_list = product_list.filter(category=category)
        
    context = {
        'equipment_list': product_list, # ใช้ชื่อตัวแปรเดิมเพื่อไม่ต้องแก้ Template เยอะ
        'categories': Product.CATEGORY_CHOICES,
        'current_category': category,
        'query': query,
    }
    return render(request, 'rentals/public/catalog.html', context)

def product_detail(request, product_id):
    """
    หน้ารายละเอียดสินค้า (Product Detail)
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Related products (Same category, exclude self)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'rentals/public/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

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
    packages = Package.objects.filter(is_active=True).order_by('price')
    return render(request, 'rentals/public/packages.html', {
        'packages': packages
    })

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

# --- Cart System ---

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # รับ quantity จาก form ถ้ามี
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'rentals/public/cart_detail.html', {'cart': cart})

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('equipment_catalog')
        
    if request.method == 'POST':
        # รับข้อมูลจากฟอร์ม Checkout (หรือใช้ข้อมูลจาก User ถ้าไม่ได้กรอก)
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        
        # Combine Date & Time
        try:
            start_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            
            # Create Booking
            booking_data = {
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'customer_email': customer_email,
                'start_time': start_dt,
                'end_time': end_dt,
                'status': 'draft'
            }
            
            # Associate with User if logged in
            if request.user.is_authenticated:
                booking_data['created_by'] = request.user
                
            booking = Booking.objects.create(**booking_data)
            
            # Create BookingItems
            for item in cart:
                BookingItem.objects.create(
                    booking=booking,
                    product=item['product'],
                    quantity=item['quantity'],
                    price_at_booking=item['price']
                )
                
            # Clear Cart
            cart.clear()
            
            # Notify
            message = f"\n📦 New Booking Request #{booking.id}\n" \
                      f"Customer: {booking.customer_name}\n" \
                      f"Items: {booking.items.count()} items\n" \
                      f"Date: {start_dt.strftime('%d/%m')} - {end_dt.strftime('%d/%m')}"
            send_line_notify(message)
            
            # Notify In-App (To Staff)
            staff_users = User.objects.filter(is_staff=True)
            for staff in staff_users:
                Notification.objects.create(
                    recipient=staff,
                    message=f"📦 New Booking #{booking.id} by {booking.customer_name}",
                    link=f"/admin/rentals/booking/{booking.id}/change/",
                    notification_type='info'
                )

            
            return render(request, 'rentals/public/booking_success.html', {'booking': booking})
            
        except ValueError:
            # Handle Date parsing error
            error = "รูปแบบวันที่หรือเวลาไม่ถูกต้อง"
            return render(request, 'rentals/public/checkout.html', {'cart': cart, 'error': error})
    
    # Pre-fill data for GET request
    context = {'cart': cart, 'today': timezone.now().date().isoformat()}
    if request.user.is_authenticated:
        context['initial_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        context['initial_email'] = request.user.email
        # Phone might be in Profile model if extended, but for now leave empty
        
    return render(request, 'rentals/public/checkout.html', context)

# --- Authentication & Legal ---
from .forms import RegisterForm
from django.contrib.auth import login

def register_view(request):
    """
    หน้าลงทะเบียนลูกค้าใหม่
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto login after register
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'rentals/public/register.html', {'form': form})

def terms_of_use(request):
    """
    หน้าเงื่อนไขการใช้งาน
    """
    return render(request, 'rentals/public/terms.html')

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    """
    หน้าโปรไฟล์ผู้ใช้ แสดงประวัติการจองและสถานะ
    """
    # ดึงประวัติการจองของผู้ใช้ เรียงจากล่าสุดไปเก่าสุด
    bookings = Booking.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'rentals/public/profile.html', context)
