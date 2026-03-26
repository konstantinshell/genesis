# Salebot Webhook Server

Flask-сервер для приёма сообщений от Salebot и сохранения их в Obsidian Vault.

## Запуск

```bash
cd salebot
pip install -r requirements.txt
python server.py
```

Сервер стартует на порту **5001**.

## Эндпоинты

- `GET /test` — проверка что сервер работает
- `POST /webhook` — приём сообщений от Salebot

## Структура данных в Obsidian

```
Obsidian Vault/
└── Salebot/
    └── clients/
        └── Иван Петров/
            └── messages.md
```

## Подключение к Salebot

1. Запустить ngrok: `ngrok http 5001`
2. Скопировать URL вида `https://xxxx.ngrok.io`
3. В настройках Salebot прописать webhook: `https://xxxx.ngrok.io/webhook`
