# Промт: Ежедневный персональный AI-совет для участника

## Когда запускать
Каждое утро (7:00-9:00) для каждого участника с профилем.

## Что читать

Для каждого участника (`profiles/[ID]/`):
1. `index.html` — анкета: имя, город, профессия, цели, трекер, амбассадор
2. `planner.json` — checklist сессий (session_1..session_6), уровень
3. `tasks.json` — текущие задачи и прогресс
4. `advice-history.json` — предыдущие советы (чтобы не повторяться)

Общие данные:
5. `network/data.json` — роль в сети, рефералы, статус бенда
6. `team/core/analysis.json` — состояние команды

## Логика генерации

1. Определи **этап участника**:
   - Нет сессий → фокус на первую NEIRY-сессию
   - 1-3 сессии → мотивация продолжать, конкретный следующий шаг
   - 4-5 сессий → почти готово, финишная прямая
   - 6 сессий → чекап пройден, переход к программе

2. Учитывай **контекст**:
   - Профессию и интересы (предлагай релевантные эксперименты)
   - Наличие трекера (если нет — предложи подключить)
   - Амбассадорский статус (если да — про продажи и сеть)
   - Прошлые советы (не повторяй то же самое)

3. Каждый день **меняй фокус**:
   - Пн: сессия/данные
   - Вт: рефлексия
   - Ср: фитнес-данные
   - Чт: нетворкинг/сеть
   - Пт: итоги недели
   - Сб: отдых и наблюдение
   - Вс: планирование

## Формат ответа

### 1. Записать совет в `profiles/[ID]/advice.md`
2-4 предложения. Обращение по имени. Конкретное действие. Без воды.

### 2. Добавить запись в `profiles/[ID]/advice-history.json`

```json
{
  "history": [
    {
      "date": "2026-04-07",
      "advice": "Текст совета...",
      "focus": "session",
      "session_count": 0
    }
  ]
}
```

## Пример для бота (Python)

```python
import json, os
from datetime import datetime

def update_advice(profile_id, new_advice, focus):
    base = f"genesis/profiles/{profile_id}"

    # 1. Записать текущий совет
    with open(f"{base}/advice.md", "w") as f:
        f.write(new_advice)

    # 2. Добавить в историю
    history_path = f"{base}/advice-history.json"
    if os.path.exists(history_path):
        with open(history_path) as f:
            data = json.load(f)
    else:
        data = {"history": []}

    data["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "advice": new_advice,
        "focus": focus,
        "session_count": get_session_count(profile_id)
    })

    with open(history_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 3. git add + commit + push (после всех участников)
```

## Правила
- Обращайся по имени
- Не повторяй совет из вчера (проверь history)
- Один конкретный шаг, не список из 5 пунктов
- Если человек активен — хвали кратко, потом действие
- Если неактивен давно — мягко напомни, без давления
