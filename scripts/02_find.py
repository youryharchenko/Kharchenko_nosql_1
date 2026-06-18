import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до бази даних
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# 2. Побудова аналітичного конвеєра (Aggregation Pipeline)
pipeline = [
    {
        # Крок 1: Розгортаємо масив артистів, щоб згрупувати дані по кожному автору окремо
        "$unwind": "$artists"
    },
    {
        # Крок 2: Групуємо документи за іменем артиста та обчислюємо агреговані метрики
        "$group": {
            "_id": "$artists",
            "total_tracks": {"$sum": 1},
            "min_popularity": {"$min": "$popularity"},
            "avg_popularity": {"$avg": "$popularity"}
        }
    },
    {
        # Крок 3: Фільтруємо артистів за бізнес-вимогами:
        # мінімум 3 треки ТА мінімальна популярність кожного треку >= 60
        "$match": {
            "total_tracks": {"$gte": 3},
            "min_popularity": {"$gte": 60}
        }
    },
    {
        # Крок 4: Сортуємо артистів за середньою популярністю (від найвищої до найнижчої)
        "$sort": {"avg_popularity": -1}
    },
    {
        # Крок 5: Обмежуємо вихід топ-20 артистами
        "$limit": 20
    },
    {
        # Крок 6: Форматуємо фінальний вигляд полів та округлюємо середнє значення
        "$project": {
            "_id": 0,
            "artist_name": "$_id",
            "tracks_count": "$total_tracks",
            "min_popularity": 1,
            "avg_popularity": {"$round": ["$avg_popularity", 1]} # Округлення до 1 знака
        }
    }
]

# 3. Виконання запиту на сервері MongoDB
print("Проводимо аналіз популярності артистів...")
results = list(collection.aggregate(pipeline))

# 4. Візуалізація результатів через Pandas
if results:
    print("\n=== ТОП-20 ПОПУЛЯРНИХ АРТИСТІВ ===")
    print(results)
else:
    print("\nАртистів, які б задовольняли такі критерії (>=3 треки, кожен з яких популярністю >= 60), не знайдено.")