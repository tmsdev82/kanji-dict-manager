import json
from typing import List
from datetime import datetime


from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app import models


async def create_kanji(connection: AsyncIOMotorClient, kanji: models.KanjiCreate) -> models.KanjiInDb:
    """
    Create a new kanji document.

    :param connection: Async database client.
    :param kanji: The kanji document to insert into the database.
    :return: Returns kanji document as it is in the database.
    """
    logger.debug(">>>>")
    kanji_doc = kanji.dict()
    logger.info(f"Creating kanji doc: {json.dumps(kanji_doc, indent=2, ensure_ascii=False)}")
    kanji_doc["updated_at"] = datetime.utcnow()

    await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].insert_one(kanji_doc)

    return models.KanjiInDb(**kanji_doc)


async def get_kanji_doc_by_kanji(connection: AsyncIOMotorClient, kanji: str) -> models.KanjiInDb:
    """
    Retrieve a single kanji document.

    :param connection: Async database client.
    :param kanji: The unique kanji to use to retrieve the kanji document from the database.
    :return: Returns kanji document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving kanji data for {kanji}...")

    kanji_doc = await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].find_one(
        {"kanji": kanji}
    )
    if kanji_doc:
        return models.KanjiInDb(**kanji_doc)


async def get_all_kanji(connection: AsyncIOMotorClient) -> List[models.KanjiInDb]:
    """
    Get all kanji documents in the database.

    :param connection: Async database client.
    :return: Returns all kanji documents as a list.
    """
    logger.debug(">>>>")
    results = connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].find()

    kanji_results = []
    async for result in results:
        kanji_results.append(models.KanjiInDb(**result))

    logger.info(f"Retrieved {len(kanji_results)} kanji.")
    return kanji_results


async def delete_kanji_doc_by_kanji(connection: AsyncIOMotorClient, kanji: str) -> None:
    """
    Delete kanji documents by kanji. All matching documents will be deleted.

    :param connection: Database connection object.
    :param kanji: The unique kanji to delete documents by.
    """

    logger.info(f"Deleting kanji '{kanji}'...")
    await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].delete_many({"kanji": kanji})
    logger.info(f"Deleted kanji '{kanji}'.")


async def update_kanji_doc_by_kanji(
    connection: AsyncIOMotorClient, kanji: str, kanjiUpdate: models.KanjiUpdate
) -> models.KanjiInDb:
    """
    Update a single kanji by kanji. Supports partial update. Only attributes set on the KanjiUpdate object
    will be updated.

    :param connection: Async database client.
    :param kanji: The unique kanji to update a document by.
    :param kanjiUpdate:  KanjiUpdate instance with updated values.
    :return: Returns kanji document as it is in the database.
    """
    logger.debug(">>>>")
    db_kanji = await get_kanji_doc_by_kanji(connection, kanji)

    if kanjiUpdate.kanji:
        db_kanji.kanji = kanjiUpdate.kanji

    if kanjiUpdate.jouyou_number:
        db_kanji.jouyou_number = kanjiUpdate.jouyou_number

    if kanjiUpdate.radical:
        db_kanji.radical = kanjiUpdate.radical

    if kanjiUpdate.strokes:
        db_kanji.strokes = kanjiUpdate.strokes

    if kanjiUpdate.jlpt:
        db_kanji.jlpt = kanjiUpdate.jlpt

    if kanjiUpdate.freq:
        db_kanji.freq = kanjiUpdate.freq

    if kanjiUpdate.onyomi:
        db_kanji.onyomi = kanjiUpdate.onyomi

    if kanjiUpdate.kunyomi:
        db_kanji.kunyomi = kanjiUpdate.kunyomi

    if kanjiUpdate.meaning:
        db_kanji.meaning = kanjiUpdate.meaning

    updated_doc = db_kanji.dict()
    logger.info(f"Updating kanji {kanji} with: {json.dumps(updated_doc, indent=2, ensure_ascii=False)}")

    await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].replace_one(
        {"kanji": kanji}, updated_doc
    )

    return db_kanji
