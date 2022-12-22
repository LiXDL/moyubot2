import json
from pymongo import MongoClient, InsertOne, ASCENDING
from pathlib import Path


client = MongoClient(
    host="localhost",
    port=27017,
    username="moyubot",
    password="moyubot",
    authSource="strr_db"
)
cwdb = client.get_database("strr_db")
dress = cwdb.get_collection("dress")

dress.drop()

dress = cwdb.get_collection("dress")
dress.create_index([("basicInfo.cardID", ASCENDING)], unique=True)

source = Path(__file__).parent / "dress"
files = list(source.glob("*.json"))

requests = []
for file in files:
    with open(file, "r") as f:
        data = json.load(f)
        data["basicInfo"]["cardID"] = int(data["basicInfo"]["cardID"])
        requests.append(InsertOne(data))

result = dress.bulk_write(requests)
print(result.bulk_api_result)
