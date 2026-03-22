#!/bin/bash

# Тестовый скрипт для проверки бэкенда
# Использование: bash test_api.sh

BACKEND_URL="http://localhost:5000"

echo "🧪 Тестирование ONTO NOTHING Backend"
echo "=================================="

# Проверка здоровья
echo ""
echo "1️⃣  Проверка здоровья сервера..."
curl -s "$BACKEND_URL/health" | python3 -m json.tool
echo ""

# Список участников
echo ""
echo "2️⃣  Список участников..."
curl -s "$BACKEND_URL/list-participants" | python3 -m json.tool
echo ""

# Тестовая загрузка
echo ""
echo "3️⃣  Тестовая загрузка данных..."
curl -s -X POST "$BACKEND_URL/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тест Тестов",
    "phone": "+7 (999) 999-99-99",
    "session": "1",
    "text": "Это автоматический тестовый отчёт. Сессия прошла хорошо, много новых ощущений и наблюдений.",
    "csv": "timestamp,heartrate,eeg_alpha,eeg_beta,eeg_theta\n09:00,72,10.5,5.2,3.1\n09:30,74,11.2,4.8,3.3\n10:00,71,12.1,4.5,3.0",
    "csv_filename": "test_metrics.csv"
  }' | python3 -m json.tool

echo ""
echo "=================================="
echo "✅ Тест завершён!"
echo ""
echo "Проверь файлы в: /Users/konstantin/Documents/Obsidian\\ Vault/Данные\\ участников/Тест\\ Тестов/"
