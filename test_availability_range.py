import os
import django
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcot_rental.settings')
django.setup()

from rentals.models import Product, BookingItem

def check_availability(product, start_date, end_date):
    print(f"\n--- Checking {product.name} for {start_date.date()} to {end_date.date()} ---")
    print(f"Total Stock: {product.quantity}")
    
    # Logic: Find bookings that OVERLAP with the requested range
    # Creating a mock overlap check query
    # Overlap Formula: (Booking Start < Request End) AND (Booking End > Request Start)
    
    overlapping_items = BookingItem.objects.filter(
        product=product,
        booking__status__in=['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active'],
        booking__start_time__lt=end_date,  # Overlap Condition 1
        booking__end_time__gt=start_date   # Overlap Condition 2
    )
    
    booked_qty = overlapping_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    print(f"Booked Qty in this range: {booked_qty}")
    
    remaining = product.quantity - booked_qty
    print(f">> AVAILABLE: {remaining}")
    return remaining

# Mock Data Test
now = timezone.now()
tmr = now + timedelta(days=1)
next_week = now + timedelta(days=7)

# Grab a product
try:
    p = Product.objects.first()
    if p:
        # Check for 'Tomorrow'
        check_availability(p, tmr, tmr + timedelta(days=1))
        
        # Check for 'Next Week'
        check_availability(p, next_week, next_week + timedelta(days=2))
    else:
        print("No products found.")
except Exception as e:
    print(e)
