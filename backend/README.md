# ONTO NOTHING — Research Data Backend

Автоматический сервер для загрузки данных с сайта прямо в папку Obsidian.

## Как это работает

```
Пользователь на сайте заполняет форму
            ↓
   Нажимает "Отправить"
            ↓
    Данные идут на backend
            ↓
   Backend создаёт папку участника
            ↓
  Сохраняет markdown + CSV файлы
            ↓
   Файлы появляются в Obsidian 🎉
```

## Установка

### 1. Установи Python 3.9+

Проверь что установлен:
```bash
python3 --version
```

### 2. Установи зависимости

В папке `backend/` запусти:
```bash
pip install -r requirements.txt
```

Или если не работает:
```bash
pip3 install Flask flask-cors
```

## Запуск сервера

### Вариант 1: Локально на твоём компьютере (рекомендуется)

```bash
cd /Users/konstantin/Documents/genesis/backend
python3 app.py
```

Увидишь:
```
🧠 ONTO NOTHING — Research Data Backend
📁 Obsidian Vault: /Users/konstantin/Documents/Obsidian Vault/Данные участников
🌐 Server running on: http://localhost:5000
✅ Health check: http://localhost:5000/health
📋 List participants: http://localhost:5000/list-participants
```

### Вариант 2: Запуск в фоне (чтобы работал всегда)

**На Mac:**
```bash
# Создаём LaunchAgent чтобы сервер запускался при старте Mac
cat > ~/Library/LaunchAgents/com.onto-nothing.backend.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.onto-nothing.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/konstantin/Documents/genesis/backend/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/onto-nothing-backend.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/onto-nothing-backend.log</string>
</dict>
</plist>
EOF

# Включаем автозапуск
launchctl load ~/Library/LaunchAgents/com.onto-nothing.backend.plist

# Проверяем статус
launchctl list | grep onto-nothing
```

Для остановки:
```bash
launchctl unload ~/Library/LaunchAgents/com.onto-nothing.backend.plist
```

## Проверка что всё работает

### Проверка сервера

```bash
# В браузере или терминале:
curl http://localhost:5000/health
```

Должно вернуть:
```json
{
  "status": "ok",
  "vault": "/Users/konstantin/Documents/Obsidian Vault/Данные участников"
}
```

### Список участников

```bash
curl http://localhost:5000/list-participants
```

## API Endpoints

### POST `/upload`

Загружает данные в Obsidian

```bash
curl -X POST http://localhost:5000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Константин Шель",
    "phone": "+7 (999) 999-99-99",
    "session": "1",
    "text": "Отличная сессия, много новых ощущений...",
    "csv": "heartrate,eeg_alpha,eeg_beta\n72,10.5,5.2\n73,11.0,4.8",
    "csv_filename": "metrics.csv"
  }'
```

**Ответ при успехе:**
```json
{
  "success": true,
  "person_folder": "/Users/konstantin/Documents/Obsidian Vault/Данные участников/Константин Шель",
  "md_file": "Session_1.md",
  "csv_file": "metrics.csv",
  "message": "✅ Данные для Константин Шель (Session 1) сохранены в Obsidian"
}
```

### GET `/list-participants`

Показывает всех участников и их сессии

```bash
curl http://localhost:5000/list-participants
```

### GET `/health`

Проверка что сервер живой

```bash
curl http://localhost:5000/health
```

## Структура файлов в Obsidian

После первой загрузки появится:

```
/Users/konstantin/Documents/Obsidian Vault/Данные участники/
├── Константин Шель/
│   ├── Session_1.md
│   ├── Session_1_metrics.csv
│   ├── Session_2.md
│   └── Session_2_metrics.csv
├── Иван Петров/
│   ├── Session_1.md
│   └── Session_1_metrics.csv
└── ...
```

## Что находится в файле Session_X.md

```markdown
# Сессия 1 — Константин Шель

**Дата загрузки:** 2026-03-22 17:30:45
**Имя:** Константин Шель
**Телефон:** +7 (999) 999-99-99
**Номер сессии:** 1

## Отчёт участника

Отличная сессия, много новых ощущений, состояние улучшилось...

---

**Файл с метриками:** `Session_1_metrics.csv`

## Метаданные

- Статус: ✅ Получено
- Источник: ONTO NOTHING Research Platform
- Ссылка на CSV: [[Session_1_metrics.csv]]
```

## Troubleshooting

### Ошибка "Connection refused"
- Убедись что сервер запущен: `python3 app.py`
- Проверь http://localhost:5000/health

### Файлы не создаются
- Проверь что папка Obsidian существует
- Убедись что у app.py есть доступ на запись

### CORS ошибки
- Backend уже настроен на CORS, должно работать
- Убедись что frontend отправляет на http://localhost:5000

## Интеграция с сайтом

Форма на странице `/research-upload/` автоматически отправляет данные на этот бэкенд.

Когда пользователь нажимает "Отправить":
1. ✅ Данные отправляются на `http://localhost:5000/upload`
2. ✅ Backend создаёт папку с именем участника
3. ✅ Сохраняет markdown файл с отчётом
4. ✅ Сохраняет CSV с метриками
5. ✅ Данные синхронизируются в Obsidian

## Production Deploy (когда будет нужно)

Когда захочешь запустить это на сервере в интернете:
- Можно использовать Heroku, Railway, Vercel, или любой другой хостинг
- Переменная окружения для пути: `OBSIDIAN_VAULT_PATH`
- Тогда нужно будет синхронизировать файлы с облаком (Google Drive, OneDrive, iCloud)

На данный момент рекомендуется локальный запуск на твоём компьютере.

## Поддержка

Если что-то не работает:
1. Проверь логи в терминале где запущен `python3 app.py`
2. Попробуй перезагрузить сервер
3. Убедись что все пути правильные
