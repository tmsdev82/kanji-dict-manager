import json
from typing import List
from datetime import datetime
from bson import ObjectId


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

    result = await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].insert_one(kanji_doc)
    logger.debug(f"Inserted Id: {result.inserted_id}")

    kanji_in_db = models.KanjiInDb(**kanji_doc)
    kanji_in_db.doc_id = result.inserted_id

    return kanji_in_db


async def get_kanji_doc_by_id(connection: AsyncIOMotorClient, doc_id: str) -> models.KanjiInDb:
    """
    Retrieve a single kanji document.

    :param connection: Async database client.
    :param doc_id: The unique doc_id to use to retrieve the kanji document from the database.
    :return: Returns kanji document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving kanji data for {doc_id}...")

    kanji_doc = await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].find_one(
        {"_id": ObjectId(doc_id)}
    )
    if kanji_doc:
        if "doc_id" in kanji_doc:
            del kanji_doc["doc_id"]
        kanji_in_db = models.KanjiInDb(**kanji_doc)
        kanji_in_db.doc_id = kanji_doc.get("_id")
        return kanji_in_db


async def get_kanji_doc_by_kanji(connection: AsyncIOMotorClient, kanji: str) -> models.KanjiInDb:
    """
    Retrieve a single kanji document.

    :param connection: Async database client.
    :param kanji: The kanji to use to retrieve the kanji document from the database.
    :return: Returns kanji document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving kanji data for {kanji}...")

    kanji_doc = await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].find_one(
        {"kanji": kanji}
    )
    if kanji_doc:
        if "doc_id" in kanji_doc:
            del kanji_doc["doc_id"]
        kanji_in_db = models.KanjiInDb(**kanji_doc)
        kanji_in_db.doc_id = kanji_doc.get("_id")
        return kanji_in_db


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
        if "doc_id" in result:
            del result["doc_id"]
        kanji_in_db = models.KanjiInDb(**result)
        kanji_in_db.doc_id = result.get("_id")
        kanji_results.append(kanji_in_db)

    logger.info(f"Retrieved {len(kanji_results)} kanji.")
    return kanji_results


async def delete_kanji_doc_by_id(connection: AsyncIOMotorClient, doc_id: str) -> None:
    """
    Delete kanji documents by doc_id. The matching document will be deleted.

    :param connection: Database connection object.
    :param doc_id: The unique doc_id to delete documents by.
    """

    logger.info(f"Deleting kanji '{doc_id}'...")
    await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].delete_one({"_id": ObjectId(doc_id)})
    logger.info(f"Deleted kanji '{doc_id}'.")


async def update_kanji_doc_by_id(
    connection: AsyncIOMotorClient, doc_id: str, kanjiUpdate: models.KanjiUpdate
) -> models.KanjiInDb:
    """
    Update a single kanji by doc_id. Supports partial update. Only attributes set on the KanjiUpdate object
    will be updated.

    :param connection: Async database client.
    :param doc_id: The unique doc_id to update a document by.
    :param kanjiUpdate:  KanjiUpdate instance with updated values.
    :return: Returns kanji document as it is in the database.
    """
    logger.debug(">>>>")
    db_kanji = await get_kanji_doc_by_id(connection, doc_id)

    if kanjiUpdate.kanji:
        db_kanji.kanji = kanjiUpdate.kanji

    if kanjiUpdate.jouyou_number:
        db_kanji.jouyou_number = kanjiUpdate.jouyou_number

    if kanjiUpdate.radical:
        db_kanji.radical = kanjiUpdate.radical

    if kanjiUpdate.strokes:
        db_kanji.strokes = kanjiUpdate.strokes

    if kanjiUpdate.jlpt_level:
        db_kanji.jlpt_level = kanjiUpdate.jlpt_level

    if kanjiUpdate.frequency_rank:
        db_kanji.frequency_rank = kanjiUpdate.frequency_rank

    if kanjiUpdate.onyomi:
        db_kanji.onyomi = kanjiUpdate.onyomi

    if kanjiUpdate.kunyomi:
        db_kanji.kunyomi = kanjiUpdate.kunyomi

    if kanjiUpdate.meaning:
        db_kanji.meaning = kanjiUpdate.meaning

    updated_doc = db_kanji.dict()
    updated_doc["doc_id"] = str(updated_doc["doc_id"])
    logger.info(f"Updating kanji {doc_id} with: {json.dumps(updated_doc, indent=2, ensure_ascii=False)}")

    await connection[settings.MONGO_DB][settings.MONGO_KANJI_COLLECTION].replace_one(
        {"_id": ObjectId(doc_id)}, updated_doc
    )

    return db_kanji
