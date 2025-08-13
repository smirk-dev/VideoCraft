#!/usr/bin/env python3
"""
Fix all timestamp access issues in professional_exporter.py
"""

import re

# Read the file
with open('src/exporters/professional_exporter.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace patterns for safe timestamp access
replacements = [
    # Pattern: cut['timestamp']
    (r"cut\['timestamp'\]", r"self._safe_get_timestamp(cut)"),
    
    # Pattern: data['cuts'][i-1]['timestamp']
    (r"data\['cuts'\]\[i-1\]\['timestamp'\]", r"self._safe_get_timestamp(data['cuts'][i-1])"),
    
    # Pattern: any_var['timestamp'] where any_var is not 'data'
    (r"(\w+)\['timestamp'\]", lambda m: f"self._safe_get_timestamp({m.group(1)})" if m.group(1) != 'data' else m.group(0)),
]

# Apply replacements
for pattern, replacement in replacements:
    if callable(replacement):
        content = re.sub(pattern, replacement, content)
    else:
        content = re.sub(pattern, replacement, content)

# Write back
with open('src/exporters/professional_exporter.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all timestamp access issues in professional_exporter.py")
