#!/usr/bin/env python3
"""Test POS core extraction"""

import re
from polishdict.api import PolishDictionaryAPI

api = PolishDictionaryAPI()

test_cases = [
    # (full_pos_text, expected_aspect)
    ("czasownik dokonany", "perfective"),
    ("czasownik niedokonany", "imperfective"),
    ("czasownik dokonany, zobacz też: robić (ndk)", "perfective"),  # The bug case!
    ("czasownik niedokonany, zobacz też: zrobić (dk)", "imperfective"),
    ("czasownik dokonany; por. robić", "perfective"),
    ("czasownik dk", "perfective"),
    ("czasownik ndk, zobacz dokonany: zrobić", "imperfective"),
]

print("Testing POS core extraction and aspect detection:")
print("=" * 80)

for pos_text, expected_aspect in test_cases:
    # Extract core (simulate what API does)
    pos_core = re.split(r'[,;]|zobacz|zobacz też|por\.|zob\.|cf\.', pos_text.lower())[0].strip()

    # Extract grammar properties
    props = api._extract_grammar_properties(pos_core, 'czasownik')
    actual_aspect = props.get('aspect', 'none')

    status = "✓" if actual_aspect == expected_aspect else "✗"
    print(f"{status} '{pos_text}'")
    print(f"   Core: '{pos_core}'")
    print(f"   Expected: {expected_aspect}, Got: {actual_aspect}")
    print()
