from fastapi import APIRouter

from app.api.api_v1.endpoints import kanji, compound_word

api_router = APIRouter()
api_router.include_router(kanji.router, prefix="/kanjis", tags=["kanjis"])
api_router.include_router(compound_word.router, prefix="/compound-words", tags=["compound words"])