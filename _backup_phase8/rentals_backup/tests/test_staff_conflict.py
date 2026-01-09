from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from rentals.models import Booking, Staff, Equipment, Studio

class StaffConflictTest(TestCase):
    def setUp(self):
        # Create Staff
        self.staff_a = Staff.objects.create(name="Cameraman A", position="cameraman")
        self.staff_b = Staff.objects.create(name="Sound B", position="sound")
        
        # Base time
        self.base_time = timezone.now()
        
        # Create initial approved booking for Staff A
        self.booking1 = Booking.objects.create(
            customer_name="Booking 1",
            start_time=self.base_time,
            end_time=self.base_time + timedelta(hours=4),
            status='approved'
        )
        self.booking1.staff.add(self.staff_a)
        self.booking1.save()

    def test_overlapping_staff_booking_raises_error(self):
        """Test that booking the same staff in overlapping time raises ValidationError"""
        booking2 = Booking(
            customer_name="Booking 2 (Conflict)",
            start_time=self.base_time + timedelta(hours=2), # Starts in middle of booking1
            end_time=self.base_time + timedelta(hours=6),
            status='approved'
        )
        # Check if validation fails for staff_a
        booking2.save() # Need to save first to get ID for M2M, but clean() is called manually usually or via form
        booking2.staff.add(self.staff_a)
        
        with self.assertRaises(ValidationError) as cm:
            booking2.clean()
        
        self.assertIn("ติดงานแล้วในช่วงเวลา", str(cm.exception))

    def test_non_overlapping_staff_booking_success(self):
        """Test that booking the same staff in non-overlapping time succeeds"""
        booking3 = Booking(
            customer_name="Booking 3 (Safe)",
            start_time=self.base_time + timedelta(hours=5), # Starts after booking1 ends
            end_time=self.base_time + timedelta(hours=8),
            status='approved'
        )
        booking3.save()
        booking3.staff.add(self.staff_a)
        
        try:
            booking3.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly for non-overlapping booking!")

    def test_other_staff_overlapping_time_success(self):
        """Test that booking DIFFERENT staff in overlapping time succeeds"""
        booking4 = Booking(
            customer_name="Booking 4 (Other Staff)",
            start_time=self.base_time + timedelta(hours=1),
            end_time=self.base_time + timedelta(hours=3),
            status='approved'
        )
        booking4.save()
        booking4.staff.add(self.staff_b) # Staff B, not A
        
        try:
            booking4.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly for different staff booking!")
