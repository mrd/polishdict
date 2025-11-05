"""
Polish Dictionary API Module
Interfaces with Wiktionary to fetch Polish word definitions and grammatical information
"""

import requests
import re
from html.parser import HTMLParser
from typing import Dict, List, Optional


class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract text content and structure"""

    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_element = None
        self.text_buffer = []

    def handle_starttag(self, tag, attrs):
        # Save previous element if any
        if self.current_element and self.text_buffer:
            self.current_element['text'] = ''.join(self.text_buffer).strip()
            self.text_buffer = []

        # Create new element
        self.current_element = {
            'tag': tag,
            'attrs': dict(attrs),
            'text': ''
        }
        self.elements.append(self.current_element)

    def handle_data(self, data):
        if data.strip():
            self.text_buffer.append(data)

    def handle_endtag(self, tag):
        if self.current_element and self.text_buffer:
            self.current_element['text'] = ''.join(self.text_buffer).strip()
            self.text_buffer = []

    def get_elements_by_tag(self, tag):
        """Get all elements with specific tag"""
        return [el for el in self.elements if el['tag'] == tag]

    def get_text_content(self):
        """Get all text content"""
        return ' '.join(el['text'] for el in self.elements if el['text'])


class PolishDictionaryAPI:
    """Handles API calls to Wiktionary for Polish word lookups"""

    def __init__(self, verbose=False):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolishDict/1.0 (Educational Tool)'
        })
        self.verbose = verbose

    def fetch_word(self, word: str) -> Dict:
        """
        Fetch word information from both Polish and English Wiktionary

        Args:
            word: Polish word to look up

        Returns:
            Dictionary containing word data from both sources
        """
        result = {
            'word': word,
            'polish_wiktionary': self._fetch_polish_wiktionary(word),
            'english_wiktionary': self._fetch_english_wiktionary(word)
        }
        return result

    def _fetch_polish_wiktionary(self, word: str) -> Optional[Dict]:
        """Fetch data from Polish Wiktionary (pl.wiktionary.org)"""
        try:
            # Use MediaWiki API to get page content
            url = "https://pl.wiktionary.org/w/api.php"
            params = {
                'action': 'parse',
                'page': word,
                'format': 'json',
                'prop': 'text|sections',
                'disabletoc': 1
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                return None

            if 'parse' not in data:
                return None

            html_content = data['parse']['text']['*']
            return self._parse_polish_wiktionary_html(html_content, word)

        except Exception as e:
            print(f"Error fetching from Polish Wiktionary: {e}")
            return None

    def _fetch_english_wiktionary(self, word: str) -> Optional[Dict]:
        """Fetch data from English Wiktionary (en.wiktionary.org)"""
        try:
            # Use MediaWiki API to get page content
            url = "https://en.wiktionary.org/w/api.php"
            params = {
                'action': 'parse',
                'page': word,
                'format': 'json',
                'prop': 'text|sections',
                'disabletoc': 1
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                return None

            if 'parse' not in data:
                return None

            html_content = data['parse']['text']['*']
            return self._parse_english_wiktionary_html(html_content, word)

        except Exception as e:
            print(f"Error fetching from English Wiktionary: {e}")
            return None

    def _parse_polish_wiktionary_html(self, html: str, word: str) -> Dict:
        """Parse HTML from Polish Wiktionary to extract definitions and grammar"""
        result = {
            'definitions': [],
            'etymology': None,
            'pronunciation': [],
            'grammar': {}
        }

        if self.verbose:
            print(f"[Polish] HTML length: {len(html)}")

        # Find part of speech sections and extract definitions from each
        pos_patterns = ['rzeczownik', 'czasownik', 'przymiotnik', 'przysłówek',
                       'zaimek', 'przyimek', 'spójnik', 'wykrzyknik', 'liczebnik',
                       'partykuła', 'wykrzyknienie']

        # Find all headings with their positions
        heading_matches = list(re.finditer(r'<h[234][^>]*>(.*?)</h[234]>', html, re.IGNORECASE))

        if self.verbose:
            print(f"[Polish] Found {len(heading_matches)} headings")

        for i, match in enumerate(heading_matches):
            heading_text = self._strip_html(match.group(1)).lower()

            # Check if this is a part of speech heading
            matched_pos = None
            for pos in pos_patterns:
                if pos in heading_text:
                    matched_pos = pos
                    break

            if matched_pos:
                if self.verbose:
                    print(f"[Polish] Found POS: {matched_pos}")

                # Extract content between this heading and the next one
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(html)
                section_content = html[section_start:section_end]

                # Find the first ordered or unordered list in this section
                list_match = re.search(r'<ol[^>]*>(.*?)</ol>', section_content, re.DOTALL)
                if not list_match:
                    list_match = re.search(r'<ul[^>]*>(.*?)</ul>', section_content, re.DOTALL)

                if list_match:
                    # Extract list items from this specific list
                    list_items = re.findall(r'<li[^>]*>(.*?)</li>', list_match.group(1), re.DOTALL)
                    if self.verbose:
                        print(f"[Polish] Found {len(list_items)} list items for {matched_pos}")

                    for item in list_items:
                        # Remove nested lists (examples, sub-definitions)
                        item_clean = re.sub(r'<[uo]l[^>]*>.*?</[uo]l>', '', item, flags=re.DOTALL)
                        definition = self._clean_text(self._strip_html(item_clean))

                        # Filter out short or metadata entries
                        if (definition and len(definition) > 5 and
                            not definition.startswith('↑') and
                            'zobacz' not in definition.lower()[:20]):
                            result['definitions'].append({
                                'pos': matched_pos,
                                'definition': definition,
                                'language': 'pl'
                            })
                            if self.verbose:
                                print(f"[Polish] Added definition: {definition[:60]}...")
                        elif self.verbose and definition:
                            print(f"[Polish] Skipped: {definition[:60]}...")
                elif self.verbose:
                    print(f"[Polish] No list found for {matched_pos}")

            # Check for pronunciation section
            elif 'wymowa' in heading_text:
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(html)
                pron_section = html[section_start:section_end]

                # Find pronunciation list items
                pron_items = re.findall(r'<li[^>]*>(.*?)</li>', pron_section, re.DOTALL)
                for item in pron_items[:3]:  # Get first few items
                    clean_pron = self._clean_text(self._strip_html(item))
                    if clean_pron and len(clean_pron) > 2:
                        result['pronunciation'].append(clean_pron)

            # Check for etymology section
            elif 'etymologia' in heading_text:
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(html)
                etym_section = html[section_start:section_end]

                # Get first paragraph
                p_match = re.search(r'<p[^>]*>(.*?)</p>', etym_section, re.DOTALL)
                if p_match:
                    result['etymology'] = self._clean_text(self._strip_html(p_match.group(1)))

        return result

    def _parse_english_wiktionary_html(self, html: str, word: str) -> Dict:
        """Parse HTML from English Wiktionary to extract definitions and grammar"""
        result = {
            'definitions': [],
            'etymology': None,
            'pronunciation': [],
            'grammar': {}
        }

        if self.verbose:
            print(f"[English] HTML length: {len(html)}")

        # Find Polish language section
        polish_match = re.search(r'<h2[^>]*>.*?<span[^>]*id="Polish"[^>]*>.*?</h2>', html, re.DOTALL)
        if not polish_match:
            if self.verbose:
                print("[English] No Polish section found")
            return result

        if self.verbose:
            print("[English] Found Polish language section")

        # Get content after Polish heading until next h2
        polish_start = polish_match.end()
        next_h2 = re.search(r'<h2[^>]*>', html[polish_start:])
        polish_end = polish_start + next_h2.start() if next_h2 else len(html)
        polish_section = html[polish_start:polish_end]

        # Find part of speech sections
        pos_patterns = ['Noun', 'Verb', 'Adjective', 'Adverb', 'Pronoun',
                       'Preposition', 'Conjunction', 'Interjection', 'Numeral', 'Particle']

        heading_matches = list(re.finditer(r'<h[34][^>]*>(.*?)</h[34]>', polish_section, re.IGNORECASE))

        if self.verbose:
            print(f"[English] Found {len(heading_matches)} headings in Polish section")

        for i, match in enumerate(heading_matches):
            heading = self._strip_html(match.group(1))

            matched_pos = None
            for pos in pos_patterns:
                if pos in heading:
                    matched_pos = pos
                    break

            if matched_pos:
                if self.verbose:
                    print(f"[English] Found POS: {matched_pos}")

                # Get section after this heading
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(polish_section)
                pos_section = polish_section[section_start:section_end]

                # Extract definitions from ordered list
                ol_match = re.search(r'<ol[^>]*>(.*?)</ol>', pos_section, re.DOTALL)
                if ol_match:
                    list_items = re.findall(r'<li[^>]*>(.*?)</li>', ol_match.group(1), re.DOTALL)
                    if self.verbose:
                        print(f"[English] Found {len(list_items)} list items for {matched_pos}")

                    for item in list_items:
                        # Extract only the main definition (before nested lists or examples)
                        item = re.sub(r'<[ou]l[^>]*>.*?</[ou]l>', '', item, flags=re.DOTALL)
                        clean_text = self._clean_text(self._strip_html(item))
                        if clean_text and len(clean_text) > 5:
                            result['definitions'].append({
                                'pos': matched_pos,
                                'definition': clean_text,
                                'language': 'en'
                            })
                            if self.verbose:
                                print(f"[English] Added definition: {clean_text[:60]}...")
                elif self.verbose:
                    print(f"[English] No ordered list found for {matched_pos}")

            # Check for pronunciation
            elif 'Pronunciation' in heading:
                if self.verbose:
                    print("[English] Found pronunciation section")
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(polish_section)
                pron_section = polish_section[section_start:section_end]
                pron_items = re.findall(r'<li[^>]*>(.*?)</li>', pron_section)
                for item in pron_items[:3]:
                    clean_pron = self._clean_text(self._strip_html(item))
                    if clean_pron and len(clean_pron) > 2:
                        result['pronunciation'].append(clean_pron)

            # Check for etymology
            elif 'Etymology' in heading:
                if self.verbose:
                    print("[English] Found etymology section")
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(polish_section)
                etym_section = polish_section[section_start:section_end]
                # Get first paragraph after etymology heading
                p_match = re.search(r'<p[^>]*>(.*?)</p>', etym_section, re.DOTALL)
                if p_match:
                    result['etymology'] = self._clean_text(self._strip_html(p_match.group(1)))

        return result

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text from HTML"""
        # Remove citations like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)
        # Remove edit links
        text = re.sub(r'\[edit\]', '', text, flags=re.IGNORECASE)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
