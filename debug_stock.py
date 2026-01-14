import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcot_rental.settings')
django.setup()

from rentals.models import Product, Booking, BookingItem
from django.utils import timezone
from django.db.models import Sum

now = timezone.now()
print(f"Time: {now}")

active_bookings = Booking.objects.filter(
    start_time__lte=now, 
    end_time__gte=now, 
    status__in=['approved', 'active']
)
print(f"\nActive Bookings (Count: {active_bookings.count()}):")
for b in active_bookings:
    print(f"- ID:{b.id} Status:{b.status} Customer:{b.customer_name}")
    for item in b.items.all():
        print(f"  * {item.product.name}: {item.quantity}")

print("\nProduct Stock:")
for p in Product.objects.all():
    booked = BookingItem.objects.filter(
        product=p,
        booking__status__in=['approved', 'active'],
        booking__start_time__lte=now,
        booking__end_time__gte=now
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0
    print(f"- {p.name}: Total={p.quantity}, Booked={booked}, Remaining={p.remaining_quantity}")
