#!/usr/bin/env python3
"""Test for 'dk' substring issue"""

# Test the substring problem
test_cases = [
    "czasownik dokonany",
    "czasownik niedokonany",
    "czasownik dk",
    "czasownik ndk",
]

for text in test_cases:
    print(f"Text: '{text}'")
    print(f"  'niedokonany' in text: {'niedokonany' in text}")
    print(f"  'ndk' in text: {'ndk' in text}")
    print(f"  'dokonany' in text: {'dokonany' in text}")
    print(f"  'dk' in text: {'dk' in text}")

    # Simulate the extraction logic
    if 'niedokonany' in text or 'ndk' in text:
        result = 'imperfective'
    elif 'dokonany' in text or 'dk' in text:
        result = 'perfective'
    else:
        result = 'none'

    print(f"  → Result: {result}")
    print()
