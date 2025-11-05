#!/usr/bin/env python3
"""
Polish Dictionary Command-Line Tool

A command-line tool to look up Polish words, returning definitions,
parts of speech, and other grammatical information in both Polish and English.
"""

import argparse
import sys
from dict_api import PolishDictionaryAPI
from formatter import DictionaryFormatter


def main():
    """Main entry point for the Polish dictionary CLI"""

    parser = argparse.ArgumentParser(
        description='Look up Polish words with definitions and grammatical information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dom          Look up the word "dom"
  %(prog)s być          Look up the verb "być"
  %(prog)s --no-color   Look up with no colored output
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
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )

    args = parser.parse_args()

    # Initialize API and formatter
    api = PolishDictionaryAPI()
    formatter = DictionaryFormatter(use_color=not args.no_color)

    try:
        # Fetch word data
        print(f"Looking up '{args.word}'...\n")
        word_data = api.fetch_word(args.word)

        # Format and display results
        output = formatter.format_result(word_data)
        print(output)

    except KeyboardInterrupt:
        print("\n\nLookup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
