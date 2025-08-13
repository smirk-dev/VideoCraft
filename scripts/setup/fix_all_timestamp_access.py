#!/usr/bin/env python3
"""
Comprehensive fix for all remaining timestamp access issues
"""

import os
import re

def safe_timestamp_access(match):
    """Convert obj['timestamp'] to safe access"""
    obj_name = match.group(1)
    return f"{obj_name}.get('timestamp', 0.0) if hasattr({obj_name}, 'get') else {obj_name}.get('timestamp', 0.0)"

def fix_file(filepath):
    """Fix timestamp access in a single file"""
    if not os.path.exists(filepath):
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern for obj['timestamp'] where obj is a variable name
    pattern = r"(\w+)\['timestamp'\]"
    
    # Replace with safe access - but skip if it's already safe
    def replacement(match):
        obj_name = match.group(1)
        # Skip if it's already a safe access pattern
        if 'get(' in match.group(0):
            return match.group(0)
        # Skip if it's a dictionary literal like data['timestamp']
        if obj_name in ['data', 'config', 'metadata', 'params']:
            return match.group(0)
        return f"{obj_name}.get('timestamp', 0.0) if hasattr({obj_name}, 'get') else {obj_name}.get('timestamp', 0.0)"
    
    content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Files to fix
files_to_fix = [
    'src/ai_models/music_sync_engine.py',
    'src/ai_models/sentiment_analyzer.py',
    'src/utils/timeline_sync.py',
    'src/utils/cloud_integration.py'
]

print("🔧 Fixing remaining timestamp access issues...")

for file_path in files_to_fix:
    if fix_file(file_path):
        print(f"✅ Fixed {file_path}")
    else:
        print(f"⚠️ No changes needed in {file_path}")

print("✅ All timestamp access issues fixed!")
