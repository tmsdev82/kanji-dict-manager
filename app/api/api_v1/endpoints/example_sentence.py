from typing import Optional, List, Any

from fastapi import APIRouter, Body, Depends, Path, Query, HTTPException, Response
from loguru import logger
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from motor.motor_asyncio import AsyncIOMotorClient

from app import models
from app.services import example_sentence_service
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/", response_model=List[models.ExampleSentenceInDb])
async def get_example_sentence_items(
    *,
    db: AsyncIOMotorClient = Depends(get_database),
    related_kanji: Optional[List[str]] = Query(None),
    ratings: Optional[List[int]] = Query(None),
    offset: Optional[int] = Query(0),
    limit: Optional[int] = Query(100),
):
    """
    Get a list of all example_sentences in the database.
    """
    logger.debug(">>>>")
    filters = models.ExampleSentenceFilterParams()
    if related_kanji:
        filters.related_kanji = related_kanji

    if ratings:
        filters.ratings = ratings

    filters.offset = offset
    filters.limit = limit

    example_sentences = await example_sentence_service.get_example_sentences(db, filters)

    return example_sentences


@router.get("/{doc_id}", response_model=models.ExampleSentenceInDb)
async def get_example_sentence_by_id(*, db: AsyncIOMotorClient = Depends(get_database), doc_id: str) -> Any:
    """
    Get a single example_sentence document using the example_sentence as a lookup.
    """
    example_sentence_result = await example_sentence_service.get_example_sentence_doc_by_id(db, doc_id)

    if not example_sentence_result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Example sentence not found")

    return example_sentence_result


@router.post("/", response_model=models.ExampleSentenceInDb, status_code=HTTP_201_CREATED)
async def create_new_example_sentence(
    *, example_sentence: models.ExampleSentenceCreate, db: AsyncIOMotorClient = Depends(get_database)
):
    """
    Create a new example_sentence document.
    """
    logger.debug(">>>>")
    example_sentence_by_example_sentence = (
        await example_sentence_service.get_example_sentence_doc_by_example_sentence(
            db, example_sentence.example_sentence
        )
    )

    if example_sentence_by_example_sentence:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Example sentence '{example_sentence.example_sentence}' already exists.",
        )

    db_example_sentence = await example_sentence_service.create_example_sentence(db, example_sentence)

    return db_example_sentence


@router.delete("/{doc_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_example_sentence_by_id(*, db: AsyncIOMotorClient = Depends(get_database), doc_id: str):
    """
    Delete a single example_sentence document using the example_sentence as a lookup.
    """
    example_sentence_by_example_sentence = await example_sentence_service.get_example_sentence_doc_by_id(
        db, doc_id
    )

    if not example_sentence_by_example_sentence:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Example sentence '{doc_id}' not found.")

    await example_sentence_service.delete_example_sentence_doc_by_id(db, doc_id)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.put("/{doc_id}", response_model=models.ExampleSentenceInDb)
async def update_example_sentence(
    *,
    db: AsyncIOMotorClient = Depends(get_database),
    doc_id: str,
    exampleSentenceUpdate: models.ExampleSentenceUpdate,
):
    """
    Update a single example_sentence document using the example_sentence as a lookup. Partial update is supported.
    """
    example_sentence = await example_sentence_service.get_example_sentence_doc_by_id(db, doc_id)

    if not example_sentence:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Example sentence '{doc_id}' not found.")

    updated_example_sentence = await example_sentence_service.update_example_sentence_doc_by_id(
        db, doc_id, exampleSentenceUpdate
    )

    return updated_example_sentence
