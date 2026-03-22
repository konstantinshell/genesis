# Profile Generator — ONTO NOTHING

Автоматически генерирует HTML профили участников из шаблона и данных Obsidian.

---

## 🚀 Быстрый старт

```bash
cd /Users/konstantin/Documents/genesis/profile-generator
python3 generate_profiles.py
```

Результаты появятся в `/Users/konstantin/Documents/genesis/profile/[name]/index.html`

---

## 📁 Структура данных

Скрипт ожидает следующую структуру в Obsidian:

```
/Users/konstantin/Documents/Obsidian Vault/Данные участников/
├── Иван Иванов/
│   ├── profile.json              ← основные данные участника
│   └── reports/                  ← обработанные отчёты
│       ├── reflection.md         ← дневная рефлексия
│       ├── fitness_summary.json  ← здоровье (сердцебиение, сон, калории)
│       └── mnip_report.json      ← MNIP индекс и рекомендации
│
├── Мария Петрова/
│   ├── profile.json
│   └── reports/
│       ├── reflection.md
│       ├── fitness_summary.json
│       └── mnip_report.json
```

---

## 📋 Формат файлов

### profile.json

```json
{
  "name": "Иван Иванов",
  "phone": "+7 (999) 123-45-67",
  "city": "Москва",
  "birthdate": "1990-03-15T00:00:00",
  "age": 35,
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2026-03-20T10:30:00.123456",
  "sessions": [
    {
      "number": 1,
      "date": "2026-03-20T15:00:00",
      "file": "Session_1.md"
    }
  ]
}
```

**Поля:**
- `name` (обязательно) — имя и фамилия участника
- `phone` — номер телефона
- `city` — город
- `birthdate` — дата рождения (ISO формат) — возраст вычисляется автоматически
- `age` — если нет birthdate, используется это поле
- `avatar_url` — ссылка на аватар (если нет, используется заглушка)
- `sessions` — массив сессий (длина = текущий этап)

### reflection.md

```markdown
# Рефлексия — День 1

Сегодня я заметил улучшение в концентрации внимания.
Практика была очень продуктивной, чувствую себя отдохнувшим.
```

Скрипт извлекает основной текст (без заголовков и форматирования).

### fitness_summary.json

```json
{
  "avg_heartrate": 72,
  "avg_sleep": 7.5,
  "vo2_max": 42.3,
  "calories": 2150
}
```

**Поля:**
- `avg_heartrate` (int) — среднее сердцебиение за 7 дней (уд/мин)
- `avg_sleep` (float) — среднее количество часов сна
- `vo2_max` (float) — максимальное потребление кислорода (ml/kg/min)
- `calories` (int) — средние калории в день

### mnip_report.json

```json
{
  "score": 72,
  "progress": "+5 пункт за неделю",
  "recommendations": "Продолжайте медитативную практику, увеличьте продолжительность до 20 минут в день."
}
```

**Поля:**
- `score` (int) — MNIP индекс (0-100)
- `progress` (string) — текстовое описание прогресса
- `recommendations` (string) — рекомендации на основе данных

---

## 🛠️ Как пользователю это работает

1. **Участник загружает данные** через Telegram бота
2. **Коворкинг команда обрабатывает данные:**
   - Создаёт `/reports/` папку в папке участника
   - Обрабатывает сырые CSV/данные
   - Создаёт JSON отчёты (fitness_summary.json, mnip_report.json)
   - Пишет reflection.md из своего анализа
3. **Автор запускает скрипт:**
   ```bash
   python3 generate_profiles.py
   ```
4. **HTML профили генерируются** и готовы к публикации на GitHub Pages

---

## 📤 Вывод скрипта

```
======================================================================
🧠 ONTO NOTHING — Profile Generator
======================================================================
📁 Obsidian Vault: /Users/konstantin/Documents/Obsidian Vault/Данные участников
📄 Template: /Users/konstantin/Documents/genesis/profile-generator/profile_template.html
📤 Output: /Users/konstantin/Documents/genesis/profile
======================================================================

📊 Найдено участников: 2

✅ Иван Иванов → /profile/ivan-ivanov/index.html
✅ Мария Петрова → /profile/mariya-petrova/index.html

======================================================================
✨ Готово! Успешно создано: 2/2
======================================================================
```

---

## 🔧 Расширенное использование

### Запуск с логированием в файл

```bash
python3 generate_profiles.py > generation.log 2>&1
```

### Запуск каждый день (cron)

Добавьте в crontab:

```bash
0 8 * * * cd /Users/konstantin/Documents/genesis/profile-generator && python3 generate_profiles.py >> ~/.onto-nothing-profiles.log 2>&1
```

Это будет запускать скрипт каждый день в 8:00 утра.

### Автоматизация с Git

```bash
#!/bin/bash
# Скрипт для генерации и коммита профилей

cd /Users/konstantin/Documents/genesis

# Генерируем профили
python3 profile-generator/generate_profiles.py

# Коммитим новые/измененные профили
git add profile/
git commit -m "📊 Update profiles — $(date '+%Y-%m-%d %H:%M')"

# Пушим на GitHub (если нужно)
# git push origin main
```

Сохраните как `update-profiles.sh` и запускайте когда нужно обновить профили.

---

## ⚠️ Что случается если данных нет?

| Сценарий | Поведение |
|---|---|
| Нет `/reports/` папки | Используются значения по умолчанию (N/A, --) |
| Нет reflection.md | "Рефлексия будет доступна после первой сессии" |
| Нет fitness_summary.json | Значения по умолчанию (72 уд/мин, 7.5 ч, --, --) |
| Нет mnip_report.json | Стандартные рекомендации |
| Нет profile.json | Участник пропускается (warning) |

---

## 🎯 Что дальше

### Шаг 1: Коворкинг подготавливает данные

Для каждого участника в Obsidian создать:

```
Иван Иванов/
├── profile.json           ← уже создан ботом
└── reports/               ← ВЫ создаёте эту папку
    ├── reflection.md      ← обработанная рефлексия
    ├── fitness_summary.json ← обработанные метрики
    └── mnip_report.json   ← вычисленный MNIP индекс
```

### Шаг 2: Генерируете профили

```bash
python3 generate_profiles.py
```

### Шаг 3: Публикуете на GitHub Pages

```bash
cd /Users/konstantin/Documents/genesis
git add profile/
git commit -m "📊 Update participant profiles"
git push
```

Профили будут доступны по URL:
- `https://konstantinshell.github.io/genesis/profile/ivan-ivanov/`
- `https://konstantinshell.github.io/genesis/profile/mariya-petrova/`

---

## 🐛 Troubleshooting

### Ошибка: "Папка Obsidian не найдена"

Проверьте путь:
```bash
ls -la "/Users/konstantin/Documents/Obsidian Vault/Данные участников"
```

### Ошибка: "Шаблон не найден"

Проверьте что `profile_template.html` находится в той же папке:
```bash
ls -la /Users/konstantin/Documents/genesis/profile-generator/
```

### Профили не создаются

1. Проверьте что участник имеет `profile.json`:
   ```bash
   ls -la "/Users/konstantin/Documents/Obsidian Vault/Данные участников/Иван Иванов/"
   ```

2. Запустите скрипт с Python debug:
   ```bash
   python3 -u generate_profiles.py
   ```

---

## 📝 Версия

- v1.0 — начальная версия
- Создана: 22.03.2026
