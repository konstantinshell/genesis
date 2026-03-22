"""
ONTO NOTHING — Автоматический бэкенд для загрузки данных
Получает данные из формы сайта и отправляет в Telegram
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с сайта

# TELEGRAM SETTINGS
TELEGRAM_BOT_TOKEN = "8656261306:AAHQ3U9ByFvkfyCY4Xp0GP9tBCekK9kip_Q"
TELEGRAM_CHAT_ID = "41537154"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_to_telegram(name, phone, session, report_text, csv_filename, csv_content):
    """
    Отправляет данные в Telegram в виде красивых сообщений
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Первое сообщение — основная информация
    main_message = f"""🧠 *ONTO NOTHING — Новые данные сессии*

👤 *Участник:* {name}
📱 *Телефон:* {phone}
📊 *Сессия:* {session}
🕐 *Дата:* {timestamp}

*📝 Отчёт:*
```
{report_text}
```

*📋 Файл с метриками:* `{csv_filename}`
"""

    try:
        # Отправляем основное сообщение
        response1 = requests.post(
            TELEGRAM_API_URL,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": main_message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )

        if not response1.ok:
            return {
                "success": False,
                "error": f"Ошибка Telegram (основное сообщение): {response1.status_code}"
            }

        # Второе сообщение — CSV данные
        csv_preview = csv_content[:3000]  # Первые 3000 символов
        if len(csv_content) > 3000:
            csv_preview += "\n...\n[данные обрезаны]"

        csv_message = f"""📊 *CSV данные для {name} (Session {session})*

```
{csv_preview}
```
"""

        response2 = requests.post(
            TELEGRAM_API_URL,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": csv_message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )

        if response2.ok:
            return {
                "success": True,
                "message": f"✅ Данные отправлены в Telegram! Проверь сообщения."
            }
        else:
            return {
                "success": True,
                "message": f"✅ Основное сообщение отправлено (CSV передача имела проблемы)"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка подключения к Telegram: {str(e)}"
        }


@app.route('/health', methods=['GET'])
def health():
    """Проверка что сервер живой"""
    return jsonify({
        "status": "ok",
        "service": "ONTO NOTHING Research Backend",
        "integration": "Telegram",
        "chat_id": TELEGRAM_CHAT_ID
    })


@app.route('/upload', methods=['POST'])
def upload():
    """
    Основной эндпоинт для загрузки данных и отправки в Telegram

    POST /upload
    {
        "name": "Константин Шель",
        "phone": "+7 (999) 999-99-99",
        "session": "1",
        "text": "Описание сессии...",
        "csv": "col1,col2\n1,2\n3,4",
        "csv_filename": "metrics.csv"
    }
    """

    try:
        data = request.get_json()

        # Валидация данных
        required_fields = ['name', 'phone', 'session', 'text', 'csv', 'csv_filename']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Отсутствует поле: {field}"
                }), 400

        # Отправляем в Telegram
        result = send_to_telegram(
            name=data['name'],
            phone=data['phone'],
            session=data['session'],
            report_text=data['text'],
            csv_filename=data['csv_filename'],
            csv_content=data['csv']
        )

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500




if __name__ == '__main__':
    print("=" * 60)
    print("🧠 ONTO NOTHING — Research Data Backend")
    print("=" * 60)
    print(f"📱 Telegram Integration: ✅ ACTIVE")
    print(f"🤖 Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"🌐 Server running on: http://localhost:3000")
    print(f"✅ Health check: http://localhost:3000/health")
    print("=" * 60)
    print("Готов к приёму данных!")
    print("=" * 60)

    app.run(debug=True, port=3000, use_reloader=False)
