from enum import Enum
from typing import Optional, List

from app.models.rwmodel import RWModel, ObjectIdStr
from app.models.compound_word import CompoundWordBase, CompoundWordInDb


class KanjiSectionEnum(str, Enum):
    a = "あ"
    i = "い"


class KanjiBase(RWModel):
    # Number in the list of common use kanji
    jouyou_number: Optional[int] = None
    kanji: Optional[str] = None
    # What section it belongs to e.g. あ、い、う、え、お etc.
    kanji_section: Optional[KanjiSectionEnum] = None
    radical: Optional[str] = None
    strokes: Optional[int] = None
    jlpt_level: Optional[str] = None
    # ranking of most used in newspapers out of 2500
    frequency_rank: Optional[int] = None
    onyomi: Optional[List[str]] = None
    kunyomi: Optional[List[str]] = None
    meaning: Optional[List[str]] = None


class KanjiCreate(KanjiBase):
    jouyou_number: int
    kanji: str
    kanji_section: KanjiSectionEnum
    onyomi: List[str]
    kunyomi: List[str]
    meaning: List[str]


class KanjiUpdate(KanjiBase):
    pass


class KanjiInDbBase(KanjiBase):
    doc_id: Optional[ObjectIdStr] = None
    kanji: str


class KanjiInDb(KanjiInDbBase):
    pass
