#!/usr/bin/env python3
"""
Polish Dictionary Command-Line Tool

A command-line tool to look up Polish words, returning definitions,
parts of speech, and other grammatical information in both Polish and English.
"""

import argparse
import sys
from polishdict.api import PolishDictionaryAPI
from polishdict.formatter import DictionaryFormatter
from polishdict.cli import generate_polish_variants


def check_and_follow_lemma(api, word_data, original_word, declension_mode, verbose):
    """Check if word_data contains a lemma reference and fetch it if needed"""
    if not declension_mode:
        return word_data

    polish_data = word_data.get('polish_wiktionary')
    english_data = word_data.get('english_wiktionary')

    # Try to find a lemma from either source
    lemma = None
    source = None
    if polish_data and polish_data.get('lemma'):
        lemma = polish_data['lemma']
        source = 'Polish'
    elif english_data and english_data.get('lemma'):
        lemma = english_data['lemma']
        source = 'English'

    if verbose:
        print(f"[DEBUG] Polish lemma: {polish_data.get('lemma') if polish_data else None}")
        print(f"[DEBUG] English lemma: {english_data.get('lemma') if english_data else None}")
        print(f"[DEBUG] Selected lemma: {lemma}")
        print(f"[DEBUG] Has declension: {bool(polish_data.get('declension')) if polish_data else False}")

    # If we have a lemma and no declension tables, look up the lemma
    has_declension = (polish_data and polish_data.get('declension')) or \
                   (english_data and english_data.get('declension'))

    if lemma and not has_declension:
        if verbose:
            print(f"Detected form page (from {source}). Looking up lemma '{lemma}' for declension...\n")
        else:
            print(f"'{word_data.get('word', original_word)}' is a form of '{lemma}'. Showing declension for '{lemma}'...\n")

        # Fetch the lemma
        lemma_data = api.fetch_word(lemma)
        # Keep 'word' clean for URLs, add display_word for header
        lemma_data['display_word'] = f"{lemma} (from form: {word_data.get('word', original_word)})"
        return lemma_data

    return word_data


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
        word_data = check_and_follow_lemma(api, word_data, args.word, args.declension, args.verbose)

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
                    # Check if this variant is a form and follow lemma if needed
                    word_data = check_and_follow_lemma(api, word_data, variant, args.declension, args.verbose)
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
                    # Check if this variant is a form and follow lemma if needed
                    word_data = check_and_follow_lemma(api, word_data, variant, args.declension, args.verbose)
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
