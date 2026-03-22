# ONTO NOTHING — Telegram Bot

Локальный Telegram бот который сохраняет данные участников прямо в папку Obsidian.

## 🚀 Быстрый старт

### 1. Установи зависимости

```bash
cd /Users/konstantin/Documents/genesis/telegram_bot
pip3 install -r requirements.txt
```

### 2. Запусти бота

```bash
python3 bot.py
```

Увидишь:
```
============================================================
🧠 ONTO NOTHING — Telegram Bot
============================================================
📁 Obsidian Vault: /Users/konstantin/Documents/Obsidian Vault/Данные участников
🤖 Bot Token: 8656261306:AAHQ3U...
============================================================
✅ Бот запущен и слушает сообщения...
============================================================
```

**Оставь этот терминал открытым!** Пока процесс работает — бот работает.

### 3. Тестируй в Telegram

Напиши боту **@rhythms_nothing_bot**:
```
/start
```

Бот спросит:
- Как тебя зовут?
- Твой телефон?

После этого ты можешь:
- Отправлять CSV файлы
- Писать описание сессий
- Все будет сохранено в Obsidian!

---

## 📁 Структура файлов

После первого пользователя появится:

```
/Users/konstantin/Documents/Obsidian Vault/Данные участников/
├── Константин Шель/
│   ├── profile.json          (профиль участника)
│   ├── Session_1.md          (описание сессии)
│   ├── Session_2.md
│   ├── metrics_1.csv         (загруженные файлы)
│   └── metrics_2.csv
```

### profile.json

```json
{
  "name": "Константин Шель",
  "phone": "+7 (999) 999-99-99",
  "created_at": "2026-03-22T19:30:45.123456",
  "sessions": [
    {
      "number": 1,
      "date": "2026-03-22T19:35:00.123456",
      "file": "Session_1.md"
    }
  ]
}
```

---

## 🧪 Как работает

### Сценарий 1: Пользователь отправляет CSV файл

```
Участник в Telegram     Бот                  Obsidian Vault
    |                    |                         |
    |-- отправляет CSV --|                         |
    |                    |-- сохраняет файл ------>|
    |                    |-- обновляет profile.json|
    |<-- подтверждение --|                         |
```

### Сценарий 2: Пользователь пишет отчёт текстом

```
Участник в Telegram     Бот                  Obsidian Vault
    |                    |                         |
    |-- пишет текст -----|                         |
    |                    |-- создаёт Session_N.md |
    |                    |-- обновляет profile.json|
    |<-- подтверждение --|                         |
```

---

## ⚙️ Запуск в фоне (LaunchAgent)

Чтобы бот запускался автоматически при старте Mac:

```bash
cat > ~/Library/LaunchAgents/com.onto-nothing.telegram-bot.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.onto-nothing.telegram-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/konstantin/Documents/genesis/telegram_bot/bot.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/onto-nothing-bot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/onto-nothing-bot.log</string>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Включаем автозапуск
launchctl load ~/Library/LaunchAgents/com.onto-nothing.telegram-bot.plist

# Проверяем статус
launchctl list | grep onto-nothing

# Логи смотрим здесь:
tail -f /tmp/onto-nothing-bot.log
```

Для остановки:
```bash
launchctl unload ~/Library/LaunchAgents/com.onto-nothing.telegram-bot.plist
```

---

## 🎯 Команды бота

- `/start` — начать, создать профиль
- `/help` — справка

---

## 📊 Что дальше

### Веб-дашборд

Создам веб-страницу которая:
- ✅ Читает profile.json из Obsidian папки
- ✅ Показывает данные участника
- ✅ Строит графики
- ✅ Отображает прогресс

### Автоматическая рассылка отчётов

Скрипт который:
- ✅ Анализирует данные из Obsidian
- ✅ Создаёт красивый отчёт
- ✅ Отправляет в Telegram участнику

---

## 🔧 Troubleshooting

### Ошибка: "ModuleNotFoundError: No module named 'telegram'"

```bash
pip3 install python-telegram-bot
```

### Ошибка: "Permission denied" при создании папки

Проверь права доступа:
```bash
ls -la "/Users/konstantin/Documents/Obsidian Vault/"
```

### Бот не отвечает

- Проверь что терминал не закрыт
- Проверь интернет соединение
- Перезагрузи бота

### Файлы не сохраняются

- Проверь что папка Obsidian существует
- Проверь права доступа: `chmod -R 755 "/Users/konstantin/Documents/Obsidian Vault/"`

---

## 📝 Структура кода

```
bot.py
├── Настройки (токен, пути)
├── Функции для работы с файлами
│   ├── sanitize_filename()
│   ├── get_user_folder()
│   ├── load_user_data()
│   └── save_user_data()
├── Обработчики команд
│   ├── /start
│   ├── /help
│   ├── receive_name()
│   ├── receive_phone()
│   ├── receive_file()
│   └── receive_text()
└── main() — запуск бота
```

---

## 🚀 Готово!

Бот полностью функционален и готов к использованию!

Участники просто:
1. Пишут `/start`
2. Вводят имя и телефон
3. Отправляют данные (CSV, текст, фото)
4. Всё автоматически сохраняется в Obsidian

Просто запусти `python3 bot.py` и наслаждайся! 🎉
