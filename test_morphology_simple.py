#!/usr/bin/env python3
"""
Simple morphology parser test with mock data

This doesn't require network access - uses example table data.
"""

import json
from polishdict.morphology import MorphologyParser

# Example: Simple noun declension table for "dom" (house) - masculine inanimate
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

# Example: "pies" (dog) - masculine animate with abbreviated headers
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

# Example: "kobieta" (woman) - feminine
NOUN_TABLE_KOBIETA = [
    ['', 'lp', 'lm'],
    ['M', 'kobieta', 'kobiety'],
    ['D', 'kobiety', 'kobiet'],
    ['C', 'kobiecie', 'kobietom'],
    ['B', 'kobietę', 'kobiety'],
    ['N', 'kobietą', 'kobietami'],
    ['Ms', 'kobiecie', 'kobietach'],
    ['W', 'kobieto', 'kobiety']
]

# Example: "okno" (window) - neuter
NOUN_TABLE_OKNO = [
    ['', 'lp', 'lm'],
    ['M', 'okno', 'okna'],
    ['D', 'okna', 'okien'],
    ['C', 'oknu', 'oknom'],
    ['B', 'okno', 'okna'],
    ['N', 'oknem', 'oknami'],
    ['Ms', 'oknie', 'oknach'],
    ['W', 'okno', 'okna']
]

# Example: "człowiek" (person) - masculine personal (suppletive plural)
NOUN_TABLE_CZLOWIEK = [
    ['', 'lp', 'lm'],
    ['M', 'człowiek', 'ludzie'],
    ['D', 'człowieka', 'ludzi'],
    ['C', 'człowiekowi', 'ludziom'],
    ['B', 'człowieka', 'ludzi'],
    ['N', 'człowiekiem', 'ludźmi'],
    ['Ms', 'człowieku', 'ludziach'],
    ['W', 'człowieku', 'ludzie']
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
    parser = MorphologyParser(verbose=False)  # Changed to False for cleaner output
    result = parser.parse(raw_table, word_class, lemma)

    if result:
        print("\n✓ Parsed successfully!")
        print("\nJSON output:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("\n✗ Parsing failed (returned None)")

    print("\n")


def main():
    print("Morphology Parser - Noun Tests")
    print("=" * 80)

    # Test 1: dom (house) - masculine inanimate
    test_table(
        "dom (house) - masculine inanimate",
        NOUN_TABLE_DOM,
        "noun",
        "dom"
    )

    # Test 2: pies (dog) - masculine animate
    test_table(
        "pies (dog) - masculine animate",
        NOUN_TABLE_PIES,
        "noun",
        "pies"
    )

    # Test 3: kobieta (woman) - feminine
    test_table(
        "kobieta (woman) - feminine",
        NOUN_TABLE_KOBIETA,
        "noun",
        "kobieta"
    )

    # Test 4: okno (window) - neuter
    test_table(
        "okno (window) - neuter",
        NOUN_TABLE_OKNO,
        "noun",
        "okno"
    )

    # Test 5: człowiek (person) - masculine personal with suppletive plural
    test_table(
        "człowiek (person) - masculine personal, suppletive plural",
        NOUN_TABLE_CZLOWIEK,
        "noun",
        "człowiek"
    )


if __name__ == '__main__':
    main()
