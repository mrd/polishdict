"""
Search and Fuzzy Matching Logic
Shared search functionality for finding Polish words with fallback strategies
"""

from .cli import generate_polish_variants


def search_with_fallback(api, word, verbose=False):
    """
    Search for a word with multiple fallback strategies.

    Search order:
    1. Original word (case-sensitive)
    2. Lowercase (if word contains uppercase)
    3. Title case (if different from lowercase)
    4. Fuzzy search with Polish character variants

    Args:
        api: PolishDictionaryAPI instance
        word (str): The word to search for
        verbose (bool): If True, print debug information

    Returns:
        tuple: (word_data, correction_message)
            - word_data: Dictionary with search results
            - correction_message: String describing any correction made, or None
    """

    def has_results(word_data):
        """Check if word_data contains any definitions"""
        if word_data.get('polish_wiktionary') and word_data['polish_wiktionary'].get('definitions'):
            return True
        if word_data.get('english_wiktionary') and word_data['english_wiktionary'].get('definitions'):
            return True
        return False

    # Step 1: Try original word (case-sensitive)
    if verbose:
        print(f"Trying original word: {word}")
    word_data = api.fetch_word(word)

    if has_results(word_data):
        return word_data, None

    # Step 2: Try lowercase if word contains uppercase letters
    if word != word.lower():
        if verbose:
            print(f"Trying lowercase variant: {word.lower()}")
        variant_data = api.fetch_word(word.lower())

        if has_results(variant_data):
            variant_data['word'] = word.lower()
            correction_msg = f"lowercase correction from '{word}'"
            return variant_data, correction_msg

    # Step 3: Try title case if different from lowercase
    if word != word.title() and word.lower() != word.title():
        if verbose:
            print(f"Trying title case variant: {word.title()}")
        variant_data = api.fetch_word(word.title())

        if has_results(variant_data):
            variant_data['word'] = word.title()
            correction_msg = f"title case correction from '{word}'"
            return variant_data, correction_msg

    # Step 4: Try fuzzy search with Polish character variants
    if any(c in word.lower() for c in 'acelnosyz'):
        if verbose:
            print(f"Trying Polish character variants for: {word}")
        variants = generate_polish_variants(word)

        for variant in variants[:20]:  # Try up to 20 variants
            if verbose:
                print(f"Trying variant: {variant}")
            variant_data = api.fetch_word(variant)

            if has_results(variant_data):
                variant_data['word'] = f"{variant} (from {word})"
                correction_msg = f"corrected from '{word}'"
                return variant_data, correction_msg

    # No results found with any strategy
    return word_data, None
