#!/usr/bin/env python3
"""
Quick test to show what aspect is extracted for a word
Run this and share the output
"""

import sys
from polishdict.api import PolishDictionaryAPI
from polishdict.morphology import MorphologyParser

word = sys.argv[1] if len(sys.argv) > 1 else "zrobić"

print(f"\n{'='*80}")
print(f"Testing: {word}")
print(f"{'='*80}\n")

api = PolishDictionaryAPI(verbose=True)
data = api.fetch_word(word)

polish_data = data.get('polish_wiktionary', {})
if not polish_data:
    print("No data fetched")
    sys.exit(1)

print(f"\n{'='*80}")
print("DECLENSION/CONJUGATION TABLES:")
print(f"{'='*80}\n")

for idx, decl in enumerate(polish_data.get('declension', []), 1):
    print(f"Table {idx}:")
    print(f"  POS: {decl.get('pos')}")
    print(f"  Type: {decl.get('type')}")
    if 'aspect' in decl:
        print(f"  Aspect: {decl['aspect']}")
    else:
        print(f"  Aspect: NOT FOUND")

    # Parse it
    parser = MorphologyParser()
    result = parser.parse(
        decl.get('table', []),
        decl.get('pos', 'verb'),
        word,
        aspect=decl.get('aspect'),
        gender=decl.get('gender'),
        animacy=decl.get('animacy')
    )

    if result:
        result_dict = result.to_dict()
        print(f"  Parsed aspect: {result_dict.get('aspect')}")
    print()
