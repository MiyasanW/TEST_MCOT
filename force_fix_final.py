
import re

path = '/Users/thanandorn/Desktop/TESTMCOT/rentals/templates/rentals/public/checkout.html'

with open(path, 'r') as f:
    content = f.read()

# Fix 1: Quantity
# Matches {{ item.quantity [newlines/spaces] }}x
content = re.sub(r'\{\{\s*item\.quantity\s*\}\}x', '{{ item.quantity }}x', content) # Normalize first if already single line but weird spacing
content = re.sub(r'\{\{\s*item\.quantity\s*\n\s*\}\}x', '{{ item.quantity }}x', content)

# Fix 2: Price
# Matches ฿{{ item.total_price|intcomma [newlines/spaces] }}
content = re.sub(r'฿\{\{\s*item\.total_price\|intcomma\s*\}\}', '฿{{ item.total_price|intcomma }}', content)
content = re.sub(r'฿\{\{\s*item\.total_price\|intcomma\s*\n\s*\}\}', '฿{{ item.total_price|intcomma }}', content)

# Generic Fix for any double braces split by newline (Fallback)
content = re.sub(r'\{\{([^\}]+)\n\s*\}\}', r'{{\1}}', content)

with open(path, 'w') as f:
    f.write(content)

print("Applied final template tag fixes.")
