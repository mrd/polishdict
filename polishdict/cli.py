"""
CLI Utility Functions
Shared functions for command-line and web interfaces
"""

import itertools


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
