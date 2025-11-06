#!/usr/bin/env python3
"""
Polish Dictionary Command-Line Tool

A command-line tool to look up Polish words, returning definitions,
parts of speech, and other grammatical information in both Polish and English.
"""

import argparse
import sys
import itertools
from dict_api import PolishDictionaryAPI
from formatter import DictionaryFormatter


def generate_polish_variants(word: str) -> list:
    """Generate possible Polish spellings for a word with ASCII characters"""
    # Map ASCII characters to their Polish equivalents
    polish_chars = {
        'a': ['a', 'ą'],
        'c': ['c', 'ć'],
        'e': ['e', 'ę'],
        'l': ['l', 'ł'],
        'n': ['n', 'ń'],
        'o': ['o', 'ó'],
        's': ['s', 'ś'],
        'z': ['z', 'ź', 'ż']
    }

    # Build list of possible characters for each position
    char_options = []
    for char in word.lower():
        if char in polish_chars:
            char_options.append(polish_chars[char])
        else:
            char_options.append([char])

    # Generate all combinations (limit to avoid explosion)
    variants = []
    for combo in itertools.product(*char_options):
        variant = ''.join(combo)
        if variant != word.lower():  # Don't include the original
            variants.append(variant)

    # Limit to a reasonable number of variants
    return variants[:20]


def main():
    """Main entry point for the Polish dictionary CLI"""

    parser = argparse.ArgumentParser(
        description='Look up Polish words with definitions and grammatical information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dom              Look up the word "dom"
  %(prog)s być              Look up the verb "być"
  %(prog)s --no-color dobra Look up with no colored output
  %(prog)s -v słowo         Look up with verbose debug output
        """
    )

    parser.add_argument(
        'word',
        help='Polish word to look up'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    parser.add_argument(
        '-d', '--declension', '--odmiana',
        action='store_true',
        dest='declension',
        help='Show declension tables instead of definitions'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose debug output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )

    args = parser.parse_args()

    # Initialize API and formatter
    api = PolishDictionaryAPI(verbose=args.verbose)
    formatter = DictionaryFormatter(use_color=not args.no_color)

    try:
        # Fetch word data
        mode_str = 'declensions' if args.declension else 'definitions'
        if args.verbose:
            print(f"Looking up '{args.word}' ({mode_str}, verbose mode)...\n")
        else:
            print(f"Looking up '{args.word}' ({mode_str})...\n")

        word_data = api.fetch_word(args.word)

        # If in declension mode and we got a form page, automatically look up the lemma
        if args.declension:
            polish_data = word_data.get('polish_wiktionary')
            if args.verbose:
                print(f"[DEBUG] Polish data exists: {polish_data is not None}")
                if polish_data:
                    print(f"[DEBUG] Lemma field: {polish_data.get('lemma')}")
                    print(f"[DEBUG] Has declension: {bool(polish_data.get('declension'))}")

            if polish_data and polish_data.get('lemma') and not polish_data.get('declension'):
                lemma = polish_data['lemma']
                if args.verbose:
                    print(f"Detected form page. Looking up lemma '{lemma}' for declension...\n")
                else:
                    print(f"'{args.word}' is a form of '{lemma}'. Showing declension for '{lemma}'...\n")

                # Fetch the lemma
                word_data = api.fetch_word(lemma)
                # Update the word to show both
                word_data['word'] = f"{lemma} (from form: {args.word})"

        # Check if we got any results
        has_results = False
        if word_data.get('polish_wiktionary') and word_data['polish_wiktionary'].get('definitions'):
            has_results = True
        if word_data.get('english_wiktionary') and word_data['english_wiktionary'].get('definitions'):
            has_results = True

        # If no results, try case-insensitive variants
        if not has_results:
            case_variants = []

            # Try lowercase if not already lowercase
            if args.word != args.word.lower():
                case_variants.append(args.word.lower())

            # Try title case if not already title case
            if args.word != args.word.title():
                case_variants.append(args.word.title())

            for variant in case_variants:
                if args.verbose:
                    print(f"Trying case variant: {variant}")
                variant_data = api.fetch_word(variant)

                # Check if this variant has results
                variant_has_results = False
                if variant_data.get('polish_wiktionary') and variant_data['polish_wiktionary'].get('definitions'):
                    variant_has_results = True
                if variant_data.get('english_wiktionary') and variant_data['english_wiktionary'].get('definitions'):
                    variant_has_results = True

                if variant_has_results:
                    if not args.verbose:
                        print(f"Found results for '{variant}' (case correction from '{args.word}'):\n")
                    word_data = variant_data
                    word_data['word'] = f"{variant}"
                    has_results = True
                    break

        # If still no results and word contains ASCII characters that could be Polish, try fuzzy search
        if not has_results and any(c in args.word.lower() for c in 'acelnosyz'):
            if not args.verbose:
                print(f"No results found for '{args.word}'. Trying Polish character variants...\n")
            variants = generate_polish_variants(args.word)

            for variant in variants:
                if args.verbose:
                    print(f"Trying variant: {variant}")
                variant_data = api.fetch_word(variant)

                # Check if this variant has results
                variant_has_results = False
                if variant_data.get('polish_wiktionary') and variant_data['polish_wiktionary'].get('definitions'):
                    variant_has_results = True
                if variant_data.get('english_wiktionary') and variant_data['english_wiktionary'].get('definitions'):
                    variant_has_results = True

                if variant_has_results:
                    print(f"Found results for '{variant}' (corrected from '{args.word}'):\n")
                    word_data = variant_data
                    word_data['word'] = f"{variant} (from {args.word})"
                    break

        # Format and display results
        output = formatter.format_result(word_data, show_declension=args.declension)
        print(output)

    except KeyboardInterrupt:
        print("\n\nLookup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
