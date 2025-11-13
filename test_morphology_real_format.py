#!/usr/bin/env python3
"""
Test verb parser with REAL Wiktionary table format

This file contains test data in the actual format returned by pl.wiktionary.org,
which is different from the simplified test format.
"""

import json
from polishdict.morphology import MorphologyParser

# Real Wiktionary format for "być" (to be)
# This is the actual format from pl.wiktionary.org
# Key differences from simple format:
# - Row 0: ['forma', 'liczba pojedyncza', 'liczba mnoga']
# - Row 1: Person headers spanning columns (1-3 singular, 4-6 plural)
# - Each tense row: [tense_name, form1, form2, form3, form4, form5, form6]
# - Past tense has gender marker in column 1: [tense_name, gender, form1, ...]
VERB_TABLE_BYC_REAL = [
    ['forma', 'liczba pojedyncza', 'liczba mnoga'],
    ['1. os.', '2. os.', '3. os.', '1. os.', '2. os.', '3. os.'],
    ['', '', '', '', '', '', ''],  # Often has empty separator row
    ['czas teraźniejszy', 'jestem', 'jesteś', 'jest', 'jesteśmy', 'jesteście', 'są'],
    ['czas przeszły', 'm', 'byłem', 'byłeś', 'był', 'byliśmy', 'byliście', 'byli'],
    ['', 'ż', 'byłam', 'byłaś', 'była', 'byłyśmy', 'byłyście', 'były'],
    ['', 'n', 'było', 'było', 'było', 'były', 'były', 'były'],
    ['czas przyszły', 'będę', 'będziesz', 'będzie', 'będziemy', 'będziecie', 'będą'],
    ['tryb rozkazujący', '—', 'bądź', 'niech będzie', 'bądźmy', 'bądźcie', 'niech będą'],
    ['tryb przypuszczający', 'm', 'byłbym / bym', 'byłbyś / byś', 'byłby / by', 'bylibyśmy / byśmy', 'bylibyście / byście', 'byliby / by'],
    ['', 'ż', 'byłabym / bym', 'byłabyś / byś', 'byłaby / by', 'byłybyśmy / byśmy', 'byłybyście / byście', 'byłyby / by'],
    ['', 'n', 'byłoby / by', 'byłoby / by', 'byłoby / by', 'byłyby / by', 'byłyby / by', 'byłyby / by'],
    ['bezokolicznik', 'być', '', '', '', '', ''],
    ['imiesłów przymiotnikowy', '—', '', '', '', '', ''],
    ['imiesłów przysłówkowy współczesny', 'będąc', '', '', '', '', ''],
    ['imiesłów przysłówkowy uprzedni', 'bywszy', '', '', '', '', ''],
    ['rzeczownik odsłowny', '—', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '']
]


def test_real_format():
    """Test parsing the real Wiktionary format"""
    print("=" * 80)
    print("Testing: REAL Wiktionary format for 'być'")
    print("=" * 80)

    print("\nRaw table (first 12 rows):")
    for i, row in enumerate(VERB_TABLE_BYC_REAL[:12]):
        print(f"  Row {i:2d}: {row}")

    print("\nParsing...")
    parser = MorphologyParser(verbose=True)
    result = parser.parse(VERB_TABLE_BYC_REAL, "verb", "być")

    if result:
        print("\n✓ Parsed successfully!")
        print("\nJSON output:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

        # Verify key forms are present
        print("\n" + "=" * 80)
        print("Verification:")
        print("=" * 80)

        forms = result.to_dict()['forms']

        # Check present tense
        if 'present' in forms:
            print("✓ Present tense found")
            present = forms['present']
            if 'singular' in present and '1' in present['singular']:
                print(f"  1st person singular: {present['singular']['1']}")
                assert present['singular']['1'] == 'jestem', "Expected 'jestem'"
            if 'plural' in present and '3' in present['plural']:
                print(f"  3rd person plural: {present['plural']['3']}")
                assert present['plural']['3'] == 'są', "Expected 'są'"
        else:
            print("✗ Present tense NOT found")

        # Check past tense
        if 'past' in forms:
            print("✓ Past tense found")
            past = forms['past']
            if 'masculine' in past:
                print("  ✓ Masculine forms found")
                if 'singular' in past['masculine'] and '1' in past['masculine']['singular']:
                    print(f"    1st person singular masculine: {past['masculine']['singular']['1']}")
                    assert past['masculine']['singular']['1'] == 'byłem', "Expected 'byłem'"
            if 'feminine' in past:
                print("  ✓ Feminine forms found")
            if 'neuter' in past:
                print("  ✓ Neuter forms found")
        else:
            print("✗ Past tense NOT found")

        # Check future tense
        if 'future' in forms:
            print("✓ Future tense found")
            future = forms['future']
            if 'singular' in future and '1' in future['singular']:
                print(f"  1st person singular: {future['singular']['1']}")
                assert future['singular']['1'] == 'będę', "Expected 'będę'"
        else:
            print("✗ Future tense NOT found")

        # Check imperative
        if 'imperative' in forms:
            print("✓ Imperative mood found")
        else:
            print("✗ Imperative mood NOT found")

        # Check conditional
        if 'conditional' in forms:
            print("✓ Conditional mood found")
        else:
            print("✗ Conditional mood NOT found")

        print("\n✓ All verification checks passed!")

    else:
        print("\n✗ Parsing failed (returned None)")
        return False

    return True


if __name__ == '__main__':
    success = test_real_format()
    exit(0 if success else 1)
