"""
Output Formatter Module
Formats dictionary results for terminal display
"""

from typing import Dict, List
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class DictionaryFormatter:
    """Formats dictionary lookup results for terminal output"""

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def format_result(self, word_data: Dict) -> str:
        """
        Format the complete word lookup result

        Args:
            word_data: Dictionary containing word information

        Returns:
            Formatted string ready for display
        """
        output = []

        word = word_data.get('word', 'Unknown')
        output.append(self._format_header(word))
        output.append("")

        # Process Polish Wiktionary data
        polish_data = word_data.get('polish_wiktionary')
        if polish_data and (polish_data.get('definitions') or
                           polish_data.get('etymology') or
                           polish_data.get('pronunciation')):
            output.append(self._colorize("=== POLISH (Polski) ===", Fore.CYAN, bold=True))
            output.append("")

            if polish_data.get('pronunciation'):
                output.append(self._colorize("Pronunciation:", Fore.YELLOW))
                for pron in polish_data['pronunciation']:
                    output.append(f"  • {pron}")
                output.append("")

            if polish_data.get('etymology'):
                output.append(self._colorize("Etymology:", Fore.YELLOW))
                output.append(f"  {polish_data['etymology']}")
                output.append("")

            if polish_data.get('definitions'):
                output.append(self._colorize("Definitions:", Fore.YELLOW))
                output.extend(self._format_definitions(polish_data['definitions']))
                output.append("")

        # Process English Wiktionary data
        english_data = word_data.get('english_wiktionary')
        if english_data and (english_data.get('definitions') or
                            english_data.get('etymology') or
                            english_data.get('pronunciation')):
            output.append(self._colorize("=== ENGLISH ===", Fore.CYAN, bold=True))
            output.append("")

            if english_data.get('pronunciation'):
                output.append(self._colorize("Pronunciation:", Fore.YELLOW))
                for pron in english_data['pronunciation']:
                    output.append(f"  • {pron}")
                output.append("")

            if english_data.get('etymology'):
                output.append(self._colorize("Etymology:", Fore.YELLOW))
                output.append(f"  {english_data['etymology']}")
                output.append("")

            if english_data.get('definitions'):
                output.append(self._colorize("Definitions:", Fore.YELLOW))
                output.extend(self._format_definitions(english_data['definitions']))
                output.append("")

            if english_data.get('grammar'):
                output.append(self._colorize("Grammar Information:", Fore.YELLOW))
                for pos, grammar in english_data['grammar'].items():
                    output.append(f"  [{pos}] {grammar}")
                output.append("")

        # Check if no results found
        if not (polish_data and polish_data.get('definitions')) and \
           not (english_data and english_data.get('definitions')):
            output.append(self._colorize("No definitions found for this word.", Fore.RED))
            output.append("")
            output.append("This could mean:")
            output.append("  • The word doesn't exist in Wiktionary")
            output.append("  • It might be misspelled")
            output.append("  • It might be a very rare or archaic term")

        return "\n".join(output)

    def _format_header(self, word: str) -> str:
        """Format the word header"""
        header = f"{'=' * 60}"
        title = f"  {word.upper()}"
        footer = f"{'=' * 60}"

        if self.use_color:
            return f"{Fore.GREEN}{Style.BRIGHT}{header}\n{title}\n{footer}{Style.RESET_ALL}"
        return f"{header}\n{title}\n{footer}"

    def _format_definitions(self, definitions: List[Dict]) -> List[str]:
        """Format a list of definitions"""
        output = []
        current_pos = None
        def_count = 0

        for defn in definitions:
            pos = defn.get('pos', 'Unknown')
            definition = defn.get('definition', '')

            # Print part of speech header if it changed
            if pos != current_pos:
                if def_count > 0:  # Add spacing between different POS
                    output.append("")
                current_pos = pos
                def_count = 0
                output.append(self._colorize(f"  [{self._format_pos(pos)}]", Fore.MAGENTA))

            # Print the definition
            def_count += 1
            output.append(f"    {def_count}. {definition}")

        return output

    def _format_pos(self, pos: str) -> str:
        """Format part of speech labels"""
        # Convert Polish POS to more readable format
        pos_mapping = {
            'rzeczownik': 'Noun (rzeczownik)',
            'czasownik': 'Verb (czasownik)',
            'przymiotnik': 'Adjective (przymiotnik)',
            'przysłówek': 'Adverb (przysłówek)',
            'zaimek': 'Pronoun (zaimek)',
            'przyimek': 'Preposition (przyimek)',
            'spójnik': 'Conjunction (spójnik)',
            'wykrzyknik': 'Interjection (wykrzyknik)',
            'liczebnik': 'Numeral (liczebnik)'
        }

        pos_lower = pos.lower().strip()
        return pos_mapping.get(pos_lower, pos)

    def _colorize(self, text: str, color: str, bold: bool = False) -> str:
        """Apply color to text if colors are enabled"""
        if not self.use_color:
            return text

        result = color + text
        if bold:
            result = Style.BRIGHT + result
        result += Style.RESET_ALL
        return result
