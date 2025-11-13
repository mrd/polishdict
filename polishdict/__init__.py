"""
Polish Dictionary Module
A module for looking up Polish words with definitions, parts of speech,
and grammatical information from Wiktionary.
"""

from .api import PolishDictionaryAPI
from .formatter import DictionaryFormatter
from .search import search_with_fallback

__version__ = '1.0.0'


def lookup_word(word, show_declension=False, verbose=False):
    """
    Look up a Polish word and return structured results.

    Args:
        word (str): The Polish word to look up
        show_declension (bool): If True, show declension/conjugation tables
        verbose (bool): If True, print debug information

    Returns:
        dict: Dictionary containing word data with keys:
            - word: The looked-up word
            - display_word: Display name (may include form info)
            - polish_wiktionary: Dict with Polish Wiktionary data
            - english_wiktionary: Dict with English Wiktionary data
    """
    api = PolishDictionaryAPI(verbose=verbose)
    word_data = api.fetch_word(word)

    return word_data


def format_word_data(word_data, show_declension=False, use_color=True):
    """
    Format word data for display.

    Args:
        word_data (dict): Word data from lookup_word()
        show_declension (bool): If True, show declension/conjugation tables
        use_color (bool): If True, use colored output (for terminal)

    Returns:
        str: Formatted string ready for display
    """
    formatter = DictionaryFormatter(use_color=use_color)
    return formatter.format_result(word_data, show_declension=show_declension)


__all__ = ['lookup_word', 'format_word_data', 'PolishDictionaryAPI', 'DictionaryFormatter', 'search_with_fallback']
