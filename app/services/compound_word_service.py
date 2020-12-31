import json
from typing import List
from bson import ObjectId
from datetime import datetime


from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.utils import Obj

from app.core.config import settings
from app import models


async def create_compound_word(
    connection: AsyncIOMotorClient, compound_word: models.CompoundWordCreate
) -> models.CompoundWordInDb:
    """
    Create a new compound_word document.

    :param connection: Async database client.
    :param compound_word: The compound_word document to insert into the database.
    :return: Returns compound_word document as it is in the database.
    """
    logger.debug(">>>>")
    compound_word_doc = compound_word.dict()
    logger.info(f"Creating compound_word doc: {json.dumps(compound_word_doc, indent=2, ensure_ascii=False)}")
    compound_word_doc["updated_at"] = datetime.utcnow()

    result = await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].insert_one(
        compound_word_doc
    )
    compound_word_in_db = models.CompoundWordInDb(**compound_word_doc)
    compound_word_in_db.doc_id = result.inserted_id

    return compound_word_in_db


async def get_compound_word_doc_by_compound_word(
    connection: AsyncIOMotorClient, compound_word: str
) -> models.CompoundWordInDb:
    """
    Retrieve a single compound_word document.

    :param connection: Async database client.
    :param compound_word: The unique compound_word to use to retrieve the compound_word document from the database.
    :return: Returns compound_word document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving compound_word data for {compound_word}...")

    compound_word_doc = await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].find_one(
        {"compound_word": compound_word}
    )
    if compound_word_doc:
        compound_word_in_db = models.CompoundWordInDb(**compound_word_doc)
        compound_word_in_db.doc_id = compound_word_doc.get("_id")

        return compound_word_in_db


async def get_compound_word_doc_by_id(connection: AsyncIOMotorClient, doc_id: str) -> models.CompoundWordInDb:
    """
    Retrieve a single compound_word document.

    :param connection: Async database client.
    :param doc_id: The unique doc_id to use to retrieve the compound_word document from the database.
    :return: Returns compound_word document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving compound_word data for {doc_id}...")

    compound_word_doc = await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].find_one(
        {"_id": ObjectId(doc_id)}
    )
    if compound_word_doc:
        if "doc_id" in compound_word_doc:
            del compound_word_doc["doc_id"]
        compound_word_in_db = models.CompoundWordInDb(**compound_word_doc)
        compound_word_in_db.doc_id = compound_word_doc.get("_id")

        return compound_word_in_db


async def get_compound_words(
    connection: AsyncIOMotorClient,
    filters: models.CompoundWordFilterParams = models.CompoundWordFilterParams(),
) -> List[models.CompoundWordInDb]:
    """
    Get all compound_word documents in the database.

    :param connection: Async database client.
    :param filters: CompoundWordFilterParams instance containing values to filter on. If no filter values
    are set, then all compound words will be returned.
    :return: Returns all compound_word documents as a list.
    """
    logger.debug(">>>>")
    query = {}
    if filters.related_kanji:
        query["related_kanji"] = {"$in": filters.related_kanji}

    if query:
        results = connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].find(query)
    else:
        results = connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].find()

    compound_word_results = []
    async for result in results:
        if "doc_id" in result:
            del result["doc_id"]
        compound_word_in_db = models.CompoundWordInDb(**result)
        compound_word_in_db.doc_id = result.get("_id")
        compound_word_results.append(compound_word_in_db)

    logger.info(f"Retrieved {len(compound_word_results)} compound_word.")
    return compound_word_results


async def delete_compound_word_doc_by_compound_word(
    connection: AsyncIOMotorClient, compound_word: str
) -> None:
    """
    Delete compound_word documents by compound_word. All matching documents will be deleted.

    :param connection: Database connection object.
    :param compound_word: The unique compound_word to delete documents by.
    """

    logger.info(f"Deleting compound_word '{compound_word}'...")
    await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].delete_many(
        {"compound_word": compound_word}
    )
    logger.info(f"Deleted compound_word '{compound_word}'.")


async def delete_compound_word_doc_by_id(connection: AsyncIOMotorClient, doc_id: str) -> None:
    """
    Delete compound_word documents by compound_word. All matching documents will be deleted.

    :param connection: Database connection object.
    :param doc_id: The unique doc_id to delete documents by.
    """

    logger.info(f"Deleting compound_word '{doc_id}'...")
    await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].delete_many(
        {"_id": ObjectId(doc_id)}
    )
    logger.info(f"Deleted compound_word '{doc_id}'.")


async def update_compound_word_doc_by_id(
    connection: AsyncIOMotorClient, doc_id: str, compoundWordUpdate: models.CompoundWordUpdate
) -> models.CompoundWordInDb:
    """
    Update a single compound_word by compound_word. Supports partial update. Only attributes set on the CompoundWordUpdate object
    will be updated.

    :param connection: Async database client.
    :param doc_id: The unique doc_id to update a document by.
    :param compoundWordUpdate:  CompoundWordUpdate instance with updated values.
    :return: Returns compound_word document as it is in the database.
    """
    logger.debug(">>>>")
    db_compound_word = await get_compound_word_doc_by_id(connection, doc_id)

    if compoundWordUpdate.compound_word:
        db_compound_word.compound_word = compoundWordUpdate.compound_word

    if compoundWordUpdate.hiragana:
        db_compound_word.hiragana = compoundWordUpdate.hiragana

    if compoundWordUpdate.translation:
        db_compound_word.translation = compoundWordUpdate.translation

    if compoundWordUpdate.related_kanji:
        db_compound_word.related_kanji = compoundWordUpdate.related_kanji

    updated_doc = db_compound_word.dict()
    updated_doc["doc_id"] = str(updated_doc["doc_id"])
    logger.info(
        f"Updating compound_word {doc_id} with: {json.dumps(updated_doc, indent=2, ensure_ascii=False)}"
    )

    await connection[settings.MONGO_DB][settings.MONGO_COMPOUND_WORD_COLLECTION].replace_one(
        {"_id": ObjectId(doc_id)}, updated_doc
    )

    return db_compound_word
