from app.models.kanji import KanjiUpdate
from typing import Optional, List, Any

from fastapi import APIRouter, Body, Depends, Path, Query, HTTPException, Response, File, UploadFile, Form
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
from app.services import kanji_dict_service
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/", response_model=List[models.KanjiDict])
async def get_kanji_dict_items(db: AsyncIOMotorClient = Depends(get_database)):
    """
    Get a list of all kanji dicts in the database.
    """
    logger.debug(">>>>")
    kanji_dicts = await kanji_dict_service.get_kanji_dicts(db)

    return kanji_dicts


@router.post("/", status_code=HTTP_201_CREATED)
async def import_kanji_dicts(
    *, kanjiDictList: List[models.KanjiDict], db: AsyncIOMotorClient = Depends(get_database)
):
    """
    Import list of kanji dictionaries. Deletes the current data from the database.
    """
    logger.debug(">>>>")

    await kanji_dict_service.import_kanji_dict_list(db, kanjiDictList)

    return {"message": "Completed successful bulk import.", "status": "OK"}


@router.post("/upload/")
async def upload_kanji_dict_file(
    file: UploadFile = File(...), db: AsyncIOMotorClient = Depends(get_database)
):
    logger.debug(f"filename: {file.filename}")
    result = await kanji_dict_service.process_file_upload(db, file)

    return {"message": "Completed successful file import.", "status": "OK"}
