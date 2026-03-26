/**
 * ONTO NOTHING — Shared Navigation
 * Вставляет шапку и подвал на каждую страницу автоматически.
 *
 * Как использовать:
 *   <script src="/components/nav.js"></script>
 *   или с относительным путём:
 *   <script src="../components/nav.js"></script>
 *
 * Активный пункт меню определяется автоматически по URL.
 */

(function () {
  // ── Определяем корень сайта ──────────────────────────────────────
  const path = window.location.pathname;

  // Формируем относительный путь до корня
  // (работает при открытии файлов напрямую через file://)
  const depth = (path.match(/\//g) || []).length - 1;
  const root = depth <= 1 ? './' : '../'.repeat(depth - 1);

  // ── Пункты меню ─────────────────────────────────────────────────
  const navItems = [
    { label: 'Главная',           href: root + 'blog/programma-issledovaniya/index.html', match: /\/programma-issledovaniya\// },
    { label: 'Neiry',             href: root + 'neiry/index.html',                        match: /\/neiry\// },
    { label: 'Блог',              href: root + 'blog/index.html',                         match: /^\/blog\/$|\/blog\/index\.html$/ },
    { label: 'Как это работает',  href: root + 'kak-eto-rabotaet/index.html',             match: /\/kak-eto-rabotaet\// },
    { label: 'ONTO NOTHING',      href: root + 'onto-nothing/index.html',                  match: /\/onto-nothing\// },
  ];

  // ── Собираем HTML навигации ──────────────────────────────────────
  const linksHtml = navItems.map(item => {
    const isActive = item.match.test(path) ? ' active' : '';
    return `<li><a href="${item.href}" class="${isActive.trim()}">${item.label}</a></li>`;
  }).join('');

  const navHtml = `
<nav class="site-nav" id="site-nav">
  <a href="${root}blog/programma-issledovaniya/index.html" class="nav-logo">RHYTHMS OF NOTHING × NEIRY</a>
  <ul class="nav-links" id="nav-links">
    ${linksHtml}
  </ul>
  <button class="nav-burger" id="nav-burger" aria-label="Меню">
    <span></span><span></span><span></span>
  </button>
</nav>`;

  // ── Вставляем навигацию в начало body ───────────────────────────
  document.body.insertAdjacentHTML('afterbegin', navHtml);

  // ── Мобильное меню — бургер ──────────────────────────────────────
  const burger = document.getElementById('nav-burger');
  const links  = document.getElementById('nav-links');

  burger.addEventListener('click', () => {
    links.classList.toggle('open');
    const isOpen = links.classList.contains('open');
    burger.setAttribute('aria-expanded', isOpen);
  });

  // Закрываем при клике на ссылку
  links.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') {
      links.classList.remove('open');
    }
  });
})();
