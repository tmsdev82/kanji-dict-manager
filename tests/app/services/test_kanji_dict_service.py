from unittest import mock

import pytest

from app import models
from app.services.kanji_dict_service import import_kanji_dict


@pytest.fixture
def kanji_dict_data():
    return {
        "jouyou_number": 1,
        "kanji": "亜",
        "kanji_section": "あ",
        "radical": "二",
        "strokes": 7,
        "jlpt_level": "1",
        "frequency_rank": 1509,
        "onyomi": ["ア"],
        "kunyomi": [""],
        "meaning": ["-sub", "asia"],
        "compound_words": [
            {"compound_word": "亜鉛", "hiragana": "あ,えん", "translation": "zinc", "related_kanji": ["亜", "鉛"]}
        ],
    }


@pytest.mark.asyncio
async def test_import_kanji_dict(kanji_dict_data):
    mock_motor_client = mock.MagicMock()
    kanjiDict = models.KanjiDict(**kanji_dict_data)
    result = await import_kanji_dict(mock_motor_client, kanjiDict)
