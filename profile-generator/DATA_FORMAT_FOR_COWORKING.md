# Формат данных для Коворкинг команды

Этот документ описывает, как подготавливать обработанные данные участников для системы профилей.

---

## 📊 Процесс обработки данных

```
Telegram бот       Coworking Team      Profile Generator    GitHub Pages
    |                  |                      |                  |
    └─> raw data ────┬─> analysis ────> reports/ ────┬──> profiles ────┬──> Website
                     │   & processing         │       │               │
                     │                        │       └── HTML ──────┘
                     └─ metrics processing ──┘
```

---

## 🎯 Ваша задача (Coworking Team)

Для каждого участника в его папке Obsidian:

```
Константин Шель/
├── profile.json          ← создан ботом, ТРОГАТЬ НЕ НУЖНО
├── Session_1.md          ← сырые данные от бота
├── Session_2.md
├── metrics_1.csv
├── metrics_2.csv
└── reports/              ← ВЫ СОЗДАЁТЕ И ЗАПОЛНЯЕТЕ
    ├── reflection.md     ← обработанная рефлексия дня
    ├── fitness_summary.json
    └── mnip_report.json
```

---

## 📝 Шаг 1: Обработка рефлексии (reflection.md)

### Что получает ваша команда:

- `Session_1.md`, `Session_2.md` и т.д. с текстом участника
- Его заметки о том, как он себя чувствует

### Что вы создаёте:

**Файл:** `reports/reflection.md`

```markdown
# Главное на сегодня

Участник сообщает об улучшении концентрации внимания после медитативной практики.
Отмечает снижение уровня стресса на 15% по сравнению с прошлой неделей.
Качество сна улучшилось, наблюдается более глубокая фаза REM.
```

**Требования:**
- Заголовок: `# Главное на сегодня` или `# Рефлексия`
- Текст 2-4 предложения (актуальное резюме дня)
- Без сложного форматирования (скрипт извлекает основной текст)
- UTF-8 кодировка

**Как создавать:**
1. Прочитайте все `Session_N.md` файлы для этого участника
2. Синтезируйте главные выводы
3. Напишите краткое резюме
4. Сохраните в `reports/reflection.md`

---

## 📊 Шаг 2: Обработка фитнес данных (fitness_summary.json)

### Что получает ваша команда:

- `metrics_1.csv`, `metrics_2.csv` с данными трекера
- CSV с колонками: `date, heartrate, sleep, vo2_max, calories`

### Что вы создаёте:

**Файл:** `reports/fitness_summary.json`

```json
{
  "avg_heartrate": 72,
  "avg_sleep": 7.5,
  "vo2_max": 42.3,
  "calories": 2150
}
```

**Требования:**
- Все значения — средние за последние 7 дней
- `avg_heartrate` — целое число (уд/мин)
- `avg_sleep` — число с одной точкой (часов)
- `vo2_max` — число с одной точкой (ml/kg/min)
- `calories` — целое число (ккал в день)

**Как создавать:**
1. Откройте все CSV файлы участника
2. Возьмите данные за последние 7 дней
3. Вычислите средние значения:
   ```python
   import pandas as pd

   df = pd.read_csv('metrics.csv')
   df['date'] = pd.to_datetime(df['date'])
   last_7_days = df[df['date'] >= df['date'].max() - pd.Timedelta(days=7)]

   summary = {
     "avg_heartrate": int(last_7_days['heartrate'].mean()),
     "avg_sleep": round(last_7_days['sleep'].mean(), 1),
     "vo2_max": round(last_7_days['vo2_max'].mean(), 1),
     "calories": int(last_7_days['calories'].mean())
   }
   ```
4. Сохраните в `reports/fitness_summary.json`

**Если данных нет:**
- Используйте defaults: `{"avg_heartrate": 72, "avg_sleep": 7.5, "vo2_max": "--", "calories": "--"}`

---

## 🧠 Шаг 3: Вычисление MNIP Индекса (mnip_report.json)

### Что получает ваша команда:

- Все сырые данные EEG/BCI от Neiry
- Фитнес метрики
- Заметки участника о самочувствии

### Что вы создаёте:

**Файл:** `reports/mnip_report.json`

```json
{
  "score": 72,
  "progress": "+8 пунктов за неделю (28%)",
  "recommendations": "Продолжайте медитативную практику по 20 минут ежедневно. Уровень нейропластичности растет стабильно. Рекомендуется увеличить интенсивность дыхательных упражнений на 5-10%."
}
```

**Требования:**
- `score` — число от 0 до 100 (MNIP индекс)
- `progress` — текстовое описание изменения за период
- `recommendations` — практические советы на основе данных (2-3 предложения)

**Как вычислять MNIP:**

MNIP (Multidimensional Neuroplasticity Index) комбинирует несколько факторов:

```
MNIP = (EEG_coherence × 0.3) + (Heart_rate_variability × 0.2) +
       (Sleep_quality × 0.2) + (Meditation_consistency × 0.15) +
       (Cognitive_performance × 0.15)
```

Где:
- `EEG_coherence` — согласованность мозговых волн (из EEG данных)
- `Heart_rate_variability` — вариабельность сердечного ритма
- `Sleep_quality` — качество сна (из фитнес трекера)
- `Meditation_consistency` — регулярность практики
- `Cognitive_performance` — когнитивная производительность (из тестов)

**Пример Python расчета:**

```python
def calculate_mnip(eeg_data, hrv, sleep_hours, sessions_count, cognitive_score):
    """Вычисляет MNIP индекс"""

    # Нормализуем EEG когерентность (0-100)
    eeg_norm = min(100, eeg_data['coherence'] * 100)

    # Нормализуем HRV (обычно 20-100 ms)
    hrv_norm = min(100, (hrv / 100) * 100)

    # Нормализуем сон (хорошо = 7-9 часов)
    sleep_norm = min(100, (sleep_hours / 9) * 100)

    # Нормализуем консистентность (количество сессий)
    consistency_norm = min(100, sessions_count * 10)

    # Нормализуем когнитивный тест (обычно 0-100)
    cognitive_norm = cognitive_score

    # Вычисляем MNIP
    mnip = (eeg_norm * 0.3 +
            hrv_norm * 0.2 +
            sleep_norm * 0.2 +
            consistency_norm * 0.15 +
            cognitive_norm * 0.15)

    return round(mnip, 1)

# Пример использования
mnip_score = calculate_mnip(
    eeg_data={'coherence': 0.65},
    hrv=65,
    sleep_hours=7.5,
    sessions_count=4,
    cognitive_score=78
)
# Результат: ~72
```

**Как создавать:**
1. Соберите все доступные данные участника
2. Вычислите MNIP по формуле выше
3. Сравните с прошлой неделей (прогресс)
4. Напишите рекомендации на основе слабых областей
5. Сохраните в `reports/mnip_report.json`

**Минимальный MNIP (если данных нет):**
```json
{
  "score": 50,
  "progress": "Недостаточно данных",
  "recommendations": "Продолжайте отслеживание. Индекс вычислится после достаточного количества сессий."
}
```

---

## ✅ Чек-лист для коворкинг команды

После обработки данных участника проверьте:

- [ ] Файл `reports/reflection.md` существует и содержит текст
- [ ] Файл `reports/fitness_summary.json` содержит все 4 метрики
- [ ] Файл `reports/mnip_report.json` содержит score, progress, recommendations
- [ ] Все JSON файлы валидны (проверьте в [jsonlint.com](https://jsonlint.com))
- [ ] Файл `profile.json` не изменён (ботом управляется)
- [ ] UTF-8 кодировка во всех файлах

---

## 🚀 Полный процесс для одного участника

### День 1-7: Участник отправляет данные

Telegram → Obsidian (по сессиям)

```
Константин Шель/
├── profile.json       ← бот создал
├── Session_1.md       ← бот создал (текст)
├── metrics_1.csv      ← бот загрузил (CSV)
└── Session_2.md
```

### После 7 дней: Коворкинг обрабатывает

```
Константин Шель/
├── profile.json
├── Session_1.md
├── metrics_1.csv
└── reports/           ← ВЫ создаёте
    ├── reflection.md  ← текст на основе сессий
    ├── fitness_summary.json  ← числа из CSV
    └── mnip_report.json      ← рассчитанный индекс
```

### Генерация профиля:

```bash
python3 generate_profiles.py
```

Результат:
```
✅ Константин Шель → /profile/konstantin-shell/index.html
```

### Публикация:

```bash
git add profile/
git commit -m "📊 Профиль Константина"
git push
```

Профиль готов: `https://konstantinshell.github.io/genesis/profile/konstantin-shell/`

---

## 📧 Контакты по вопросам

Если у вас есть вопросы по форматам данных:
- Проверьте примеры выше
- Запустите `generate_profiles.py` и посмотрите на ошибки
- Убедитесь что JSON валиден (используйте [jsonlint.com](https://jsonlint.com))

