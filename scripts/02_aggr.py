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
        # Крок 1: Обчислюємо настрій (mood) для кожного треку на основі порогових значень 0.5
        "$project": {
            "mood": {
                "$cond": [
                    # Умова для happy: valence >= 0.5 ТА energy >= 0.5
                    {"$and": [
                        {"$gte": ["$audio_features.valence", 0.5]},
                        {"$gte": ["$audio_features.energy", 0.5]}
                    ]},
                    "happy",
                    {"$cond": [
                        # Умова для angry: valence < 0.5 ТА energy >= 0.5
                        {"$and": [
                            {"$lt": ["$audio_features.valence", 0.5]},
                            {"$gte": ["$audio_features.energy", 0.5]}
                        ]},
                        "angry",
                        {"$cond": [
                            # Умова для calm: valence >= 0.5 ТА energy < 0.5
                            {"$and": [
                                {"$gte": ["$audio_features.valence", 0.5]},
                                {"$lt": ["$audio_features.energy", 0.5]}
                            ]},
                            "calm",
                            # Якщо жодна умова не підійшла, залишається sad (valence < 0.5 i energy < 0.5)
                            "sad"
                        ]}
                    ]}
                ]
            }
        }
    },
    {
        # Крок 2: Групуємо за вирахуваним настроєм та рахуємо кількість треків у кожній категорії
        "$group": {
            "_id": "$mood",
            "tracks_count": {"$sum": 1}
        }
    },
    {
        # Крок 3: Сортуємо за кількістю треків (від найбільшої категорії до найменшої)
        "$sort": {
            "tracks_count": -1
        }
    },
    {
        # Крок 4: Красиво перейменовуємо поля для фінального виведення
        "$project": {
            "_id": 0,
            "mood": "$_id",
            "tracks_count": 1
        }
    }
]

# 3. Виконання запиту на сервері MongoDB
print("Аналізуємо емоційну карту треків за моделлю валентності та енергії...")
results = list(collection.aggregate(pipeline))

# 4. Візуалізація результатів через Pandas DataFrame
if results:
    print("\n=== РАСПОДІЛ МУЗИЧНОГО МАСИВУ ЗА НАСТРОЄМ ===")
    print(results)
else:
    print("\nНе вдалося отримати дані для аналізу. Перевірте наявність колекції tracks.")