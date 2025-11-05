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

        # Check if this is a form/redirect page (common patterns)
        form_patterns = [
            r'zobacz hasło:?\s*<a[^>]*>([^<]+)</a>',
            r'forma\s+(?:rzeczownika|czasownika|przymiotnika)\s+<a[^>]*>([^<]+)</a>',
            r'<p[^>]*>\s*forma.*?<a[^>]*>([^<]+)</a>'
        ]

        for pattern in form_patterns:
            form_ref = re.search(pattern, html, re.IGNORECASE)
            if form_ref:
                lemma = self._strip_html(form_ref.group(1))
                if self.verbose:
                    print(f"[Polish] This appears to be a form page, main entry: '{lemma}'")
                result['definitions'].append({
                    'pos': 'forma',
                    'definition': f'Zobacz hasło: {lemma}',
                    'language': 'pl'
                })
                break

        # Find all headings with their positions
        heading_matches = list(re.finditer(r'<h[234][^>]*>(.*?)</h[234]>', html, re.IGNORECASE))

        if self.verbose:
            print(f"[Polish] Found {len(heading_matches)} headings")
            for idx, hm in enumerate(heading_matches):
                h_text = self._strip_html(hm.group(1))
                print(f"[Polish]   Heading {idx+1}: '{h_text}'")

        # First, find the Polish language section
        polish_section_start = None
        polish_section_end = None

        for i, match in enumerate(heading_matches):
            heading_text = self._strip_html(match.group(1)).lower()

            # Look for Polish language section
            if 'język polski' in heading_text or heading_text.endswith('(polski)'):
                polish_section_start = match.end()
                # Find the next language section (or end of document)
                for j in range(i + 1, len(heading_matches)):
                    next_heading = self._strip_html(heading_matches[j].group(1)).lower()
                    if 'język' in next_heading or next_heading.count('(') > 0:
                        polish_section_end = heading_matches[j].start()
                        break
                if polish_section_end is None:
                    polish_section_end = len(html)
                break

        if polish_section_start is None:
            if self.verbose:
                print("[Polish] No Polish language section found")
            return result

        if self.verbose:
            print(f"[Polish] Found Polish section from {polish_section_start} to {polish_section_end}")

        # Extract only the Polish section
        polish_section = html[polish_section_start:polish_section_end]

        if self.verbose:
            print(f"[Polish] Using definition list structure (dl/dt/dd tags)")
            # Save Polish section to file for debugging
            with open('/tmp/polish_section_debug.html', 'w', encoding='utf-8') as f:
                f.write(polish_section)
            print(f"[Polish] Saved Polish section to /tmp/polish_section_debug.html")

        # Polish Wiktionary uses <dl> structure with data-field attributes
        # Find pronunciation (wymowa)
        wymowa_match = re.search(r'<dt[^>]*>.*?data-field="wymowa".*?</dt>\s*<dd>(.*?)</dd>', polish_section, re.DOTALL)
        if wymowa_match:
            pron_html = wymowa_match.group(1)
            # Extract IPA
            ipa_matches = re.findall(r'<span[^>]*class="ipa"[^>]*>(.*?)</span>', pron_html)
            for ipa in ipa_matches:
                clean_ipa = self._clean_text(self._strip_html(ipa))
                if clean_ipa:
                    result['pronunciation'].append(f"IPA: {clean_ipa}")
                    if self.verbose:
                        print(f"[Polish] Found pronunciation: IPA: {clean_ipa}")

        # Find etymology (etymologia)
        etym_match = re.search(r'<dt[^>]*>.*?data-field="etymologia".*?</dt>\s*<dd>(.*?)</dd>', polish_section, re.DOTALL)
        if etym_match:
            etym_html = etym_match.group(1)
            result['etymology'] = self._clean_text(self._strip_html(etym_html))
            if self.verbose:
                print(f"[Polish] Found etymology: {result['etymology'][:60]}...")

        # Find definitions/meanings (znaczenia marker)
        # NOTE: In Polish Wiktionary, the znaczenia <dd> is EMPTY!
        # The actual definitions come AFTER in separate <p> and <dl> blocks
        znaczenia_pos = re.search(r'<dt[^>]*>.*?data-field="znaczenia".*?</dt>', polish_section)
        if znaczenia_pos:
            if self.verbose:
                print(f"[Polish] Found znaczenia marker at position {znaczenia_pos.end()}")

            # Extract content after znaczenia marker
            content_after_znaczenia = polish_section[znaczenia_pos.end():]

            # Find all <p><i>POS info</i></p> followed by <dl><dd>definitions</dd></dl> blocks
            # Pattern: <p>...rzeczownik...</p> then <dl><dd>(1.1) def...</dd></dl>
            # Note: Some have nested <i><i>...</i></i> tags, so we match the whole <p>...</p>
            pos_blocks = re.findall(
                r'<p>(.*?(?:rzeczownik|czasownik|przymiotnik|przysłówek|zaimek|przyimek|spójnik|wykrzyknik|liczebnik|partykuła|wykrzyknienie).*?)</p>\s*<dl>(.*?)</dl>',
                content_after_znaczenia,
                re.DOTALL | re.IGNORECASE
            )

            if self.verbose:
                print(f"[Polish] Found {len(pos_blocks)} POS blocks with definitions")

            for pos_text, definitions_html in pos_blocks:
                # Extract POS from the <p><i> text
                pos_clean = self._clean_text(pos_text).lower()
                detected_pos = None
                pos_patterns = ['rzeczownik', 'czasownik', 'przymiotnik', 'przysłówek',
                               'zaimek', 'przyimek', 'spójnik', 'wykrzyknik', 'liczebnik',
                               'partykuła', 'wykrzyknienie']
                for pos in pos_patterns:
                    if pos in pos_clean:
                        detected_pos = pos
                        break

                if self.verbose:
                    print(f"[Polish] Processing POS: {detected_pos or pos_clean}")

                # Extract all <dd> items from this block
                dd_items = re.findall(r'<dd>\s*\([0-9.]+\)(.*?)</dd>', definitions_html, re.DOTALL)

                if self.verbose:
                    print(f"[Polish] Found {len(dd_items)} definitions for this POS")

                for item in dd_items:
                    # Clean up the definition
                    definition = self._clean_text(self._strip_html(item))

                    if definition and len(definition) > 5:
                        result['definitions'].append({
                            'pos': detected_pos or 'nieznany',
                            'definition': definition,
                            'language': 'pl'
                        })
                        if self.verbose:
                            print(f"[Polish] Added: {definition[:60]}...")
        elif self.verbose:
            print(f"[Polish] No znaczenia section found at all")

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

        # Find Polish language section - be strict about matching
        # English Wiktionary structure: <h2 id="Polish">Polish</h2>
        polish_match = re.search(r'<h2[^>]*id="Polish"[^>]*>.*?</h2>', html, re.DOTALL)

        if self.verbose and not polish_match:
            # Debug: show the actual Polish h2 section
            polish_h2 = re.search(r'<h2[^>]*id="Polish"[^>]*>.*?</h2>', html, re.DOTALL)
            if polish_h2:
                print(f"[English] Found h2 with id='Polish' but pattern didn't match:")
                print(f"[English] Raw HTML: {polish_h2.group(0)[:200]}")
            else:
                print("[English] No h2 with id='Polish' found either")

        # Try alternative pattern - must have "Polish" as the main text in the span
        if not polish_match:
            polish_match = re.search(r'<h2[^>]*>\s*<span[^>]*>\s*Polish\s*</span>\s*</h2>', html, re.IGNORECASE)

        if not polish_match:
            if self.verbose:
                # Show what h2 sections we found
                h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
                print(f"[English] No Polish section found. Found {len(h2_matches)} h2 sections:")
                for idx, h2 in enumerate(h2_matches[:10]):
                    h2_clean = self._strip_html(h2).strip()
                    print(f"[English]   Section {idx+1}: '{h2_clean}'")
            return result

        if self.verbose:
            # Show what section was matched
            matched_text = self._strip_html(polish_match.group(0)).strip()
            print(f"[English] Found Polish language section: '{matched_text}'")

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
