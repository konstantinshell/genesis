# Карта навигации и подвала

Какие страницы подключают `nav.js` + `footer.js`, а какие — standalone.

---

## Страницы сайта (nav + footer)

| Страница | Путь | nav.js | footer.js |
|---|---|---|---|
| Главная | `index.html` | + | + |
| Ритмы жизни | `ritmy/` | + | + |
| Исследование | `issledovanie/` | + | + |
| Neiry | `neiry/` | + | + |
| Блог | `blog/` | + | + |
| Записаться | `zapisatsya/` | + | + |
| Как это работает | `kak-eto-rabotaet/` | + | + |
| Партнёры | `partners/` | + | + |
| Дорожная карта | `roadmap/` | + | + |
| Политика конфиденциальности | `privacy/` | + | + |
| Гайд Whoop | `blog/whoop-guide/` | + | + |
| Гайд Apple Watch | `blog/apple-watch-guide/` | + | + |
| Гайд Garmin | `blog/garmin-guide/` | + | + |
| Носимые трекеры | `blog/nosimye-trekery/` | + | + |
| Транскрипция | `blog/transcription/` | + | + |
| Программа исследования | `blog/programma-issledovaniya/` | + | + |
| MNIP презентация | `blog/mnpi-presentation/` | + | + |
| Neiry презентация | `blog/neiry-presentation/` | + | + |
| Нарратив презентация | `blog/prezentaciya-narrativ/` | + | + |
| MNIP | `mnip/` | + | + |

---

## Standalone-страницы (без nav и footer)

Эти страницы **не должны** иметь общую навигацию — у них свой контекст, дизайн или точка входа.

| Страница | Путь | Почему standalone |
|---|---|---|
| Сеть | `network/` | Реферальная карта, standalone |
| NDA | `nda/` | Юридический документ, отправляется ботом |
| Логотип | `logo/` | Визуальная страница, только лого |
| Telegram mini-app | `mini-app/` | Встроена в Telegram WebApp |
| Neiry Capsule Guide | `neiry/guide.html` | Standalone гайд, свой дизайн |

---

## Профили участников (без nav и footer)

Все страницы в `profiles/` — standalone. Открываются из Telegram-бота, свой тёмный дизайн.

| Путь |
|---|
| `profiles/alena/` |
| `profiles/viktor/` |
| `profiles/1067307749/` |
| `profiles/1139648370/` |
| `profiles/147991795/` |
| `profiles/1610267716/` |
| `profiles/221246992/` |
| `profiles/261261504/` |
| `profiles/319756543/` |
| `profiles/407124980/` |
| `profiles/41537154/` |
| `profiles/424514495/` |
| `profiles/429205054/` |
| `profiles/479910423/` |
| `profiles/57740229/` |
| `profiles/652364423/` |
| `profiles/8211648754/` |
| `profiles/8678544199/` |

---

## Как пользоваться

- При создании **новой страницы сайта** — добавь nav.js + footer.js и отметь здесь
- При создании **standalone-страницы** (презентация, профиль, документ) — НЕ добавляй nav/footer, отметь здесь
- Если страница меняет статус — обнови эту таблицу
