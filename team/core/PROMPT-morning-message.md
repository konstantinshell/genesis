# Промт: Утреннее сообщение участникам

## Когда запускать
Каждый день. Бот проверяет timezone каждого участника и отправляет в **8:00 локального времени**.

## Как определить время

```python
from datetime import datetime
import pytz

def is_morning(timezone_str, target_hour=8):
    """Проверяет, наступило ли утро (8:00) в часовом поясе участника"""
    tz = pytz.timezone(timezone_str)
    local_now = datetime.now(tz)
    return local_now.hour == target_hour and local_now.minute < 15
```

## Часовые пояса участников (из network/data.json → timezone)

| Timezone | UTC | Участники |
|----------|-----|-----------|
| Europe/Moscow | +3 | Большинство (Москва, Ставрополь, Сочи, Подмосковье) |
| Asia/Yekaterinburg | +5 | Вадим (Чусовой), Вероника (Челябинск) |
| Asia/Colombo | +5:30 | Вячеслав (Шри-Ланка) |
| Asia/Ho_Chi_Minh | +7 | Константин, Яна (Нячанг) |
| Asia/Makassar | +8 | Валентина (Бали) |

## Что отправляет бот

### Утреннее сообщение (8:00 локального)

```
Доброе утро, {имя}! ☀️

Что ты планируешь создать сегодня? Как собираешься отдохнуть?

Запиши утреннюю рефлексию — это занимает 2 минуты.
```

**Кнопка:** `[🌅 Утренняя рефлексия]` → `t.me/ritmnothingbot?start=morning`

### Вечернее сообщение (21:00 локального)

```
Добрый вечер, {имя} 🌙

Как прошёл день? Что получилось, что не получилось?
```

**Кнопка:** `[🌙 Вечерняя рефлексия]` → `t.me/ritmnothingbot?start=evening`

## Код для бота (Python)

```python
import json, pytz
from datetime import datetime

def get_participants_for_morning():
    """Возвращает список участников, у которых сейчас 8 утра"""
    with open('genesis/network/data.json') as f:
        net = json.load(f)

    ready = []

    def walk(node):
        if not node.get('real'): return
        tz_str = node.get('timezone', 'Europe/Moscow')
        tg = node.get('tg')
        name = node.get('name', '').split()[0]  # Имя
        if tg and is_morning(tz_str, 8):
            ready.append({'tg': tg, 'name': name, 'timezone': tz_str})
        for ch in node.get('children', []):
            walk(ch)

    for ch in net.get('children', []):
        walk(ch)

    return ready

def is_morning(tz_str, hour):
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    return now.hour == hour and now.minute < 15

# Запускать каждые 15 минут через cron:
# */15 * * * * python3 send_morning.py
```

## Важно
- Проверять каждые 15 минут (чтобы покрыть все часовые пояса)
- Не отправлять повторно (хранить в Redis/файле дату последней отправки)
- Выходные: можно смягчить тон, убрать "создать", оставить "отдохнуть"
- Если участник неактивен >7 дней — добавить мягкое напоминание
