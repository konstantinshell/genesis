# ONTO NOTHING — Profile System Complete Guide

Полная документация системы автоматического создания профилей участников исследования.

---

## 🎯 Что было создано

Встроенная система для автоматического создания индивидуальных HTML профилей участников:

```
Telegram Bot          Obsidian Vault         Profile Generator      GitHub Pages
    ↓                     ↓                         ↓                    ↓
User sends            Raw data stored       Processes data        Published
data via Telegram ──→ (sessions, CSV)  ──→ & generates HTML  ──→ profile pages
                          ↓
                    Coworking team
                    processes data
                    into /reports/
```

---

## 📁 Complete Project Structure

```
genesis/
├── index.html                          ← главная страница
├── CLAUDE.md                           ← инструкции для Claude
├── PROFILE_SYSTEM_GUIDE.md             ← этот файл
│
├── css/                                ← общие стили
│   ├── style.css
│   └── nav.css
│
├── components/                         ← переиспользуемые компоненты
│   ├── nav.js                          ← навигация
│   └── footer.js                       ← подвал
│
├── profile/                            ← СГЕНЕРИРОВАННЫЕ профили
│   ├── ivan-ivanov/index.html
│   ├── maria-petrova/index.html
│   └── [другие профили]
│
├── profile-generator/                  ← СИСТЕМА ГЕНЕРАЦИИ
│   ├── generate_profiles.py            ← главный скрипт
│   ├── profile_template.html           ← шаблон HTML
│   ├── README.md                       ← как использовать
│   └── DATA_FORMAT_FOR_COWORKING.md    ← спец для коворкинга
│
├── telegram_bot/                       ← TELEGRAM БОТ
│   ├── bot.py                          ← основной код бота
│   ├── requirements.txt
│   ├── README.md
│   └── start.sh
│
└── ...другие страницы...
```

---

## 🔄 Полный цикл работы

### Фаза 1: Сбор данных (Telegram Bot)

**Участник действует:**
```
/start → Введи имя → Введи телефон → Отправь данные (CSV/текст)
```

**Результат в Obsidian:**
```
/Users/konstantin/Documents/Obsidian Vault/Данные участников/
└── Иван Иванов/
    ├── profile.json         ← создан ботом
    ├── Session_1.md         ← текст сессии
    ├── metrics_1.csv        ← загруженные данные
    └── Session_2.md
```

**Файл profile.json (пример):**
```json
{
  "name": "Иван Иванов",
  "phone": "+7 (999) 123-45-67",
  "city": "Москва",
  "birthdate": "1990-03-15T00:00:00",
  "avatar_url": "https://...",
  "created_at": "2026-03-20T10:30:00",
  "user_id": 123456789,
  "sessions": [
    {
      "number": 1,
      "date": "2026-03-20T15:00:00",
      "file": "Session_1.md"
    }
  ]
}
```

**После 7 дней:** участник завершил все сессии 📊

---

### Фаза 2: Обработка данных (Coworking Team)

**Коворкинг команда:**
1. Анализирует Session_N.md и metrics_N.csv
2. Вычисляет статистику и MNIP индекс
3. Создаёт файлы в папке `/reports/`

**Что создают:**

#### `/reports/reflection.md`
Синтезированная рефлексия дня из всех сессий:
```markdown
# Главное на сегодня

Отличная практика. Улучшение концентрации на 20%.
Сон улучшился, больше REM фаз.
```

#### `/reports/fitness_summary.json`
Обработанные метрики фитнес трекера (последние 7 дней):
```json
{
  "avg_heartrate": 68,
  "avg_sleep": 8.2,
  "vo2_max": 45.7,
  "calories": 2340
}
```

#### `/reports/mnip_report.json`
Вычисленный нейропластичности индекс:
```json
{
  "score": 78,
  "progress": "+12 пунктов за неделю (18%)",
  "recommendations": "Продолжайте практику по 20 минут ежедневно..."
}
```

**Результат:**
```
Иван Иванов/
├── profile.json
├── Session_1.md
├── metrics_1.csv
└── reports/                    ← создано коворкингом
    ├── reflection.md
    ├── fitness_summary.json
    └── mnip_report.json
```

---

### Фаза 3: Генерация профилей (Profile Generator)

**Вы запускаете:**
```bash
cd /Users/konstantin/Documents/genesis/profile-generator
python3 generate_profiles.py
```

**Что происходит:**
```
Шаг 1: Сканируем все папки участников в Obsidian
       ├─ проверяем наличие profile.json
       └─ находим 5 участников ✓

Шаг 2: Для каждого участника:
       ├─ читаем profile.json
       ├─ читаем /reports/reflection.md
       ├─ читаем /reports/fitness_summary.json
       ├─ читаем /reports/mnip_report.json
       └─ загружаем шаблон

Шаг 3: Подставляем данные в шаблон:
       ├─ {{NAME}} → "Иван"
       ├─ {{SURNAME}} → "Иванов"
       ├─ {{CITY}} → "Москва"
       ├─ {{PHONE}} → "+7 (999) 123-45-67"
       ├─ {{AGE}} → "35" (вычислено из birthdate)
       ├─ {{RESEARCH_STAGE}} → "3" (по количеству сессий)
       ├─ {{REFLECTION}} → "Отличная практика..."
       ├─ {{AVG_HEARTRATE}} → "68"
       ├─ {{AVG_SLEEP}} → "8.2"
       ├─ {{VO2_MAX}} → "45.7"
       ├─ {{CALORIES}} → "2340"
       ├─ {{MNIP_INDEX}} → "78"
       ├─ {{MNIP_PROGRESS}} → "+12 пунктов за неделю (18%)"
       └─ {{MNIP_RECOMMENDATIONS}} → "Продолжайте практику..."

Шаг 4: Сохраняем HTML в правильное место:
       /Users/konstantin/Documents/genesis/profile/ivan-ivanov/index.html
```

**Вывод скрипта:**
```
======================================================================
🧠 ONTO NOTHING — Profile Generator
======================================================================
📁 Obsidian Vault: /Users/konstantin/Documents/Obsidian Vault/Данные участников
📄 Template: /Users/konstantin/Documents/genesis/profile-generator/profile_template.html
📤 Output: /Users/konstantin/Documents/genesis/profile
======================================================================

📊 Найдено участников: 5

✅ Иван Иванов → /profile/ivan-ivanov/index.html
✅ Мария Петрова → /profile/maria-petrova/index.html
✅ Сергей Сидоров → /profile/sergey-sidorov/index.html
✅ Алиса Волкова → /profile/alisa-volkova/index.html
✅ Максим Петров → /profile/maksim-petrov/index.html

======================================================================
✨ Готово! Успешно создано: 5/5
======================================================================
```

---

### Фаза 4: Публикация на GitHub Pages

**Коммитим профили:**
```bash
cd /Users/konstantin/Documents/genesis

# Добавляем все новые/изменённые профили
git add profile/

# Коммитим с понятным сообщением
git commit -m "📊 Update participant profiles (5 profiles generated)"

# Пушим на GitHub
git push origin main
```

**Результат:**
- GitHub Pages автоматически обновляет сайт
- Профили доступны по URL:
  - `https://konstantinshell.github.io/genesis/profile/ivan-ivanov/`
  - `https://konstantinshell.github.io/genesis/profile/maria-petrova/`
  - и т.д.

---

## 🎨 Что видит участник

Профиль участника — это красивая страница похожая на профиль в macOS:

```
┌─────────────────────────────────────┐
│         ONTO NOTHING Profile        │
├─────────────────────────────────────┤
│                                     │
│            [AVATAR]                 │
│                                     │
│         Иван Иванов                │
│    📍 Москва  📱 +7...  🎂 35 лет  │
│                                     │
│  Этап исследования 3                │
│                                     │
├─────────────────────────────────────┤
│ 📋 Твоя миссия                      │
│ Пройти 7 сессий. Завершено 3/7     │
├─────────────────────────────────────┤
│ ⭐ Главное на сегодня              │
│ Отличная практика. Улучшение       │
│ концентрации на 20%...              │
├─────────────────────────────────────┤
│ 💪 Данные фитнес трекера            │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│ │  68  │ │  8.2 │ │45.7  │ │2340  ││
│ │уд/мин│ │  ч   │ │ml/kg │ │ккал  ││
│ └──────┘ └──────┘ └──────┘ └──────┘│
├─────────────────────────────────────┤
│ 🧠 Твой MNIP Index                  │
│            78                       │
│   +12 пунктов за неделю (18%)       │
│   Продолжайте практику по 20 минут..│
└─────────────────────────────────────┘
```

---

## 🔧 Доступные команды

### Генерировать все профили

```bash
cd /Users/konstantin/Documents/genesis/profile-generator
python3 generate_profiles.py
```

### Генерировать с логированием

```bash
python3 generate_profiles.py > /tmp/profile_generation.log 2>&1
cat /tmp/profile_generation.log
```

### Автоматизировать ежедневно (macOS)

Создайте файл `~/Library/LaunchAgents/com.onto-nothing.profile-generator.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.onto-nothing.profile-generator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/konstantin/Documents/genesis/profile-generator/generate_profiles.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>StandardOutPath</key>
    <string>/tmp/profile-generator.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/profile-generator.log</string>
</dict>
</plist>
```

Затем:
```bash
launchctl load ~/Library/LaunchAgents/com.onto-nothing.profile-generator.plist
```

Проверить статус:
```bash
launchctl list | grep onto-nothing
tail -f /tmp/profile-generator.log
```

---

## 📊 Примеры данных

### Пример 1: Новый участник (1 день)

**profile.json:**
```json
{
  "name": "Алиса Волкова",
  "phone": "+7 (999) 555-44-33",
  "city": "СПб",
  "birthdate": "1998-07-20T00:00:00",
  "created_at": "2026-03-22T14:00:00",
  "sessions": [
    {
      "number": 1,
      "date": "2026-03-22T16:00:00",
      "file": "Session_1.md"
    }
  ]
}
```

**Результат профиля:**
```
Имя: Алиса Волкова
Возраст: 27 лет (вычислено)
Этап исследования: 2
Сессий завершено: 1/7
Рефлексия: Рефлексия будет доступна после первой сессии
Метрики: N/A (нет /reports/)
MNIP: N/A (нет /reports/)
```

### Пример 2: Активный участник (4 недели)

**profile.json:**
```json
{
  "name": "Сергей Сидоров",
  "sessions": [
    {...}, {...}, {...}, {...}, {...}, {...}, {...}
  ]
}
```

**Результат профиля:**
```
Этап исследования: 8 (завершил все 7 + продолжает)
Сессий завершено: 7/7 ✅
Рефлексия: "Значительное улучшение внимания..."
Метрики: ВСЕ значения доступны (processed в /reports/)
MNIP: 85 (высокий прогресс)
```

---

## 🐛 Troubleshooting

### Проблема: "Нет участников"

Проверьте что участники имеют `profile.json`:
```bash
ls /Users/konstantin/Documents/Obsidian\ Vault/Данные\ участников/*/profile.json
```

### Проблема: "Какой-то участник не создаётся"

Проверьте что у него есть profile.json:
```bash
cat "/Users/konstantin/Documents/Obsidian Vault/Данные участников/Имя Фамилия/profile.json"
```

### Проблема: "Данные не обновляются"

Проверьте что `/reports/` папка существует и содержит файлы:
```bash
ls "/Users/konstantin/Documents/Obsidian Vault/Данные участников/Имя Фамилия/reports/"
```

### Проблема: "JSON ошибка"

Проверьте JSON на валидность:
```bash
python3 -m json.tool "/Users/konstantin/Documents/Obsidian Vault/Данные участников/Имя Фамилия/reports/mnip_report.json"
```

---

## 🎓 Образование и Документация

**Для пользователей (вы):**
- `profile-generator/README.md` — как запускать скрипт

**Для коворкинг команды:**
- `profile-generator/DATA_FORMAT_FOR_COWORKING.md` — как подготавливать данные

**Для технических специалистов:**
- `profile-generator/generate_profiles.py` — исходный код

---

## 🚀 Следующие шаги

### ✅ Уже сделано
- Telegram бот собирает данные
- HTML шаблон профиля создан
- Python скрипт генерирует профили
- Документация для коворкинга написана
- Всё закоммичено в git

### 📋 Что можно добавить в будущем

1. **Автоматический коммит и push**
   ```bash
   # После генерации профилей, auto-commit и push на GitHub
   ```

2. **Уведомления участникам**
   - Отправлять ссылку на профиль в Telegram когда он готов

3. **Интерактивные графики**
   - D3.js графики динамики MNIP
   - Тренды здоровья

4. **Сравнение с другими участниками**
   - Анонимные сравнения прогресса
   - Лидерборды

5. **Экспорт отчётов**
   - PDF версия профиля
   - Еженедельные резюме по email

---

## 📞 Помощь и поддержка

**Основные команды:**

```bash
# Запуск генератора
python3 /Users/konstantin/Documents/genesis/profile-generator/generate_profiles.py

# Проверка логов Telegram бота
tail -f /tmp/onto-nothing-bot.log

# Проверка GitHub Pages
open https://konstantinshell.github.io/genesis/profile/

# Навигация в Obsidian папку
open "/Users/konstantin/Documents/Obsidian Vault/Данные участников"
```

---

## 📌 Чек-лист запуска

Перед публикацией профилей:

- [ ] Коворкинг команда создала `/reports/` папку и файлы
- [ ] Все JSON файлы валидны (jsonlint.com)
- [ ] Запустили `python3 generate_profiles.py`
- [ ] Скрипт вывел ✅ для всех участников
- [ ] Проверили что HTML файлы создались: `ls /Users/konstantin/Documents/genesis/profile/*/`
- [ ] Раскрыли один из профилей в браузере и проверили данные
- [ ] Коммитили: `git add profile/ && git commit -m "Update profiles"`
- [ ] Пушили: `git push origin main`
- [ ] Проверили на GitHub Pages: `https://konstantinshell.github.io/genesis/profile/...`

---

**Версия:** 1.0
**Создано:** 22.03.2026
**Статус:** ✅ Готово к использованию
