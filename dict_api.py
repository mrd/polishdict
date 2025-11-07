"""
Polish Dictionary API Module
Interfaces with Wiktionary to fetch Polish word definitions and grammatical information
"""

import requests
import re
import html
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
            'grammar': {},
            'declension': [],
            'pos_blocks': [],  # Track POS blocks with definition ranges
            'lemma': None  # If this is a form, store the lemma word
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
                result['lemma'] = lemma  # Store lemma for automatic lookup
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

            current_def_num = 1  # Track definition numbers

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

                # Track the start of this POS block's definitions
                start_def_num = current_def_num

                # Extract all <dd> items from this block
                dd_items = re.findall(r'<dd>\s*\([0-9.]+\)(.*?)</dd>', definitions_html, re.DOTALL)

                if self.verbose:
                    print(f"[Polish] Found {len(dd_items)} definitions for this POS")

                for item in dd_items:
                    # Remove embedded style/script/link tags first
                    item = re.sub(r'<style[^>]*>.*?</style>', '', item, flags=re.DOTALL)
                    item = re.sub(r'<script[^>]*>.*?</script>', '', item, flags=re.DOTALL)
                    item = re.sub(r'<link[^>]*>', '', item)
                    # Clean up the definition
                    definition = self._clean_text(self._strip_html(item))

                    if definition and len(definition) > 5:
                        result['definitions'].append({
                            'pos': detected_pos or 'nieznany',
                            'definition': definition,
                            'language': 'pl'
                        })
                        current_def_num += 1
                        if self.verbose:
                            print(f"[Polish] Added: {definition[:60]}...")

                # Track this POS block with its definition range
                if current_def_num > start_def_num:
                    result['pos_blocks'].append({
                        'pos': detected_pos or 'nieznany',
                        'start_def': start_def_num,
                        'end_def': current_def_num - 1
                    })
                    if self.verbose:
                        print(f"[Polish] POS block '{detected_pos}' has definitions {start_def_num}-{current_def_num - 1}")
        elif self.verbose:
            print(f"[Polish] No znaczenia section found at all")

        # Find declension tables (odmiana)
        odmiana_pos = re.search(r'<dt[^>]*>.*?data-field="odmiana".*?</dt>', polish_section)
        if odmiana_pos:
            if self.verbose:
                print(f"[Polish] Found odmiana marker")

            # Extract content after odmiana marker
            content_after_odmiana = polish_section[odmiana_pos.end():]

            # Find HTML tables in the odmiana section
            tables = re.findall(r'<table[^>]*class="[^"]*wikitable[^"]*odmiana[^"]*"[^>]*>(.*?)</table>', content_after_odmiana, re.DOTALL)

            if self.verbose:
                print(f"[Polish] Found {len(tables)} declension tables")

            # Associate tables with POS blocks based on order
            for idx, table_html in enumerate(tables):
                # Parse the table
                table_data = self._parse_html_table(table_html)
                if table_data:
                    # Associate with POS block if available
                    if idx < len(result['pos_blocks']):
                        pos_block = result['pos_blocks'][idx]
                        # Determine table type based on POS
                        table_type = 'conjugation' if pos_block['pos'] == 'czasownik' else 'declension'
                        result['declension'].append({
                            'table': table_data,
                            'start_def': pos_block['start_def'],
                            'end_def': pos_block['end_def'],
                            'pos': pos_block['pos'],
                            'type': table_type
                        })
                        if self.verbose:
                            print(f"[Polish] {table_type.capitalize()} table {idx+1} associated with definitions {pos_block['start_def']}-{pos_block['end_def']}")
                    else:
                        # No POS block association available
                        result['declension'].append({
                            'table': table_data,
                            'start_def': None,
                            'end_def': None,
                            'pos': None,
                            'type': 'declension'
                        })
                    if self.verbose:
                        print(f"[Polish] Parsed table with {len(table_data)} rows")

        # Check if definitions contain lemma references (e.g., "lm od: pies", "D od: dom")
        if not result['lemma'] and result['definitions']:
            for defn in result['definitions']:
                definition_text = defn.get('definition', '')
                # Patterns: "lm od: word", "D od: word", "forma od: word", verb conjugations, etc.
                lemma_patterns = [
                    r'(?:lm|lp|D|C|B|Ms|W|N)\s+od:\s+([^\s,;:.]+)',  # Case abbreviations
                    r'forma\s+od:\s+([^\s,;:.]+)',
                    r'czasownika\s+([^\s,;:.]+)',  # "czasownika być" = of verb być
                    r'od:\s+([^\s,;:.]+)'  # Generic "from: word"
                ]
                for pattern in lemma_patterns:
                    lemma_match = re.search(pattern, definition_text, re.IGNORECASE)
                    if lemma_match:
                        lemma = lemma_match.group(1).strip()
                        result['lemma'] = lemma
                        if self.verbose:
                            print(f"[Polish] Extracted lemma from definition: '{lemma}'")
                        break
                if result['lemma']:
                    break

        return result

    def _parse_english_wiktionary_html(self, html: str, word: str) -> Dict:
        """Parse HTML from English Wiktionary to extract definitions and grammar"""
        result = {
            'definitions': [],
            'etymology': None,
            'pronunciation': [],
            'grammar': {},
            'declension': [],
            'pos_blocks': [],  # Track POS blocks with definition ranges
            'declension_anchor': None,  # Anchor for declension/conjugation section
            'conjugation_anchor': None,  # Anchor for conjugation section
            'lemma': None  # If this is a form, store the lemma word
        }
        current_def_num = 1  # Track definition numbers
        current_pos_block = None  # Track current POS being processed

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

        heading_matches = list(re.finditer(r'<h[345]([^>]*)>(.*?)</h[345]>', polish_section, re.IGNORECASE))

        if self.verbose:
            print(f"[English] Found {len(heading_matches)} headings in Polish section")

        for i, match in enumerate(heading_matches):
            heading_tag = match.group(1)  # Tag attributes including id
            heading = self._strip_html(match.group(2))

            matched_pos = None
            for pos in pos_patterns:
                if pos in heading:
                    matched_pos = pos
                    break

            if matched_pos:
                # Start a new POS block
                if current_pos_block:
                    # Save the previous POS block
                    result['pos_blocks'].append(current_pos_block)
                    if self.verbose:
                        print(f"[English] Completed POS block '{current_pos_block['pos']}' with definitions {current_pos_block['start_def']}-{current_pos_block['end_def']}")

                current_pos_block = {
                    'pos': matched_pos,
                    'start_def': current_def_num,
                    'end_def': current_def_num - 1,  # Will update as we add definitions
                    'grammar_info': None  # Will store gender, aspect, diminutive, etc.
                }

                if self.verbose:
                    print(f"[English] Found POS: {matched_pos}")

                # Get section after this heading
                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(polish_section)
                pos_section = polish_section[section_start:section_end]

                # Extract grammatical info line (appears before <ol> but after heading)
                # Pattern: word followed by grammar markers (m/f/n, pf/impf, diminutive, etc.)
                # Example: "pies m animal (diminutive piesek, augmentative psisko)"
                # This typically appears in a <p> tag or <strong> tag before the <ol>
                before_ol = pos_section.split('<ol', 1)[0]  # Get everything before the definitions list
                # Look for <p><strong>word</strong> ... grammar info ... </p>
                grammar_pattern = r'<p[^>]*>.*?<strong[^>]*>' + re.escape(word) + r'</strong>\s*(.*?)</p>'
                grammar_match = re.search(grammar_pattern, before_ol, re.DOTALL | re.IGNORECASE)
                if grammar_match:
                    grammar_html = grammar_match.group(1)
                    # Clean up the grammar info
                    grammar_html = re.sub(r'<style[^>]*>.*?</style>', '', grammar_html, flags=re.DOTALL)
                    grammar_html = re.sub(r'<script[^>]*>.*?</script>', '', grammar_html, flags=re.DOTALL)
                    grammar_html = re.sub(r'<link[^>]*>', '', grammar_html)
                    grammar_info = self._clean_text(self._strip_html(grammar_html))
                    if grammar_info and len(grammar_info) > 1:
                        current_pos_block['grammar_info'] = grammar_info
                        if self.verbose:
                            print(f"[English] Found grammar info: {grammar_info}")

                # Extract definitions from ordered list
                ol_match = re.search(r'<ol[^>]*>(.*?)</ol>', pos_section, re.DOTALL)
                if ol_match:
                    list_items = re.findall(r'<li[^>]*>(.*?)</li>', ol_match.group(1), re.DOTALL)
                    if self.verbose:
                        print(f"[English] Found {len(list_items)} list items for {matched_pos}")

                    for item in list_items:
                        # Remove embedded style/script/link tags first
                        item = re.sub(r'<style[^>]*>.*?</style>', '', item, flags=re.DOTALL)
                        item = re.sub(r'<script[^>]*>.*?</script>', '', item, flags=re.DOTALL)
                        item = re.sub(r'<link[^>]*>', '', item)
                        # Extract only the main definition (before nested lists or examples)
                        item = re.sub(r'<[ou]l[^>]*>.*?</[ou]l>', '', item, flags=re.DOTALL)
                        clean_text = self._clean_text(self._strip_html(item))
                        if clean_text and len(clean_text) > 5:
                            result['definitions'].append({
                                'pos': matched_pos,
                                'definition': clean_text,
                                'language': 'en'
                            })
                            current_pos_block['end_def'] = current_def_num
                            current_def_num += 1
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
                    # Remove embedded style/script/link tags
                    item = re.sub(r'<style[^>]*>.*?</style>', '', item, flags=re.DOTALL)
                    item = re.sub(r'<script[^>]*>.*?</script>', '', item, flags=re.DOTALL)
                    item = re.sub(r'<link[^>]*>', '', item)
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
                    etym_html = p_match.group(1)
                    # Remove embedded style/script/link tags
                    etym_html = re.sub(r'<style[^>]*>.*?</style>', '', etym_html, flags=re.DOTALL)
                    etym_html = re.sub(r'<script[^>]*>.*?</script>', '', etym_html, flags=re.DOTALL)
                    etym_html = re.sub(r'<link[^>]*>', '', etym_html)
                    result['etymology'] = self._clean_text(self._strip_html(etym_html))

            # Check for declension or conjugation
            elif 'Declension' in heading or 'Conjugation' in heading:
                table_type = 'conjugation' if 'Conjugation' in heading else 'declension'

                # Extract the anchor ID from the heading tag
                id_match = re.search(r'id="([^"]+)"', heading_tag)
                if id_match:
                    anchor_id = id_match.group(1)
                    if table_type == 'conjugation':
                        result['conjugation_anchor'] = anchor_id
                    else:
                        result['declension_anchor'] = anchor_id
                    if self.verbose:
                        print(f"[English] Found {table_type} section with anchor: {anchor_id}")
                elif self.verbose:
                    print(f"[English] Found {table_type} section (no anchor found)")

                section_start = match.end()
                section_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(polish_section)
                decl_section = polish_section[section_start:section_end]

                # Find tables in the declension/conjugation section
                tables = re.findall(r'<table[^>]*>(.*?)</table>', decl_section, re.DOTALL)
                if self.verbose:
                    print(f"[English] Found {len(tables)} {table_type} tables")

                for table_html in tables:
                    # Parse the table
                    table_data = self._parse_html_table(table_html)
                    if table_data:
                        # Associate with the current POS block
                        if current_pos_block:
                            result['declension'].append({
                                'table': table_data,
                                'start_def': current_pos_block['start_def'],
                                'end_def': current_pos_block['end_def'],
                                'pos': current_pos_block['pos'],
                                'type': table_type
                            })
                            if self.verbose:
                                print(f"[English] {table_type.capitalize()} table associated with definitions {current_pos_block['start_def']}-{current_pos_block['end_def']}")
                        else:
                            # No POS block association
                            result['declension'].append({
                                'table': table_data,
                                'start_def': None,
                                'end_def': None,
                                'pos': None,
                                'type': table_type
                            })
                        if self.verbose:
                            print(f"[English] Parsed {table_type} table with {len(table_data)} rows")

        # Save the last POS block if it exists
        if current_pos_block and current_pos_block['end_def'] >= current_pos_block['start_def']:
            result['pos_blocks'].append(current_pos_block)
            if self.verbose:
                print(f"[English] Completed POS block '{current_pos_block['pos']}' with definitions {current_pos_block['start_def']}-{current_pos_block['end_def']}")

        # Check if definitions contain lemma references (e.g., "plural of pies", "genitive of dom")
        if not result['lemma'] and result['definitions']:
            for defn in result['definitions']:
                definition_text = defn.get('definition', '')
                # Patterns: "plural of word", "genitive of word", "inflection of word", verb forms, etc.
                lemma_patterns = [
                    r'(?:plural|singular|genitive|dative|accusative|instrumental|locative|vocative)\s+(?:of|form of)\s+([^\s,;:.]+)',
                    r'(?:first|second|third)-person\s+(?:singular|plural)\s+(?:present|past|future|imperative)\s+of\s+([^\s,;:.]+)',  # Verb conjugations
                    r'(?:impersonal|imperfective|perfective)\s+(?:present|past|future|imperative)\s+of\s+([^\s,;:.]+)',  # Impersonal/aspect forms
                    r'inflection of\s+([^\s,;:.]+)',
                    r'form of\s+([^\s,;:.]+)'
                ]
                for pattern in lemma_patterns:
                    lemma_match = re.search(pattern, definition_text, re.IGNORECASE)
                    if lemma_match:
                        lemma = lemma_match.group(1).strip()
                        result['lemma'] = lemma
                        if self.verbose:
                            print(f"[English] Extracted lemma from definition: '{lemma}'")
                        break
                if result['lemma']:
                    break

        return result

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode all HTML entities (&#47;, &#91;, &#93;, &nbsp;, etc.)
        text = html.unescape(text)
        return text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text from HTML"""
        # Remove citations like [1], [2], [note 1], etc.
        text = re.sub(r'\[[^\]]*\d+[^\]]*\]', '', text)
        # Remove edit links
        text = re.sub(r'\[edit\]', '', text, flags=re.IGNORECASE)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _parse_html_table(self, table_html: str) -> List[List[str]]:
        """Parse an HTML table into a list of rows"""
        rows = []

        # Find all table rows
        tr_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

        for tr in tr_matches:
            row = []
            # Find all cells (both th and td)
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.DOTALL)

            for cell in cells:
                # Remove style/script/link tags
                cell = re.sub(r'<style[^>]*>.*?</style>', '', cell, flags=re.DOTALL)
                cell = re.sub(r'<script[^>]*>.*?</script>', '', cell, flags=re.DOTALL)
                cell = re.sub(r'<link[^>]*>', '', cell)
                # Clean the cell content
                cell_text = self._clean_text(self._strip_html(cell))
                row.append(cell_text)

            if row:  # Only add non-empty rows
                rows.append(row)

        return rows
