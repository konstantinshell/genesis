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
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode

# НАСТРОЙКИ
TELEGRAM_BOT_TOKEN = "8656261306:AAHQ3U9ByFvkfyCY4Xp0GP9tBCekK9kip_Q"
OBSIDIAN_VAULT = Path("/Users/konstantin/Documents/Obsidian Vault/Данные участников")
WEBSITE_URL = "https://konstantinshell.github.io/genesis"

# Создаём папку если её нет
OBSIDIAN_VAULT.mkdir(parents=True, exist_ok=True)

# Состояния для ConversationHandler (регистрация)
WAITING_FOR_NAME, WAITING_FOR_SURNAME, WAITING_FOR_AGE, WAITING_FOR_PHONE, WAITING_FOR_CITY, WAITING_FOR_RESEARCH_HISTORY = range(6)


def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def generate_profile_url(name: str, surname: str, phone: str) -> str:
    """Генерирует URL профиля на основе имени, фамилии и последних 4 цифр телефона"""
    # Извлекаем последние 4 цифры из номера
    phone_digits = ''.join(filter(str.isdigit, phone))
    last_4_digits = phone_digits[-4:] if len(phone_digits) >= 4 else phone_digits

    # Создаём URL-friendly часть
    full_name = f"{name} {surname}".lower()
    safe_name = sanitize_filename(full_name).replace('_', '-')

    # Генерируем имя папки
    if last_4_digits:
        folder_name = f"{safe_name}-{last_4_digits}"
    else:
        folder_name = safe_name

    return f"{WEBSITE_URL}/profile/{folder_name}"


def get_user_folder(user_id: int, name: str, surname: str) -> Path:
    """Получает или создаёт папку пользователя"""
    full_name = f"{name} {surname}".strip()
    safe_name = sanitize_filename(full_name)
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


def get_user_folder_by_id(user_id: int) -> Path:
    """Находит папку пользователя по user_id"""
    for folder in OBSIDIAN_VAULT.iterdir():
        if folder.is_dir():
            profile_file = folder / "profile.json"
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if data.get('user_id') == user_id:
                            return folder
                    except:
                        pass
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога с пользователем"""
    user_id = update.effective_user.id
    context.user_data['user_id'] = user_id

    await update.message.reply_text(
        "🧠 Добро пожаловать в ONTO NOTHING!\n\n"
        "Я помогу тебе отслеживать прогресс твоих сессий.\n\n"
        "Давайте начнём с регистрации.\n\n"
        "❓ Как тебя зовут? (Только имя)"
    )

    return WAITING_FOR_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем имя пользователя"""
    name = update.message.text.strip()
    context.user_data['name'] = name

    await update.message.reply_text(
        f"✅ Спасибо, {name}!\n\n"
        "❓ Ваша фамилия?"
    )

    return WAITING_FOR_SURNAME


async def receive_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем фамилию пользователя"""
    surname = update.message.text.strip()
    context.user_data['surname'] = surname

    await update.message.reply_text(
        f"✅ Хорошо!\n\n"
        "❓ Ваш возраст? (введите число, например: 28)"
    )

    return WAITING_FOR_AGE


async def receive_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем возраст пользователя"""
    age_text = update.message.text.strip()

    try:
        age = int(age_text)
        if age < 18 or age > 100:
            await update.message.reply_text(
                "❌ Возраст должен быть от 18 до 100 лет. Попробуйте снова:"
            )
            return WAITING_FOR_AGE
        context.user_data['age'] = age
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введите число (например: 28)"
        )
        return WAITING_FOR_AGE

    await update.message.reply_text(
        f"✅ Вам {age} лет!\n\n"
        "❓ Ваш номер телефона? (например: +7 (999) 123-45-67)"
    )

    return WAITING_FOR_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем номер телефона пользователя"""
    phone = update.message.text.strip()
    context.user_data['phone'] = phone

    await update.message.reply_text(
        f"✅ Спасибо!\n\n"
        "❓ Ваш город?"
    )

    return WAITING_FOR_CITY


async def receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем город пользователя"""
    city = update.message.text.strip()
    context.user_data['city'] = city

    await update.message.reply_text(
        f"✅ {city} — чудесно!\n\n"
        "❓ Вы уже принимали участие в исследованиях? (Да/Нет)"
    )

    return WAITING_FOR_RESEARCH_HISTORY


async def receive_research_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем информацию об опыте исследований"""
    response = update.message.text.strip().lower()

    if response in ['да', 'yes', 'y']:
        context.user_data['research_history'] = True
    elif response in ['нет', 'no', 'n']:
        context.user_data['research_history'] = False
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, ответьте 'Да' или 'Нет'"
        )
        return WAITING_FOR_RESEARCH_HISTORY

    # Сохраняем профиль
    name = context.user_data['name']
    surname = context.user_data['surname']
    age = context.user_data['age']
    phone = context.user_data['phone']
    city = context.user_data['city']
    research_history = context.user_data['research_history']
    user_id = context.user_data['user_id']

    user_folder = get_user_folder(user_id, name, surname)

    # Загружаем или создаём профиль
    user_data = load_user_data(user_folder)
    user_data['name'] = f"{name} {surname}"
    user_data['age'] = age
    user_data['phone'] = phone
    user_data['city'] = city
    user_data['research_history'] = "Да" if research_history else "Нет"
    user_data['user_id'] = user_id
    user_data['created_at'] = datetime.now().isoformat()
    user_data['sessions'] = user_data.get('sessions', [])

    # Сохраняем профиль
    save_user_data(user_folder, user_data)
    context.user_data['user_folder'] = str(user_folder)

    # Генерируем ссылку на профиль
    profile_url = generate_profile_url(name, surname, phone)

    keyboard = [
        [InlineKeyboardButton("📊 Мой профиль", url=profile_url)],
        [InlineKeyboardButton("📤 Загрузить данные", callback_data="upload_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ Профиль создан!\n\n"
        f"👤 {name} {surname}\n"
        f"📱 {phone}\n"
        f"📍 {city}\n"
        f"🎂 {age} лет\n"
        f"📚 Опыт в исследованиях: {'Да' if research_history else 'Нет'}\n\n"
        f"🔗 *Ссылка на профиль:*\n`{profile_url}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Как это работает:\n"
        f"1️⃣ Выбери тип данных для загрузки\n"
        f"2️⃣ Отправь файл или текст\n"
        f"3️⃣ Я сохраню в твоей папке\n"
        f"4️⃣ Профиль обновится автоматически",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    return ConversationHandler.END


async def upload_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора типа загрузки"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📋 Пройти сессию (1-7)", callback_data="choose_session")],
        [InlineKeyboardButton("📅 План на день", callback_data="plan_day")],
        [InlineKeyboardButton("📊 Выгрузка за день", callback_data="export_day")],
        [InlineKeyboardButton("📅 План на неделю", callback_data="plan_week")],
        [InlineKeyboardButton("📊 Выгрузка за неделю", callback_data="export_week")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📤 Выбери тип данных для загрузки:\n\n"
        "*Сессии:*\n"
        "Пройди одну из 7 сессий исследования\n\n"
        "*Планы и выгрузки:*\n"
        "День или неделя данных",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def choose_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор номера сессии"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Сессия 1️⃣", callback_data="session_1"),
         InlineKeyboardButton("Сессия 2️⃣", callback_data="session_2"),
         InlineKeyboardButton("Сессия 3️⃣", callback_data="session_3")],
        [InlineKeyboardButton("Сессия 4️⃣", callback_data="session_4"),
         InlineKeyboardButton("Сессия 5️⃣", callback_data="session_5"),
         InlineKeyboardButton("Сессия 6️⃣", callback_data="session_6")],
        [InlineKeyboardButton("Сессия 7️⃣", callback_data="session_7")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🎯 Выбери номер сессии (1-7):",
        reply_markup=reply_markup
    )


async def session_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сессия выбрана, готовимся к загрузке"""
    query = update.callback_query
    await query.answer()

    session_num = query.data.split('_')[1]
    context.user_data['current_session'] = session_num

    await query.edit_message_text(
        f"✅ Сессия {session_num} выбрана!\n\n"
        f"📤 Теперь отправь в чат:\n"
        f"• CSV файл с метриками\n"
        f"• Или текстовое описание\n"
        f"• Или аудиозапись\n\n"
        f"💡 *Совет:* Аудиозапись ты сможешь увидеть в своем профиле!",
        parse_mode=ParseMode.MARKDOWN
    )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получаем файлы от пользователя"""
    user_id = update.effective_user.user_id
    message = update.message

    # Ищем папку пользователя
    user_folder = get_user_folder_by_id(user_id)

    if not user_folder:
        await message.reply_text("❌ Папка не найдена. Начни с /start")
        return

    # Работаем с файлом
    if message.document:
        file = await message.document.get_file()
        filename = sanitize_filename(message.document.file_name)
        filepath = user_folder / filename

        await file.download_to_drive(filepath)

        # Обновляем профиль
        user_data = load_user_data(user_folder)
        session_num = context.user_data.get('current_session', '1')

        user_data['sessions'].append({
            'number': int(session_num),
            'date': datetime.now().isoformat(),
            'file': filename
        })
        save_user_data(user_folder, user_data)

        await message.reply_text(
            f"✅ Файл сохранён!\n\n"
            f"📁 {filename}\n"
            f"📊 Сессия: {session_num}\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Данные синхронизируются в Obsidian..."
        )

    # ТЕКСТ
    elif message.text and not message.text.startswith('/'):
        text = message.text.strip()
        session_num = context.user_data.get('current_session', '1')
        user_data = load_user_data(user_folder)

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

        user_data['sessions'].append({
            'number': int(session_num),
            'date': datetime.now().isoformat(),
            'file': md_filename
        })
        save_user_data(user_folder, user_data)

        await message.reply_text(
            f"✅ Отчёт сохранён!\n\n"
            f"📝 {md_filename}\n"
            f"📊 Сессия: {session_num}\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Данные синхронизируются в Obsidian..."
        )

    # АУДИО
    elif message.audio or message.voice:
        file_obj = message.audio or message.voice
        file = await file_obj.get_file()

        session_num = context.user_data.get('current_session', '1')
        file_ext = 'mp3' if message.audio else 'ogg'
        filename = f"session_{session_num}_audio.{file_ext}"
        filepath = user_folder / filename

        await file.download_to_drive(filepath)

        user_data = load_user_data(user_folder)
        user_data['sessions'].append({
            'number': int(session_num),
            'date': datetime.now().isoformat(),
            'file': filename,
            'type': 'audio'
        })
        save_user_data(user_folder, user_data)

        await message.reply_text(
            f"✅ Аудиозапись сохранена!\n\n"
            f"🎙️ {filename}\n"
            f"📊 Сессия: {session_num}\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"💡 Ты сможешь послушать её в своём профиле!"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Справка по командам"""
    await update.message.reply_text(
        "🧠 *ONTO NOTHING Bot*\n\n"
        "*Команды:*\n"
        "/start — создать профиль\n"
        "/help — эта справка\n\n"
        "*Как использовать:*\n"
        "1. /start — отвечаешь на вопросы\n"
        "2. Нажимаешь 'Загрузить данные'\n"
        "3. Выбираешь тип (сессия, план, выгрузка)\n"
        "4. Отправляешь данные\n"
        "5. Всё сохраняется в Obsidian",
        parse_mode=ParseMode.MARKDOWN
    )


def main():
    """Запуск бота"""
    print("=" * 60)
    print("🧠 ONTO NOTHING — Telegram Bot v2.1")
    print("=" * 60)
    print(f"📁 Obsidian Vault: {OBSIDIAN_VAULT}")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print("=" * 60)
    print("✅ Бот запущен и слушает сообщения...")
    print("=" * 60)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ConversationHandler ТОЛЬКО для регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            WAITING_FOR_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_surname)],
            WAITING_FOR_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
            WAITING_FOR_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            WAITING_FOR_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)],
            WAITING_FOR_RESEARCH_HISTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_research_history)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Обработчики
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))

    # Callback обработчики для кнопок (ВНЕ ConversationHandler)
    app.add_handler(CallbackQueryHandler(upload_menu_callback, pattern="^upload_menu$"))
    app.add_handler(CallbackQueryHandler(choose_session_callback, pattern="^choose_session$"))
    app.add_handler(CallbackQueryHandler(session_selected_callback, pattern="^session_[1-7]$"))
    app.add_handler(CallbackQueryHandler(upload_menu_callback, pattern="^plan_day$"))
    app.add_handler(CallbackQueryHandler(upload_menu_callback, pattern="^export_day$"))
    app.add_handler(CallbackQueryHandler(upload_menu_callback, pattern="^plan_week$"))
    app.add_handler(CallbackQueryHandler(upload_menu_callback, pattern="^export_week$"))

    # Загрузка файлов и текста
    app.add_handler(MessageHandler(filters.Document.ALL, receive_file))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, receive_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_file))

    # Запускаем бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
