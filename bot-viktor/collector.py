"""
collector.py — слушает Telegram чаты, сохраняет сообщения в MD и файлы по датам

Структура в Obsidian:
  VIP клиенты/Виктор/2026-04-02/chat.md
  VIP клиенты/Виктор/2026-04-02/*.csv
"""

import requests
import os
import time
import logging
from datetime import datetime, timezone, timedelta

from config import BOT_TOKEN, CLIENTS_PATH, COACH_TELEGRAM_ID, CHATS
from config import SESSION_START_HOUR, SESSION_END_HOUR, EVENING_START_HOUR

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
MSK = timezone(timedelta(hours=3))


def get_updates(offset=None):
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except Exception as e:
        log.error(f"getUpdates error: {e}")
        return []


def download_file(file_id, dest_path):
    r = requests.get(f"{API}/getFile", params={"file_id": file_id})
    file_path = r.json()["result"]["file_path"]
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    content = requests.get(url).content
    with open(dest_path, "wb") as f:
        f.write(content)
    log.info(f"  Файл сохранён: {dest_path}")


def classify_message(from_id, hour_msk):
    if from_id == COACH_TELEGRAM_ID:
        return "coach"
    if hour_msk < SESSION_START_HOUR:
        return "pre_session"
    if SESSION_START_HOUR <= hour_msk < SESSION_END_HOUR:
        return "during_session"
    if hour_msk >= EVENING_START_HOUR:
        return "evening"
    return "client"


def section_header(msg_type):
    headers = {
        "coach":          "## Заметки тренера",
        "pre_session":    "## Рефлексия до сессии",
        "during_session": "## Во время сессии (клиент)",
        "evening":        "## Вечерняя рефлексия",
        "client":         "## Сообщения клиента",
    }
    return headers.get(msg_type, "## Прочее")


def get_day_dir(client_name, date_str):
    day_dir = os.path.join(CLIENTS_PATH, client_name, date_str)
    os.makedirs(day_dir, exist_ok=True)
    return day_dir


def append_to_chat_md(day_dir, time_str, from_name, msg_type, text, file_links):
    chat_file = os.path.join(day_dir, "chat.md")
    existing = ""
    if os.path.exists(chat_file):
        with open(chat_file, "r", encoding="utf-8") as f:
            existing = f.read()
    section = section_header(msg_type)
    lines = []
    if text:
        lines.append(f"**{time_str} {from_name}:** {text}")
    for link in file_links:
        lines.append(f"**{time_str} {from_name}:** [[{link}]]")
    entry = "\n".join(lines)
    if not existing:
        content = f"# Чат — {day_dir.split('/')[-1]}\n\n{section}\n{entry}\n"
    elif section in existing:
        content = existing.rstrip() + "\n" + entry + "\n"
    else:
        content = existing.rstrip() + f"\n\n{section}\n{entry}\n"
    with open(chat_file, "w", encoding="utf-8") as f:
        f.write(content)


def save_message(chat_id, message):
    if chat_id not in CHATS:
        return
    client = CHATS[chat_id]
    client_name = client["name"]
    raw_date = message.get("forward_date") or message["date"]
    ts = datetime.fromtimestamp(raw_date, tz=MSK)
    date_str = ts.strftime("%Y-%m-%d")
    time_str = ts.strftime("%H:%M")
    from_id = message.get("from", {}).get("id")
    from_name = message.get("from", {}).get("first_name", "?")
    msg_type = classify_message(from_id, ts.hour)
    if from_id != COACH_TELEGRAM_ID and client.get("client_telegram_id") is None:
        client["client_telegram_id"] = from_id
        log.info(f"  Клиент найден: id={from_id}")
    day_dir = get_day_dir(client_name, date_str)
    text = message.get("text") or message.get("caption") or ""
    file_links = []
    if "photo" in message:
        photo = message["photo"][-1]
        fname = f"photo_{time_str.replace(':', '')}.jpg"
        download_file(photo["file_id"], os.path.join(day_dir, fname))
        file_links.append(fname)
    elif "document" in message:
        doc = message["document"]
        fname = doc.get("file_name", f"file_{time_str.replace(':', '')}")
        download_file(doc["file_id"], os.path.join(day_dir, fname))
        if not fname.lower().endswith(".csv"):
            file_links.append(fname)
        else:
            log.info(f"  ЭЭГ данные: {fname}")
    elif "voice" in message or "audio" in message:
        audio = message.get("voice") or message.get("audio")
        ext = "ogg" if "voice" in message else "mp3"
        fname = f"audio_{time_str.replace(':', '')}.{ext}"
        download_file(audio["file_id"], os.path.join(day_dir, fname))
        file_links.append(fname)
    if text or file_links:
        append_to_chat_md(day_dir, time_str, from_name, msg_type, text, file_links)
    log.info(f"[{client['display']}] {time_str} {from_name}: {text[:60] or '[файл]'}")


def main():
    log.info("Коллектор Виктора запущен. Сохраняю в Obsidian...")
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message")
            if not msg:
                continue
            chat_id = msg["chat"]["id"]
            if chat_id not in CHATS:
                log.info(f"Неизвестный чат: id={chat_id}, title={msg['chat'].get('title', '?')}")
                continue
            save_message(chat_id, msg)
        time.sleep(1)


if __name__ == "__main__":
    main()
