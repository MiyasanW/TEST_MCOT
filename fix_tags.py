
import re
import os

path = '/Users/thanandorn/Desktop/TESTMCOT/rentals/templates/rentals/public/checkout.html'

with open(path, 'r') as f:
    content = f.read()

# Pattern: {{ ... [newline] ... }}
# Finds tags that span generic whitespace including newlines
# Replaces with single line version
def fix_split_tags(text):
    # Regex to find {{ ... }} spanning multiple lines
    # We look for {{, then anything not }}, then }}, flag DOTALL makes . match newline
    pattern = re.compile(r'(\{\{[^}]*\}\})', re.DOTALL)
    
    def replacement(match):
        s = match.group(0)
        if '\n' in s:
            print(f"Fixing split tag: {s!r}")
            # Remove newlines and excess whitespace
            clean = re.sub(r'\s+', ' ', s)
            return clean
        return s

    return pattern.sub(replacement, text)

new_content = fix_split_tags(content)

if new_content != content:
    with open(path, 'w') as f:
        f.write(new_content)
    print("Fixed split template tags.")
else:
    print("No split template tags found.")
