#!/usr/bin/env python3
"""
Test grammar property extraction from POS block text
"""

from polishdict.api import PolishDictionaryAPI

def test_aspect_extraction():
    """Test aspect extraction for verbs"""
    api = PolishDictionaryAPI()

    test_cases = [
        ("czasownik niedokonany", "czasownik", {'aspect': 'imperfective'}),
        ("czasownik dokonany", "czasownik", {'aspect': 'perfective'}),
        ("czasownik dwuaspektowy", "czasownik", {'aspect': 'biaspectual'}),
        ("czasownik ndk", "czasownik", {'aspect': 'imperfective'}),
        ("czasownik dk", "czasownik", {'aspect': 'perfective'}),
        ("czasownik", "czasownik", {}),  # No aspect marker
    ]

    print("Testing aspect extraction:")
    print("=" * 80)

    for pos_text, pos, expected in test_cases:
        result = api._extract_grammar_properties(pos_text, pos)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{pos_text}' → {result}")
        if result != expected:
            print(f"  Expected: {expected}")

    print()

def test_gender_extraction():
    """Test gender extraction for nouns"""
    api = PolishDictionaryAPI()

    test_cases = [
        ("rzeczownik rodzaju męskiego", "rzeczownik", {'gender': 'masculine'}),
        ("rzeczownik rodzaju żeńskiego", "rzeczownik", {'gender': 'feminine'}),
        ("rzeczownik rodzaju nijakiego", "rzeczownik", {'gender': 'neuter'}),
        ("rzeczownik męski", "rzeczownik", {'gender': 'masculine'}),
        ("rzeczownik m", "rzeczownik", {'gender': 'masculine'}),
        ("rzeczownik ż", "rzeczownik", {'gender': 'feminine'}),
        ("rzeczownik n", "rzeczownik", {'gender': 'neuter'}),
        ("rzeczownik", "rzeczownik", {}),  # No gender marker
    ]

    print("Testing gender extraction:")
    print("=" * 80)

    for pos_text, pos, expected in test_cases:
        result = api._extract_grammar_properties(pos_text, pos)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{pos_text}' → {result}")
        if result != expected:
            print(f"  Expected: {expected}")

    print()

def test_animacy_extraction():
    """Test animacy extraction for masculine nouns"""
    api = PolishDictionaryAPI()

    test_cases = [
        ("rzeczownik męski osobowy", "rzeczownik", {'gender': 'masculine', 'animacy': 'personal'}),
        ("rzeczownik męski żywotny", "rzeczownik", {'gender': 'masculine', 'animacy': 'animate'}),
        ("rzeczownik męski nieżywotny", "rzeczownik", {'gender': 'masculine', 'animacy': 'inanimate'}),
        ("rzeczownik m mos", "rzeczownik", {'gender': 'masculine', 'animacy': 'personal'}),
        ("rzeczownik m mzw", "rzeczownik", {'gender': 'masculine', 'animacy': 'animate'}),
        ("rzeczownik m mnzw", "rzeczownik", {'gender': 'masculine', 'animacy': 'inanimate'}),
        ("rzeczownik męski", "rzeczownik", {'gender': 'masculine'}),  # No animacy marker
    ]

    print("Testing animacy extraction:")
    print("=" * 80)

    for pos_text, pos, expected in test_cases:
        result = api._extract_grammar_properties(pos_text, pos)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{pos_text}' → {result}")
        if result != expected:
            print(f"  Expected: {expected}")

    print()

def main():
    print("\nGrammar Property Extraction Tests")
    print("=" * 80)
    print()

    test_aspect_extraction()
    test_gender_extraction()
    test_animacy_extraction()

    print("=" * 80)
    print("All tests completed!")

if __name__ == '__main__':
    main()
