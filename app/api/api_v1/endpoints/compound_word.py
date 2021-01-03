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
from app.services import compound_word_service
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/", response_model=List[models.CompoundWordInDb])
async def get_compound_word_items(
    *,
    db: AsyncIOMotorClient = Depends(get_database),
    related_kanji: Optional[List[str]] = Query(None),
    ratings: Optional[List[int]] = Query(None),
    offset: Optional[int] = Query(0),
    limit: Optional[int] = Query(100),
):
    """
    Get a list of all compound_words in the database.
    """
    logger.debug(">>>>")
    filters = models.CompoundWordFilterParams()
    if related_kanji:
        filters.related_kanji = related_kanji
    if ratings:
        filters.ratings = ratings

    filters.offset = offset
    filters.limit = limit

    compound_words = await compound_word_service.get_compound_words(db, filters)

    return compound_words


@router.get("/{doc_id}", response_model=models.CompoundWordInDb)
async def get_compound_word_by_id(*, db: AsyncIOMotorClient = Depends(get_database), doc_id: str) -> Any:
    """
    Get a single compound_word document using the compound_word as a lookup.
    """
    compound_word_result = await compound_word_service.get_compound_word_doc_by_id(db, doc_id)

    if not compound_word_result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Compound word not found")

    return compound_word_result


@router.post("/", response_model=models.CompoundWordInDb, status_code=HTTP_201_CREATED)
async def create_new_compound_word(
    *, compound_word: models.CompoundWordCreate, db: AsyncIOMotorClient = Depends(get_database)
):
    """
    Create a new compound_word document.
    """
    logger.debug(">>>>")
    compound_word_by_compound_word = await compound_word_service.get_compound_word_doc_by_compound_word(
        db, compound_word.compound_word
    )

    if compound_word_by_compound_word:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Compound word '{compound_word.compound_word}' already exists.",
        )

    db_compound_word = await compound_word_service.create_compound_word(db, compound_word)

    return db_compound_word


@router.delete("/{doc_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_compound_word_by_id(*, db: AsyncIOMotorClient = Depends(get_database), doc_id: str):
    """
    Delete a single compound_word document using the compound_word as a lookup.
    """
    compound_word_by_compound_word = await compound_word_service.get_compound_word_doc_by_id(db, doc_id)

    if not compound_word_by_compound_word:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Compound word '{doc_id}' not found.")

    await compound_word_service.delete_compound_word_doc_by_id(db, doc_id)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.put("/{doc_id}", response_model=models.CompoundWordInDb)
async def update_compound_word(
    *,
    db: AsyncIOMotorClient = Depends(get_database),
    doc_id: str,
    compoundWordUpdate: models.CompoundWordUpdate,
):
    """
    Update a single compound_word document using the compound_word as a lookup. Partial update is supported.
    """
    compound_word = await compound_word_service.get_compound_word_doc_by_id(db, doc_id)

    if not compound_word:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Compound word '{doc_id}' not found.")

    updated_compound_word = await compound_word_service.update_compound_word_doc_by_id(
        db, doc_id, compoundWordUpdate
    )

    return updated_compound_word
