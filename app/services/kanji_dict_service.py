import shutil
from fastapi.datastructures import UploadFile
from app.models import example_sentence, kanji
import json
from typing import List
from datetime import datetime
from bson import ObjectId
from pathlib import Path


from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app import models
from app.services import kanji_service, compound_word_service, example_sentence_service


async def import_kanji_dict(connection: AsyncIOMotorClient, kanjiDict: models.KanjiDict) -> models.KanjiDict:
    """
    Create new kanji, compound word, and example sentences based on kanji dict data.
    Will also update compound word and example sentences related kanji arrays when needed.

    :param connection: Async database client.
    :param kanjiDictList: A list of KanjiDict instances to import.
    """
    logger.debug(">>>>")
    kanji_dict_doc = kanjiDict.dict(exclude_unset=True)

    kanji = kanji_dict_doc.get("kanji")

    existing_kanji = await kanji_service.get_kanji_doc_by_kanji(connection, kanji)
    if existing_kanji:
        logger.info(f"Kanji {kanji} already exists, updating.")
        kanji_update = models.KanjiUpdate(**kanji_dict_doc)
        await kanji_service.update_kanji_doc_by_id(connection, str(existing_kanji.doc_id), kanji_update)
    else:
        logger.info(f"Kanji {kanji} does not exist, creating.")
        kanji_create = models.KanjiCreate(**kanji_dict_doc)
        await kanji_service.create_kanji(connection, kanji_create)

    compound_words_data = kanji_dict_doc.get("compound_words")
    if compound_words_data:
        for compound_word_item in compound_words_data:
            compound_word = compound_word_item.get("compound_word")

            existing_compound_word = await compound_word_service.get_compound_word_doc_by_compound_word(
                connection, compound_word
            )
            if existing_compound_word:
                logger.info(f"Compound word: {compound_word} already exists")
                # Update associated kanji only?
                compound_word_update = models.CompoundWordUpdate(**existing_compound_word.dict())
                if compound_word_update.related_kanji and not kanji in compound_word_update.related_kanji:
                    compound_word_update.related_kanji.append(kanji)
                    await compound_word_service.update_compound_word_doc_by_id(
                        connection, existing_compound_word.doc_id, compound_word_update
                    )

            else:
                compound_word_create = models.CompoundWordCreate(**compound_word_item)
                compound_word_create.related_kanji = [kanji]
                await compound_word_service.create_compound_word(connection, compound_word_create)

    example_sentences_data = kanji_dict_doc.get("example_sentences")
    if example_sentences_data:
        for example_sentence_item in example_sentences_data:
            example_sentence = example_sentence_item.get("compound_word")

            existing_example_sentence = (
                await example_sentence_service.get_example_sentence_doc_by_example_sentence(
                    connection, example_sentence
                )
            )
            if existing_example_sentence:
                logger.info(f"Example sentence: {example_sentence} already exists")
                # Update associated kanji only?
                example_sentence_update = models.ExampleSentenceUpdate(**existing_example_sentence.dict())
                if (
                    example_sentence_update.related_kanji
                    and not kanji in example_sentence_update.related_kanji
                ):
                    example_sentence_update.related_kanji.append(kanji)
                    await example_sentence_service.update_example_sentence_doc_by_id(
                        connection, existing_example_sentence.doc_id, example_sentence_update
                    )

            else:
                example_sentence_create = models.ExampleSentenceCreate(**example_sentence_item)
                example_sentence_create.related_kanji = [kanji]
                await example_sentence_service.create_example_sentence(connection, example_sentence_create)


async def import_kanji_dict_list(
    connection: AsyncIOMotorClient, kanjiDictList: List[models.KanjiDict], replace_all: bool = True
) -> List[models.KanjiDict]:
    """
    Create new kanji, compound word, and example sentences based on kanji dict
    data in bulk from a list.

    :param connection: Async database client.
    :param kanjiDictList: A list of KanjiDict instances to import.
    :param replace_all: Flag that determines if all documents in all collections should be deleted first.
    """

    if replace_all:
        await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].drop()
        await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].drop()
        await connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].drop()

    imported_kanji_dicts = []
    for kanjiDict in kanjiDictList:
        result = await import_kanji_dict(connection, kanjiDict)
        if result:
            imported_kanji_dicts.append(result)


def populate_lookup(lookup, data_items, items_key):
    for data_item in data_items:
        # data_item.doc_id = str(data_item.doc_id)
        for related_kanji in data_item.related_kanji:
            lookup_item = lookup.get(related_kanji)
            if not lookup_item:
                lookup_item = {"compound_words": [], "example_sentences": []}
                lookup[related_kanji] = lookup_item

            lookup_item[items_key].append(data_item)


async def get_kanji_dicts(connection: AsyncIOMotorClient) -> List[models.KanjiDict]:
    """
    Retrieve list of KanjiDict matching query. Combines kanji, related compound words, and related example sentences into one dicitonary object.
    And returns all kanji dictionaries as a list.

    :param connection: Async database client.
    """

    kanjis = await kanji_service.get_all_kanji(connection)
    compound_words = await compound_word_service.get_compound_words(connection)
    example_sentences = await example_sentence_service.get_example_sentences(connection)

    lookup = {}
    populate_lookup(lookup, compound_words, "compound_words")
    populate_lookup(lookup, example_sentences, "example_sentences")

    kanji_dicts = []
    for kanji_item in kanjis:
        looked_up_item = lookup.get(kanji_item.kanji)

        kanji_dict = models.KanjiDict(**kanji_item.dict())
        kanji_dict.doc_id = ObjectId(kanji_dict.doc_id)

        if not looked_up_item:
            continue

        kanji_dict.compound_words = looked_up_item["compound_words"]
        kanji_dict.example_sentences = looked_up_item["example_sentences"]

        kanji_dicts.append(kanji_dict)

    return kanji_dicts


async def process_file_upload(connection, upload_file: UploadFile) -> None:
    logger.debug(">>>>")
    try:

        kanji_json = json.load(upload_file.file)
        logger.info(f"Kanji dict file contains {len(kanji_json)} kanji.")

        kanji_dict_list = []
        for kanji_dict in kanji_json:
            kanji_dict_converted = models.KanjiDict(**kanji_dict)
            kanji_dict_list.append(kanji_dict_converted)

        result = await import_kanji_dict_list(connection, kanji_dict_list)
    finally:
        upload_file.file.close()