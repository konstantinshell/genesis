from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json

app = Flask(__name__)
CORS(app)

OBSIDIAN_VAULT = Path("/Users/konstantin/Documents/Obsidian Vault/Данные участников")

@app.route('/health', methods=['GET'])
def health():
    print("✅ Health check получена")
    return jsonify({"status": "ok", "vault": str(OBSIDIAN_VAULT)})

@app.route('/upload', methods=['POST'])
def upload():
    print("📨 Получен POST запрос!")
    try:
        data = request.get_json()
        print(f"Данные: {data}")
        
        name = data.get('name', 'Unknown')
        print(f"Создаю папку для: {name}")
        
        person_folder = OBSIDIAN_VAULT / name
        person_folder.mkdir(parents=True, exist_ok=True)
        print(f"✅ Папка создана: {person_folder}")
        
        return jsonify({"success": True, "message": f"✅ Папка создана для {name}"}), 200
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🧠 ONTO NOTHING — Debug Mode")
    print(f"📁 Vault: {OBSIDIAN_VAULT}")
    print(f"🌐 http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=False, port=3000, use_reloader=False)
