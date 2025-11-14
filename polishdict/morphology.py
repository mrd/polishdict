"""
Morphology Parser Module

Parses raw declension/conjugation tables from Wiktionary into structured
morphological data with semantic meaning attached to each form.

Design based on MORPHOLOGY_DESIGN.md
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class WordClass(Enum):
    """Part of speech categories"""
    VERB = 'verb'
    NOUN = 'noun'
    ADJECTIVE = 'adjective'
    PRONOUN = 'pronoun'
    NUMERAL = 'numeral'
    ADVERB = 'adverb'


class Aspect(Enum):
    """Verb aspect"""
    IMPERFECTIVE = 'imperfective'
    PERFECTIVE = 'perfective'
    BIASPECTUAL = 'biaspectual'


class Gender(Enum):
    """Grammatical gender"""
    MASCULINE = 'masculine'
    FEMININE = 'feminine'
    NEUTER = 'neuter'


class Animacy(Enum):
    """Animacy for masculine nouns"""
    PERSONAL = 'personal'  # masculine personal (virile)
    ANIMATE = 'animate'
    INANIMATE = 'inanimate'


class Case(Enum):
    """Polish cases"""
    NOMINATIVE = 'nominative'  # mianownik
    GENITIVE = 'genitive'  # dopełniacz
    DATIVE = 'dative'  # celownik
    ACCUSATIVE = 'accusative'  # biernik
    INSTRUMENTAL = 'instrumental'  # narzędnik
    LOCATIVE = 'locative'  # miejscownik
    VOCATIVE = 'vocative'  # wołacz


class Number(Enum):
    """Grammatical number"""
    SINGULAR = 'singular'
    PLURAL = 'plural'


class Tense(Enum):
    """Verb tenses"""
    PRESENT = 'present'
    PAST = 'past'
    FUTURE = 'future'


class Mood(Enum):
    """Verb moods"""
    INDICATIVE = 'indicative'
    CONDITIONAL = 'conditional'
    IMPERATIVE = 'imperative'


class Person(Enum):
    """Grammatical person"""
    FIRST = '1'
    SECOND = '2'
    THIRD = '3'
    IMPERSONAL = 'impersonal'


# Type alias for form values that can have variants
FormValue = Union[str, Dict[str, str]]  # Either "word" or {"primary": "word", "archaic": "oldword"}


@dataclass
class MorphologicalForms:
    """Base class for morphological forms"""
    word_class: WordClass
    lemma: str
    forms: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        result = asdict(self)
        # Convert enums to strings
        if isinstance(self.word_class, Enum):
            result['word_class'] = self.word_class.value
        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class VerbConjugation(MorphologicalForms):
    """Verb conjugation data"""
    aspect: Optional[Aspect] = None

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.aspect and isinstance(self.aspect, Enum):
            result['aspect'] = self.aspect.value
        return result


@dataclass
class NounDeclension(MorphologicalForms):
    """Noun declension data"""
    gender: Optional[Gender] = None
    animacy: Optional[Animacy] = None

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.gender and isinstance(self.gender, Enum):
            result['gender'] = self.gender.value
        if self.animacy and isinstance(self.animacy, Enum):
            result['animacy'] = self.animacy.value
        return result


@dataclass
class AdjectiveDeclension(MorphologicalForms):
    """Adjective declension data"""
    pass


class MorphologyParser:
    """
    Parses raw table data into structured morphological forms.

    Handles:
    - Noun declensions (7 cases × 2 numbers × gender/animacy variations)
    - Verb conjugations (tenses × moods × persons × numbers × genders)
    - Adjective declensions (cases × numbers × genders × comparison degrees)
    """

    # Polish case names to recognize in table headers
    CASE_LABELS = {
        'mianownik': Case.NOMINATIVE,
        'mian.': Case.NOMINATIVE,
        'm': Case.NOMINATIVE,
        'dopełniacz': Case.GENITIVE,
        'dop.': Case.GENITIVE,
        'd': Case.GENITIVE,
        'celownik': Case.DATIVE,
        'cel.': Case.DATIVE,
        'c': Case.DATIVE,
        'biernik': Case.ACCUSATIVE,
        'biern.': Case.ACCUSATIVE,
        'b': Case.ACCUSATIVE,
        'narzędnik': Case.INSTRUMENTAL,
        'narz.': Case.INSTRUMENTAL,
        'n': Case.INSTRUMENTAL,
        'miejscownik': Case.LOCATIVE,
        'miej.': Case.LOCATIVE,
        'ms': Case.LOCATIVE,
        'wołacz': Case.VOCATIVE,
        'woł.': Case.VOCATIVE,
        'w': Case.VOCATIVE,
    }

    # Number labels
    NUMBER_LABELS = {
        'liczba pojedyncza': Number.SINGULAR,
        'lp': Number.SINGULAR,
        'l.poj.': Number.SINGULAR,
        'pojedyncza': Number.SINGULAR,
        'liczba mnoga': Number.PLURAL,
        'lm': Number.PLURAL,
        'l.mn.': Number.PLURAL,
        'mnoga': Number.PLURAL,
    }

    # Person labels for verbs
    PERSON_LABELS = {
        '1. os.': Person.FIRST,
        '2. os.': Person.SECOND,
        '3. os.': Person.THIRD,
        '1 os.': Person.FIRST,
        '2 os.': Person.SECOND,
        '3 os.': Person.THIRD,
        'ja': Person.FIRST,
        'ty': Person.SECOND,
        'on/ona/ono': Person.THIRD,
    }

    # Gender labels
    GENDER_LABELS = {
        'rodzaj męski': Gender.MASCULINE,
        'męski': Gender.MASCULINE,
        'm.': Gender.MASCULINE,
        'rodzaj żeński': Gender.FEMININE,
        'żeński': Gender.FEMININE,
        'ż.': Gender.FEMININE,
        'rodzaj nijaki': Gender.NEUTER,
        'nijaki': Gender.NEUTER,
        'n.': Gender.NEUTER,
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def parse(
        self,
        raw_table: List[List[str]],
        word_class: str,
        lemma: str,
        aspect: Optional[str] = None,
        gender: Optional[str] = None,
        animacy: Optional[str] = None
    ) -> Optional[MorphologicalForms]:
        """
        Main entry point for parsing.

        Args:
            raw_table: 2D list of strings from HTML table
            word_class: Type of word ('noun', 'verb', 'adjective')
            lemma: Base form of the word
            aspect: (Optional) For verbs: 'imperfective', 'perfective', or 'biaspectual'
            gender: (Optional) For nouns/adjectives: 'masculine', 'feminine', or 'neuter'
            animacy: (Optional) For masculine nouns: 'personal', 'animate', or 'inanimate'

        Returns:
            Parsed morphological data or None if parsing fails

        Note:
            Aspect, gender, and animacy are lexical properties that should come from
            the word's headword information, not the conjugation/declension table.
            These are typically extracted from Wiktionary's headword templates.
        """
        if not raw_table or not lemma:
            return None

        try:
            if word_class.lower() in ['noun', 'rzeczownik']:
                return self._parse_noun_declension(raw_table, lemma, gender=gender, animacy=animacy)
            elif word_class.lower() in ['verb', 'czasownik']:
                return self._parse_verb_conjugation(raw_table, lemma, aspect=aspect)
            elif word_class.lower() in ['adjective', 'przymiotnik']:
                return self._parse_adjective_declension(raw_table, lemma)
            else:
                if self.verbose:
                    print(f"[MorphologyParser] Unknown word class: {word_class}")
                return None
        except Exception as e:
            if self.verbose:
                print(f"[MorphologyParser] Error parsing table: {e}")
            return None

    def _identify_table_structure(self, raw_table: List[List[str]]) -> Dict[str, Any]:
        """
        Identify the structure of the table (headers, dimensions, layout).

        Returns:
            Dict with keys:
                - header_rows: List of row indices that are headers
                - header_cols: List of column indices that are headers
                - dimensions: Dict mapping dimension names to their values
                - layout: 'case_rows' or 'case_cols' etc.
        """
        structure = {
            'header_rows': [],
            'header_cols': [],
            'dimensions': {},
            'layout': None
        }

        if not raw_table:
            return structure

        # Check first row for case labels (typical layout)
        first_row = [cell.lower().strip() for cell in raw_table[0]]
        has_case_in_first_row = any(
            label in first_row for label in self.CASE_LABELS.keys()
        )

        # Check first column for case labels
        first_col = [row[0].lower().strip() if row else '' for row in raw_table]
        has_case_in_first_col = any(
            label in first_col for label in self.CASE_LABELS.keys()
        )

        if has_case_in_first_row:
            structure['layout'] = 'case_cols'
            structure['header_rows'] = [0]
        elif has_case_in_first_col:
            structure['layout'] = 'case_rows'
            structure['header_cols'] = [0]

        return structure

    def _parse_noun_declension(
        self,
        raw_table: List[List[str]],
        lemma: str,
        gender: Optional[str] = None,
        animacy: Optional[str] = None
    ) -> Optional[NounDeclension]:
        """
        Parse a noun declension table.

        Typical layout:
        - Rows: cases (7)
        - Columns: number (singular/plural)

        Or:
        - Rows: cases
        - Columns: singular, plural (for different genders/animacies)
        """
        if self.verbose:
            print(f"[MorphologyParser] Parsing noun declension for '{lemma}'")

        structure = self._identify_table_structure(raw_table)

        # Parse gender and animacy if provided as strings
        gender_enum = None
        if gender:
            gender_lower = gender.lower()
            if gender_lower in ['masculine', 'męski', 'm']:
                gender_enum = Gender.MASCULINE
            elif gender_lower in ['feminine', 'żeński', 'ż']:
                gender_enum = Gender.FEMININE
            elif gender_lower in ['neuter', 'nijaki', 'n']:
                gender_enum = Gender.NEUTER

        animacy_enum = None
        if animacy:
            animacy_lower = animacy.lower()
            if animacy_lower in ['personal', 'osobowy', 'mos']:
                animacy_enum = Animacy.PERSONAL
            elif animacy_lower in ['animate', 'żywotny', 'mzw']:
                animacy_enum = Animacy.ANIMATE
            elif animacy_lower in ['inanimate', 'nieżywotny', 'mnzw']:
                animacy_enum = Animacy.INANIMATE

        # Initialize noun declension
        noun = NounDeclension(
            word_class=WordClass.NOUN,
            lemma=lemma,
            forms={
                'singular': {},
                'plural': {}
            },
            gender=gender_enum,
            animacy=animacy_enum
        )

        if self.verbose:
            print(f"[MorphologyParser] Table structure: {structure}")

        # Parse based on layout
        if structure['layout'] == 'case_rows':
            # Most common: cases in rows, numbers in columns
            self._parse_noun_case_rows(raw_table, noun)
        elif structure['layout'] == 'case_cols':
            # Less common: cases in columns, numbers in rows
            self._parse_noun_case_cols(raw_table, noun)
        else:
            if self.verbose:
                print("[MorphologyParser] Unknown layout, attempting heuristic parsing")
            # Try to parse with heuristics
            self._parse_noun_case_rows(raw_table, noun)

        return noun

    def _parse_noun_case_rows(self, raw_table: List[List[str]], noun: NounDeclension):
        """
        Parse noun table where cases are in rows.

        Expected format:
        Row 0: ['', 'liczba pojedyncza', 'liczba mnoga']  or  ['', 'lp', 'lm']
        Row 1: ['mianownik', 'dom', 'domy']
        Row 2: ['dopełniacz', 'domu', 'domów']
        ...
        """
        if len(raw_table) < 2:
            return

        # Find header row (usually first row)
        header_row = raw_table[0]

        # Identify which columns are singular and plural
        sing_col = None
        plur_col = None

        for col_idx, cell in enumerate(header_row):
            cell_lower = self._normalize_cell(cell).lower()

            # Check for singular markers
            if any(label in cell_lower for label in ['pojedyncza', 'lp', 'l.poj', 'singular']):
                sing_col = col_idx
                if self.verbose:
                    print(f"[MorphologyParser] Found singular column at index {col_idx}")

            # Check for plural markers
            if any(label in cell_lower for label in ['mnoga', 'lm', 'l.mn', 'plural']):
                plur_col = col_idx
                if self.verbose:
                    print(f"[MorphologyParser] Found plural column at index {col_idx}")

        # If not found in header, assume columns 1 and 2 (only if both are missing)
        # Don't assume singular if we already found plural in column 1
        if sing_col is None and plur_col is None and len(header_row) >= 2:
            sing_col = 1
            if self.verbose:
                print(f"[MorphologyParser] Assuming singular at column 1")
        if sing_col is None and plur_col is None and len(header_row) >= 3:
            plur_col = 2
            if self.verbose:
                print(f"[MorphologyParser] Assuming plural at column 2")
        # If we only found one of them, the other remains None
        elif sing_col is None and plur_col is not None and len(header_row) >= 3:
            # Found plural, assume singular is in a different column
            sing_col = 2 if plur_col == 1 else 1
            if self.verbose:
                print(f"[MorphologyParser] Found plural at {plur_col}, assuming singular at {sing_col}")
        elif plur_col is None and sing_col is not None and len(header_row) >= 3:
            # Found singular, assume plural is in a different column
            plur_col = 2 if sing_col == 1 else 1
            if self.verbose:
                print(f"[MorphologyParser] Found singular at {sing_col}, assuming plural at {plur_col}")

        # Parse data rows
        for row_idx in range(1, len(raw_table)):
            row = raw_table[row_idx]
            if len(row) < 2:
                continue

            # First cell should be case label
            case_label = self._normalize_cell(row[0]).lower().strip()

            # Try to match case - exact match first for abbreviations
            case = None

            # Try exact match first (for abbreviations like M, D, C, etc.)
            if case_label in self.CASE_LABELS:
                case = self.CASE_LABELS[case_label]
            else:
                # Try substring match for full words
                for label, case_enum in self.CASE_LABELS.items():
                    if len(label) > 2:  # Only do substring matching for full words
                        if label in case_label or case_label in label:
                            case = case_enum
                            break

            if case is None:
                if self.verbose:
                    print(f"[MorphologyParser] Could not identify case for '{case_label}'")
                continue

            case_name = case.value  # e.g., 'nominative'

            if self.verbose:
                print(f"[MorphologyParser] Row {row_idx}: {case_name}")

            # Extract singular form
            if sing_col is not None and sing_col < len(row):
                sing_form = self._normalize_cell(row[sing_col])
                if sing_form and sing_form != '-' and sing_form != '—':
                    noun.forms['singular'][case_name] = sing_form
                    if self.verbose:
                        print(f"[MorphologyParser]   singular: {sing_form}")

            # Extract plural form
            if plur_col is not None and plur_col < len(row):
                plur_form = self._normalize_cell(row[plur_col])
                if plur_form and plur_form != '-' and plur_form != '—':
                    noun.forms['plural'][case_name] = plur_form
                    if self.verbose:
                        print(f"[MorphologyParser]   plural: {plur_form}")

    def _parse_noun_case_cols(self, raw_table: List[List[str]], noun: NounDeclension):
        """
        Parse noun table where cases are in columns (less common).
        """
        # TODO: Implement if we encounter this layout
        if self.verbose:
            print("[MorphologyParser] case_cols layout not yet implemented")
        pass

    def _parse_verb_conjugation(
        self,
        raw_table: List[List[str]],
        lemma: str,
        aspect: Optional[str] = None
    ) -> Optional[VerbConjugation]:
        """
        Parse a verb conjugation table.

        Typical layouts vary widely for verbs:
        - Present tense: rows=person, cols=number
        - Past tense: rows=person/gender, cols=number
        - Multiple tables for different tenses/moods
        """
        if self.verbose:
            print(f"[MorphologyParser] Parsing verb conjugation for '{lemma}'")

        structure = self._identify_table_structure(raw_table)

        # Parse aspect if provided as string
        aspect_enum = None
        if aspect:
            aspect_lower = aspect.lower()
            if aspect_lower in ['imperfective', 'niedokonany', 'ndk', 'impf']:
                aspect_enum = Aspect.IMPERFECTIVE
            elif aspect_lower in ['perfective', 'dokonany', 'dk', 'pf']:
                aspect_enum = Aspect.PERFECTIVE
            elif aspect_lower in ['biaspectual', 'dwuaspektowy']:
                aspect_enum = Aspect.BIASPECTUAL

        # Initialize verb conjugation
        verb = VerbConjugation(
            word_class=WordClass.VERB,
            lemma=lemma,
            forms={},
            aspect=aspect_enum
        )

        if self.verbose:
            print(f"[MorphologyParser] Table structure: {structure}")

        # Try to parse as person-rows layout (most common)
        self._parse_verb_person_rows(raw_table, verb)

        return verb

    def _parse_verb_person_rows(self, raw_table: List[List[str]], verb: VerbConjugation):
        """
        Parse verb table - handles both simple and complex Wiktionary formats.

        Real Wiktionary format (być):
        Row 0: ['forma', 'liczba pojedyncza', 'liczba mnoga']
        Row 1: ['1. os.', '2. os.', '3. os.', '1. os.', '2. os.', '3. os.']
        Row 2: ['bezokolicznik', 'być']
        Row 3: ['czas teraźniejszy', 'jestem', 'jesteś', 'jest', 'jesteśmy', 'jesteście', 'są']
        Row 4: ['czas przeszły', 'm', 'byłem', 'byłeś', 'był', 'byliśmy', 'byliście', 'byli']
        Row 5: ['', 'ż', 'byłam', 'byłaś', 'była', 'byłyśmy', 'byłyście', 'były']

        Columns 1-3: singular (1st, 2nd, 3rd person)
        Columns 4-6: plural (1st, 2nd, 3rd person)
        """
        if len(raw_table) < 2:
            return

        # Check if this is the complex Wiktionary format
        if len(raw_table) > 1 and len(raw_table[0]) >= 2:
            first_cell = self._normalize_cell(raw_table[0][0]).lower()
            if 'forma' in first_cell or 'bezokolicznik' in first_cell:
                # This is the complex Wiktionary format
                self._parse_verb_complex_format(raw_table, verb)
                return

        # Fall back to simple format (my test cases)
        self._parse_verb_simple_format(raw_table, verb)

    def _parse_verb_complex_format(self, raw_table: List[List[str]], verb: VerbConjugation):
        """Parse the complex Wiktionary verb table format"""

        # Columns: 0=form name, 1-3=singular (1,2,3 person), 4-6=plural (1,2,3 person)
        sing_cols = [1, 2, 3]
        plur_cols = [4, 5, 6]

        current_tense = None
        current_gender = None

        for row_idx, row in enumerate(raw_table):
            if len(row) < 2:
                continue

            first_cell = self._normalize_cell(row[0]).lower().strip()

            # Skip header rows
            if 'forma' in first_cell or first_cell.startswith('1.') or first_cell.startswith('pozostał'):
                continue

            # Check for tense/mood markers
            if 'teraźniejsz' in first_cell or 'present' in first_cell:
                current_tense = 'present'
                current_gender = None
            elif 'przeszł' in first_cell or 'past' in first_cell:
                current_tense = 'past'
                current_gender = None  # Will be set by gender marker
            elif 'przyszł' in first_cell or 'future' in first_cell:
                current_tense = 'future'
                current_gender = None
            elif 'rozkazuj' in first_cell or 'imperative' in first_cell:
                current_tense = 'imperative'
                current_gender = None
            elif 'przypuszcz' in first_cell or 'conditional' in first_cell:
                current_tense = 'conditional'
                current_gender = None
            elif 'bezokolicznik' in first_cell or 'infinitive' in first_cell:
                # Extract infinitive
                if len(row) > 1:
                    verb.forms['infinitive'] = self._normalize_cell(row[1])
                continue

            # Check for gender marker (single letter in first or second column)
            if len(row) > 1:
                second_cell = self._normalize_cell(row[1]).lower().strip()
                # If first cell is empty and second is a gender, it's a gender row
                if not first_cell or first_cell == '':
                    if second_cell in ['m', 'm.', 'męski']:
                        current_gender = 'masculine'
                        first_cell_idx = 2  # Forms start from column 2
                    elif second_cell in ['ż', 'ż.', 'żeński']:
                        current_gender = 'feminine'
                        first_cell_idx = 2
                    elif second_cell in ['n', 'n.', 'nijaki']:
                        current_gender = 'neuter'
                        first_cell_idx = 2
                    else:
                        continue
                # Or if tense name is in first cell and gender in second
                elif second_cell in ['m', 'm.', 'męski', 'ż', 'ż.', 'żeński', 'n', 'n.', 'nijaki']:
                    if second_cell in ['m', 'm.', 'męski']:
                        current_gender = 'masculine'
                    elif second_cell in ['ż', 'ż.', 'żeński']:
                        current_gender = 'feminine'
                    elif second_cell in ['n', 'n.', 'nijaki']:
                        current_gender = 'neuter'
                    first_cell_idx = 2  # Forms start from column 2
                else:
                    first_cell_idx = 1  # No gender, forms start from column 1
            else:
                first_cell_idx = 1

            if current_tense is None:
                continue

            # Initialize structure
            if current_tense not in verb.forms:
                verb.forms[current_tense] = {}

            # Extract forms
            if current_gender:
                # Past/conditional tense with gender
                if current_gender not in verb.forms[current_tense]:
                    verb.forms[current_tense][current_gender] = {
                        'singular': {},
                        'plural': {}
                    }

                # Extract singular forms (persons 1, 2, 3)
                for i, col_idx in enumerate([first_cell_idx, first_cell_idx + 1, first_cell_idx + 2]):
                    if col_idx < len(row):
                        form = self._normalize_cell(row[col_idx])
                        # Clean up alternative forms like "jestem / -(e)m"
                        if '/' in form:
                            form = form.split('/')[0].strip()
                        if form and form not in ['-', '—', '']:
                            verb.forms[current_tense][current_gender]['singular'][str(i + 1)] = form
                            if self.verbose:
                                print(f"[MorphologyParser]   {current_tense}/{current_gender}/singular/{i+1}: {form}")

                # Extract plural forms (persons 1, 2, 3)
                for i, col_idx in enumerate([first_cell_idx + 3, first_cell_idx + 4, first_cell_idx + 5]):
                    if col_idx < len(row):
                        form = self._normalize_cell(row[col_idx])
                        if '/' in form:
                            form = form.split('/')[0].strip()
                        if form and form not in ['-', '—', '']:
                            verb.forms[current_tense][current_gender]['plural'][str(i + 1)] = form
                            if self.verbose:
                                print(f"[MorphologyParser]   {current_tense}/{current_gender}/plural/{i+1}: {form}")
            else:
                # Present/future/imperative (no gender)
                if 'singular' not in verb.forms[current_tense]:
                    verb.forms[current_tense]['singular'] = {}
                if 'plural' not in verb.forms[current_tense]:
                    verb.forms[current_tense]['plural'] = {}

                # Extract singular forms
                for i, col_idx in enumerate([first_cell_idx, first_cell_idx + 1, first_cell_idx + 2]):
                    if col_idx < len(row):
                        form = self._normalize_cell(row[col_idx])
                        if '/' in form:
                            form = form.split('/')[0].strip()
                        if form and form not in ['-', '—', '']:
                            verb.forms[current_tense]['singular'][str(i + 1)] = form
                            if self.verbose:
                                print(f"[MorphologyParser]   {current_tense}/singular/{i+1}: {form}")

                # Extract plural forms
                for i, col_idx in enumerate([first_cell_idx + 3, first_cell_idx + 4, first_cell_idx + 5]):
                    if col_idx < len(row):
                        form = self._normalize_cell(row[col_idx])
                        if '/' in form:
                            form = form.split('/')[0].strip()
                        if form and form not in ['-', '—', '']:
                            verb.forms[current_tense]['plural'][str(i + 1)] = form
                            if self.verbose:
                                print(f"[MorphologyParser]   {current_tense}/plural/{i+1}: {form}")

    def _parse_verb_simple_format(self, raw_table: List[List[str]], verb: VerbConjugation):
        """
        Parse simple verb table format (from test cases).

        Simple format:
        Row 0: ['', 'liczba pojedyncza', 'liczba mnoga']
        Row 1: ['1. os.', 'jestem', 'jesteśmy']
        Row 2: ['2. os.', 'jesteś', 'jesteście']
        Row 3: ['3. os.', 'jest', 'są']

        For past tense with genders:
        Row 1: ['1. os. m.', 'byłem', 'byliśmy']
        """
        if len(raw_table) < 2:
            return

        # Determine tense and gender from person labels
        # Default is present tense
        current_tense = 'present'
        current_gender = None

        # Check first data row for gender markers or tense info
        if len(raw_table) > 1:
            first_label = self._normalize_cell(raw_table[1][0]).lower()
            if 'm.' in first_label or first_label.endswith('m'):
                current_gender = 'masculine'
                current_tense = 'past'  # Past tense typically has gender
            elif 'ż.' in first_label or first_label.endswith('ż'):
                current_gender = 'feminine'
                current_tense = 'past'
            elif 'n.' in first_label or first_label.endswith('n'):
                current_gender = 'neuter'
                current_tense = 'past'

        for row_idx, row in enumerate(raw_table):
            if row_idx == 0:  # Skip header row
                continue

            if len(row) < 3:
                continue

            label = self._normalize_cell(row[0]).lower().strip()

            if not label:
                continue

            # Update gender if it changes within the table
            if 'ż.' in label or label.endswith('ż'):
                current_gender = 'feminine'
            elif 'n.' in label or label.endswith('n'):
                current_gender = 'neuter'
            elif 'm.' in label or label.endswith('m'):
                current_gender = 'masculine'

            # Extract person number
            person = None
            if '1' in label or label.startswith('1'):
                person = '1'
            elif '2' in label or label.startswith('2'):
                person = '2'
            elif '3' in label or label.startswith('3'):
                person = '3'

            if person is None:
                continue

            # Extract forms
            singular_form = self._normalize_cell(row[1]) if len(row) > 1 else None
            plural_form = self._normalize_cell(row[2]) if len(row) > 2 else None

            # Build the nested structure
            if current_tense not in verb.forms:
                verb.forms[current_tense] = {}

            if current_gender:
                # Gendered tense (past, conditional)
                if current_gender not in verb.forms[current_tense]:
                    verb.forms[current_tense][current_gender] = {}

                if singular_form and singular_form != '—':
                    if 'singular' not in verb.forms[current_tense][current_gender]:
                        verb.forms[current_tense][current_gender]['singular'] = {}
                    verb.forms[current_tense][current_gender]['singular'][person] = singular_form

                if plural_form and plural_form != '—':
                    if 'plural' not in verb.forms[current_tense][current_gender]:
                        verb.forms[current_tense][current_gender]['plural'] = {}
                    verb.forms[current_tense][current_gender]['plural'][person] = plural_form
            else:
                # Non-gendered tense (present, future, imperative)
                if singular_form and singular_form != '—':
                    if 'singular' not in verb.forms[current_tense]:
                        verb.forms[current_tense]['singular'] = {}
                    verb.forms[current_tense]['singular'][person] = singular_form

                if plural_form and plural_form != '—':
                    if 'plural' not in verb.forms[current_tense]:
                        verb.forms[current_tense]['plural'] = {}
                    verb.forms[current_tense]['plural'][person] = plural_form

            if self.verbose:
                if current_gender:
                    if singular_form:
                        print(f"[MorphologyParser]   {current_tense}/{current_gender}/singular/{person}: {singular_form}")
                    if plural_form:
                        print(f"[MorphologyParser]   {current_tense}/{current_gender}/plural/{person}: {plural_form}")
                else:
                    if singular_form:
                        print(f"[MorphologyParser]   {current_tense}/singular/{person}: {singular_form}")
                    if plural_form:
                        print(f"[MorphologyParser]   {current_tense}/plural/{person}: {plural_form}")

    def _parse_adjective_declension(self, raw_table: List[List[str]], lemma: str) -> Optional[AdjectiveDeclension]:
        """
        Parse an adjective declension table.

        Adjectives decline like nouns but with additional complexity:
        - Must agree with noun in case, number, gender, animacy
        - Separate forms for masculine personal plural (virile)
        - May have comparative and superlative forms

        Table structure:
        Row 0: ['przypadek', 'liczba pojedyncza', 'liczba mnoga']
        Row 1: ['mos/mzw', 'mrz', 'ż', 'n', 'mos', 'nmos']  # gender/animacy headers
        Rows 2+: case rows with forms

        May have degree markers like:
        - 'stopień wyższy lepszy' (comparative)
        - 'stopień najwyższy najlepszy' (superlative)
        """
        if self.verbose:
            print(f"[MorphologyParser] Parsing adjective declension for '{lemma}'")

        # Initialize adjective declension
        adjective = AdjectiveDeclension(
            word_class=WordClass.ADJECTIVE,
            lemma=lemma,
            forms={
                'positive': {},
                'comparative': {},
                'superlative': {}
            }
        )

        if len(raw_table) < 3:
            return adjective

        # Parse the table by sections (positive, comparative, superlative)
        sections = self._split_adjective_table_by_degree(raw_table)

        for degree, section_rows in sections.items():
            if section_rows:
                degree_forms = self._parse_adjective_degree_section(section_rows)
                adjective.forms[degree] = degree_forms
                if self.verbose:
                    print(f"[MorphologyParser] Parsed {degree} degree with {len(degree_forms)} entries")

        return adjective

    def _split_adjective_table_by_degree(self, raw_table: List[List[str]]) -> Dict[str, List[List[str]]]:
        """
        Split adjective table into sections by comparison degree.

        Returns dict with keys 'positive', 'comparative', 'superlative'
        """
        sections = {
            'positive': [],
            'comparative': [],
            'superlative': []
        }

        current_degree = 'positive'
        skip_next = False  # Skip header rows after degree markers

        for idx, row in enumerate(raw_table):
            if not row:
                continue

            # Check for degree markers
            first_cell = self._normalize_cell(row[0]).lower()

            # Detect degree markers
            if 'stopień wyższy' in first_cell or 'stopień wyższ' in first_cell:
                current_degree = 'comparative'
                skip_next = True  # Skip the next header row
                continue
            elif 'stopień najwyższy' in first_cell or 'stopień najwyższ' in first_cell:
                current_degree = 'superlative'
                skip_next = True
                continue

            # Skip header row after degree marker
            if skip_next and 'przypadek' in first_cell:
                skip_next = False
                continue

            sections[current_degree].append(row)

        return sections

    def _parse_adjective_degree_section(self, section_rows: List[List[str]]) -> Dict:
        """
        Parse one degree section of adjective declension.

        Due to HTML colspan merging, different cases have different column counts.
        We extract forms simply by case without trying to precisely map all
        gender/animacy combinations (which vary due to merged cells).

        Returns dict mapping case to list of forms:
        {
            'nominative': ['dobry', 'dobra', 'dobre', 'dobrzy', 'dobre'],
            'genitive': ['dobrego', 'dobrej', 'dobrego', 'dobrych'],
            ...
        }
        """
        if len(section_rows) < 3:
            return {}

        result = {}

        # Parse case rows (starting from row 2, skipping headers)
        for row_idx in range(2, len(section_rows)):
            row = section_rows[row_idx]
            if len(row) < 2:
                continue

            # First cell is case name
            case_label = self._normalize_cell(row[0]).lower().strip()

            # Match case
            case = None
            if case_label in self.CASE_LABELS:
                case = self.CASE_LABELS[case_label]
            else:
                for label, case_enum in self.CASE_LABELS.items():
                    if len(label) > 2 and (label in case_label or case_label in label):
                        case = case_enum
                        break

            if case is None:
                continue

            case_name = case.value

            # Extract all forms for this case (columns 1 onward)
            forms = []
            for col_idx in range(1, len(row)):
                form = self._normalize_cell(row[col_idx])
                if form and form not in ['-', '—', '']:
                    forms.append(form)

            if forms:
                result[case_name] = forms

        return result

    def _parse_adjective_headers(self, header_row: List[str]) -> Dict[int, tuple]:
        """
        Parse adjective gender/animacy header row.

        The header row doesn't include the case label column, so:
        header_row[0] maps to data_row[1], header_row[1] maps to data_row[2], etc.

        Returns dict mapping data column index to (number, gender_animacy) tuple.
        Example: {1: ('singular', 'masculine_personal'), ...}
        """
        column_map = {}

        if len(header_row) < 1:
            return column_map

        # Common patterns in adjective tables
        # Singular: mos/mzw, mrz, ż, n (columns 1-4)
        # Plural: mos, nmos (columns 5-6 or later)

        for header_idx in range(len(header_row)):
            cell = self._normalize_cell(header_row[header_idx]).lower().strip()

            # Data column index is header_idx + 1 (because data rows have case label in column 0)
            data_col_idx = header_idx + 1

            # Singular forms
            if cell in ['mos/mzw', 'mos / mzw', 'm os/zw', 'mos / mzw']:
                column_map[data_col_idx] = ('singular', 'masculine_personal')
            elif cell in ['mrz', 'm rz', 'm.rz.', 'masculine_inanimate']:
                column_map[data_col_idx] = ('singular', 'masculine_inanimate')
            elif cell in ['ż', 'ż.', 'feminine']:
                column_map[data_col_idx] = ('singular', 'feminine')
            elif cell in ['n', 'n.', 'neuter']:
                column_map[data_col_idx] = ('singular', 'neuter')
            # Plural forms
            elif cell in ['mos', 'm os', 'm.os.', 'masculine_personal']:
                column_map[data_col_idx] = ('plural', 'masculine_personal')
            elif cell in ['nmos', 'nie-mos', 'niemęskoosobowy', 'nonmasculine']:
                column_map[data_col_idx] = ('plural', 'nonmasculine_personal')

        return column_map

    def _normalize_cell(self, cell: str) -> str:
        """Normalize a table cell value"""
        return cell.strip().replace('\u00a0', ' ')  # Replace non-breaking spaces

    def _is_header_cell(self, cell: str) -> bool:
        """Check if a cell is likely a header"""
        cell_lower = cell.lower().strip()

        # Check if it matches known labels
        if cell_lower in self.CASE_LABELS:
            return True
        if cell_lower in self.NUMBER_LABELS:
            return True
        if cell_lower in self.PERSON_LABELS:
            return True
        if cell_lower in self.GENDER_LABELS:
            return True

        return False
