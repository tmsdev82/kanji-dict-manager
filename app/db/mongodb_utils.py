from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.db.mongodb import db


async def connect_to_mongo():
    """
    Establish mongodb connection.
    """
    logger.debug(">>>>")
    logger.info("Connecting to mongodb...")
    credentials = ""
    if settings.MONGO_USER:
        credentials = f"{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@"

    connection_string = (
        f"mongodb://{credentials}{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}"
    )
    logger.debug(f"Connection string: {connection_string}")
    db.client = AsyncIOMotorClient(connection_string)

    logger.info("Mongodb connection established.")


async def close_mongo_connection():
    """
    Close mongodb connection.
    """
    logger.debug(">>>>")
    logger.info("Closing mongo connection...")
    db.client.close()
    logger.info("Closed mongo connection.")