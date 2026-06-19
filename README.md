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

1. Для чого використовується інструкція $unwind?

Коли документ містить масив, стандартні операції фільтрації або групування бачать цей масив як єдине ціле. Інструкція $unwind розбиває один такий документ на кілька окремих документів — по одному для кожного елемента масиву.

2. Чим $stdDevPop відрізняється від $stdDevSamp?

$stdDevPop рахує відхилення для всієї генеральної сукупності (Повна генеральна сукупність (Population), Ділиться на N), а $stdDevSamp — лише для її частини (Статистична вибірка (Sample), Ділиться на N−1).

## Частина 3 — Аналітика через Aggregation Pipeline

### Завдання 1. Топ-10 виконавців за середньою популярністю

scripts/01_aggr.py

```
Розраховуємо топ-10 найпопулярніших виконавців...

=== ТОП-10 ВИКОНАВЦІВ ЗА СЕРЕДНЬОЮ ПОПУЛЯРНІСТЮ ===
[{'artist_name': 'Olivia Rodrigo', 'avg_popularity': 87.4}, {'artist_name': 'Måneskin', 'avg_popularity': 83.7}, {'artist_name': 'Lil Nas X', 'avg_popularity': 83.5}, {'artist_name': 'One Direction', 'avg_popularity': 83.0}, {'artist_name': 'TV Girl', 'avg_popularity': 82.0}, {'artist_name': 'Bomba Estéreo', 'avg_popularity': 81.5}, {'artist_name': 'Mora', 'avg_popularity': 79.7}, {'artist_name': 'Beach Bunny', 'avg_popularity': 79.4}, {'artist_name': 'Mitski', 'avg_popularity': 78.9}, {'artist_name': 'Jhay Cortez', 'avg_popularity': 78.7}]
```

### Завдання 2. Розподіл треків за настроєм

scripts/02_aggr.py

```
Аналізуємо емоційну карту треків за моделлю валентності та енергії...

=== РАСПОДІЛ МУЗИЧНОГО МАСИВУ ЗА НАСТРОЄМ ===
[{'tracks_count': 43404, 'mood': 'happy'}, {'tracks_count': 38761, 'mood': 'angry'}, {'tracks_count': 23086, 'mood': 'sad'}, {'tracks_count': 8748, 'mood': 'calm'}]
```

### Завдання 3. Найбільш «танцювальний» жанр

scripts/03_aggr.py

```
=== ТОП-10 НАЙКРАЩИХ МУЗИЧНИХ ЖАНРІВ ДЛЯ ТАНЦІВ ===
[{'tracks_count': 1000, 'genre': 'kids', 'avg_danceability': 0.779, 'avg_energy': 0.613, 'avg_valence': 0.681}, {'tracks_count': 1000, 'genre': 'chicago-house', 'avg_danceability': 0.766, 'avg_energy': 0.733, 'avg_valence': 0.587}, {'tracks_count': 1000, 'genre': 'reggaeton', 'avg_danceability': 0.759, 'avg_energy': 0.739, 'avg_valence': 0.643}, {'tracks_count': 1000, 'genre': 'latino', 'avg_danceability': 0.757, 'avg_energy': 0.732, 'avg_valence': 0.63}, {'tracks_count': 1000, 'genre': 'reggae', 'avg_danceability': 0.745, 'avg_energy': 0.726, 'avg_valence': 0.648}, {'tracks_count': 1000, 'genre': 'hip-hop', 'avg_danceability': 0.736, 'avg_energy': 0.683, 'avg_valence': 0.551}, {'tracks_count': 1000, 'genre': 'dancehall', 'avg_danceability': 0.734, 'avg_energy': 0.685, 'avg_valence': 0.629}, {'tracks_count': 1000, 'genre': 'minimal-techno', 'avg_danceability': 0.729, 'avg_energy': 0.68, 'avg_valence': 0.284}, {'tracks_count': 1000, 'genre': 'detroit-techno', 'avg_danceability': 0.723, 'avg_energy': 0.711, 'avg_valence': 0.469}, {'tracks_count': 1000, 'genre': 'latin', 'avg_danceability': 0.722, 'avg_energy': 0.727, 'avg_valence': 0.631}]
```

1. У запиті 1 ми фільтруємо виконавців, у яких менше 5 треків. Як зміниться результат, якщо знизити поріг до 1? А що станеться, якщо вибирати виконавців із більш ніж 50 треками? Поясніть результат.

Якщо ми дозволимо брати участь в аналізі виконавцям, які мають у базі хоча б один-єдиний трек, результат топ-10 повністю зміниться і заповниться невідомими (нішевими) артистами. Без обмеження мінімальної кількості треків, автори одного випадкового суперхіта витіснять реальних лідерів індустрії з перших позицій рейтингу.

Якщо ми встановимо жорсткий фільтр — брати лише тих, у кого в базі є понад 50 треків, результат топ-10 знову зміниться, але тепер у протилежний бік. Зі списку зникнуть нішеві та молоді поп-зірки, а сам топ стане набагато стабільнішим та "елітнішим". Коли у виконавця більше 50 треків, його середня популярність стає максимально об'єктивною. Випадкові коливання одного успішного синглу більше не мають вирішального значення. Середній показник відображає стабільний довготривалий інтерес слухачів до всієї дискографії артиста.

2. У запиті 3 ми фільтруємо жанри з менше ніж 100 треками. Чи зміниться результат, якщо знизити поріг до 50? Поясніть результат.

Зниження порогу зі 100 до 50 треків для фільтрації жанрів практично не змінить фінальний результат (топ-10 найкращих танцювальних жанрів), проте цей крок несе в собі серйозні ризики для аналітики. У цьому датасеті кожен основний музичний жанр (наприклад, pop, rock, hip-hop, dance, alternative, acoustic тощо) представлений фіксованою та досить великою кількістю треків — рівно 1000 документів на один жанр. Відповідно, математичне середнє ($avg) для кожного з них прорахується по тих самих документах, і лідери танцювального топу залишаться на своїх місцях.

Якби ви збирали дані з стрімінгу Spotify в реальному часі без попередньої фільтрації датасету, зниження порогу до 50 треків могло б призвести до таких наслідків: у базі могли б з'явитися дуже специфічні або локальні теги (наприклад, якийсь рідкісний піджанр електронної музики на кшталт "uk-hardcore-revival"), представлений всього 55 треками.

Для поточного очищеного датасету зміна порогу зі 100 до 50 нічого не змінить, бо жанри великі й стабільні. Проте залишати поріг не менше 100 — це хороша інженерна практика (Best Practice), яка гарантує, що аналітична модель захищена від «шуму» та випадкових аномалій у майбутньому, якщо база даних почне розширюватися новими сирими треками.

## Частина 4 — Індекси та оптимізація

### Завдання 1. Аналіз запиту та індексація

scripts/01_index.py

```
======================================================================
КРОК 1: АНАЛІЗ ПЛАНУ ВИКОНАННЯ БЕЗ ІНДЕКСІВ
======================================================================
{'executionStages': {'advanced': 354,
                     'executionTimeMillisEstimate': 83,
                     'inputStage': {'advanced': 354,
                                    'direction': 'forward',
                                    'docsExamined': 113999,
                                    'executionTimeMillisEstimate': 80,
                                    'filter': {'$and': [{'track_genre': {'$eq': 'pop'}},
                                                        {'audio_features.danceability': {'$gte': 0.7}}]},
                                    'isEOF': 1,
                                    'nReturned': 354,
                                    'needTime': 113645,
                                    'needYield': 0,
                                    'restoreState': 5,
                                    'saveState': 5,
                                    'stage': 'COLLSCAN',
                                    'works': 114000},
                     'isCached': False,
                     'isEOF': 1,
                     'memLimit': 33554432,
                     'nReturned': 354,
                     'needTime': 114000,
                     'needYield': 0,
                     'restoreState': 5,
                     'saveState': 5,
                     'sortPattern': {'popularity': -1},
                     'spilledDataStorageSize': 0,
                     'spills': 0,
                     'stage': 'SORT',
                     'totalDataSizeSorted': 197854,
                     'type': 'simple',
                     'usedDisk': False,
                     'works': 114355},
 'executionSuccess': True,
 'executionTimeMillis': 83,
 'nReturned': 354,
 'totalDocsExamined': 113999,
 'totalKeysExamined': 0}

======================================================================
КРОК 2: СТВОРЕННЯ СКЛАДЕНОГО ІНДЕКСУ ЗА ПРАВИЛОМ ESR
======================================================================
Індекс 'idx_genre_popularity_dance' успішно створено!

======================================================================
КРОК 3: ПОВТОРНИЙ АНАЛІЗ ПЛАНУ ВИКОНАННЯ ПІСЛЯ СТВОРЕННЯ ІНДЕКСУ
======================================================================
{'executionStages': {'advanced': 354,
                     'alreadyHasObj': 0,
                     'docsExamined': 354,
                     'executionTimeMillisEstimate': 0,
                     'inputStage': {'advanced': 354,
                                    'direction': 'forward',
                                    'dupsDropped': 0,
                                    'dupsTested': 0,
                                    'executionTimeMillisEstimate': 0,
                                    'indexBounds': {'audio_features.danceability': ['[0.7, '
                                                                                    'inf.0]'],
                                                    'popularity': ['[MaxKey, '
                                                                   'MinKey]'],
                                                    'track_genre': ['["pop", '
                                                                    '"pop"]']},
                                    'indexName': 'idx_genre_popularity_dance',
                                    'indexVersion': 2,
                                    'isEOF': 1,
                                    'isMultiKey': False,
                                    'isPartial': False,
                                    'isSparse': False,
                                    'isUnique': False,
                                    'keyPattern': {'audio_features.danceability': 1,
                                                   'popularity': -1,
                                                   'track_genre': 1},
                                    'keysExamined': 412,
                                    'multiKeyPaths': {'audio_features.danceability': [],
                                                      'popularity': [],
                                                      'track_genre': []},
                                    'nReturned': 354,
                                    'needTime': 57,
                                    'needYield': 0,
                                    'restoreState': 0,
                                    'saveState': 0,
                                    'seeks': 58,
                                    'stage': 'IXSCAN',
                                    'works': 412},
                     'isCached': False,
                     'isEOF': 1,
                     'nReturned': 354,
                     'needTime': 57,
                     'needYield': 0,
                     'restoreState': 0,
                     'saveState': 0,
                     'stage': 'FETCH',
                     'works': 412},
 'executionSuccess': True,
 'executionTimeMillis': 2,
 'nReturned': 354,
 'totalDocsExamined': 354,
 'totalKeysExamined': 412}

======================================================================
ПОРІВНЯЛЬНИЙ ПІДСУМОК:
======================================================================
Час виконання БЕЗ індексу: 83 мс
Час виконання З індексом:  2 мс
Документів перевірено БЕЗ індексу: 113999
Документів перевірено З індексом:  354
```

1. Що змінилося в плані виконання?

До створення індексу запит виконувався за 82 мс. Після створення індексу час впав до 2 мс.

2. Як зрозуміти, що індекс використовується? Наведіть скріншот або значення полів із explain(), які це підтверджують.

totalDocsExamined: Після створення індексу це число стало рівним кількості документів (354), які реально повернув запит (nReturned). Це означає, що MongoDB більше не читає «зайві» документи з диска.

### Завдання 2. Індекс для інших полів

scripts/02_index.py

```
======================================================================
КРОК 1: СТВОРЕННЯ СКЛАДЕНОГО ІНДЕКСУ ДЛЯ ФОКУС-ЗАПИТІВ
======================================================================
Складений індекс 'idx_explicit_instrumental_speechiness' успішно створено!

======================================================================
КРОК 2: ПЕРЕВІРКА ВИКОРИСТАННЯ ІНДЕКСУ ЧЕРЕЗ EXPLAIN()
======================================================================

--- СТРАТЕГІЯ ПОШУКУ (Winning Plan) ---
{'inputStage': {'direction': 'forward',
                'indexBounds': {'audio_features.instrumentalness': ['(0.5, '
                                                                    'inf.0]'],
                                'audio_features.speechiness': ['[-inf.0, 0.1)'],
                                'explicit': ['[false, false]']},
                'indexName': 'idx_explicit_instrumental_speechiness',
                'indexVersion': 2,
                'isMultiKey': False,
                'isPartial': False,
                'isSparse': False,
                'isUnique': False,
                'keyPattern': {'audio_features.instrumentalness': 1,
                               'audio_features.speechiness': 1,
                               'explicit': 1},
                'multiKeyPaths': {'audio_features.instrumentalness': [],
                                  'audio_features.speechiness': [],
                                  'explicit': []},
                'stage': 'IXSCAN'},
 'isCached': False,
 'stage': 'FETCH'}

--- СТАТИСТИКА ВИКОНАННЯ (Execution Stats) ---
Час виконання запиту: 52 мс
Кількість перевірених документів (docsExamined): 16141
Кількість знайдених треків (nReturned): 16141
```

MongoDB не використовує COLLSCAN. Головний етап (stage) має значення IXSCAN, а всередині нього вказано назву нового індексу. Показник docsExamined  дорівнює nReturned. Тобто жодної зайвої операції зчитування не було виконано.

### Завдання 3. Покривний запит

```javascript
db.tracks.find({
  track_genre: "pop",
  popularity: { $gte: 70 }
});
```

Питання: Чи є цей запит покривним (covered query)? Надайте розгорнуту та обґрунтовану відповідь у файлі README.

Цей запит не є покривним (not a covered query), попри те, що для його полів частково існує відповідний індекс.

Для того щоб запит став покривним, мають одночасно виконуватися дві умови:
* Індекс повинен включати всі поля фільтрації запиту.
* Запит повинен повертати (через проєкцію) тільки ті поля, які заіндексовані, і обов'язково вимикати унікальний ідентифікатор _id, якщо його немає в індексі.

У нашому випадку обидві умови порушено.

Щоб змусити цей запит працювати виключно в межах індексу без звернення до колекції, потрібно виконати дві умови в коді:
* Запитувати лише ті поля, які є в індексі (track_genre, popularity).
* Явно вимкнути поле _id в об'єкті проєкції за допомогою 0.

```javascript
db.tracks.find(
  { 
    track_genre: "pop", 
    popularity: { $gte: 70 } 
  }, 
  { 
    _id: 0,             // 1. Обов'язково вимикаємо _id
    track_genre: 1,     // 2. Беремо поле з індексу
    popularity: 1       // 3. Беремо поле з індексу
  }
);
```