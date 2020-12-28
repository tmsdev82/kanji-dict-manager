from typing import Optional

from app.models.rwmodel import RWModel


class CompoundWordBase(RWModel):
    kanji: Optional[str] = None
    hiragana: Optional[str] = None
    translation: Optional[str] = None


class CompoundWordCreate(CompoundWordBase):
    kanji: str
    hiragana: str
    translation: str


class CompoundWordUpdate(CompoundWordBase):
    pass


class CompoundWordInDbBase(CompoundWordBase):
    kanji: str
    hiragana: str
    translation: str


class CompoundWordInDb(CompoundWordInDbBase):
    pass