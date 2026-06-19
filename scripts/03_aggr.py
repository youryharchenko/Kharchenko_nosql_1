import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до бази даних
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# 2. Побудова Aggregation Pipeline
pipeline = [
    {
        # Крок 1: Групуємо треки за жанром та рахуємо середні метрики й кількість треків
        "$group": {
            "_id": "$track_genre",
            "avg_danceability": {"$avg": "$audio_features.danceability"},
            "avg_energy": {"$avg": "$audio_features.energy"},
            "avg_valence": {"$avg": "$audio_features.valence"},
            "tracks_count": {"$sum": 1}
        }
    },
    {
        # Крок 2: Відфільтровуємо малочисельні жанри (залишаємо лише ті, де >= 100 треків)
        "$match": {
            "tracks_count": {"$gte": 100}
        }
    },
    {
        # Крок 3: Сортуємо жанри за показником танцювальності від найвищого до найнижчого
        "$sort": {
            "avg_danceability": -1
        }
    },
    {
        # Крок 4: Обмежуємо вивід, наприклад, топ-10 найкращими танцювальними жанрами
        "$limit": 10
    },
    {
        # Крок 5: Форматуємо поля та округлюємо середні значення до 3 знаків після коми
        "$project": {
            "_id": 0,
            "genre": "$_id",
            "avg_danceability": {"$round": ["$avg_danceability", 3]},
            "avg_energy": {"$round": ["$avg_energy", 3]},
            "avg_valence": {"$round": ["$avg_valence", 3]},
            "tracks_count": 1
        }
    }
]

# 3. Виконання запиту на сервері MongoDB
print("Шукаємо найкращі музичні жанри для танців...")
results = list(collection.aggregate(pipeline))

# 4. Візуалізація результатів через Pandas DataFrame
if results:
    print("\n=== ТОП-10 НАЙКРАЩИХ МУЗИЧНИХ ЖАНРІВ ДЛЯ ТАНЦІВ ===")
    print(results)
else:
    print("\nДані для аналізу відсутні. Перевірте колекцію tracks.")