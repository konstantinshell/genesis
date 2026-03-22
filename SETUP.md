# 🧠 ONTO NOTHING — Полная система автоматизации

## Что ты построил:

### ✅ Сайт (GitHub Pages)
- Главная страница
- 7+ других страниц
- Форма загрузки данных на `/research-upload/`
- Навигация и брендинг

### ✅ Бэкенд (Python Flask)
- Получает данные из формы
- Создаёт файлы прямо в Obsidian
- Организует по именам и сессиям

### ✅ Интеграция Obsidian
- Данные падают в папку `/Users/konstantin/Documents/Obsidian Vault/Данные участников`
- Автоматическое создание папок по именам
- Markdown файлы с отчётами
- CSV файлы с метриками

---

## 🚀 КАК ЗАПУСТИТЬ

### Шаг 1: Установи Python зависимости

```bash
cd /Users/konstantin/Documents/genesis/backend
pip3 install -r requirements.txt
```

Или вручную:
```bash
pip3 install Flask flask-cors
```

### Шаг 2: Запусти бэкенд сервер

```bash
cd /Users/konstantin/Documents/genesis/backend
python3 app.py
```

Увидишь:
```
🧠 ONTO NOTHING — Research Data Backend
📁 Obsidian Vault: /Users/konstantin/Documents/Obsidian Vault/Данные участников
🌐 Server running on: http://localhost:5000
```

**ОСТАВЬ этот терминал открытым!** Пока терминал работает — бэкенд работает.

### Шаг 3: Откройся на сайт

1. Откройся на сайт: https://konstantinshell.github.io/genesis/research-upload/
2. Заполни форму:
   - Имя
   - Телефон
   - Сессия (1-7)
   - Текст отчёта
   - CSV файл
3. Нажми "Отправить"

### Шаг 4: Проверь Obsidian

В папке `/Users/konstantin/Documents/Obsidian Vault/Данные участников/` появится:

```
Константин Шель/
├── Session_1.md      ← Markdown с отчётом
└── Session_1_metrics.csv ← CSV файл
```

Obsidian автоматически синхронизирует и ты увидишь файлы! 🎉

---

## 📋 Если что-то не работает

### Ошибка: "Connection refused"
✅ **Решение:** Проверь что бэкенд запущен
```bash
# В отдельном терминале:
curl http://localhost:5000/health
```

Должно вернуть: `{"status": "ok", ...}`

### Ошибка: "mkdir permission denied"
✅ **Решение:** Проверь что папка Obsidian существует
```bash
ls -la "/Users/konstantin/Documents/Obsidian Vault/Данные участников"
```

### Файлы не появляются в Obsidian
✅ **Решение:**
- Проверь что файлы созданы: `ls -la "/Users/konstantin/Documents/Obsidian Vault/Данные участников/Константин\ Шель/"`
- Откройся в Obsidian на эту папку (может нужна ручная синхронизация)
- Перезагрузи Obsidian (Cmd+R)

### Form говорит "ошибка соединения"
✅ **Решение:**
1. Проверь что бэкенд запущен на http://localhost:5000
2. Проверь что с браузера видно сервер: откройся http://localhost:5000/health
3. Может быть CORS проблема (но она должна быть решена в коде)

---

## 🔄 Автоматический запуск (опционально)

Чтобы бэкенд запускался автоматически при старте Mac:

```bash
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

# Включаем:
launchctl load ~/Library/LaunchAgents/com.onto-nothing.backend.plist

# Проверяем:
launchctl list | grep onto-nothing
```

Теперь при каждом старте Mac сервер запустится автоматически!

Для остановки:
```bash
launchctl unload ~/Library/LaunchAgents/com.onto-nothing.backend.plist
```

---

## 📡 API Эндпоинты (для отладки)

### Проверка здоровья сервера
```bash
curl http://localhost:5000/health
```

### Список всех участников
```bash
curl http://localhost:5000/list-participants
```

### Тестовая загрузка
```bash
curl -X POST http://localhost:5000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовый Пользователь",
    "phone": "+7 (999) 999-99-99",
    "session": "1",
    "text": "Это тестовый отчёт",
    "csv": "heartrate,eeg\n72,10.5\n73,11.0",
    "csv_filename": "test_metrics.csv"
  }'
```

---

## 🎯 Следующие шаги

### Для локального использования (сейчас):
✅ Запусти бэкенд локально
✅ Форма на сайте отправляет данные на localhost:5000
✅ Файлы создаются в Obsidian
✅ Всё работает!

### Если позже захочешь в интернет:
- Перенести бэкенд на сервер (Heroku, Railway, etc)
- Синхронизировать файлы через облако (Google Drive, OneDrive, etc)
- Обновить URL в форме с localhost на реальный URL

Но на данный момент локальный запуск — идеален для твоего использования!

---

## 📁 Файловая структура

```
genesis/
├── index.html                          ← Главная
├── css/
│   ├── style.css
│   └── nav.css
├── components/
│   ├── nav.js
│   └── footer.js
├── research-upload/
│   └── index.html                      ← ФОРМА (отправляет на бэкенд)
├── backend/                            ← БЭКЕНД СЕРВЕР
│   ├── app.py                          ← Основной код (Flask)
│   ├── requirements.txt                ← Зависимости
│   ├── README.md                       ← Подробная документация
│   └── .gitignore
└── SETUP.md                            ← Этот файл
```

---

## 💡 Как это всё работает под капотом

1. **Пользователь на сайте** → Заполняет форму `/research-upload/`
2. **JavaScript форма** → Отправляет POST запрос на `http://localhost:5000/upload`
3. **Flask бэкенд** → Получает JSON с данными
4. **Обработка** → Санитизирует имя, создаёт папку
5. **Создание файлов:**
   - Markdown файл: `/Users/konstantin/Documents/Obsidian Vault/Данные участников/{name}/Session_{session}.md`
   - CSV файл: `/Users/konstantin/Documents/Obsidian Vault/Данные участников/{name}/{csv_filename}`
6. **Obsidian синхронизирует** → Ты видишь новые файлы в приложении
7. **Успех!** → Форма показывает зелёное сообщение

---

## 🎉 Готово!

Ты построил полную систему:
- ✅ Веб-сайт на собственном коде
- ✅ Форму для сбора данных
- ✅ Бэкенд для обработки
- ✅ Автоматическую интеграцию с Obsidian

**Запусти:** `python3 /Users/konstantin/Documents/genesis/backend/app.py`

И всё начнёт работать! 🚀
