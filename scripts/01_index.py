import os
import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Підключення до бази даних
client = MongoClient(os.environ["MONGO_URI"])
db = client["spotify"]
collection = db["tracks"]

# Визначаємо наш запит та сортування
filter_query = {
    "track_genre": "pop",
    "audio_features.danceability": {"$gte": 0.7}
}
sort_query = [("popularity", -1)]


print("======================================================================")
print("КРОК 1: АНАЛІЗ ПЛАНУ ВИКОНАННЯ БЕЗ ІНДЕКСІВ")
print("======================================================================")

# Оскільки в pymongo немає прямого методу .explain() у ланцюжку find(),
# ми використовуємо команду двигуна бази даних 'explain'
explain_before = db.command({
    "explain": {
        "find": collection.name,
        "filter": filter_query,
        "sort": dict(sort_query)
    },
    "verbosity": "executionStats"  # Обов'язково вказуємо цей режим для отримання статистики
})

# Витягуємо статистику виконання
execution_stats_before = explain_before.get("executionStats", {})
pprint.pprint(execution_stats_before)

# Зверніть увагу на executionTimeMillis та totalDocsExamined у виводі консолі.
# Без індексів totalDocsExamined дорівнюватиме загальній кількості треків у базі (~114k).


print("\n======================================================================")
print("КРОК 2: СТВОРЕННЯ СКЛАДЕНОГО ІНДЕКСУ ЗА ПРАВИЛОМ ESR")
print("======================================================================")

# Послідовність: Equality (track_genre) -> Sort (popularity) -> Range (danceability)
index_spec = [
    ("track_genre", 1),
    ("popularity", -1),
    ("audio_features.danceability", 1)
]

# Створюємо індекс
index_name = collection.create_index(index_spec, name="idx_genre_popularity_dance")
print(f"Індекс '{index_name}' успішно створено!")


print("\n======================================================================")
print("КРОК 3: ПОВТОРНИЙ АНАЛІЗ ПЛАНУ ВИКОНАННЯ ПІСЛЯ СТВОРЕННЯ ІНДЕКСУ")
print("======================================================================")

# Запускаємо explain знову
explain_after = db.command({
    "explain": {
        "find": collection.name,
        "filter": filter_query,
        "sort": dict(sort_query)
    },
    "verbosity": "executionStats"
})

execution_stats_after = explain_after.get("executionStats", {})
pprint.pprint(execution_stats_after)


print("\n======================================================================")
print("ПОРІВНЯЛЬНИЙ ПІДСУМОК:")
print("======================================================================")
print(f"Час виконання БЕЗ індексу: {execution_stats_before.get('executionTimeMillis')} мс")
print(f"Час виконання З індексом:  {execution_stats_after.get('executionTimeMillis')} мс")
print(f"Документів перевірено БЕЗ індексу: {execution_stats_before.get('totalDocsExamined')}")
print(f"Документів перевірено З індексом:  {execution_stats_after.get('totalDocsExamined')}")