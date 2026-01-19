
import re

file_path = '/Users/thanandorn/Desktop/TESTMCOT/templates/admin/inventory_dashboard.html'
with open(file_path, 'rb') as f:
    content = f.read()

print(f"File size: {len(content)} bytes")

# Look for non-ascii
try:
    decoded = content.decode('utf-8')
    print("UTF-8 Decode: OK")
except Exception as e:
    print(f"UTF-8 Decode FAIL: {e}")

# Check specific line around "entry.entry_title"
lines = content.split(b'\n')
for i, line in enumerate(lines):
    if b'entry.entry_title' in line:
        print(f"Line {i+1}: {line}")
        # Print hex
        print(f"HEX: {line.hex()}")
