
path = '/Users/thanandorn/Desktop/TESTMCOT/rentals/templates/rentals/public/checkout.html'
import re

with open(path, 'r') as f:
    content = f.read()

# Fix 1: Item Quantity
# Pattern: {{ item.quantity [NEWLINE] }}x
pattern1 = r'(\{\{\s*item\.quantity)\s*\n\s*(\}\})'
if re.search(pattern1, content):
    print("Found Split Quantity. Fixing...")
    content = re.sub(pattern1, r'{{ item.quantity }}', content)

# Fix 2: Item Total Price
# Pattern: ฿{{ item.total_price|intcomma [NEWLINE] }}
pattern2 = r'(\{\{\s*item\.total_price\|intcomma)\s*\n\s*(\}\})'
if re.search(pattern2, content):
    print("Found Split Price. Fixing...")
    content = re.sub(pattern2, r'{{ item.total_price|intcomma }}', content)

with open(path, 'w') as f:
    f.write(content)

print("Done.")
