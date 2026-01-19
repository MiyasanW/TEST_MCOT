from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product, Booking, BookingItem, PackageItem

@staff_member_required
def inventory_dashboard(request):
    products = Product.objects.filter(is_active=True).order_by('category', 'name')
    inventory_data = []

    for product in products:
        # Calculate Ledger
        ledger = []
        
        # Find bookings relevant to this product
        # 1. Direct BookingItems
        booking_items = BookingItem.objects.filter(
            product=product,
            booking__status__in=['approved', 'active', 'pending_deposit', 'quotation_sent'], # Consider 'reserved' statuses
            booking__end_time__gte=timezone.now() # Only future/current
        ).select_related('booking')

        for bi in booking_items:
            # Try to identify if this product came from a package?
            # Since we don't have a direct link, we'll check if the booking has other items that match a package signature?
            # Or simplified: checks if this product is part of any package?
            # The User requested "from package what".
            # WITHOUT a direct link, this is heuristic.
            # We'll stick to explicit data for now.
            
            # Check assigned equipment (Serial Numbers)
            assigned_equipment = bi.booking.equipment.filter(product=product)
            if assigned_equipment.exists():
                detail_text = f"Assigned: {', '.join([e.serial_number for e in assigned_equipment])}"
            else:
                detail_text = "Requested (Pending Assignment)"

            ledger.append({
                'date': bi.booking.start_time,
                'booking': bi.booking,
                'change': -bi.quantity,
                'detail': detail_text,
                'package_name': None # Placeholder
            })

        # Sort ledger by date
        ledger.sort(key=lambda x: x['date'])

        inventory_data.append({
            'product': product,
            'total_stock': product.quantity,
            'available_stock': product.remaining_quantity, # Use existing property
            'ledger': ledger
        })

    return render(request, 'admin/inventory_dashboard.html', {
        'inventory': inventory_data,
        'title': 'Inventory Dashboard'
    })
