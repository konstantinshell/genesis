#!/usr/bin/env python3
"""
Salebot Webhook Server
Принимает сообщения от Salebot и сохраняет их в Obsidian Vault
"""

import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SALEBOT_API_KEY = os.getenv("SALEBOT_API_KEY")
OBSIDIAN_PATH = Path(os.getenv("OBSIDIAN_PATH", "/Users/konstantin/Documents/Obsidian Vault"))
CLIENTS_DIR = OBSIDIAN_PATH / "Salebot" / "clients"


def sanitize_name(name: str) -> str:
    """Очищает имя для использования в пути папки"""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '-')
    return name.strip().strip('-') or "unknown"


def save_message(client_id: str, client_name: str, message_text: str, raw_data: dict):
    """Сохраняет сообщение в Obsidian"""
    safe_name = sanitize_name(client_name)
    client_dir = CLIENTS_DIR / safe_name
    client_dir.mkdir(parents=True, exist_ok=True)

    messages_file = client_dir / "messages.md"

    # Создаём файл с заголовком если он новый
    if not messages_file.exists():
        with open(messages_file, 'w', encoding='utf-8') as f:
            f.write(f"# Переписка: {client_name}\n\n")
            f.write(f"**client_id:** {client_id}\n\n")
            f.write("---\n\n")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"""## {timestamp}
**От:** {client_name}
**Текст:** {message_text}
**client_id:** {client_id}

---

"""

    with open(messages_file, 'a', encoding='utf-8') as f:
        f.write(entry)

    print(f"[{timestamp}] Сохранено сообщение от {client_name} (id: {client_id})")
    return str(messages_file)


@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "status": "ok",
        "message": "Salebot server running",
        "clients_dir": str(CLIENTS_DIR),
        "api_key_loaded": bool(SALEBOT_API_KEY)
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "Empty body"}), 400

        print(f"[WEBHOOK] Получен запрос: {json.dumps(data, ensure_ascii=False)[:300]}")

        # Извлекаем данные — Salebot может слать разные форматы
        client_id = str(
            data.get('client_id') or
            data.get('user_id') or
            data.get('id') or
            'unknown'
        )

        # Имя клиента
        first_name = data.get('name') or data.get('first_name') or ''
        last_name = data.get('last_name') or data.get('surname') or ''
        client_name = f"{first_name} {last_name}".strip() or f"client_{client_id}"

        # Текст сообщения
        message_text = (
            data.get('message') or
            data.get('text') or
            data.get('content') or
            '[нет текста]'
        )

        # Сохраняем
        saved_to = save_message(client_id, client_name, message_text, data)

        return jsonify({
            "status": "ok",
            "saved_to": saved_to,
            "client": client_name,
            "client_id": client_id
        })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    CLIENTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Salebot сервер стартует на порту 5001")
    print(f"Obsidian path: {OBSIDIAN_PATH}")
    print(f"Клиенты будут сохраняться в: {CLIENTS_DIR}")
    app.run(host='0.0.0.0', port=5001, debug=True)
