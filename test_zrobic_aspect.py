#!/usr/bin/env python3
"""
Direct test of aspect extraction for zrobić
This forces a fresh import to ensure latest code is used
"""

import sys
import importlib

# Force reload of modules to get latest code
if 'polishdict.api' in sys.modules:
    importlib.reload(sys.modules['polishdict.api'])
if 'polishdict.morphology' in sys.modules:
    importlib.reload(sys.modules['polishdict.morphology'])

from polishdict.api import PolishDictionaryAPI
import re

# Test the extraction function directly
api = PolishDictionaryAPI()

print("="*80)
print("DIRECT FUNCTION TEST")
print("="*80)

test_cases = [
    ("czasownik dokonany", "czasownik"),
    ("czasownik dokonany, zobacz też: robić (ndk)", "czasownik"),
    ("czasownik niedokonany", "czasownik"),
]

for pos_text, pos in test_cases:
    # Simulate what the API does
    pos_clean = pos_text.lower()
    pos_core = re.split(r'[,;]|zobacz|zobacz też|por\.|zob\.|cf\.', pos_clean)[0].strip()
    props = api._extract_grammar_properties(pos_core, pos)

    print(f"\nInput: '{pos_text}'")
    print(f"Core:  '{pos_core}'")
    print(f"Props: {props}")

print("\n" + "="*80)
print("REAL WIKTIONARY TEST (requires network)")
print("="*80)

try:
    word = "zrobić"
    print(f"\nFetching {word}...")
    data = api.fetch_word(word)

    polish_data = data.get('polish_wiktionary', {})
    if polish_data:
        print(f"\nPOS Blocks found: {len(polish_data.get('pos_blocks', []))}")
        for idx, block in enumerate(polish_data.get('pos_blocks', []), 1):
            print(f"\nBlock {idx}:")
            print(f"  POS: {block.get('pos')}")
            print(f"  Aspect: {block.get('aspect', 'NOT FOUND')}")

        print(f"\nDeclension tables found: {len(polish_data.get('declension', []))}")
        for idx, decl in enumerate(polish_data.get('declension', []), 1):
            print(f"\nTable {idx}:")
            print(f"  POS: {decl.get('pos')}")
            print(f"  Aspect: {decl.get('aspect', 'NOT FOUND')}")
    else:
        print("No Polish Wiktionary data found")

except Exception as e:
    print(f"Error: {e}")
