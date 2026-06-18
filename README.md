# Завдання 1. Аналітична платформа для музичного стрімінгового сервісу

## Частина 1 — Завантаження даних та проєктування схеми

### 1.1. Завантаження сирих даних

Скрипт завантаження трохи доопрацьовано.

Додано: 

```python
path = kagglehub.dataset_download("maharshipandya/-spotify-tracks-dataset")
print("Path to dataset files:", path)
```

Протокол завантаження:

```
Path to dataset files: ~/.cache/kagglehub/datasets/maharshipandya/-spotify-tracks-dataset/versions/1
Завантажуємо114000 треків...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 114/114 [04:43<00:00,  2.48s/it]
Завантажено документів:113999
Приклад документа:
{'_id': ObjectId('6a33d8e204bc20659c04115e'), 'Unnamed: 0': 0, 'track_id': '5SuOikwiRyPMVoIQDJUgSV', 'artists': 'Gen Hoshino', 'album_name': 'Comedy', 'track_name': 'Comedy', 'popularity': 73, 'duration_ms': 230666, 'explicit': False, 'danceability': 0.676, 'energy': 0.461, 'key': 1, 'loudness': -6.746, 'mode': 0, 'speechiness': 0.143, 'acousticness': 0.0322, 'instrumentalness': 1.01e-06, 'liveness': 0.358, 'valence': 0.715, 'tempo': 87.917, 'time_signature': 4, 'track_genre': 'acoustic'}
```

### 1.2. Трансформація схеми через Aggregation Pipeline

Для трансформації використаємо скрипт на Python з pipeline scripts/02_transform.py.


Протокол трансформації:

```
Запуск агрегації через Python...
Трансформацію завершено! Документів у tracks: 113999
Приклад документа:
{'_id': ObjectId('6a33d8e204bc20659c04115e'), 'track_id': '5SuOikwiRyPMVoIQDJUgSV', 'album_name': 'Comedy', 'track_name': 'Comedy', 'popularity': 73, 'duration_ms': 230666, 'explicit': False, 'track_genre': 'acoustic', 'artists': ['Gen Hoshino'], 'audio_features': {'danceability': 0.676, 'energy': 0.461, 'loudness': -6.746, 'speechiness': 0.143, 'acousticness': 0.0322, 'instrumentalness': 1.01e-06, 'liveness': 0.358, 'valence': 0.715, 'tempo': 87.917, 'key': 1, 'mode': 0, 'time_signature': 4}, 'duration_sec': 230.7, 'popularity_tier': 'high'}
```

1. Чому аудіо-характеристики винесені в окремий об’єкт audio_features, а не зберігаються плоско? Коли таке вкладення вигідне, а коли створює проблеми?

Згрупувавши технічні метрики в audio_features, ми відокремили базову метаінформацію про трек, від специфічних фіч, які потрібні лише для аналітики чи рекомендаційних алгоритмів.
Якщо потрібно отримати значення фічі, синтаксис запитів стає довшим, бо доводиться повсюди використовувати "крапкову нотацію".


2. Чому виконавці зберігаються як масив, а не як рядок? Які запити стають простішими?

Якщо поле є рядком, MongoDB будує звичайний індекс. Якщо поле є масивом, MongoDB автоматично створює так званий Multikey-індекс. Це означає, що база даних створює окремий індексний запис для кожного елемента масиву.

Коли дані лежать у масиві, синтаксис MongoDB дозволяє робитизапити без використання важких регулярних виразів чи розбиття рядків на льоту.
Наприклад, пошук треків конкретного виконавця, підрахунок треків для кожного артиста або фільтрація за кількістю авторів.

3. Що таке $out і чим він відрізняється від $merge? Коли використовувати кожен?

Оператор $out бере результат агрегації і записує його в колекцію. Якщо вказана колекція вже існувала, $out повністю видаляє її разом з усіма старими документами та індексами, а на її місці створює нову, куди записує лише свіжі результати агрегації.

Оператор $merge не видаляє стару колекцію. Замість цього він порівнює нові документи зі старими за унікальним ключем (зазвичай за _id) і виконує злиття (апдейт) даних.

Для початкової трансформації сирого датасету Spotify у нову чисту структуру $out є правильним рішенням, бо він гарантує, що в базі не залишиться "сміття" від попередніх невдалих тестів. Але якби цей додаток працював у реальному часі й стрімив нові треки щохвилини, ми б перейшли на $merge.

## Частина 2 — Запити до даних

### Завдання 1. Треки для вечірки

scripts/01_find.py

```
=== ТОП ТРЕКІВ ДЛЯ ВЕЧІРКИ (FIND) ===
[{'track_name': 'Hold On - Remix', 'popularity': 56, 'artists': ['Chord Overstreet', 'Deepend'], 'duration_sec': 188.1}, {'track_name': 'Kaleidoscope', 'popularity': 62, 'artists': ['A Great Big World'], 'duration_sec': 229.3}, {'track_name': 'アジアの純真', 'popularity': 32, 'artists': ['Yosui Inoue', 'Tamio Okuda'], 'duration_sec': 233.3}, {'track_name': 'All My Loving (Original Version)', 'popularity': 31, 'artists': ['Masaharu Fukuyama'], 'duration_sec': 245.8}, {'track_name': 'Outside Villanova', 'popularity': 29, 'artists': ['Eric Hutchinson'], 'duration_sec': 255.7}, {'track_name': 'I Wanna Be Your Ghost (feat. Ghosts)', 'popularity': 50, 'artists': ['Gen Hoshino'], 'duration_sec': 225.5}, {'track_name': 'Rocksteady', 'popularity': 28, 'artists': ['Marc Broussard'], 'duration_sec': 243.8}, {'track_name': 'A Million Years', 'popularity': 28, 'artists': ['Johnnyswim'], 'duration_sec': 219.9}, {'track_name': '青空、ひとりきり - Remastered 2018', 'popularity': 26, 'artists': ['Yosui Inoue'], 'duration_sec': 260.9}, {'track_name': 'Terapia', 'popularity': 39, 'artists': ['BaianaSystem'], 'duration_sec': 261.4}]
```

### Завдання 2. Виконавці, у яких усі треки популярні

scripts/02_find.py

```
=== ТОП-20 ПОПУЛЯРНИХ АРТИСТІВ ===
[{'min_popularity': 89, 'artist_name': 'Harry Styles', 'tracks_count': 3, 'avg_popularity': 92.0}, {'min_popularity': 90, 'artist_name': 'Luar La L', 'tracks_count': 4, 'avg_popularity': 90.5}, {'min_popularity': 86, 'artist_name': 'Olivia Rodrigo', 'tracks_count': 5, 'avg_popularity': 87.4}, {'min_popularity': 87, 'artist_name': 'BYOR', 'tracks_count': 4, 'avg_popularity': 87.0}, {'min_popularity': 79, 'artist_name': 'IVE', 'tracks_count': 3, 'avg_popularity': 84.0}, {'min_popularity': 76, 'artist_name': 'Måneskin', 'tracks_count': 12, 'avg_popularity': 83.7}, {'min_popularity': 77, 'artist_name': 'Lil Nas X', 'tracks_count': 11, 'avg_popularity': 83.5}, {'min_popularity': 81, 'artist_name': 'Morgan Wallen', 'tracks_count': 3, 'avg_popularity': 83.3}, {'min_popularity': 80, 'artist_name': 'One Direction', 'tracks_count': 5, 'avg_popularity': 83.0}, {'min_popularity': 80, 'artist_name': 'TV Girl', 'tracks_count': 5, 'avg_popularity': 82.0}, {'min_popularity': 81, 'artist_name': 'Mac DeMarco', 'tracks_count': 4, 'avg_popularity': 81.5}, {'min_popularity': 81, 'artist_name': 'Cults', 'tracks_count': 3, 'avg_popularity': 81.3}, {'min_popularity': 79, 'artist_name': 'Ricky Montgomery', 'tracks_count': 4, 'avg_popularity': 80.5}, {'min_popularity': 79, 'artist_name': 'Luke Combs', 'tracks_count': 3, 'avg_popularity': 80.3}, {'min_popularity': 80, 'artist_name': 'Declan McKenna', 'tracks_count': 3, 'avg_popularity': 80.0}, {'min_popularity': 80, 'artist_name': 'Joy Again', 'tracks_count': 3, 'avg_popularity': 80.0}, {'min_popularity': 69, 'artist_name': 'Mora', 'tracks_count': 7, 'avg_popularity': 79.7}, {'min_popularity': 70, 'artist_name': 'Maroon 5', 'tracks_count': 3, 'avg_popularity': 79.7}, {'min_popularity': 73, 'artist_name': 'Beach Bunny', 'tracks_count': 7, 'avg_popularity': 79.4}, {'min_popularity': 75, 'artist_name': 'HVME', 'tracks_count': 3, 'avg_popularity': 79.0}]
```

### Завдання 3. Нетипові треки

scripts/03_find.py

```
Аналізуємо жанри на наявність треків з аномальним темпом...

Знайдено жанрів з аномальними треками: 112
...
```

### Завдання 4: Треки для фонової роботи

scripts/04_find.py

```
=== ТОП-10 ТРЕКІВ ДЛЯ ФОНОВОЇ РОБОТИ ТА КОНЦЕНТРАЦІЇ ===
[{'album_name': 'everything i wanted', 'track_name': 'everything i wanted', 'popularity': 86, 'track_genre': 'electro', 'artists': ['Billie Eilish'], 'audio_features': {'loudness': -14.454, 'instrumentalness': 0.657}}, {'album_name': 'Best White Noise for Baby Sleep - Loopable with No Fade', 'track_name': 'Clean White Noise - Loopable with no fade', 'popularity': 85, 'track_genre': 'sleep', 'artists': ['White Noise Baby Sleep', 'White Noise for Babies'], 'audio_features': {'loudness': -28.46, 'instrumentalness': 1.0}}, {'album_name': 'In A Time Lapse', 'track_name': 'Experience', 'popularity': 79, 'track_genre': 'ambient', 'artists': ['Ludovico Einaudi', 'Daniel Hope', 'I Virtuosi Italiani'], 'audio_features': {'loudness': -10.634, 'instrumentalness': 0.961}}, {'album_name': 'In A Time Lapse', 'track_name': 'Experience', 'popularity': 79, 'track_genre': 'classical', 'artists': ['Ludovico Einaudi', 'Daniel Hope', 'I Virtuosi Italiani'], 'audio_features': {'loudness': -10.634, 'instrumentalness': 0.961}}, {'album_name': 'Show Me How', 'track_name': 'Show Me How', 'popularity': 79, 'track_genre': 'indie', 'artists': ['Men I Trust'], 'audio_features': {'loudness': -11.997, 'instrumentalness': 0.534}}, {'album_name': 'Show Me How', 'track_name': 'Show Me How', 'popularity': 79, 'track_genre': 'indie-pop', 'artists': ['Men I Trust'], 'audio_features': {'loudness': -11.997, 'instrumentalness': 0.534}}, {'album_name': 'Cigarettes After Sex', 'track_name': 'K.', 'popularity': 78, 'track_genre': 'ambient', 'artists': ['Cigarettes After Sex'], 'audio_features': {'loudness': -10.261, 'instrumentalness': 0.846}}, {'album_name': 'Cigarettes After Sex', 'track_name': 'K.', 'popularity': 78, 'track_genre': 'indie', 'artists': ['Cigarettes After Sex'], 'audio_features': {'loudness': -10.261, 'instrumentalness': 0.846}}, {'album_name': 'Cigarettes After Sex', 'track_name': 'K.', 'popularity': 78, 'track_genre': 'indie-pop', 'artists': ['Cigarettes After Sex'], 'audio_features': {'loudness': -10.261, 'instrumentalness': 0.846}}, {'album_name': 'melanchole', 'track_name': 'i was all over her', 'popularity': 77, 'track_genre': 'indie-pop', 'artists': ['salvia palth'], 'audio_features': {'loudness': -12.835, 'instrumentalness': 0.853}}]
```
