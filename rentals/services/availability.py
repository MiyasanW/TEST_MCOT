from django.utils import timezone
from django.db.models import Sum, Q

# Import models inside functions to avoid circular imports if strictly necessary, 
# but usually service layers are imported by views/forms, so importing models here is fine.
from rentals.models import BookingItem, Booking

class AvailabilityService:
    """
    Centralized service for checking product availability and stock.
    Replaces ad-hoc logic in views and models.
    """

    @staticmethod
    def get_booked_quantity(product, start_time, end_time, exclude_booking_id=None):
        """
        Calculates how many units of a product are booked/reserved 
        during the specified time range.
        
        Args:
            product: The Product instance.
            start_time: datetime object (inclusive start).
            end_time: datetime object (exclusive end).
            exclude_booking_id: (Optional) ID of a booking to ignore (for edit mode).
            
        Returns:
            int: Total quantity booked.
        """
        if not start_time or not end_time:
            return 0

        # Query for overlapping bookings
        # Status that consumes availability:
        # - draft (temporarily locks stock)
        # - quotation_sent
        # - pending_deposit
        # - approved
        # - active
        # (completed/problem/cancelled do NOT consume stock for future dates, usually)
        # Note: 'problem' items might need manual check, but for now we assume they are returned or handled separately.
        
        active_statuses = ['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active']
        
        query = Q(booking__status__in=active_statuses) & \
                Q(product=product) & \
                Q(booking__start_time__lt=end_time) & \
                Q(booking__end_time__gt=start_time)

        if exclude_booking_id:
            query &= ~Q(booking__id=exclude_booking_id)

        booked_qty = BookingItem.objects.filter(query).aggregate(Sum('quantity'))['quantity__sum'] or 0
        return booked_qty

    @staticmethod
    def get_available_quantity(product, start_time, end_time, exclude_booking_id=None):
        """
        Returns the actual number of items available for booking in the given range.
        
        Formula: Total Stock - Max(Booked Quantity in overlap)
        """
        booked_qty = AvailabilityService.get_booked_quantity(product, start_time, end_time, exclude_booking_id)
        return max(0, product.quantity - booked_qty)

    @staticmethod
    def check_availability(product, start_time, end_time, requested_quantity=1, exclude_booking_id=None):
        """
        Checks if a specific quantity can be booked.
        
        Returns:
            (bool, str): (True, "") if available, (False, "Error message") if not.
        """
        available = AvailabilityService.get_available_quantity(product, start_time, end_time, exclude_booking_id)
        if available >= requested_quantity:
            return True, ""
        
        msg = f"สินค้า '{product.name}' ไม่พอสำหรับการจองในช่วงเวลานี้ (เหลือ {available} ชิ้น)"
        return False, msg

    @staticmethod
    def check_resource_overlap(resource_field, resource_instance, start_time, end_time, exclude_booking_id=None):
        """
        Checks if a specific resource (Equipment, Studio, Staff) is booked in the given range.
        
        Args:
            resource_field: Field name in Booking model (e.g., 'equipment', 'studios', 'staff')
            resource_instance: The specific object instance.
            start_time, end_time: datetime range.
            exclude_booking_id: ID to exclude.
            
        Returns:
            (bool, Booking/None): (True, None) if available.
                                  (False, ConflictingBooking) if overlapping.
        """
        # Statuses that block resources
        blocking_statuses = ['approved', 'active', 'quotation_sent', 'pending_deposit'] 
        
        query = Q(status__in=blocking_statuses) & \
                Q(start_time__lt=end_time) & \
                Q(end_time__gt=start_time)

        # Dynamic field lookup
        kwargs = {resource_field: resource_instance}
        query &= Q(**kwargs)

        if exclude_booking_id:
            query &= ~Q(id=exclude_booking_id)

        conflict = Booking.objects.filter(query).first()
        if conflict:
            return False, conflict
            
        return True, None

    @staticmethod
    def validate_cart(cart, start_time, end_time):
        """
        Validates an entire cart against the requested time range.
        
        Returns:
            (bool, str): (True, "") if all items are available.
                         (False, "Error message for first invalid item") if any fail.
        """
        if not start_time or not end_time:
            return False, "กรุณาระบุวันเวลารับ-คืนของ"
            
        for item in cart:
            product = item['product']
            quantity = item['quantity']
            
            is_valid, error_msg = AvailabilityService.check_availability(product, start_time, end_time, quantity)
            if not is_valid:
                return False, error_msg
                
        return True, ""
