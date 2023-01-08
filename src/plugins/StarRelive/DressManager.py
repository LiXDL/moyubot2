import motor.motor_asyncio
from enum import Enum

from pymongo.errors import DuplicateKeyError

from .util.formatter import dict2dto
from .dto.Dress import Dress

async_client = motor.motor_asyncio.AsyncIOMotorClient(
    host="localhost",
    port=27017,
    username="moyubot",
    password="moyubot",
    authSource="strr_db"
)
DRESSES = async_client.get_database("strr_db").get_collection("dress")


def shutdown():
    async_client.close


#   Empty out the dress collection, only used to force rewrite.
async def empty():
    await DRESSES.delete_many({})


async def insert_dress(document: dict):
    document["basicInfo"]["cardID"] = int(document["basicInfo"]["cardID"])
    try:
        await DRESSES.insert_one(document)
    except DuplicateKeyError:
        pass


async def get_dress(cid: int) -> Dress:
    raw_dress = await DRESSES.find_one({"basicInfo.cardID": cid})
    return dict2dto(raw_dress)

