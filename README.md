# Polish Dictionary CLI Tool

A command-line tool to look up Polish words, returning definitions, parts of speech, and other grammatical information in both Polish and English from Wiktionary.

## Features

- **Dual-language support**: Fetches definitions from both Polish (pl.wiktionary.org) and English (en.wiktionary.org) Wiktionary
- **Comprehensive information**: Displays:
  - Word definitions
  - Parts of speech (noun, verb, adjective, etc.)
  - Pronunciation (IPA notation when available)
  - Etymology
  - Grammatical information
- **Colored output**: Beautiful, easy-to-read colored terminal output (can be disabled)
- **Simple interface**: Just type the word you want to look up

## Installation

### Requirements

- Python 3.6 or higher
- Internet connection

### Setup

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

The tool requires:
- `requests` - for making HTTP requests to Wiktionary API
- `colorama` - for cross-platform colored terminal output

## Usage

### Basic Usage

```bash
python3 polishdict.py <word>
```

or make it executable and run directly:

```bash
chmod +x polishdict.py
./polishdict.py <word>
```

### Examples

Look up a noun:
```bash
./polishdict.py dom
```

Look up a verb:
```bash
./polishdict.py być
```

Look up an adjective:
```bash
./polishdict.py piękny
```

### Options

- `--no-color`: Disable colored output for terminals that don't support colors
- `-v, --verbose`: Enable verbose debug output to troubleshoot parsing issues
- `--version`: Show version information
- `--help`: Show help message

### Examples with options

Disable colored output:
```bash
./polishdict.py --no-color komputer
```

Enable verbose debug mode (useful for troubleshooting):
```bash
./polishdict.py -v dobra
```

## Output Format

The tool displays results in the following format:

```
============================================================
  WORD
============================================================

=== POLISH (Polski) ===

Pronunciation:
  • IPA: /word/

Etymology:
  Etymology information if available

Definitions:
  [Part of Speech]
    1. First definition
    2. Second definition

=== ENGLISH ===

Pronunciation:
  • IPA: /word/

Definitions:
  [Part of Speech]
    1. English definition
    2. Another definition
```

## How It Works

The tool uses the MediaWiki API provided by Wiktionary to:

1. Query both Polish and English Wiktionary for the given word
2. Parse the returned HTML content to extract:
   - Definitions organized by part of speech
   - Pronunciation information (IPA)
   - Etymology when available
   - Grammatical information
3. Format the information in a clear, readable format with color coding

## Supported Parts of Speech

### Polish (Polski)
- rzeczownik (noun)
- czasownik (verb)
- przymiotnik (adjective)
- przysłówek (adverb)
- zaimek (pronoun)
- przyimek (preposition)
- spójnik (conjunction)
- wykrzyknik (interjection)
- liczebnik (numeral)

### English
- Noun
- Verb
- Adjective
- Adverb
- Pronoun
- Preposition
- Conjunction
- Interjection
- Numeral

## Troubleshooting

### No results found

If the tool reports "No definitions found", this could mean:
- The word doesn't exist in Wiktionary
- The word might be misspelled
- It might be a very rare or archaic term
- Try searching for the base form of the word (e.g., infinitive for verbs)

**Debug tip**: Use the `-v` or `--verbose` flag to see detailed information about what the parser is finding:
```bash
./polishdict.py -v <word>
```
This will show you:
- HTML content length received from Wiktionary
- Number of headings found
- Parts of speech detected
- Number of definitions extracted
- Which definitions were added or skipped

### Network errors

If you see connection errors:
- Check your internet connection
- Wiktionary servers might be temporarily unavailable
- Try again in a few moments

### Character encoding issues

Make sure your terminal supports UTF-8 encoding to properly display Polish characters like:
- ą, ć, ę, ł, ń, ó, ś, ź, ż

## Project Structure

```
polishdict/
├── polishdict.py     # Main CLI script
├── dict_api.py       # Wiktionary API interface
├── formatter.py      # Output formatting
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## API and Data Source

This tool uses:
- **Data source**: Wiktionary (pl.wiktionary.org and en.wiktionary.org)
- **API**: MediaWiki Action API
- **License**: Content from Wiktionary is available under the Creative Commons Attribution-ShareAlike 3.0 License

## Contributing

Suggestions and improvements are welcome! Some ideas for enhancement:
- Cache frequently looked-up words
- Add support for word forms/conjugations
- Export definitions to file
- Interactive mode
- Support for other languages

## License

This tool is provided as-is for educational purposes. Wiktionary content is licensed under CC BY-SA 3.0.

## Author

Created as a command-line utility for Polish language learners and enthusiasts.

## Version

1.0 - Initial release
