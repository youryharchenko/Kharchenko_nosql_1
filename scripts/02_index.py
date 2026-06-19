import os
import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до бази даних
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# Визначаємо типовий запит для фонової роботи
focus_query = {
    "audio_features.instrumentalness": {"$gt": 0.5},
    "audio_features.speechiness": {"$lt": 0.1},
    "explicit": False
}

print("======================================================================")
print("КРОК 1: СТВОРЕННЯ СКЛАДЕНОГО ІНДЕКСУ ДЛЯ ФОКУС-ЗАПИТІВ")
print("======================================================================")

# Створюємо складений індекс. Порядок полів оптимізовано для фільтрації:
# Спочатку explicit (чітке бінарне відсікання), потім інструментальність та безмовність
index_spec = [
    ("explicit", 1),
    ("audio_features.instrumentalness", 1),
    ("audio_features.speechiness", 1)
]

index_name = collection.create_index(index_spec, name="idx_explicit_instrumental_speechiness")
print(f"Складений індекс '{index_name}' успішно створено!")


print("\n======================================================================")
print("КРОК 2: ПЕРЕВІРКА ВИКОРИСТАННЯ ІНДЕКСУ ЧЕРЕЗ EXPLAIN()")
print("======================================================================")

# Запускаємо explain для нашого пошуку
explain_output = db.command({
    "explain": {
        "find": collection.name,
        "filter": focus_query
    },
    "verbosity": "executionStats"
})

# Витягуємо ключові секції плану виконання
winning_plan = explain_output.get("queryPlanner", {}).get("winningPlan", {})
execution_stats = explain_output.get("executionStats", {})

print("\n--- СТРАТЕГІЯ ПОШУКУ (Winning Plan) ---")
# Перевіряємо, який етап вибрав двигун MongoDB
pprint.pprint(winning_plan)

print("\n--- СТАТИСТИКА ВИКОНАННЯ (Execution Stats) ---")
print(f"Час виконання запиту: {execution_stats.get('executionTimeMillis')} мс")
print(f"Кількість перевірених документів (docsExamined): {execution_stats.get('totalDocsExamined')}")
print(f"Кількість знайдених треків (nReturned): {execution_stats.get('nReturned')}")