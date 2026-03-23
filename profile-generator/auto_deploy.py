#!/usr/bin/env python3
"""
ONTO NOTHING — Auto Deploy
Генерирует профили и пушит на GitHub автоматически
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Пути
GENESIS_DIR = Path("/Users/konstantin/Documents/genesis")
OBSIDIAN_VAULT = Path("/Users/konstantin/Documents/Obsidian Vault/Данные участников")
TEMPLATE_PATH = GENESIS_DIR / "profile-generator" / "profile_template.html"
OUTPUT_BASE = GENESIS_DIR / "profile"

# Git configuration - use SSH with configured keys
GIT_REMOTE = "git@github.com:konstantinshell/genesis.git"

# Логирование
LOG_FILE = Path("/tmp/onto-nothing-autoupdate.log")

def log(message: str):
    """Логирует сообщение в файл и консоль"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def run_command(cmd: str, cwd: Path = None) -> bool:
    """Выполняет bash команду, возвращает True если успешно"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            log(f"❌ Command failed: {cmd}")
            log(f"   Error: {result.stderr}")
            return False
        if result.stdout:
            log(f"   {result.stdout.strip()}")
        return True
    except Exception as e:
        log(f"❌ Exception running command: {str(e)}")
        return False

def transliterate(text: str) -> str:
    """Транслитерирует русский текст в латиницу"""
    trans_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
        'я': 'ya'
    }
    result = []
    for char in text.lower():
        result.append(trans_table.get(char, char))
    return ''.join(result)

def sanitize_name(name: str) -> str:
    """Преобразует имя в безопасное имя папки для URL"""
    safe = transliterate(name.lower())
    safe = re.sub(r'[^\w\s-]', '', safe)
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
    lines = []
    for line in md_content.split('\n'):
        if line.strip() and not line.startswith('#') and not line.startswith('**') and not line.startswith('---'):
            lines.append(line.strip())
    return ' '.join(lines)

def generate_profiles() -> bool:
    """Генерирует профили для всех участников"""
    log("🧠 Starting profile generation...")

    # Загружаем шаблон
    if not TEMPLATE_PATH.exists():
        log(f"❌ Template not found: {TEMPLATE_PATH}")
        return False

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        TEMPLATE = f.read()

    if not OBSIDIAN_VAULT.exists():
        log(f"❌ Obsidian vault not found: {OBSIDIAN_VAULT}")
        return False

    # Находим все папки участников
    participant_folders = [
        d for d in OBSIDIAN_VAULT.iterdir()
        if d.is_dir() and (d / "profile.json").exists()
    ]

    if not participant_folders:
        log("ℹ️  No participants found")
        return True

    log(f"📊 Found {len(participant_folders)} participants")

    success_count = 0
    for folder in sorted(participant_folders):
        try:
            participant_name = folder.name
            profile_data = load_json(folder / "profile.json")

            if not profile_data:
                log(f"⚠️  {participant_name}: profile.json is empty")
                continue

            # Загружаем данные
            reports_dir = folder / "reports"
            reflection_md = load_text(reports_dir / "reflection.md")
            mnip_report = load_json(reports_dir / "mnip_report.json")
            fitness_data = load_json(reports_dir / "fitness_summary.json")

            # Подготавливаем данные
            name_parts = profile_data.get('name', 'Unknown').split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            safe_name = participant_name

            age = 0
            if 'birthdate' in profile_data:
                age = get_age_from_birthdate(profile_data['birthdate'])
            elif 'age' in profile_data:
                age = profile_data['age']

            reflection_text = reflection_md
            if reflection_text.startswith('#'):
                reflection_text = extract_markdown_text(reflection_md)

            mnip_index = mnip_report.get('score', 'N/A')
            mnip_progress = mnip_report.get('progress', 'Данные обновляются...')
            mnip_recommendations = mnip_report.get('recommendations', 'Продолжайте отслеживать свои метрики.')

            avg_heartrate = fitness_data.get('avg_heartrate', '72')
            avg_sleep = fitness_data.get('avg_sleep', '7.5')
            vo2_max = fitness_data.get('vo2_max', '--')
            calories = fitness_data.get('calories', '--')

            avatar_url = profile_data.get('avatar_url', 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Ccircle cx="50" cy="50" r="50" fill="%235F5FFF"/%3E%3Ctext x="50" y="60" font-size="50" font-weight="bold" fill="white" text-anchor="middle"%3E%3F%3C/text%3E%3C/svg%3E')

            last_update = datetime.now().strftime('%d.%m.%Y %H:%M')

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

            # Создаём папку и сохраняем HTML
            output_dir = OUTPUT_BASE / safe_name
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "index.html"

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            log(f"✅ {participant_name}")
            success_count += 1

        except Exception as e:
            log(f"❌ {folder.name}: {str(e)}")

    log(f"✨ Generated {success_count}/{len(participant_folders)} profiles")
    return True

def deploy_to_github() -> bool:
    """Коммитит и пушит профили на GitHub"""
    log("📤 Deploying to GitHub...")

    # Проверяем есть ли изменения
    if not run_command("git status --short", cwd=GENESIS_DIR):
        log("❌ Git status check failed")
        return False

    # Git add
    if not run_command("git add profile/", cwd=GENESIS_DIR):
        log("❌ Git add failed")
        return False

    # Git commit
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"Auto-update profiles - {timestamp}"
    if not run_command(f'git commit -m "{commit_msg}"', cwd=GENESIS_DIR):
        log("⚠️  Nothing to commit or commit failed")

    # Git push
    if not run_command("git push origin main", cwd=GENESIS_DIR):
        log("❌ Git push failed")
        return False

    log("✅ Deployed to GitHub")
    return True

def main():
    """Главная функция"""
    log("=" * 70)
    log("🚀 ONTO NOTHING — Auto Deploy")
    log("=" * 70)

    # Генерируем профили
    if not generate_profiles():
        log("❌ Profile generation failed")
        return False

    # Пушим на GitHub
    if not deploy_to_github():
        log("❌ GitHub deployment failed")
        return False

    log("=" * 70)
    log("🎉 Auto deploy completed successfully!")
    log("=" * 70)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
