from typing import Optional, List

from app.models.rwmodel import RWModel, ObjectIdStr


class ExampleSentenceFilterParams(RWModel):
    related_kanji: List[str] = []


class ExampleSentenceBase(RWModel):
    example_sentence: Optional[str] = None
    hiragana: Optional[str] = None
    translation: Optional[str] = None
    related_kanji: Optional[List[str]]


class ExampleSentenceCreate(ExampleSentenceBase):
    example_sentence: str
    hiragana: str
    translation: str


class ExampleSentenceUpdate(ExampleSentenceBase):
    pass


class ExampleSentenceInDbBase(ExampleSentenceBase):
    doc_id: Optional[ObjectIdStr] = None
    example_sentence: str
    hiragana: str
    translation: str


class ExampleSentenceInDb(ExampleSentenceInDbBase):
    pass