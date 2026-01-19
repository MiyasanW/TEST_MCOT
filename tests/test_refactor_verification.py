
import os
import django
from datetime import datetime, timedelta
import sys

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcot_rental.settings')
django.setup()

from rentals.models import Product, Booking, BookingItem, Equipment, Staff, Studio
from rentals.services.availability import AvailabilityService
from django.utils import timezone
from django.contrib.auth.models import User

def test_availability_service():
    print("\n--- Testing AvailabilityService ---")
    
    # 1. Setup Data
    product = Product.objects.first()
    if not product:
        print("SKIP: No product found.")
        return

    now = timezone.now()
    start_time = now + timedelta(days=1)
    end_time = now + timedelta(days=3)
    
    # Create a dummy booking (Draft)
    b = Booking.objects.create(
        customer_name="Test Bug Hunter",
        start_time=start_time,
        end_time=end_time,
        status='draft'
    )
    BookingItem.objects.create(booking=b, product=product, quantity=1)
    
    # 2. Test Check Availability (Should fail if we demand too much)
    # Assume product has quantity=X. We booked 1.
    # If we ask for (Total) again in the SAME period, it should fail (if quantity is low) or pass (if high).
    # Let's force a fail by asking for product.quantity + 1
    
    too_many = product.quantity + 1
    is_valid, msg = AvailabilityService.check_availability(product, start_time, end_time, too_many)
    print(f"Scenario 1 (Over limit): Valid={is_valid}, Msg='{msg}'")
    assert is_valid == False, "Should fail when asking more than stock"
    
    # 3. Test Non-Overlapping (Next Month)
    future_start = now + timedelta(days=30)
    future_end = now + timedelta(days=32)
    is_valid, msg = AvailabilityService.check_availability(product, future_start, future_end, product.quantity)
    print(f"Scenario 2 (Future/No Overlap): Valid={is_valid}")
    assert is_valid == True, "Should pass when booking in free slot"

    # Cleanup
    b.delete()
    print("AvailabilityService: PASS")

def test_resource_overlap():
    print("\n--- Testing Resource Overlap (Admin Logic) ---")
    
    # Setup
    studio = Studio.objects.first()
    if not studio:
        print("SKIP: No studio found.")
        return

    now = timezone.now()
    start_time = now + timedelta(days=5)
    end_time = now + timedelta(days=6)
    
    # Create conflicting booking (Approved)
    b1 = Booking.objects.create(
        customer_name="Blocker User",
        start_time=start_time,
        end_time=end_time,
        status='approved'
    )
    b1.studios.add(studio)
    
    # Test Overlap
    is_valid, conflict = AvailabilityService.check_resource_overlap('studios', studio, start_time, end_time)
    print(f"Scenario 1 (Direct Overlap): Valid={is_valid}, Conflict={conflict}")
    assert is_valid == False, "Should fail on direct overlap"
    
    # Test Exclusion (Edit Mode)
    is_valid, conflict = AvailabilityService.check_resource_overlap('studios', studio, start_time, end_time, exclude_booking_id=b1.id)
    print(f"Scenario 2 (Self Exclude): Valid={is_valid}")
    assert is_valid == True, "Should pass when excluding self"
    
    # Cleanup
    b1.delete()
    print("ResourceOverlap: PASS")

if __name__ == "__main__":
    try:
        test_availability_service()
        test_resource_overlap()
        print("\n✅ All Tests Passed. No obvious bugs found in Logic layer.")
    except AssertionError as e:
        print(f"\n❌ BUG FOUND: {e}")
    except Exception as e:
        print(f"\n❌ CRASH: {e}")
        import traceback
        traceback.print_exc()
