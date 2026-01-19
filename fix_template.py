#!/usr/bin/env python3
"""Fix Django template tags split across multiple lines"""
import re

#  Read the template
with open('templates/admin/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all {{ ... }} tags split across lines
content = re.sub(r'\{\{[\s\n]+', '{{ ', content)
content = re.sub(r'[\s\n]+\}\}', ' }}', content)

# Fix all {% ... %} tags split across lines  
content = re.sub(r'\{%[\s\n]+', '{% ', content)
content = re.sub(r'[\s\n]+%\}', ' %}', content)

# Write back
with open('templates/admin/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed template tags!")
