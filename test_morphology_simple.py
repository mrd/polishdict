#!/usr/bin/env python3
"""
Simple morphology parser test with mock data

This doesn't require network access - uses example table data.
"""

import json
from polishdict.morphology import MorphologyParser

# Example: Simple noun declension table for "dom" (house)
# Typical Wiktionary format
NOUN_TABLE_DOM = [
    ['', 'liczba pojedyncza', 'liczba mnoga'],  # Header row
    ['mianownik', 'dom', 'domy'],
    ['dopełniacz', 'domu', 'domów'],
    ['celownik', 'domowi', 'domom'],
    ['biernik', 'dom', 'domy'],
    ['narzędnik', 'domem', 'domami'],
    ['miejscownik', 'domu', 'domach'],
    ['wołacz', 'domie', 'domy']
]

# Example: Another common format with abbreviated headers
NOUN_TABLE_PIES = [
    ['', 'lp', 'lm'],
    ['M', 'pies', 'psy'],
    ['D', 'psa', 'psów'],
    ['C', 'psu', 'psom'],
    ['B', 'psa', 'psy'],
    ['N', 'psem', 'psami'],
    ['Ms', 'psie', 'psach'],
    ['W', 'psie', 'psy']
]

def test_table(name, raw_table, word_class, lemma):
    """Test parsing a single table"""
    print(f"\n{'=' * 80}")
    print(f"Testing: {name}")
    print(f"Lemma: {lemma}, Word class: {word_class}")
    print(f"{'=' * 80}\n")

    print("Raw table:")
    for i, row in enumerate(raw_table):
        print(f"  Row {i}: {row}")

    print("\nParsing...")
    parser = MorphologyParser(verbose=True)
    result = parser.parse(raw_table, word_class, lemma)

    if result:
        print("\nParsed successfully!")
        print("\nJSON output:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("\nParsing failed (returned None)")

    print("\n")


def main():
    print("Morphology Parser Simple Test")
    print("=" * 80)

    # Test 1: dom (house) - masculine inanimate noun
    test_table(
        "dom (house) - full labels",
        NOUN_TABLE_DOM,
        "noun",
        "dom"
    )

    # Test 2: pies (dog) - masculine animate noun with abbreviations
    test_table(
        "pies (dog) - abbreviated labels",
        NOUN_TABLE_PIES,
        "noun",
        "pies"
    )


if __name__ == '__main__':
    main()
