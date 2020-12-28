from fastapi import APIRouter

from app.api.api_v1.endpoints import kanji

api_router = APIRouter()
api_router.include_router(kanji.router, prefix="/kanjis", tags=["kanjis"])