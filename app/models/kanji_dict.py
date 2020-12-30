from typing import Optional, List

from app.models.compound_word import CompoundWordBase
from app.models.example_sentence import ExampleSentenceBase
from app.models.kanji import KanjiBase
from app.models.rwmodel import RWModel, ObjectIdStr


class KanjiDictBase(KanjiBase):
    compound_words: Optional[List[CompoundWordBase]] = []
    example_sentences: Optional[List[ExampleSentenceBase]] = []


class KanjiDict(KanjiDictBase):
    pass
