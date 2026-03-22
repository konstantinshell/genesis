#!/usr/bin/env python3
"""
ONTO NOTHING — Telegram Bot
Сохраняет данные участников прямо в Obsidian папку
"""

import os
import json
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from telegram.constants import ParseMode

# НАСТРОЙКИ
TELEGRAM_BOT_TOKEN = "8656261306:AAHQ3U9ByFvkfyCY4Xp0GP9tBCekK9kip_Q"
OBSIDIAN_VAULT = Path("/Users/konstantin/Documents/Obsidian Vault/Данные участников")
WEBSITE_URL = "https://konstantinshell.github.io/genesis"

# Создаём папку если её нет
OBSIDIAN_VAULT.mkdir(parents=True, exist_ok=True)

# Состояния для ConversationHandler
WAITING_FOR_NAME, WAITING_FOR_PHONE, WAITING_FOR_SESSION = range(3)

# Хранилище данных сессии пользователя
user_sessions = {}


def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def get_user_folder(user_id: int, name: str) -> Path:
    """Получает или создаёт папку пользователя"""
    safe_name = sanitize_filename(name)
    user_folder = OBSIDIAN_VAULT / safe_name
    user_folder.mkdir(parents=True, exist_ok=True)
    return user_folder


def load_user_data(user_folder: Path) -> dict:
    """Загружает данные пользователя из profile.json"""
    profile_file = user_folder / "profile.json"
    if profile_file.exists():
        with open(profile_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_user_data(user_folder: Path, data: dict):
    """Сохраняет данные пользователя в profile.json"""
    profile_file = user_folder / "profile.json"
    with open(profile_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога с пользователем"""
    user_id = update.effective_user.id

    # Проверяем есть ли уже папка
    user_data = context.user_data

    await update.message.reply_text(
        "🧠 *Добро пожаловать в ONTO NOTHING!*\n\n"
        "Я помогу тебе отслеживать прогресс твоих сессий.\n\n"
        "Сначала представься — как тебя зовут?",
        parse_mode=ParseMode.MARKDOWN
    )

    return WAITING_FOR_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем имя пользователя"""
    name = update.message.text.strip()
    user_id = update.effective_user.id

    # Сохраняем в контекст
    context.user_data['name'] = name
    context.user_data['user_id'] = user_id

    # Создаём папку
    user_folder = get_user_folder(user_id, name)
    context.user_data['user_folder'] = str(user_folder)

    await update.message.reply_text(
        f"👤 Спасибо, {name}!\n\n"
        "Теперь твой номер телефона (например: +7 (999) 123-45-67)",
        parse_mode=ParseMode.MARKDOWN
    )

    return WAITING_FOR_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем телефон пользователя"""
    phone = update.message.text.strip()
    name = context.user_data['name']
    user_folder = Path(context.user_data['user_folder'])

    # Загружаем или создаём профиль
    user_data = load_user_data(user_folder)
    user_data['name'] = name
    user_data['phone'] = phone
    user_data['created_at'] = datetime.now().isoformat()
    user_data['sessions'] = user_data.get('sessions', [])

    # Сохраняем профиль
    save_user_data(user_folder, user_data)
    context.user_data['user_data'] = user_data

    # Создаём ссылку на профиль
    profile_url = f"{WEBSITE_URL}/profile/{name.replace(' ', '-')}"

    keyboard = [
        [InlineKeyboardButton("📊 Мой профиль", url=profile_url)],
        [InlineKeyboardButton("📤 Загрузить данные", callback_data="upload_data")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ *Профиль создан!*\n\n"
        f"📊 Твой профиль: {profile_url}\n\n"
        f"*Как это работает:*\n"
        f"1. Отправь мне CSV файл с метриками\n"
        f"2. Или опиши результаты текстом\n"
        f"3. Я сохраню всё в твоей папке\n"
        f"4. Профиль обновится автоматически\n\n"
        f"*Начни с отправки данных сессии:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    return ConversationHandler.END


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получаем файлы от пользователя"""
    user_id = update.effective_user.id
    message = update.message

    # Проверяем есть ли папка пользователя
    user_folder = None
    for folder in OBSIDIAN_VAULT.iterdir():
        if folder.is_dir():
            profile_file = folder / "profile.json"
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    if data.get('user_id') == user_id or not data.get('user_id'):
                        user_folder = folder
                        break

    if not user_folder:
        await message.reply_text(
            "❌ Папка не найдена. Начни с /start"
        )
        return

    # Работаем с файлом
    if message.document:
        file = await message.document.get_file()
        filename = sanitize_filename(message.document.file_name)
        filepath = user_folder / filename

        await file.download_to_drive(filepath)

        # Обновляем профиль
        user_data = load_user_data(user_folder)
        session_num = len(user_data.get('sessions', [])) + 1

        user_data['sessions'].append({
            'number': session_num,
            'date': datetime.now().isoformat(),
            'file': filename
        })

        save_user_data(user_folder, user_data)

        await message.reply_text(
            f"✅ *Файл сохранён!*\n\n"
            f"📁 Файл: {filename}\n"
            f"📊 Сессия: {session_num}\n"
            f"🕐 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Данные синхронизируются в Obsidian..."
        )


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получаем текстовое описание сессии"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text.startswith('/'):
        return

    # Ищем папку пользователя по user_id в profile.json
    user_folder = None
    for folder in OBSIDIAN_VAULT.iterdir():
        if folder.is_dir():
            profile_file = folder / "profile.json"
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        # Проверяем есть ли user_id
                        if data.get('user_id') == user_id:
                            user_folder = folder
                            break
                        # Если нет user_id, берём первую попавшуюся папку (для отладки)
                        if not user_folder and not data.get('user_id'):
                            user_folder = folder
                    except:
                        pass

    if not user_folder:
        await update.message.reply_text(
            "❌ Папка не найдена. Начни с /start"
        )
        return

    # Обновляем профиль
    user_data = load_user_data(user_folder)
    session_num = len(user_data.get('sessions', [])) + 1

    # Создаём markdown файл
    md_content = f"""# Сессия {session_num}

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Участник:** {user_data.get('name', 'Unknown')}

## Отчёт

{text}

---

*Создано через Telegram бот ONTO NOTHING*
"""

    md_filename = f"Session_{session_num}.md"
    md_filepath = user_folder / md_filename

    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # Обновляем profile.json
    user_data['sessions'].append({
        'number': session_num,
        'date': datetime.now().isoformat(),
        'file': md_filename
    })

    save_user_data(user_folder, user_data)

    await update.message.reply_text(
        f"✅ *Отчёт сохранён!*\n\n"
        f"📊 Сессия: {session_num}\n"
        f"📝 Файл: {md_filename}\n"
        f"🕐 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Данные синхронизируются в Obsidian..."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Справка по командам"""
    await update.message.reply_text(
        "🧠 *ONTO NOTHING Bot*\n\n"
        "*Команды:*\n"
        "/start — начать, создать профиль\n"
        "/help — эта справка\n\n"
        "*Как использовать:*\n"
        "1. /start — создаёшь профиль\n"
        "2. Отправляешь CSV файл или текст\n"
        "3. Бот сохраняет в Obsidian\n"
        "4. Профиль обновляется автоматически\n\n"
        "📁 Все данные в: Obsidian → Данные участников",
        parse_mode=ParseMode.MARKDOWN
    )


def main():
    """Запуск бота"""
    print("=" * 60)
    print("🧠 ONTO NOTHING — Telegram Bot")
    print("=" * 60)
    print(f"📁 Obsidian Vault: {OBSIDIAN_VAULT}")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print("=" * 60)
    print("✅ Бот запущен и слушает сообщения...")
    print("=" * 60)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ConversationHandler для /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            WAITING_FOR_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Обработчики
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))

    # Запускаем бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
