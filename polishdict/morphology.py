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

    def parse(self, raw_table: List[List[str]], word_class: str, lemma: str) -> Optional[MorphologicalForms]:
        """
        Main entry point for parsing.

        Args:
            raw_table: 2D list of strings from HTML table
            word_class: Type of word ('noun', 'verb', 'adjective')
            lemma: Base form of the word

        Returns:
            Parsed morphological data or None if parsing fails
        """
        if not raw_table or not lemma:
            return None

        try:
            if word_class.lower() in ['noun', 'rzeczownik']:
                return self._parse_noun_declension(raw_table, lemma)
            elif word_class.lower() in ['verb', 'czasownik']:
                return self._parse_verb_conjugation(raw_table, lemma)
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

    def _parse_noun_declension(self, raw_table: List[List[str]], lemma: str) -> Optional[NounDeclension]:
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

        # Initialize noun declension
        noun = NounDeclension(
            word_class=WordClass.NOUN,
            lemma=lemma,
            forms={
                'singular': {},
                'plural': {}
            }
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

        # If not found in header, assume columns 1 and 2
        if sing_col is None and len(header_row) >= 2:
            sing_col = 1
            if self.verbose:
                print(f"[MorphologyParser] Assuming singular at column 1")
        if plur_col is None and len(header_row) >= 3:
            plur_col = 2
            if self.verbose:
                print(f"[MorphologyParser] Assuming plural at column 2")

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

    def _parse_verb_conjugation(self, raw_table: List[List[str]], lemma: str) -> Optional[VerbConjugation]:
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

        # Initialize verb conjugation
        verb = VerbConjugation(
            word_class=WordClass.VERB,
            lemma=lemma,
            forms={}
        )

        if self.verbose:
            print(f"[MorphologyParser] Table structure: {structure}")

        # Try to parse as person-rows layout (most common)
        self._parse_verb_person_rows(raw_table, verb)

        return verb

    def _parse_verb_person_rows(self, raw_table: List[List[str]], verb: VerbConjugation):
        """
        Parse verb table where persons are in rows.

        Expected formats:

        Simple (present tense):
        Row 0: ['', 'lp', 'lm']
        Row 1: ['1. os.', 'jestem', 'jesteśmy']
        Row 2: ['2. os.', 'jesteś', 'jesteście']
        Row 3: ['3. os.', 'jest', 'są']

        Complex (past tense with gender):
        Row 0: ['', 'lp', 'lm']
        Row 1: ['1. os. m.', 'byłem', 'byliśmy']
        Row 2: ['2. os. m.', 'byłeś', 'byliście']
        ...
        """
        if len(raw_table) < 2:
            return

        # Find header row
        header_row = raw_table[0]

        # Identify which columns are singular and plural
        sing_col = None
        plur_col = None

        for col_idx, cell in enumerate(header_row):
            cell_lower = self._normalize_cell(cell).lower()

            if any(label in cell_lower for label in ['pojedyncza', 'lp', 'l.poj', 'singular']):
                sing_col = col_idx
                if self.verbose:
                    print(f"[MorphologyParser] Found singular column at index {col_idx}")

            if any(label in cell_lower for label in ['mnoga', 'lm', 'l.mn', 'plural']):
                plur_col = col_idx
                if self.verbose:
                    print(f"[MorphologyParser] Found plural column at index {col_idx}")

        # If not found in header, assume columns 1 and 2
        if sing_col is None and len(header_row) >= 2:
            sing_col = 1
        if plur_col is None and len(header_row) >= 3:
            plur_col = 2

        # Parse data rows
        for row_idx in range(1, len(raw_table)):
            row = raw_table[row_idx]
            if len(row) < 2:
                continue

            # First cell contains person (and possibly gender)
            person_label = self._normalize_cell(row[0]).lower().strip()

            # Try to extract person
            person = None
            for label, person_enum in self.PERSON_LABELS.items():
                if label.lower() in person_label:
                    person = person_enum
                    break

            if person is None:
                if self.verbose:
                    print(f"[MorphologyParser] Could not identify person for '{person_label}'")
                continue

            # Try to extract gender (for past tense)
            gender = None
            for label, gender_enum in self.GENDER_LABELS.items():
                if label.lower() in person_label:
                    gender = gender_enum
                    break

            if self.verbose:
                print(f"[MorphologyParser] Row {row_idx}: person={person.value}, gender={gender.value if gender else None}")

            # Determine tense based on presence of gender
            # (This is a heuristic - ideally we'd get tense from context/metadata)
            tense = 'past' if gender else 'present'

            # Initialize nested structure if needed
            if tense not in verb.forms:
                verb.forms[tense] = {}

            # For past tense, organize by gender first
            if gender:
                gender_key = gender.value
                if gender_key not in verb.forms[tense]:
                    verb.forms[tense][gender_key] = {
                        'singular': {},
                        'plural': {}
                    }

                # Extract singular form
                if sing_col is not None and sing_col < len(row):
                    sing_form = self._normalize_cell(row[sing_col])
                    if sing_form and sing_form != '-' and sing_form != '—':
                        verb.forms[tense][gender_key]['singular'][person.value] = sing_form
                        if self.verbose:
                            print(f"[MorphologyParser]   {tense}/{gender_key}/singular/{person.value}: {sing_form}")

                # Extract plural form
                if plur_col is not None and plur_col < len(row):
                    plur_form = self._normalize_cell(row[plur_col])
                    if plur_form and plur_form != '-' and plur_form != '—':
                        verb.forms[tense][gender_key]['plural'][person.value] = plur_form
                        if self.verbose:
                            print(f"[MorphologyParser]   {tense}/{gender_key}/plural/{person.value}: {plur_form}")

            else:
                # Present tense (no gender)
                if 'singular' not in verb.forms[tense]:
                    verb.forms[tense]['singular'] = {}
                if 'plural' not in verb.forms[tense]:
                    verb.forms[tense]['plural'] = {}

                # Extract singular form
                if sing_col is not None and sing_col < len(row):
                    sing_form = self._normalize_cell(row[sing_col])
                    if sing_form and sing_form != '-' and sing_form != '—':
                        verb.forms[tense]['singular'][person.value] = sing_form
                        if self.verbose:
                            print(f"[MorphologyParser]   {tense}/singular/{person.value}: {sing_form}")

                # Extract plural form
                if plur_col is not None and plur_col < len(row):
                    plur_form = self._normalize_cell(row[plur_col])
                    if plur_form and plur_form != '-' and plur_form != '—':
                        verb.forms[tense]['plural'][person.value] = plur_form
                        if self.verbose:
                            print(f"[MorphologyParser]   {tense}/plural/{person.value}: {plur_form}")

    def _parse_adjective_declension(self, raw_table: List[List[str]], lemma: str) -> Optional[AdjectiveDeclension]:
        """
        Parse an adjective declension table.

        Adjectives decline like nouns but with additional complexity:
        - Must agree with noun in case, number, gender, animacy
        - Separate forms for masculine personal plural (virile)
        - May have comparative and superlative forms
        """
        if self.verbose:
            print(f"[MorphologyParser] Parsing adjective declension for '{lemma}'")

        structure = self._identify_table_structure(raw_table)

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

        # TODO: Implement actual parsing logic

        if self.verbose:
            print(f"[MorphologyParser] Table structure: {structure}")

        return adjective

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
