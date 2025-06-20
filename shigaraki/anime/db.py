from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection
from config import config

DB_URL = config.MONGODB_URI

_MGCLIENT: AgnosticClient = AsyncIOMotorClient(DB_URL)

_DATABASE: AgnosticDatabase = _MGCLIENT[config.DATABASE_NAME]


def get_collection(name: str) -> AgnosticCollection:
    """ Create or Get Collection from your database """
    return _DATABASE[name]

__all__ = ['get_collection']


def _close_db() -> None:
    _MGCLIENT.close()
