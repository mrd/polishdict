#!/usr/bin/env python3
"""
Verb conjugation parser tests

Tests verb conjugation table parsing with various tenses and moods.
"""

import json
from polishdict.morphology import MorphologyParser

# Example: "być" (to be) - present tense
# This is one of the most common verb table formats
VERB_TABLE_BYC_PRESENT = [
    ['', 'liczba pojedyncza', 'liczba mnoga'],
    ['1. os.', 'jestem', 'jesteśmy'],
    ['2. os.', 'jesteś', 'jesteście'],
    ['3. os.', 'jest', 'są']
]

# Example: "mieć" (to have) - present tense with abbreviated headers
VERB_TABLE_MIEC_PRESENT = [
    ['', 'lp', 'lm'],
    ['1 os.', 'mam', 'mamy'],
    ['2 os.', 'masz', 'macie'],
    ['3 os.', 'ma', 'mają']
]

# Example: past tense table (has gender dimension)
# Format: rows are person+gender, columns are numbers
VERB_TABLE_BYC_PAST = [
    ['', 'lp', 'lm'],
    ['1. os. m.', 'byłem', 'byliśmy'],
    ['2. os. m.', 'byłeś', 'byliście'],
    ['3. os. m.', 'był', 'byli'],
    ['1. os. ż.', 'byłam', 'byłyśmy'],
    ['2. os. ż.', 'byłaś', 'byłyście'],
    ['3. os. ż.', 'była', 'były'],
    ['3. os. n.', 'było', 'były']
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
        print("\n✓ Parsed successfully!")
        print("\nJSON output:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("\n✗ Parsing failed (returned None)")

    print("\n")


def main():
    print("Morphology Parser - Verb Conjugation Tests")
    print("=" * 80)

    # Test 1: być - present tense
    test_table(
        "być (to be) - present tense",
        VERB_TABLE_BYC_PRESENT,
        "verb",
        "być"
    )

    # Test 2: mieć - present tense with abbreviations
    test_table(
        "mieć (to have) - present tense",
        VERB_TABLE_MIEC_PRESENT,
        "verb",
        "mieć"
    )

    # Test 3: być - past tense (with genders)
    test_table(
        "być (to be) - past tense (with genders)",
        VERB_TABLE_BYC_PAST,
        "verb",
        "być"
    )


if __name__ == '__main__':
    main()
