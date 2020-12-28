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
async def get_compound_word_items(db: AsyncIOMotorClient = Depends(get_database)):
    """
    Get a list of all compound_words in the database.
    """
    logger.debug(">>>>")
    compound_words = await compound_word_service.get_all_compound_word(db)

    return compound_words


@router.get("/{compound_word}", response_model=models.CompoundWordInDb)
async def get_compound_word(*, db: AsyncIOMotorClient = Depends(get_database), compound_word: str) -> Any:
    """
    Get a single compound_word document using the compound_word as a lookup.
    """
    compound_word_result = await compound_word_service.get_compound_word_doc_by_compound_word(
        db, compound_word
    )

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


@router.delete("/{compound_word}", status_code=HTTP_204_NO_CONTENT)
async def delete_compound_word(*, db: AsyncIOMotorClient = Depends(get_database), compound_word: str):
    """
    Delete a single compound_word document using the compound_word as a lookup.
    """
    compound_word_by_compound_word = await compound_word_service.get_compound_word_doc_by_compound_word(
        db, compound_word
    )

    if not compound_word_by_compound_word:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Compound word '{compound_word}' not found."
        )

    await compound_word_service.delete_compound_word_doc_by_compound_word(db, compound_word)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.put("/{compound_word}", response_model=models.CompoundWordInDb)
async def update_compound_word(
    *,
    db: AsyncIOMotorClient = Depends(get_database),
    compound_word: str,
    compoundWordUpdate: models.CompoundWordUpdate,
):
    """
    Update a single compound_word document using the compound_word as a lookup. Partial update is supported.
    """
    compound_word_by_compound_word = await compound_word_service.get_compound_word_doc_by_compound_word(
        db, compound_word
    )

    if not compound_word_by_compound_word:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Compound word '{compound_word}' not found."
        )

    updated_compound_word = await compound_word_service.update_compound_word_doc_by_compound_word(
        db, compound_word, compoundWordUpdate
    )

    return updated_compound_word
