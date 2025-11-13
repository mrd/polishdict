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
from polishdict.search import search_with_fallback


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

        # Use shared search logic with fallback strategies
        word_data, correction_msg = search_with_fallback(api, args.word, verbose=args.verbose)

        # If a correction was made, print the message
        if correction_msg and not args.verbose:
            print(f"Found results for '{word_data['word']}' ({correction_msg}):\n")

        # If in declension mode and we got a form page, automatically look up the lemma
        word_data = check_and_follow_lemma(api, word_data, word_data.get('word', args.word), args.declension, args.verbose)

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
