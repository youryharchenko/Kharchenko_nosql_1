import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до БД
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# 2. Оголошення умов фільтрації та проєкції полів
query = {
    "audio_features.danceability": {"$gt": 0.7},
    "audio_features.energy": {"$gt": 0.7},
    "duration_sec": {"$gte": 180, "$lte": 300}
}

projection = {
    "_id": 0,
    "track_name": 1,
    "artists": 1,
    "popularity": 1,
    "duration_sec": 1
}

# 3. Виконання запиту з лімітом у 10 треків
cursor = collection.find(query, projection).limit(10)

print("=== ТОП ТРЕКІВ ДЛЯ ВЕЧІРКИ (FIND) ===")
print(list(cursor))