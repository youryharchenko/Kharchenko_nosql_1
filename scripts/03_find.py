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
        # Крок 1: Групуємо за жанром, рахуємо середнє значення та стандартне відхилення,
        # а також зберігаємо всі документи треків у масив для подальшої фільтрації
        "$group": {
            "_id": "$track_genre",
            "avg_tempo": {"$avg": "$audio_features.tempo"},
            "std_dev": {"$stdDevPop": "$audio_features.tempo"},
            "all_tracks": {
                "$push": {
                    "_id": "$_id",
                    "track_name": "$track_name",
                    "popularity": "$popularity",
                    "artists": "$artists",
                    "audio_features": {
                        "tempo": "$audio_features.tempo"
                    }
                }
            }
        }
    },
    {
        # Крок 2: Обчислюємо поріг для аномалій (outlier_threshold = avg_tempo + 2 * std_dev)
        "$set": {
            "outlier_threshold": {
                "$add": ["$avg_tempo", {"$multiply": [2, "$std_dev"]}]
            }
        }
    },
    {
        # Крок 3: Фільтруємо масив треків, залишаючи лише ті, у яких tempo > outlier_threshold
        "$set": {
            "outlier_tracks": {
                "$filter": {
                    "input": "$all_tracks",
                    "as": "track",
                    "cond": {
                        "$gt": ["$$track.audio_features.tempo", "$outlier_threshold"]
                    }
                }
            }
        }
    },
    {
        # Крок 4: Залишаємо лише ті жанри, в яких знайшовся бодай один такий нетиповий трек
        "$match": {
            "outlier_tracks.0": {"$exists": True}
        }
    },
    {
        # Крок 5: Форматуємо фінальний вигляд документа згідно з вашими вимогами
        # Округляємо числові значення до 1 знака після коми для чистоти результату
        "$project": {
            "_id": 0,
            "genre": "$_id",
            "avg_tempo": {"$round": ["$avg_tempo", 1]},
            "outlier_threshold": {"$round": ["$outlier_threshold", 1]},
            "outlier_tracks": 1
        }
    },
    {
        # Крок 6: Сортуємо жанри за назвою для зручності відображення
        "$sort": {"genre": 1}
    }
]

# 3. Виконання запиту
print("Аналізуємо жанри на наявність треків з аномальним темпом...")
results = list(collection.aggregate(pipeline))

# 4. Виведення результатів
print(f"\nЗнайдено жанрів з аномальними треками: {len(results)}")
print("======================================================================")

print(results[0:3])