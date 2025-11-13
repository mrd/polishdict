# Polish Dictionary

A comprehensive Polish dictionary tool that looks up Polish words with definitions, grammatical information, and declension/conjugation tables from Wiktionary. Available as both a command-line tool and a web application.

## Features

- **Dual-source lookups**: Queries both Polish (pl.wiktionary.org) and English (en.wiktionary.org) Wiktionary
- **Automatic lemma following**: In declension mode, automatically redirects inflected forms to their base forms
- **Declension/conjugation tables**: View full inflection tables for nouns, adjectives, and verbs
- **Fuzzy search**: Automatically tries Polish character variants (e.g., a→ą, c→ć) for misspelled words
- **Comprehensive information**: Displays:
  - Word definitions
  - Parts of speech (noun, verb, adjective, proper noun, etc.)
  - Pronunciation (IPA notation when available)
  - Etymology
  - Grammatical information (gender, aspect, etc.)
- **Multiple interfaces**:
  - Command-line tool with colored output
  - Mobile-friendly web application
  - Python module for integration into other projects
- **Smart URL anchors**: Links directly to relevant sections in Wiktionary pages

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
- `flask` - for web application (optional, only needed for webapp.py)

## Usage

### Command-Line Interface

Look up a Polish word:
```bash
./polishdict.py dom
```

Show declension/conjugation tables:
```bash
./polishdict.py -d dom           # Show noun declension
./polishdict.py -d być           # Show verb conjugation
./polishdict.py --declension dobry  # Show adjective declension
```

Inflected forms automatically redirect to lemmas in declension mode:
```bash
./polishdict.py -d psy      # Redirects to "pies"
./polishdict.py -d jestem   # Redirects to "być"
```

Other options:
```bash
./polishdict.py --no-color komputer  # Disable colored output
./polishdict.py -v słowo             # Verbose debug mode
./polishdict.py --help               # Show help message
```

### Web Application

Start the Flask web server:
```bash
python3 webapp.py
```

Then open your browser to `http://localhost:5000`

The web interface features:
- Mobile-friendly responsive design
- Search form with declension mode checkbox
- Color-coded sections for Polish/English definitions
- Formatted tables for declension/conjugation
- Automatic fuzzy search for misspellings
- Direct links to Wiktionary pages

### Python Module

You can also use polishdict as a Python module in your own code:

```python
import polishdict

# Look up a word
word_data = polishdict.lookup_word('dom', show_declension=False)

# Format the results for display
formatted = polishdict.format_word_data(word_data, show_declension=False, use_color=True)
print(formatted)

# Or use the API directly
from polishdict.api import PolishDictionaryAPI

api = PolishDictionaryAPI(verbose=False)
word_data = api.fetch_word('być')

# Access specific data
polish_defs = word_data['polish_wiktionary']['definitions']
english_defs = word_data['english_wiktionary']['definitions']
declension = word_data['polish_wiktionary']['declension']
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
├── polishdict.py           # Command-line interface
├── webapp.py               # Flask web application
├── templates/
│   └── index.html         # Web interface HTML
├── polishdict/            # Core module
│   ├── __init__.py       # Public API exports
│   ├── api.py            # Wiktionary API client
│   ├── formatter.py      # Terminal output formatter
│   └── cli.py            # Shared utility functions
├── requirements.txt       # Python dependencies
├── TODO                   # Development tasks
└── README.md             # This file
```

## API and Data Source

This tool uses:
- **Data source**: Wiktionary (pl.wiktionary.org and en.wiktionary.org)
- **API**: MediaWiki Action API
- **License**: Content from Wiktionary is available under the Creative Commons Attribution-ShareAlike 3.0 License

## Contributing

Suggestions and improvements are welcome! Some ideas for future enhancement:
- Cache frequently looked-up words to reduce API calls
- Export definitions to various formats (JSON, PDF, etc.)
- Support for additional languages
- Browser extension integration
- Offline mode with downloaded database

## License

This tool is provided as-is for educational purposes. Wiktionary content is licensed under CC BY-SA 3.0.

## Author

Created as a command-line utility for Polish language learners and enthusiasts.

## Version History

- **2.0** - Major refactoring: Python module structure, Flask web application, declension/conjugation tables, automatic lemma following, fuzzy search
- **1.0** - Initial CLI release with basic lookups
