# ONTO NOTHING — Архитектура сайта

Этот файл — инструкция для Claude. Читай его в начале каждого чата, чтобы понять структуру проекта.

---

## Структура проекта

```
genesis/
├── index.html                  ← Главная страница (сложная, со своими стилями)
├── CLAUDE.md                   ← Этот файл
├── css/
│   ├── style.css               ← Общие стили (токены, типографика, карточки, кнопки)
│   └── nav.css                 ← Стили навигации и подвала
├── components/
│   ├── nav.js                  ← Общая навигация (вставляется JS-ом)
│   └── footer.js               ← Общий подвал (вставляется JS-ом)
├── ritmy/index.html            ← Ритмы жизни
├── issledovanie/index.html     ← Исследование
├── mnip/index.html             ← MNIP (продукт)
├── neiry/index.html            ← Neiry (партнёр/технология)
├── blog/index.html             ← Блог (список статей)
├── zapisatsya/index.html       ← Записаться (форма заявки)
└── kak-eto-rabotaet/index.html ← Как это работает (шаги методологии)
```

---

## Назначение страниц

| Страница | Путь | Назначение |
|---|---|---|
| Главная | `index.html` | Hero + EEG-анимация, основной лендинг |
| Ритмы жизни | `ritmy/` | Биологические ритмы и практика |
| Исследование | `issledovanie/` | Наука, методология, данные ЭЭГ |
| MNIP | `mnip/` | Описание продукта MNIP |
| Neiry | `neiry/` | Нейроинтерфейсы Neiry |
| Блог | `blog/` | Список статей, ссылки на посты |
| Записаться | `zapisatsya/` | Форма заявки |
| Как это работает | `kak-eto-rabotaet/` | Пошаговая методология |

---

## Навигация — как работает

Навигация живёт в **одном месте**: `components/nav.js`

- Скрипт вставляет `<nav>` в начало `<body>` через `insertAdjacentHTML`
- Активный пункт меню определяется автоматически по `window.location.pathname`
- Кнопка «Как это работает» выделена отдельным стилем `.nav-cta`
- Мобильное меню открывается бургером (работает без jQuery)

**Где менять пункты меню:** `components/nav.js`, массив `navItems` (строки ~20-28)

**Где менять кнопку CTA:** `components/nav.js`, объект `ctaItem` (строка ~30)

---

## Подвал — как работает

Подвал живёт в `components/footer.js`

- Вставляется перед `</body>` через `insertAdjacentHTML('beforeend', ...)`
- Список ссылок в подвале: массив `footerLinks` в том же файле
- Год в копирайте обновляется автоматически через `new Date().getFullYear()`

**Где менять подвал:** `components/footer.js`

---

## Дизайн-токены (CSS-переменные)

Определены в `css/style.css` в `:root`:

```css
--bg:      #ECEEF2   /* фон страницы */
--text:    #16161A   /* основной текст */
--muted:   #888896   /* приглушённый текст */
--accent:  #5F5FFF   /* фиолетовый акцент */
--blue:    #0A84FF   /* синий акцент */
--fh:      "Oswald"  /* шрифт заголовков */
--fb:      "Jost"    /* шрифт тела */
--fm:      "Courier Prime"  /* моноширинный */
--ft:      "VT323"   /* терминальный */
```

---

## Как добавить новую страницу

1. Создать папку: `mkdir новая-страница`
2. Создать файл `новая-страница/index.html` по шаблону ниже
3. Добавить пункт в `components/nav.js` → массив `navItems`
4. Добавить пункт в `components/footer.js` → массив `footerLinks`

### Шаблон новой страницы

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Название — ONTO NOTHING</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Jost:wght@400;500;600&family=Oswald:wght@500;600;700&family=VT323&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/nav.css">
</head>
<body>

<div class="page-orbs">
  <span></span>
  <span></span>
</div>

<main>
  <section class="page-hero s">
    <div class="s-inner">
      <span class="tag">категория</span>
      <h1>Заголовок страницы</h1>
      <p>Краткое описание.</p>
    </div>
  </section>

  <section class="s">
    <div class="s-inner">
      <!-- контент -->
    </div>
  </section>
</main>

<script src="../components/nav.js"></script>
<script src="../components/footer.js"></script>
</body>
</html>
```

> **Важно:** пути `../css/` и `../components/` — относительные от папки страницы.
> Для вложенных страниц (например, `blog/post-1/`) используй `../../css/` и `../../components/`.

---

## Особенности главной страницы

`index.html` — сложная страница с собственными инлайн-стилями и JS-анимациями (EEG, орбы). Она **не подключает** `css/style.css` — стили встроены прямо в `<style>`. Навигация и подвал на главной пока **не подключены** — можно добавить при необходимости, добавив скрипты перед `</body>` и скорректировав отступы.

---

## Правила при создании страниц для блога

> **ОБЯЗАТЕЛЬНО:** Когда пользователь просит создать страницу для блога — **всегда** выполняй ВСЕ шаги:

1. **Создать папку** в `blog/` (например, `blog/название-поста/`)
2. **Создать `index.html`** в этой папке с контентом
3. **Подключить навигацию и подвал** — добавить перед `</body>`:
   ```html
   <script src="../../components/nav.js"></script>
   <script src="../../components/footer.js"></script>
   ```
4. **Подключить стили навигации** в `<head>`:
   ```html
   <link rel="stylesheet" href="../../css/nav.css">
   ```
5. **Добавить карточку в `blog/index.html`** — вставить `<a class="post-card">` в начало `#grid-articles` с датой, заголовком и описанием. Если статья свежая — добавить плашку `<span class="post-badge-new">NEW</span>`

Пример карточки:
```html
<a href="./название-поста/index.html" class="post-card">
  <span class="post-badge-new">NEW</span>
  <div class="post-date">2026-04-06</div>
  <div class="post-title">Заголовок статьи</div>
  <p class="post-excerpt">Краткое описание статьи для карточки в блоге.</p>
</a>
```

> **Не забывай!** Без карточки в `blog/index.html` страница будет существовать, но до неё нельзя будет добраться из блога.

---

## Стек

- Чистый HTML + CSS + JavaScript
- Без фреймворков, без сборщиков
- Открывается локально через `file://` или любой статический сервер
