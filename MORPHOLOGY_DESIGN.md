# Design Proposal: Structured Morphological Data Format

## Overview
Design a flexible, hierarchical data structure for representing Polish morphological forms (conjugations and declensions) that can handle the complexity of the language while remaining extensible for edge cases.

## Current State
- Tables are parsed as flat 2D arrays: `List[List[str]]`
- No semantic structure or meaning attached to forms
- Difficult to query specific forms programmatically

## Requirements

### Verb Conjugations
Must handle:
- **Aspect**: imperfective, perfective (often separate lemmas)
- **Tense**: present, past, future
- **Mood**: indicative, conditional, imperative
- **Person**: 1st, 2nd, 3rd, impersonal
- **Number**: singular, plural
- **Gender** (past tense only): masculine, feminine, neuter
- **Special forms**: infinitive, participles (active, passive, adjectival), gerunds

### Noun Declensions
Must handle:
- **Number**: singular, plural
- **Case**: nominative, genitive, dative, accusative, instrumental, locative, vocative (7 cases)
- **Gender**: masculine, feminine, neuter
- **Animacy** (masculine only): personal (virile), animate, inanimate
- **Special cases**: plurale tantum, singulare tantum

### Adjective Declensions
Must handle:
- **Number**: singular, plural
- **Case**: all 7 cases
- **Gender**: masculine (personal/animate/inanimate), feminine, neuter
- **Comparison**: positive, comparative, superlative

## Proposed Data Structure

### Design Principles
1. **Hierarchical**: Nest dimensions in order of linguistic importance
2. **Flexible**: Use optional fields for missing/inapplicable dimensions
3. **Queryable**: Allow easy programmatic access to specific forms
4. **Extensible**: Easy to add new dimensions or special cases
5. **JSON-compatible**: Must serialize cleanly to JSON

### Core Schema

```python
{
    'word_class': str,  # 'verb', 'noun', 'adjective', 'pronoun', etc.
    'lemma': str,  # Base form
    'aspect': Optional[str],  # For verbs: 'imperfective', 'perfective'
    'gender': Optional[str],  # For nouns/adjectives: 'masculine', 'feminine', 'neuter'
    'animacy': Optional[str],  # For masculine nouns: 'personal', 'animate', 'inanimate'
    'forms': dict,  # Hierarchical structure of inflected forms
    'metadata': dict  # Additional info (tantum forms, irregularities, etc.)
}
```

### Example: Verb Conjugation (być - to be, imperfective)

```python
{
    'word_class': 'verb',
    'lemma': 'być',
    'aspect': 'imperfective',
    'forms': {
        'infinitive': 'być',
        'present': {
            'singular': {
                '1': 'jestem',
                '2': 'jesteś',
                '3': 'jest'
            },
            'plural': {
                '1': 'jesteśmy',
                '2': 'jesteście',
                '3': 'są'
            }
        },
        'past': {
            'masculine': {
                'singular': {
                    '1': 'byłem',
                    '2': 'byłeś',
                    '3': 'był'
                },
                'plural': {
                    '1': 'byliśmy',  # personal
                    '2': 'byliście',  # personal
                    '3': 'byli'  # personal
                }
            },
            'feminine': {
                'singular': {
                    '1': 'byłam',
                    '2': 'byłaś',
                    '3': 'była'
                },
                'plural': {
                    '1': 'byłyśmy',
                    '2': 'byłyście',
                    '3': 'były'
                }
            },
            'neuter': {
                'singular': {
                    '3': 'było'  # Only 3rd person for neuter
                },
                'plural': {
                    '3': 'były'
                }
            }
        },
        'future': {
            'singular': {
                '1': 'będę',
                '2': 'będziesz',
                '3': 'będzie'
            },
            'plural': {
                '1': 'będziemy',
                '2': 'będziecie',
                '3': 'będą'
            }
        },
        'conditional': {
            'masculine': {
                'singular': {
                    '1': 'byłbym',
                    '2': 'byłbyś',
                    '3': 'byłby'
                },
                # ... similar structure to past tense
            }
        },
        'imperative': {
            'singular': {
                '2': 'bądź'
            },
            'plural': {
                '1': 'bądźmy',
                '2': 'bądźcie'
            }
        },
        'participles': {
            'active_adjectival': {
                # Can be further nested by case/gender if needed
                'nominative': {
                    'masculine': 'będący',
                    'feminine': 'będąca',
                    'neuter': 'będące'
                }
            },
            'passive_adjectival': None  # Not applicable for być
        },
        'gerund': {
            'present': 'będąc',
            'past': None
        }
    },
    'metadata': {
        'irregular': True,
        'notes': 'Highly irregular verb'
    }
}
```

### Example: Noun Declension (pies - dog, masculine animate)

```python
{
    'word_class': 'noun',
    'lemma': 'pies',
    'gender': 'masculine',
    'animacy': 'animate',
    'forms': {
        'singular': {
            'nominative': 'pies',
            'genitive': 'psa',
            'dative': 'psu',
            'accusative': 'psa',
            'instrumental': 'psem',
            'locative': 'psie',
            'vocative': 'psie'
        },
        'plural': {
            'nominative': 'psy',
            'genitive': 'psów',
            'dative': 'psom',
            'accusative': 'psy',
            'instrumental': 'psami',
            'locative': 'psach',
            'vocative': 'psy'
        }
    },
    'metadata': {}
}
```

### Example: Noun Declension (człowiek - person, masculine personal)

Note: Personal masculine has different plural forms

```python
{
    'word_class': 'noun',
    'lemma': 'człowiek',
    'gender': 'masculine',
    'animacy': 'personal',
    'forms': {
        'singular': {
            'nominative': 'człowiek',
            'genitive': 'człowieka',
            'dative': 'człowiekowi',
            'accusative': 'człowieka',
            'instrumental': 'człowiekiem',
            'locative': 'człowieku',
            'vocative': 'człowieku'
        },
        'plural': {
            'nominative': 'ludzie',  # Suppletive form!
            'genitive': 'ludzi',
            'dative': 'ludziom',
            'accusative': 'ludzi',
            'instrumental': 'ludźmi',
            'locative': 'ludziach',
            'vocative': 'ludzie'
        }
    },
    'metadata': {
        'irregular': True,
        'notes': 'Suppletive plural forms (człowiek → ludzie)'
    }
}
```

### Example: Adjective Declension (dobry - good)

```python
{
    'word_class': 'adjective',
    'lemma': 'dobry',
    'forms': {
        'positive': {
            'singular': {
                'masculine': {
                    'personal': {  # For agreement with masculine personal nouns
                        'nominative': 'dobry',
                        'genitive': 'dobrego',
                        # ... other cases
                    },
                    'animate': {
                        'nominative': 'dobry',
                        'genitive': 'dobrego',
                        # ... other cases
                    },
                    'inanimate': {
                        'nominative': 'dobry',
                        'accusative': 'dobry',  # Different from animate/personal
                        # ... other cases
                    }
                },
                'feminine': {
                    'nominative': 'dobra',
                    'genitive': 'dobrej',
                    # ... other cases
                },
                'neuter': {
                    'nominative': 'dobre',
                    'genitive': 'dobrego',
                    # ... other cases
                }
            },
            'plural': {
                'personal': {  # Masculine personal plural (virile)
                    'nominative': 'dobrzy',
                    'genitive': 'dobrych',
                    # ... other cases
                },
                'nonpersonal': {  # All other plurals
                    'nominative': 'dobre',
                    'genitive': 'dobrych',
                    # ... other cases
                }
            }
        },
        'comparative': {
            # Similar structure but with forms like 'lepszy', 'lepsza', 'lepsze'
            # ... (simplified for brevity)
        },
        'superlative': {
            # Forms like 'najlepszy', 'najlepsza', 'najlepsze'
            # ... (simplified for brevity)
        }
    },
    'metadata': {
        'comparison': 'irregular',  # dobry → lepszy (not dobrszy)
        'notes': 'Irregular comparative/superlative'
    }
}
```

## Alternative: Flat Structure with Keys

For simpler querying, we could use a flat structure with composite keys:

```python
{
    'word_class': 'verb',
    'lemma': 'być',
    'aspect': 'imperfective',
    'forms': {
        'infinitive': 'być',
        'present_1_sg': 'jestem',
        'present_2_sg': 'jesteś',
        'present_3_sg': 'jest',
        'present_1_pl': 'jesteśmy',
        'present_2_pl': 'jesteście',
        'present_3_pl': 'są',
        'past_masc_1_sg': 'byłem',
        'past_masc_2_sg': 'byłeś',
        'past_masc_3_sg': 'był',
        # ... etc
    }
}
```

**Pros**:
- Flat, easy to query by key
- Simple serialization

**Cons**:
- Keys become very long and complex
- Harder to enumerate all forms for a dimension
- Less structured, harder to validate
- No clear hierarchy

## Recommendation

**Use the hierarchical structure** for the following reasons:

1. **Better represents linguistic reality**: The nesting reflects how linguists think about morphology
2. **More maintainable**: Clear structure makes it easier to add new dimensions
3. **Easier validation**: Can validate that all required dimensions are present
4. **Better for UI**: Natural tree structure for displaying tables
5. **Flexible**: Can handle missing/optional dimensions gracefully

## Implementation Strategy

### Phase 1: Parse Raw Tables
Keep current `_parse_html_table()` that returns 2D arrays.

### Phase 2: Interpret Tables
New function: `_interpret_declension_table(table_data, word_class)` that:
- Identifies header rows (case names, tense/person labels, etc.)
- Maps cell positions to linguistic dimensions
- Builds hierarchical structure

### Phase 3: Expose Structured Data
Add new API method:
```python
def get_structured_morphology(word: str) -> Dict:
    """
    Returns structured morphological data for a word.
    """
```

## Table Interpretation Challenges

### Identifying Table Structure
Wiktionary tables vary in format. We need heuristics:

1. **Look for header rows**: First row/column usually contains dimension labels
2. **Recognize Polish labels**:
   - Cases: "mianownik", "dopełniacz", "celownik", "biernik", "narzędnik", "miejscownik", "wołacz"
   - Numbers: "liczba pojedyncza", "liczba mnoga", "lp", "lm"
   - Persons: "1. os.", "2. os.", "3. os."
   - Genders: "rodzaj męski", "rodzaj żeński", "rodzaj nijaki", "m.", "ż.", "n."
   - Tenses: "czas teraźniejszy", "przeszły", "przyszły"
3. **Handle merged cells**: Tables often use rowspan/colspan
4. **Multiple tables**: One word might have multiple tables (e.g., different aspects of a verb)

### Edge Cases to Handle
- Suppletive forms (człowiek → ludzie)
- Defective paradigms (missing forms)
- Tantum forms (only singular or only plural)
- Alternative forms (multiple valid inflections)
- Regional variants
- Archaic forms

## File Organization

Suggested new module: `polishdict/morphology.py`

```python
# polishdict/morphology.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class WordClass(Enum):
    VERB = 'verb'
    NOUN = 'noun'
    ADJECTIVE = 'adjective'
    PRONOUN = 'pronoun'
    NUMERAL = 'numeral'

class Aspect(Enum):
    IMPERFECTIVE = 'imperfective'
    PERFECTIVE = 'perfective'
    BIASPECTUAL = 'biaspectual'

class Gender(Enum):
    MASCULINE = 'masculine'
    FEMININE = 'feminine'
    NEUTER = 'neuter'

class Animacy(Enum):
    PERSONAL = 'personal'  # masculine personal (virile)
    ANIMATE = 'animate'
    INANIMATE = 'inanimate'

@dataclass
class MorphologicalForms:
    """Base class for morphological forms"""
    word_class: WordClass
    lemma: str
    forms: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VerbConjugation(MorphologicalForms):
    aspect: Optional[Aspect] = None

@dataclass
class NounDeclension(MorphologicalForms):
    gender: Optional[Gender] = None
    animacy: Optional[Animacy] = None

@dataclass
class AdjectiveDeclension(MorphologicalForms):
    pass

class MorphologyParser:
    """Parses raw table data into structured morphological forms"""

    def parse(self, raw_table: List[List[str]], word_class: str, lemma: str) -> MorphologicalForms:
        """Main entry point for parsing"""
        pass

    def _identify_table_structure(self, raw_table: List[List[str]]) -> Dict:
        """Identify headers and structure of the table"""
        pass

    def _parse_verb_conjugation(self, raw_table: List[List[str]]) -> VerbConjugation:
        """Parse verb conjugation table"""
        pass

    def _parse_noun_declension(self, raw_table: List[List[str]]) -> NounDeclension:
        """Parse noun declension table"""
        pass

    def _parse_adjective_declension(self, raw_table: List[List[str]]) -> AdjectiveDeclension:
        """Parse adjective declension table"""
        pass
```

## Next Steps

1. Create the `morphology.py` module with data classes
2. Implement table structure identification (headers, dimensions)
3. Implement parser for simple noun declension first (easiest case)
4. Test with various nouns (different genders, animacies)
5. Implement verb conjugation parser
6. Implement adjective declension parser
7. Handle edge cases and irregularities
8. Add validation
9. Update API to expose structured data
10. Update formatter to use structured data for display
10a. Especially handle mobile web app display, which is tricky to do with large tables - this will need thought and discussion.

## Questions for Discussion

1. Should we keep both raw tables AND structured data, or replace raw with structured?

Keep both.

2. How should we handle alternative/variant forms? (e.g., list vs single value)

A dict with keys ["primary", "Kashubian", "archaic", ...]

3. Should we validate completeness of paradigms or allow partial data?

Partial, I think.

4. How important is support for archaic/regional forms?

Not terribly important but you can include it as above.

5. Should we include grammatical rules/patterns in metadata?

If they can be described in a reasonably brief way.
