#!/usr/bin/env python3
"""
ONTO NOTHING — Profile Generator
Генерирует HTML профили участников из шаблона и данных Obsidian
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Пути
OBSIDIAN_VAULT = Path("/Users/konstantin/Documents/Obsidian Vault/Данные участников")
TEMPLATE_PATH = Path(__file__).parent / "profile_template.html"
OUTPUT_BASE = Path(__file__).parent.parent / "profile"  # ../profile

# Загружаем шаблон
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    TEMPLATE = f.read()


def sanitize_name(name: str) -> str:
    """Преобразует имя в безопасное имя папки для URL"""
    # Убираем спецсимволы, заменяем пробелы на дефисы
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    safe = re.sub(r'[-\s]+', '-', safe)
    return safe.strip('-')


def load_json(filepath: Path) -> Dict[str, Any]:
    """Загружает JSON файл или возвращает пустой dict"""
    if not filepath.exists():
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def load_text(filepath: Path) -> str:
    """Загружает текстовый файл или возвращает пустую строку"""
    if not filepath.exists():
        return ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return ""


def get_age_from_birthdate(birthdate_iso: str) -> int:
    """Вычисляет возраст из ISO даты рождения"""
    try:
        birth = datetime.fromisoformat(birthdate_iso)
        today = datetime.now()
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return age
    except:
        return 0


def extract_markdown_text(md_content: str) -> str:
    """Извлекает основной текст из markdown файла"""
    # Убираем заголовки и форматирование, оставляем текст
    lines = []
    for line in md_content.split('\n'):
        # Пропускаем строки с только #, **, и т.п.
        if line.strip() and not line.startswith('#') and not line.startswith('**') and not line.startswith('---'):
            lines.append(line.strip())
    return ' '.join(lines)


def generate_profile(participant_folder: Path) -> bool:
    """
    Генерирует HTML профиль для одного участника
    Возвращает True если успешно, False если ошибка
    """
    try:
        participant_name = participant_folder.name

        # Загружаем profile.json
        profile_data = load_json(participant_folder / "profile.json")

        if not profile_data:
            print(f"⚠️  {participant_name}: profile.json не найден, пропускаем")
            return False

        # Загружаем processed reports
        reports_dir = participant_folder / "reports"
        reflection_md = load_text(reports_dir / "reflection.md")
        mnip_report = load_json(reports_dir / "mnip_report.json")
        fitness_data = load_json(reports_dir / "fitness_summary.json")

        # Подготавливаем данные для подстановки
        name_parts = profile_data.get('name', 'Unknown').split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Вычисляем возраст если есть birthdate
        age = 0
        if 'birthdate' in profile_data:
            age = get_age_from_birthdate(profile_data['birthdate'])
        elif 'age' in profile_data:
            age = profile_data['age']

        # Подготавливаем отражение (извлекаем текст из markdown)
        reflection_text = reflection_md
        if reflection_text.startswith('#'):
            reflection_text = extract_markdown_text(reflection_md)

        # Подготавливаем MNIP данные
        mnip_index = mnip_report.get('score', 'N/A')
        mnip_progress = mnip_report.get('progress', 'Данные обновляются...')
        mnip_recommendations = mnip_report.get('recommendations', 'Продолжайте отслеживать свои метрики.')

        # Подготавливаем фитнес данные
        avg_heartrate = fitness_data.get('avg_heartrate', '72')
        avg_sleep = fitness_data.get('avg_sleep', '7.5')
        vo2_max = fitness_data.get('vo2_max', '--')
        calories = fitness_data.get('calories', '--')

        # Получаем аватар (если есть в профиле)
        avatar_url = profile_data.get('avatar_url', 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Ccircle cx="50" cy="50" r="50" fill="%235F5FFF"/%3E%3Ctext x="50" y="60" font-size="50" font-weight="bold" fill="white" text-anchor="middle"%3E%3F%3C/text%3E%3C/svg%3E')

        # Последнее обновление
        last_update = datetime.now().strftime('%d.%m.%Y %H:%M')

        # Определяем этап исследования (по количеству сессий)
        sessions = profile_data.get('sessions', [])
        research_stage = len(sessions) + 1
        session_count = len(sessions)

        # Подстановка в шаблон
        html = TEMPLATE

        replacements = {
            '{{NAME}}': first_name,
            '{{SURNAME}}': last_name,
            '{{AVATAR_URL}}': avatar_url,
            '{{CITY}}': profile_data.get('city', 'Не указан'),
            '{{PHONE}}': profile_data.get('phone', 'Не указан'),
            '{{AGE}}': str(age),
            '{{RESEARCH_STAGE}}': str(research_stage),
            '{{SESSION_COUNT}}': str(session_count),
            '{{REFLECTION}}': reflection_text or 'Рефлексия будет доступна после первой сессии',
            '{{AVG_HEARTRATE}}': str(avg_heartrate),
            '{{AVG_SLEEP}}': str(avg_sleep),
            '{{VO2_MAX}}': str(vo2_max),
            '{{CALORIES}}': str(calories),
            '{{MNIP_INDEX}}': str(mnip_index),
            '{{MNIP_PROGRESS}}': mnip_progress,
            '{{MNIP_RECOMMENDATIONS}}': mnip_recommendations,
            '{{LAST_UPDATE}}': last_update
        }

        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)

        # Создаём папку для профиля
        safe_name = sanitize_name(first_name + ' ' + last_name)
        output_dir = OUTPUT_BASE / safe_name
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "index.html"

        # Сохраняем HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ {participant_name} → /profile/{safe_name}/index.html")
        return True

    except Exception as e:
        print(f"❌ {participant_folder.name}: {str(e)}")
        return False


def main():
    """Генерирует профили для всех участников"""

    print("=" * 70)
    print("🧠 ONTO NOTHING — Profile Generator")
    print("=" * 70)
    print(f"📁 Obsidian Vault: {OBSIDIAN_VAULT}")
    print(f"📄 Template: {TEMPLATE_PATH}")
    print(f"📤 Output: {OUTPUT_BASE}")
    print("=" * 70)
    print()

    if not OBSIDIAN_VAULT.exists():
        print(f"❌ Папка Obsidian не найдена: {OBSIDIAN_VAULT}")
        return

    if not TEMPLATE_PATH.exists():
        print(f"❌ Шаблон не найден: {TEMPLATE_PATH}")
        return

    # Находим все папки участников
    participant_folders = [
        d for d in OBSIDIAN_VAULT.iterdir()
        if d.is_dir() and (d / "profile.json").exists()
    ]

    if not participant_folders:
        print("ℹ️  Нет участников с profile.json")
        return

    print(f"📊 Найдено участников: {len(participant_folders)}\n")

    # Генерируем профили
    success_count = 0
    for folder in sorted(participant_folders):
        if generate_profile(folder):
            success_count += 1

    print()
    print("=" * 70)
    print(f"✨ Готово! Успешно создано: {success_count}/{len(participant_folders)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
