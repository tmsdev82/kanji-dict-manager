from app.models.kanji import KanjiUpdate
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
from app.services import kanji_service
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/", response_model=List[models.KanjiInDb])
async def get_kanji_items(db: AsyncIOMotorClient = Depends(get_database)):
    """
    Get a list of all kanji in the database.
    """
    logger.debug(">>>>")
    kanjis = await kanji_service.get_all_kanji(db)

    return kanjis


@router.get("/{kanji}", response_model=models.KanjiInDb)
async def get_kanji(*, db: AsyncIOMotorClient = Depends(get_database), kanji: str) -> Any:
    """
    Get a single kanji document using the kanji as a lookup.
    """
    kanji_result = await kanji_service.get_kanji_doc_by_kanji(db, kanji)

    if not kanji_result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Kanji not found")

    return kanji_result


@router.post("/", response_model=models.KanjiInDb, status_code=HTTP_201_CREATED)
async def create_new_kanji(*, kanji: models.KanjiCreate, db: AsyncIOMotorClient = Depends(get_database)):
    """
    Create a new kanji document.
    """
    logger.debug(">>>>")
    kanji_by_kanji = await kanji_service.get_kanji_doc_by_kanji(db, kanji.kanji)

    if kanji_by_kanji:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Kanji '{kanji.kanji}' already exists."
        )

    db_kanji = await kanji_service.create_kanji(db, kanji)

    return db_kanji


@router.delete("/{kanji}", status_code=HTTP_204_NO_CONTENT)
async def delete_kanji(*, db: AsyncIOMotorClient = Depends(get_database), kanji: str):
    """
    Delete a single kanji document using the kanji as a lookup.
    """
    kanji_by_kanji = await kanji_service.get_kanji_doc_by_kanji(db, kanji)

    if not kanji_by_kanji:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Kanji '{kanji}' not found.")

    await kanji_service.delete_kanji_doc_by_kanji(db, kanji)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.put("/{kanji}", response_model=models.KanjiInDb)
async def update_kanji(
    *, db: AsyncIOMotorClient = Depends(get_database), kanji: str, kanjiUpdate: KanjiUpdate
):
    """
    Update a single kanji document using the kanji as a lookup. Partial update is supported.
    """
    kanji_by_kanji = await kanji_service.get_kanji_doc_by_kanji(db, kanji)

    if not kanji_by_kanji:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Kanji '{kanji}' not found.")

    updated_kanji = await kanji_service.update_kanji_doc_by_kanji(db, kanji, kanjiUpdate)

    return updated_kanji
