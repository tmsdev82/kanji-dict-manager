from typing import Optional, List

from app.models.rwmodel import RWModel


class CompoundWordBase(RWModel):
    compound_word: Optional[str] = None
    hiragana: Optional[str] = None
    translation: Optional[str] = None
    related_kanji: Optional[List[str]]


class CompoundWordCreate(CompoundWordBase):
    compound_word: str
    hiragana: str
    translation: str


class CompoundWordUpdate(CompoundWordBase):
    pass


class CompoundWordInDbBase(CompoundWordBase):
    compound_word: str
    hiragana: str
    translation: str


class CompoundWordInDb(CompoundWordInDbBase):
    pass