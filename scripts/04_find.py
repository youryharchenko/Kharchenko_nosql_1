import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до бази даних
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# 2. Формування умов пошуку (Query)
# Враховуємо: loudness < -10, speechiness < 0.1, instrumentalness > 0.5, explicit є False
query = {
    "audio_features.loudness": {"$lt": -10},
    "audio_features.speechiness": {"$lt": 0.1},
    "audio_features.instrumentalness": {"$gt": 0.5},
    "explicit": False
}

# 3. Визначення полів для виведення (Projection)
projection = {
    "_id": 0,
    "track_name": 1,
    "artists": 1,
    "album_name": 1,
    "track_genre": 1,
    "popularity": 1,
    "audio_features.instrumentalness": 1,
    "audio_features.loudness": 1
}

# 4. Виконання запиту
# Сортуємо за спаданням популярності (popularity: -1) та обмежуємо 10 записами
cursor = collection.find(query, projection).sort("popularity", -1).limit(10)

# 5. Візуалізація результатів
result = list(cursor)

if result:
    print("=== ТОП-10 ТРЕКІВ ДЛЯ ФОНОВОЇ РОБОТИ ТА КОНЦЕНТРАЦІЇ ===")
    print(result)
else:
    print("Треків за такими критеріями не знайдено.")