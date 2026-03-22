"""
ONTO NOTHING — Автоматический бэкенд для загрузки данных в Obsidian
Получает данные из формы сайта и создаёт файлы прямо в папке Obsidian
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с сайта

# ПУТИ
OBSIDIAN_VAULT = Path("/Users/konstantin/Documents/Obsidian Vault/Данные участников")

# Создаём папку если её нет
OBSIDIAN_VAULT.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename):
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def create_session_file(name, phone, session, report_text, csv_filename, csv_content):
    """
    Создаёт папку участника и сохраняет файлы сессии

    Структура:
    /Данные участников/
    ├── Константин Шель/
    │   ├── Session_1.md
    │   └── Session_1_metrics.csv
    └── ...
    """

    # Чистим имя для использования в пути
    safe_name = sanitize_filename(name)
    person_folder = OBSIDIAN_VAULT / safe_name
    person_folder.mkdir(parents=True, exist_ok=True)

    # Создаём Markdown файл с информацией о сессии
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""# Сессия {session} — {name}

**Дата загрузки:** {timestamp}
**Имя:** {name}
**Телефон:** {phone}
**Номер сессии:** {session}

## Отчёт участника

{report_text}

---

**Файл с метриками:** `{csv_filename}`

## Метаданные

- Статус: ✅ Получено
- Источник: ONTO NOTHING Research Platform
- Ссылка на CSV: [[{csv_filename}]]
"""

    # Сохраняем markdown файл
    md_filename = f"Session_{session}.md"
    md_filepath = person_folder / md_filename

    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # Сохраняем CSV файл
    csv_safename = sanitize_filename(csv_filename)
    csv_filepath = person_folder / csv_safename

    with open(csv_filepath, 'w', encoding='utf-8') as f:
        f.write(csv_content)

    return {
        "success": True,
        "person_folder": str(person_folder),
        "md_file": md_filename,
        "csv_file": csv_safename,
        "message": f"✅ Данные для {name} (Session {session}) сохранены в Obsidian"
    }


@app.route('/health', methods=['GET'])
def health():
    """Проверка что сервер живой"""
    return jsonify({"status": "ok", "vault": str(OBSIDIAN_VAULT)})


@app.route('/upload', methods=['POST'])
def upload():
    """
    Основной эндпоинт для загрузки данных

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

        # Создаём файлы в Obsidian
        result = create_session_file(
            name=data['name'],
            phone=data['phone'],
            session=data['session'],
            report_text=data['text'],
            csv_filename=data['csv_filename'],
            csv_content=data['csv']
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/list-participants', methods=['GET'])
def list_participants():
    """Список всех участников и их сессий"""
    try:
        participants = {}

        for person_folder in OBSIDIAN_VAULT.iterdir():
            if person_folder.is_dir():
                sessions = []
                for file in person_folder.iterdir():
                    if file.suffix == '.md':
                        sessions.append(file.name)

                participants[person_folder.name] = {
                    "sessions": sorted(sessions),
                    "count": len(sessions)
                }

        return jsonify({
            "success": True,
            "vault_path": str(OBSIDIAN_VAULT),
            "participants": participants,
            "total_participants": len(participants)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🧠 ONTO NOTHING — Research Data Backend")
    print("=" * 60)
    print(f"📁 Obsidian Vault: {OBSIDIAN_VAULT}")
    print(f"🌐 Server running on: http://localhost:5000")
    print(f"✅ Health check: http://localhost:5000/health")
    print(f"📋 List participants: http://localhost:5000/list-participants")
    print("=" * 60)

    app.run(debug=True, port=5000)
