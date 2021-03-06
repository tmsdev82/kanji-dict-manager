from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.mongodb_utils import connect_to_mongo, close_mongo_connection
from app.utils.log_config import init_logging

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

init_logging()


def setup():
    """
    Configure the FastAPI app, router, eventhandlers, etc.
    """
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_event_handler("startup", connect_to_mongo)
    app.add_event_handler("shutdown", close_mongo_connection)

    app.include_router(api_router, prefix=settings.API_V1_STR)


setup()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", log_level="debug")
