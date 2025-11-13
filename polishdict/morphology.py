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
        'M': Case.NOMINATIVE,
        'dopełniacz': Case.GENITIVE,
        'dop.': Case.GENITIVE,
        'D': Case.GENITIVE,
        'celownik': Case.DATIVE,
        'cel.': Case.DATIVE,
        'C': Case.DATIVE,
        'biernik': Case.ACCUSATIVE,
        'biern.': Case.ACCUSATIVE,
        'B': Case.ACCUSATIVE,
        'narzędnik': Case.INSTRUMENTAL,
        'narz.': Case.INSTRUMENTAL,
        'N': Case.INSTRUMENTAL,
        'miejscownik': Case.LOCATIVE,
        'miej.': Case.LOCATIVE,
        'Ms': Case.LOCATIVE,
        'wołacz': Case.VOCATIVE,
        'woł.': Case.VOCATIVE,
        'W': Case.VOCATIVE,
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

        # TODO: Implement actual parsing logic
        # This is a placeholder - we'll implement the full logic in the next iteration

        if self.verbose:
            print(f"[MorphologyParser] Table structure: {structure}")

        return noun

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

        # TODO: Implement actual parsing logic

        if self.verbose:
            print(f"[MorphologyParser] Table structure: {structure}")

        return verb

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
