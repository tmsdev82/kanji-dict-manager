from typing import Optional, List

from app.models.rwmodel import RWModel, ObjectIdStr


class CompoundWordFilterParams(RWModel):
    related_kanji: List[str] = []


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
    doc_id: Optional[ObjectIdStr] = None
    compound_word: str
    hiragana: str
    translation: str


class CompoundWordInDb(CompoundWordInDbBase):
    pass