"""
update.py — читает отчёты из Отчеты/ и обновляет веб-страницу Виктора
Запуск: python3 update.py
"""
import os
import sys
import re
import requests
from datetime import datetime, timezone, timedelta
from config import CLIENTS_PATH, VAULT_PATH, CHATS, BOT_TOKEN

MSK = timezone(timedelta(hours=3))

def load_reports(client_name, reports_dir, n=10):
    path = os.path.join(CLIENTS_PATH, client_name, reports_dir)
    if not os.path.exists(path):
        return []
    files = sorted([f for f in os.listdir(path) if f.endswith(".md")], reverse=True)[:n]
    result = []
    for fname in files:
        date_str = fname.replace(".md", "")
        with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
            result.append({"date": date_str, "content": f.read()})
    return result

def send_telegram(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    )

def main():
    for chat_id, client_info in CHATS.items():
        client_name = client_info["name"]
        reports_dir = client_info.get("reports_dir", "Отчеты")
        reports = load_reports(client_name, reports_dir)
        if not reports:
            print(f"[{client_info['display']}] Нет отчётов")
            continue
        print(f"[{client_info['display']}] {len(reports)} отчётов найдено")
        msg = f"Страница *{client_info['display']}* обновлена\nВсего сессий: {len(reports)}"
        send_telegram(chat_id, msg)
        print(f"  Уведомление отправлено")
    print("Готово.")

if __name__ == "__main__":
    main()
