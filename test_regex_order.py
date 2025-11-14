#!/usr/bin/env python3
"""Test regex split order"""

import re

test_text = "czasownik dokonany, zobacz też: robić (ndk)"

# Current pattern (wrong order)
pattern1 = r'[,;]|zobacz|zobacz też|por\.|zob\.|cf\.'
result1 = re.split(pattern1, test_text.lower())
print("Pattern 1 (current):", pattern1)
print("Result:", result1)
print("First part:", result1[0].strip())
print()

# Fixed pattern (longer matches first)
pattern2 = r'[,;]|zobacz też|zobacz|por\.|zob\.|cf\.'
result2 = re.split(pattern2, test_text.lower())
print("Pattern 2 (fixed):", pattern2)
print("Result:", result2)
print("First part:", result2[0].strip())
print()

# Test with just "zobacz"
test_text2 = "czasownik dokonany, zobacz: robić (ndk)"
result3 = re.split(pattern2, test_text2.lower())
print("Test with just 'zobacz':", result3)
print("First part:", result3[0].strip())
