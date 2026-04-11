#!/usr/bin/env python3
"""
Google Keep → один Markdown файл.

Использование:
  1. Скачай архив с takeout.google.com (только Google Keep)
  2. Распакуй архив
  3. Запусти:
     python3 keep2md.py /path/to/Takeout/Keep -o заметки.md

Без -o сохранит в keep_notes.md в текущей папке.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


def parse_keep_json(filepath):
    """Читает один JSON-файл заметки Google Keep."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "").strip()
    text = data.get("textContent", "").strip()

    # Чеклисты (listContent)
    list_items = data.get("listContent", [])
    if list_items:
        lines = []
        for item in list_items:
            checked = item.get("isChecked", False)
            item_text = item.get("text", "").strip()
            marker = "[x]" if checked else "[ ]"
            lines.append(f"- {marker} {item_text}")
        text = "\n".join(lines)

    # Метки
    labels = [l.get("name", "") for l in data.get("labels", [])]

    # Дата (userEditedTimestampUsec в микросекундах)
    ts = data.get("userEditedTimestampUsec", 0)
    if ts:
        dt = datetime.fromtimestamp(ts / 1_000_000)
        date_str = dt.strftime("%Y-%m-%d %H:%M")
    else:
        date_str = ""

    # Закреплена / в архиве / в корзине
    pinned = data.get("isPinned", False)
    archived = data.get("isArchived", False)
    trashed = data.get("isTrashed", False)

    # Аннотации (ссылки)
    annotations = data.get("annotations", [])
    urls = [a.get("url", "") for a in annotations if a.get("url")]

    return {
        "title": title,
        "text": text,
        "labels": labels,
        "date": date_str,
        "pinned": pinned,
        "archived": archived,
        "trashed": trashed,
        "urls": urls,
    }


def notes_to_markdown(notes):
    """Превращает список заметок в один Markdown-текст."""
    parts = []
    parts.append(f"# Google Keep — все заметки\n")
    parts.append(f"Экспорт: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    parts.append(f"Всего заметок: {len(notes)}\n")
    parts.append("---\n")

    for i, note in enumerate(notes, 1):
        title = note["title"] or "Без заголовка"
        tags = ""
        if note["labels"]:
            tags = " ".join(f"`#{l}`" for l in note["labels"])

        flags = []
        if note["pinned"]:
            flags.append("pinned")
        if note["archived"]:
            flags.append("archived")
        if note["trashed"]:
            flags.append("trashed")
        flags_str = f" ({', '.join(flags)})" if flags else ""

        parts.append(f"## {i}. {title}{flags_str}\n")
        if note["date"]:
            parts.append(f"**Дата:** {note['date']}\n")
        if tags:
            parts.append(f"**Метки:** {tags}\n")
        parts.append("")
        if note["text"]:
            parts.append(note["text"])
        if note["urls"]:
            parts.append("")
            for url in note["urls"]:
                parts.append(f"- {url}")
        parts.append("")
        parts.append("---\n")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Google Keep JSON → Markdown")
    parser.add_argument("keep_dir", help="Папка с JSON-файлами из Takeout/Keep")
    parser.add_argument("-o", "--output", default="keep_notes.md", help="Путь к выходному .md файлу")
    parser.add_argument("--skip-trashed", action="store_true", help="Пропустить удалённые заметки")
    parser.add_argument("--skip-archived", action="store_true", help="Пропустить архивные заметки")
    args = parser.parse_args()

    keep_path = Path(args.keep_dir)
    if not keep_path.is_dir():
        print(f"Ошибка: папка не найдена: {keep_path}")
        sys.exit(1)

    json_files = sorted(keep_path.glob("*.json"))
    if not json_files:
        print(f"Ошибка: JSON-файлов не найдено в {keep_path}")
        sys.exit(1)

    print(f"Найдено JSON-файлов: {len(json_files)}")

    notes = []
    errors = 0
    for jf in json_files:
        try:
            note = parse_keep_json(jf)
            if args.skip_trashed and note["trashed"]:
                continue
            if args.skip_archived and note["archived"]:
                continue
            notes.append(note)
        except Exception as e:
            print(f"  Ошибка в {jf.name}: {e}")
            errors += 1

    # Сортировка: сначала закреплённые, потом по дате (новые сверху)
    notes.sort(key=lambda n: (not n["pinned"], n["date"] or ""), reverse=False)
    notes.sort(key=lambda n: n["pinned"], reverse=True)

    md = notes_to_markdown(notes)

    output_path = Path(args.output)
    output_path.write_text(md, encoding="utf-8")

    print(f"Готово! Сохранено {len(notes)} заметок в {output_path}")
    if errors:
        print(f"Ошибок при чтении: {errors}")


if __name__ == "__main__":
    main()
