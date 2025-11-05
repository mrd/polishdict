"""
Output Formatter Module
Formats dictionary results for terminal display
"""

from typing import Dict, List
from urllib.parse import quote
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class DictionaryFormatter:
    """Formats dictionary lookup results for terminal output"""

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def format_result(self, word_data: Dict, show_declension: bool = False) -> str:
        """
        Format the complete word lookup result

        Args:
            word_data: Dictionary containing word information
            show_declension: If True, show declension tables instead of definitions

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
                           polish_data.get('pronunciation') or
                           polish_data.get('declension')):
            output.append(self._colorize("=== POLISH (Polski) ===", Fore.CYAN, bold=True))
            output.append("")

            if show_declension:
                # Show declension/conjugation tables
                if polish_data.get('declension'):
                    # Determine if we have conjugations or declensions
                    has_conjugation = any(t.get('type') == 'conjugation' for t in polish_data['declension'])
                    has_declension = any(t.get('type') == 'declension' for t in polish_data['declension'])

                    if has_conjugation and has_declension:
                        output.append(self._colorize("Odmiana (Declension/Conjugation):", Fore.YELLOW))
                    elif has_conjugation:
                        output.append(self._colorize("Odmiana (Conjugation):", Fore.YELLOW))
                    else:
                        output.append(self._colorize("Odmiana (Declension):", Fore.YELLOW))
                    output.append("")

                    for idx, table_info in enumerate(polish_data['declension']):
                        # Show which definitions this table applies to
                        table_type_label = "koniugacja" if table_info.get('type') == 'conjugation' else "odmiana"
                        if table_info.get('start_def') and table_info.get('end_def'):
                            if table_info['start_def'] == table_info['end_def']:
                                def_range = f"For definition {table_info['start_def']}"
                            else:
                                def_range = f"For definitions {table_info['start_def']}-{table_info['end_def']}"

                            if table_info.get('pos'):
                                output.append(self._colorize(f"{def_range} ({table_info['pos']} - {table_type_label}):", Fore.GREEN))
                            else:
                                output.append(self._colorize(f"{def_range} ({table_type_label}):", Fore.GREEN))
                        else:
                            output.append(self._colorize(f"Table {idx + 1} ({table_type_label}):", Fore.GREEN))

                        output.extend(self._format_table(table_info['table']))
                        output.append("")
                else:
                    output.append("No declension/conjugation tables found.")
                    output.append("")
            else:
                # Show definitions (default behavior)
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

            # Add URL to Polish Wiktionary page
            polish_url = f"https://pl.wiktionary.org/wiki/{quote(word)}"
            output.append(self._colorize(f"More: {polish_url}", Fore.BLUE))
            output.append("")

        # Process English Wiktionary data
        english_data = word_data.get('english_wiktionary')
        if english_data and (english_data.get('definitions') or
                            english_data.get('etymology') or
                            english_data.get('pronunciation') or
                            english_data.get('declension')):
            output.append(self._colorize("=== ENGLISH ===", Fore.CYAN, bold=True))
            output.append("")

            if show_declension:
                # Show declension/conjugation tables
                if english_data.get('declension'):
                    # Determine if we have conjugations or declensions
                    has_conjugation = any(t.get('type') == 'conjugation' for t in english_data['declension'])
                    has_declension = any(t.get('type') == 'declension' for t in english_data['declension'])

                    if has_conjugation and has_declension:
                        output.append(self._colorize("Declension/Conjugation:", Fore.YELLOW))
                    elif has_conjugation:
                        output.append(self._colorize("Conjugation:", Fore.YELLOW))
                    else:
                        output.append(self._colorize("Declension:", Fore.YELLOW))
                    output.append("")

                    for idx, table_info in enumerate(english_data['declension']):
                        # Show which definitions this table applies to
                        table_type_label = table_info.get('type', 'declension')
                        if table_info.get('start_def') and table_info.get('end_def'):
                            if table_info['start_def'] == table_info['end_def']:
                                def_range = f"For definition {table_info['start_def']}"
                            else:
                                def_range = f"For definitions {table_info['start_def']}-{table_info['end_def']}"

                            if table_info.get('pos'):
                                output.append(self._colorize(f"{def_range} ({table_info['pos']} - {table_type_label}):", Fore.GREEN))
                            else:
                                output.append(self._colorize(f"{def_range} ({table_type_label}):", Fore.GREEN))
                        else:
                            output.append(self._colorize(f"Table {idx + 1} ({table_type_label}):", Fore.GREEN))

                        output.extend(self._format_table(table_info['table']))
                        output.append("")
                else:
                    output.append("No declension/conjugation tables found.")
                    output.append("")
            else:
                # Show definitions (default behavior)
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

            # Add URL to English Wiktionary page with smart anchor
            # If in declension mode and we have declension/conjugation sections, link to them
            if show_declension and (english_data.get('conjugation_anchor') or english_data.get('declension_anchor')):
                # Prefer conjugation anchor if available (for verbs), otherwise use declension
                anchor = english_data.get('conjugation_anchor') or english_data.get('declension_anchor')
                english_url = f"https://en.wiktionary.org/wiki/{quote(word)}#{anchor}"
            else:
                # Default to Polish section anchor
                english_url = f"https://en.wiktionary.org/wiki/{quote(word)}#Polish"
            output.append(self._colorize(f"More: {english_url}", Fore.BLUE))
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

    def _format_table(self, table_data: List[List[str]]) -> List[str]:
        """Format a table for terminal display with proper column alignment"""
        if not table_data:
            return ["  (empty table)"]

        output = []

        # Calculate column widths
        col_widths = []
        num_cols = max(len(row) for row in table_data)

        for col_idx in range(num_cols):
            max_width = 0
            for row in table_data:
                if col_idx < len(row):
                    # Strip ANSI color codes for width calculation
                    cell_text = row[col_idx]
                    max_width = max(max_width, len(cell_text))
            col_widths.append(max_width)

        # Format each row
        for row_idx, row in enumerate(table_data):
            formatted_cells = []
            for col_idx, cell in enumerate(row):
                width = col_widths[col_idx]
                # Pad cell to column width
                padded_cell = cell.ljust(width)

                # Colorize header row (first row)
                if row_idx == 0:
                    padded_cell = self._colorize(padded_cell, Fore.CYAN, bold=True)

                formatted_cells.append(padded_cell)

            # Join cells with separator
            row_str = "  │ " + " │ ".join(formatted_cells) + " │"
            output.append(row_str)

            # Add separator after header row
            if row_idx == 0:
                separator = "  ├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
                output.append(separator)

        return output
