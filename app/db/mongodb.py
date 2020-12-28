from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    """
    Returns current instance of the AsycIOMotorClient for the app.
    This function is used for depedency injections on the API endpoints.
    """
    return db.client