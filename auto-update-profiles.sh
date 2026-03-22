#!/bin/bash
# ONTO NOTHING — Автообновление профилей каждые 30 минут

LOG_FILE="/tmp/onto-nothing-profiles.log"
GENESIS_DIR="/Users/konstantin/Documents/genesis"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"

echo "==============================" >> "$LOG_FILE"
echo "🧠 Запуск: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# Генерируем профили
echo "📊 Генерируем профили..." >> "$LOG_FILE"
cd "$GENESIS_DIR"
$PYTHON profile-generator/generate_profiles.py >> "$LOG_FILE" 2>&1

# Проверяем есть ли изменения
cd "$GENESIS_DIR"
CHANGES=$(git status --porcelain)

if [ -z "$CHANGES" ]; then
    echo "✅ Изменений нет, пуш не нужен" >> "$LOG_FILE"
else
    echo "📤 Есть изменения, коммитим..." >> "$LOG_FILE"
    git add profile/ >> "$LOG_FILE" 2>&1
    git commit -m "Auto: обновление профилей $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
    echo "✅ Запушено на GitHub Pages!" >> "$LOG_FILE"
fi

echo "🏁 Готово: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
