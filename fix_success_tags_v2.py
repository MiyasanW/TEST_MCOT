
import re
import os

path = '/Users/thanandorn/Desktop/TESTMCOT/rentals/templates/rentals/public/booking_success.html'

with open(path, 'r') as f:
    content = f.read()

# Robust pattern: find {{ ... }} that might span multiple lines
# We use re.DOTALL so dot matches newlines, but we must be careful to match minimal {{ ... }}
# Pattern: \{(?:\{)(.*?)(?:\})\}
pattern = re.compile(r'\{\{(.*?)\}\}', re.DOTALL)

def replacement(match):
    text = match.group(1)
    if '\n' in text:
        # Replace newlines and extra spaces with single space
        cleaned = re.sub(r'\s+', ' ', text).strip()
        print(f"Fixed: {text!r} -> {cleaned!r}")
        return f"{{{{ {cleaned} }}}}"
    return match.group(0)

new_content = pattern.sub(replacement, content)

if new_content != content:
    with open(path, 'w') as f:
        f.write(new_content)
    print("Files updated.")
else:
    print("No changes needed.")
