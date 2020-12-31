from typing import Optional, List

from app.models.compound_word import CompoundWordInDb
from app.models.example_sentence import ExampleSentenceInDb
from app.models.kanji import KanjiInDb
from app.models.rwmodel import RWModel, ObjectIdStr


class KanjiDictBase(KanjiInDb):
    compound_words: Optional[List[CompoundWordInDb]] = []
    example_sentences: Optional[List[ExampleSentenceInDb]] = []


class KanjiDict(KanjiDictBase):
    pass
