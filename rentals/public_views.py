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
        
    # --- Date-Based Availability Logic ---
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Validation Date
    search_start_date = None
    search_end_date = None
    
    if start_date and end_date:
        try:
            from datetime import datetime
            from django.db.models import Sum
            from .models import BookingItem # Already imported at top, but keeping for context of snippet
            
            # Parse Date (Assuming format YYYY-MM-DD from HTML5 input)
            search_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            search_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Adjust end date to cover the full day (if needed) or assuming user inputs inclusive range
            # For simplicity, let's assume end_date is inclusive 23:59:59 or handle as date object comparison
            
            # Calculate Remaining for EACH product in the list
            for product in product_list:
                # Find overlapping bookings
                booked_qty = BookingItem.objects.filter(
                    product=product,
                    booking__status__in=['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active'],
                    booking__start_time__lte=search_end_date,
                    booking__end_time__gte=search_start_date
                ).aggregate(Sum('quantity'))['quantity__sum'] or 0
                
                # Attach attribute dynamically
                product.calculated_remaining = max(0, product.quantity - booked_qty)
                product.is_date_filtered = True
                
        except ValueError:
            pass # Invalid date format, ignore
            
    if not search_start_date:
        # Default case: Show TOTAL quantity if no date selected
        for product in product_list:
            product.calculated_remaining = product.quantity
            product.is_date_filtered = False
            
    context = {
        'equipment_list': product_list, 
        'categories': Product.CATEGORY_CHOICES,
        'current_category': category,
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'rentals/public/catalog.html', context)

def product_detail(request, product_id):
    """
    หน้ารายละเอียดสินค้า (Product Detail)
    รองรับการระบุวันที่เช่า (start_date, end_date) เพื่อเช็ค Available
    """
    product = get_object_or_404(Product, id=product_id)
    
    # --- Date-Based Availability Logic ---
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    search_start_date = None
    search_end_date = None
    
    # Default: Show "Total Available Now" if no date selected
    # But if date selected, calculate "Available in Range"
    product.calculated_remaining = product.remaining_quantity # Default fallback
    
    if start_date and end_date:
        try:
            from datetime import datetime
            from django.db.models import Sum
            from .models import BookingItem
            
            search_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            search_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Check overlap
            booked_qty = BookingItem.objects.filter(
                product=product,
                booking__status__in=['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active'],
                booking__start_time__lte=search_end_date,
                booking__end_time__gte=search_start_date
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            product.calculated_remaining = max(0, product.quantity - booked_qty)
            product.is_date_filtered = True
            
        except ValueError:
            pass 
    
    # Related products (Same category, exclude self)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'rentals/public/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'start_date': start_date,
        'end_date': end_date,
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
    packages = Package.objects.filter(is_active=True).prefetch_related('items__product').order_by('price')
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
    quantity = int(request.POST.get('quantity', 1))
    
    # Validation: Date is mandatory for rental
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if not start_date or not end_date:
        # If accessing directly without dates, redirect back to product detail
        # In a real app, add a flash message "Please select dates"
        return redirect('product_detail', product_id=product.id)

    # Save dates to SESSION (Global Booking Period)
    # This assumes a "One Booking = One Period" model for simplicity
    request.session['booking_start_date'] = start_date
    request.session['booking_end_date'] = end_date
    
    # Check Stock for Specific Dates
    # (Re-calculate availability for server-side security)
    from datetime import datetime
    from django.db.models import Sum
    from .models import BookingItem
    
    s_date = datetime.strptime(start_date, "%Y-%m-%d")
    e_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    booked_qty = BookingItem.objects.filter(
        product=product,
        booking__status__in=['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active'],
        booking__start_time__lte=e_date,
        booking__end_time__gte=s_date
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    real_available = max(0, product.quantity - booked_qty)
    
    if real_available < quantity:
        # Stock might have changed or was invalid
        return redirect('product_detail', product_id=product.id)
        
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
            
            # --- STOCK VALIDATION ---
            for item in cart:
                product = item['product']
                req_qty = item['quantity']
                if product.remaining_quantity < req_qty:
                    error = f"ขออภัย สินค้า '{product.name}' คงเหลือไม่เพียงพอ (เหลือ {product.remaining_quantity} ชิ้น)"
                    return render(request, 'rentals/public/checkout.html', {'cart': cart, 'error': error})
            # ------------------------
            
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
