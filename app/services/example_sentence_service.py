import json
from typing import List
from bson import ObjectId
from datetime import datetime


from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.utils import Obj

from app.core.config import settings
from app import models


async def create_example_sentence(
    connection: AsyncIOMotorClient, example_sentence: models.ExampleSentenceCreate
) -> models.ExampleSentenceInDb:
    """
    Create a new example_sentence document.

    :param connection: Async database client.
    :param example_sentence: The example_sentence document to insert into the database.
    :return: Returns example_sentence document as it is in the database.
    """
    logger.debug(">>>>")
    example_sentence_doc = example_sentence.dict()
    logger.info(
        f"Creating example_sentence doc: {json.dumps(example_sentence_doc, indent=2, ensure_ascii=False)}"
    )
    example_sentence_doc["updated_at"] = datetime.utcnow()

    result = await connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].insert_one(
        example_sentence_doc
    )
    example_sentence_in_db = models.ExampleSentenceInDb(**example_sentence_doc)
    example_sentence_in_db.doc_id = result.inserted_id

    return example_sentence_in_db


async def get_example_sentence_doc_by_example_sentence(
    connection: AsyncIOMotorClient, example_sentence: str
) -> models.ExampleSentenceInDb:
    """
    Retrieve a single example_sentence document.

    :param connection: Async database client.
    :param example_sentence: The unique example_sentence to use to retrieve the example_sentence document from the database.
    :return: Returns example_sentence document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving example_sentence data for {example_sentence}...")

    example_sentence_doc = await connection[settings.MONGO_DB][
        settings.MONGO_EXAMPLE_SENTENCE_COLLECTION
    ].find_one({"example_sentence": example_sentence})
    if example_sentence_doc:
        example_sentence_in_db = models.ExampleSentenceInDb(**example_sentence_doc)
        example_sentence_in_db.doc_id = example_sentence_doc.get("_id")

        return example_sentence_in_db


async def get_example_sentence_doc_by_id(
    connection: AsyncIOMotorClient, doc_id: str
) -> models.ExampleSentenceInDb:
    """
    Retrieve a single example_sentence document.

    :param connection: Async database client.
    :param doc_id: The unique doc_id to use to retrieve the example_sentence document from the database.
    :return: Returns example_sentence document as it is in the database.
    """
    logger.debug(">>>>")
    logger.info(f"Retrieving example_sentence data for {doc_id}...")

    example_sentence_doc = await connection[settings.MONGO_DB][
        settings.MONGO_EXAMPLE_SENTENCE_COLLECTION
    ].find_one({"_id": ObjectId(doc_id)})
    if example_sentence_doc:
        if "doc_id" in example_sentence_doc:
            del example_sentence_doc["doc_id"]
        example_sentence_in_db = models.ExampleSentenceInDb(**example_sentence_doc)
        example_sentence_in_db.doc_id = example_sentence_doc.get("_id")

        return example_sentence_in_db


async def get_example_sentences(
    connection: AsyncIOMotorClient,
    filters: models.ExampleSentenceFilterParams = models.ExampleSentenceFilterParams(),
) -> List[models.ExampleSentenceInDb]:
    """
    Get all example_sentence documents in the database.

    :param connection: Async database client.
    :param filters: ExampleSentenceFilterParams instance containing values to filter on. If no filter values
    are set, then all example sentences will be returned.
    :return: Returns all example_sentence documents as a list.
    """
    logger.debug(">>>>")
    query = {}
    if filters.related_kanji:
        query["related_kanji"] = {"$in": filters.related_kanji}

    if query:
        results = connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].find(query)
    else:
        results = connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].find()

    example_sentence_results = []
    async for result in results:
        if "doc_id" in result:
            del result["doc_id"]
        example_sentence_in_db = models.ExampleSentenceInDb(**result)
        example_sentence_in_db.doc_id = result.get("_id")
        example_sentence_results.append(example_sentence_in_db)

    logger.info(f"Retrieved {len(example_sentence_results)} example_sentence.")
    return example_sentence_results


async def delete_example_sentence_doc_by_example_sentence(
    connection: AsyncIOMotorClient, example_sentence: str
) -> None:
    """
    Delete example_sentence documents by example_sentence. All matching documents will be deleted.

    :param connection: Database connection object.
    :param example_sentence: The unique example_sentence to delete documents by.
    """

    logger.info(f"Deleting example_sentence '{example_sentence}'...")
    await connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].delete_many(
        {"example_sentence": example_sentence}
    )
    logger.info(f"Deleted example_sentence '{example_sentence}'.")


async def delete_example_sentence_doc_by_id(connection: AsyncIOMotorClient, doc_id: str) -> None:
    """
    Delete example_sentence documents by example_sentence. All matching documents will be deleted.

    :param connection: Database connection object.
    :param doc_id: The unique doc_id to delete documents by.
    """

    logger.info(f"Deleting example_sentence '{doc_id}'...")
    await connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].delete_many(
        {"_id": ObjectId(doc_id)}
    )
    logger.info(f"Deleted example_sentence '{doc_id}'.")


async def update_example_sentence_doc_by_id(
    connection: AsyncIOMotorClient, doc_id: str, exampleSentenceUpdate: models.ExampleSentenceUpdate
) -> models.ExampleSentenceInDb:
    """
    Update a single example_sentence by example_sentence. Supports partial update. Only attributes set on the ExampleSentenceUpdate object
    will be updated.

    :param connection: Async database client.
    :param doc_id: The unique doc_id to update a document by.
    :param exampleSentenceUpdate:  ExampleSentenceUpdate instance with updated values.
    :return: Returns example_sentence document as it is in the database.
    """
    logger.debug(">>>>")
    db_example_sentence = await get_example_sentence_doc_by_id(connection, doc_id)

    if exampleSentenceUpdate.example_sentence:
        db_example_sentence.example_sentence = exampleSentenceUpdate.example_sentence

    if exampleSentenceUpdate.hiragana:
        db_example_sentence.hiragana = exampleSentenceUpdate.hiragana

    if exampleSentenceUpdate.translation:
        db_example_sentence.translation = exampleSentenceUpdate.translation

    if exampleSentenceUpdate.related_kanji:
        db_example_sentence.related_kanji = exampleSentenceUpdate.related_kanji

    updated_doc = db_example_sentence.dict()
    updated_doc["doc_id"] = str(updated_doc["doc_id"])
    logger.info(
        f"Updating example_sentence {doc_id} with: {json.dumps(updated_doc, indent=2, ensure_ascii=False)}"
    )

    await connection[settings.MONGO_DB][settings.MONGO_EXAMPLE_SENTENCE_COLLECTION].replace_one(
        {"_id": ObjectId(doc_id)}, updated_doc
    )

    return db_example_sentence
