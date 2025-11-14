#!/usr/bin/env python3
"""
Debug aspect extraction for a specific word
"""

import sys
from polishdict.api import PolishDictionaryAPI

word = sys.argv[1] if len(sys.argv) > 1 else "zrobić"

print(f"Fetching '{word}' from Polish Wiktionary...")
print("=" * 80)

api = PolishDictionaryAPI(verbose=True)
data = api.fetch_word(word)

polish_data = data.get('polish_wiktionary', {})
print("\n" + "=" * 80)
print("POS BLOCKS:")
print("=" * 80)

for idx, block in enumerate(polish_data.get('pos_blocks', []), 1):
    print(f"\nBlock {idx}:")
    print(f"  POS: {block.get('pos')}")
    if 'aspect' in block:
        print(f"  Aspect: {block['aspect']}")
    if 'gender' in block:
        print(f"  Gender: {block['gender']}")
    if 'animacy' in block:
        print(f"  Animacy: {block['animacy']}")
    print(f"  Definitions: {block.get('start_def')}-{block.get('end_def')}")

print("\n" + "=" * 80)
print("DECLENSION TABLES:")
print("=" * 80)

for idx, decl in enumerate(polish_data.get('declension', []), 1):
    print(f"\nTable {idx}:")
    print(f"  Type: {decl.get('type')}")
    print(f"  POS: {decl.get('pos')}")
    if 'aspect' in decl:
        print(f"  Aspect: {decl['aspect']}")
    if 'gender' in decl:
        print(f"  Gender: {decl['gender']}")
    if 'animacy' in decl:
        print(f"  Animacy: {decl['animacy']}")
