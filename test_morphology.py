#!/usr/bin/env python3
"""
Test script for morphology parser

Usage:
    python3 test_morphology.py dom
    python3 test_morphology.py być
    python3 test_morphology.py -v pies  # verbose mode
"""

import sys
import argparse
import json
from polishdict.api import PolishDictionaryAPI
from polishdict.morphology import MorphologyParser


def main():
    parser = argparse.ArgumentParser(description='Test morphology parser with a Polish word')
    parser.add_argument('word', help='Polish word to test')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    # Fetch word data using existing API
    print(f"Fetching data for '{args.word}'...")
    api = PolishDictionaryAPI(verbose=args.verbose)
    word_data = api.fetch_word(args.word)

    # Extract Polish declension tables
    polish_data = word_data.get('polish_wiktionary', {})
    declensions = polish_data.get('declension', [])

    if not declensions:
        print(f"\nNo declension/conjugation tables found for '{args.word}'")
        return

    print(f"\nFound {len(declensions)} table(s)\n")
    print("=" * 80)

    # Test morphology parser on each table
    morph_parser = MorphologyParser(verbose=args.verbose)

    for idx, decl in enumerate(declensions, 1):
        print(f"\nTable {idx}:")
        print(f"Type: {decl.get('type', 'unknown')}")
        print(f"POS: {decl.get('pos', 'unknown')}")

        # Show extracted grammar properties
        if 'aspect' in decl:
            print(f"Aspect: {decl['aspect']}")
        if 'gender' in decl:
            print(f"Gender: {decl['gender']}")
        if 'animacy' in decl:
            print(f"Animacy: {decl['animacy']}")

        raw_table = decl.get('table', [])
        if not raw_table:
            print("  (empty table)")
            continue

        # Show raw table
        print(f"\nRaw table ({len(raw_table)} rows):")
        print("-" * 80)
        for row_idx, row in enumerate(raw_table):
            print(f"  Row {row_idx}: {row}")

        # Try to parse it with extracted grammar properties
        word_class = decl.get('pos', 'noun')  # Default to noun if unknown
        lemma = args.word
        aspect = decl.get('aspect')
        gender = decl.get('gender')
        animacy = decl.get('animacy')

        print(f"\nParsing as {word_class}...")
        parsed = morph_parser.parse(raw_table, word_class, lemma, aspect=aspect, gender=gender, animacy=animacy)

        if parsed:
            print("\nParsed structure:")
            print("-" * 80)
            print(json.dumps(parsed.to_dict(), indent=2, ensure_ascii=False))
        else:
            print("\n(parsing returned None)")

        print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
