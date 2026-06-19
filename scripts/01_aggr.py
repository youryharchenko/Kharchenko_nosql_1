import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до бази даних MongoDB
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# 2. Побудова аналітичного конвеєра (Aggregation Pipeline)
pipeline = [
    {
        # Крок 1: Розгортаємо масив артистів, щоб кожен виконавець рахувався окремо
        "$unwind": "$artists"
    },
    {
        # Крок 2: Групуємо документи за іменем артиста, рахуємо кількість треків та середню популярність
        "$group": {
            "_id": "$artists",
            "tracks_count": {"$sum": 1},
            "avg_popularity": {"$avg": "$popularity"}
        }
    },
    {
        # Крок 3: Фільтруємо виконавців, залишаючи лише тих, у кого є щонайменше 5 треків
        "$match": {
            "tracks_count": {"$gte": 5}
        }
    },
    {
        # Крок 4: Сортуємо виконавців за спаданням середньої популярності
        "$sort": {
            "avg_popularity": -1
        }
    },
    {
        # Крок 5: Обмежуємо результат топ-10 виконавцями
        "$limit": 10
    },
    {
        # Крок 6: Форматуємо фінальний вигляд документа (округлюємо популярність до 1 знака)
        "$project": {
            "_id": 0,
            "artist_name": "$_id",
            "avg_popularity": {"$round": ["$avg_popularity", 1]}
        }
    }
]

# 3. Виконання запиту на сервері MongoDB
print("Розраховуємо топ-10 найпопулярніших виконавців...")
results = list(collection.aggregate(pipeline))

# 4. Візуалізація результатів через Pandas DataFrame
if results:
    print("\n=== ТОП-10 ВИКОНАВЦІВ ЗА СЕРЕДНЬОЮ ПОПУЛЯРНІСТЮ ===")
    print(results)
else:
    print("\nДані для аналізу відсутні або виконавців із ≥ 5 треками не знайдено.")