import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
DB_NAME = "spotify"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

pipeline = [
    {
        "$project": {
            "_id": 1, "track_id": 1, "track_name": 1, "album_name": 1,
            "explicit": 1, "popularity": 1, "duration_ms": 1, "track_genre": 1,
            "artists_raw": "$artists",
            "danceability": 1, "energy": 1, "loudness": 1, "speechiness": 1, 
            "acousticness": 1, "instrumentalness": 1, "liveness": 1, "valence": 1, 
            "tempo": 1, "key": 1, "mode": 1, "time_signature": 1
        }
    },
    {
        "$set": {
            "artists": {
                "$map": {
                    "input": { "$split": [ "$artists_raw", ";" ] },
                    "as": "artist",
                    "in": { "$trim": { "input": "$$artist" } }
                }
            },
            "audio_features": {
                "danceability": "$danceability", "energy": "$energy", "loudness": "$loudness",
                "speechiness": "$speechiness", "acousticness": "$acousticness", 
                "instrumentalness": "$instrumentalness", "liveness": "$liveness", 
                "valence": "$valence", "tempo": "$tempo", "key": "$key", 
                "mode": "$mode", "time_signature": "$time_signature"
            },
            "duration_sec": { "$round": [ { "$divide": [ "$duration_ms", 1000 ] }, 1 ] },
            "popularity_tier": {
                "$switch": {
                    "branches": [
                        { "case": { "$gte": [ "$popularity", 70 ] }, "then": "high" },
                        { "case": { "$gte": [ "$popularity", 40 ] }, "then": "medium" }
                    ],
                    "default": "low"
                }
            }
        }
    },
    {
        "$unset": [
            "artists_raw", "danceability", "energy", "loudness", "speechiness", 
            "acousticness", "instrumentalness", "liveness", "valence", 
            "tempo", "key", "mode", "time_signature"
        ]
    },
    {
        "$out": "tracks"
    }
]

print("Запуск агрегації через Python...")
db["tracks"].drop()
db["tracks_raw"].aggregate(pipeline)
print(f"Трансформацію завершено! Документів у tracks: {db['tracks'].count_documents({})}")
print(f"Приклад документа:")
print(db["tracks"].find_one())