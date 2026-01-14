
import re

path = '/Users/thanandorn/Desktop/TESTMCOT/rentals/templates/rentals/public/booking_success.html'

with open(path, 'r') as f:
    content = f.read()

# Fix Booking ID
# Pattern: #{{ booking.id }}
content = re.sub(r'#\{\{\s*booking\.id\s*\}\}', '#{{ booking.id }}', content)

# Fix Status
# Pattern: {{ booking.get_status_display }}
content = re.sub(r'\{\{\s*booking\.get_status_display\s*\}\}', '{{ booking.get_status_display }}', content)

# Generic Fix for any double braces split by newline (Fallback)
content = re.sub(r'\{\{([^\}]+)\n\s*\}\}', r'{{\1}}', content)

with open(path, 'w') as f:
    f.write(content)

print("Applied template tag fixes to booking_success.html.")
