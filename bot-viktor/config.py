import os

BOT_TOKEN = "1168583074:AAGSYIDZ25Y5wpZlLciE_Dt5d1yRfXPBEiQ"

VAULT_PATH = os.path.expanduser("~/Documents/Obsidian Vault/genesis")
BOT_PATH = os.path.join(VAULT_PATH, "bot-viktor")
CLIENTS_PATH = os.path.expanduser("~/Documents/Obsidian Vault/VIP клиенты")

COACH_TELEGRAM_ID = 41537154

CHATS = {
    -5257190682: {
        "name": "Виктор",
        "display": "Виктор",
        "client_telegram_id": None,
        "reports_dir": "Отчеты",
    },
}

SESSION_START_HOUR = 9
SESSION_END_HOUR = 11
EVENING_START_HOUR = 17
