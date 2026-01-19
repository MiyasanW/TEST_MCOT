from django.contrib.auth.models import User
from .models import Booking, BookingItem, Notification
from .services.notify import send_line_notify


class BookingService:
    """
    Service layer for handling booking creation and related operations.
    Centralizes booking logic to keep views thin.
    """
    
    @staticmethod
    def create_booking_from_cart(cart, booking_data, user=None):
        """
        Creates a booking from cart items.
        
        Args:
            cart: Cart instance with items
            booking_data: dict with customer info and dates
                - customer_name
                - customer_phone
                - customer_email
                - start_time (datetime)
                - end_time (datetime)
                - status (default: 'draft')
            user: Optional authenticated User instance
            
        Returns:
            Booking instance
            
        Raises:
            ValueError: If cart is empty or booking_data is invalid
        """
        if not cart or len(cart) == 0:
            raise ValueError("Cart is empty")
            
        # Validate required fields
        required_fields = ['customer_name', 'customer_phone', 'customer_email', 
                          'start_time', 'end_time']
        for field in required_fields:
            if field not in booking_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default status
        if 'status' not in booking_data:
            booking_data['status'] = 'draft'
            
        # Associate user if provided
        if user and user.is_authenticated:
            booking_data['created_by'] = user
            
        # Create booking
        booking = Booking.objects.create(**booking_data)
        
        # Create booking items from cart
        for item in cart:
            BookingItem.objects.create(
                booking=booking,
                product=item['product'],
                quantity=item['quantity'],
                price_at_booking=item['price']
            )
        
        # Send notifications
        BookingService._send_booking_notifications(booking)
        
        return booking
    
    @staticmethod
    def _send_booking_notifications(booking):
        """
        Sends LINE and in-app notifications for new bookings.
        
        Args:
            booking: Booking instance
        """
        # LINE Notification
        message = (
            f"\n📦 New Booking Request #{booking.id}\n"
            f"Customer: {booking.customer_name}\n"
            f"Items: {booking.items.count()} items\n"
            f"Date: {booking.start_time.strftime('%d/%m')} - {booking.end_time.strftime('%d/%m')}"
        )
        send_line_notify(message)
        
        # In-App Notification (To Staff)
        staff_users = User.objects.filter(is_staff=True)
        for staff in staff_users:
            Notification.objects.create(
                recipient=staff,
                message=f"📦 New Booking #{booking.id} by {booking.customer_name}",
                link=f"/admin/rentals/booking/{booking.id}/change/",
                notification_type='info'
            )
