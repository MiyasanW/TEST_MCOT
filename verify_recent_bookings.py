import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcot_rental.settings')
django.setup()

from rentals.models import Booking, BookingItem, Product

print("--- Recent Bookings (Last 3) ---")
bookings = Booking.objects.order_by('-created_at')[:3]

for b in bookings:
    print(f"\nBooking ID: {b.id} | Status: {b.status} | Customer: {b.customer_name}")
    print(f"Time: {b.start_time} - {b.end_time}")
    items = b.items.all()
    for item in items:
        p = item.product
        print(f"  - product: {p.name} (Qty: {item.quantity})")
        print(f"    -> Product Total Stock: {p.quantity}")
        print(f"    -> Product Remaining: {p.remaining_quantity}")

print("\n-------------------------------")
print("VERIFICATION: The 'Product Total Stock' should remain constant (e.g. 10).")
print("VERIFICATION: The 'Product Remaining' should decrease based on active bookings.")
