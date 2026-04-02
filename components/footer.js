/**
 * ONTO NOTHING — Shared Footer
 * Вставляет подвал перед закрывающим тегом </body>.
 *
 * Как использовать:
 *   <script src="/components/footer.js"></script>
 */

(function () {
  const path = window.location.pathname;
  const depth = (path.match(/\//g) || []).length - 1;
  const root = depth <= 1 ? './' : '../'.repeat(depth - 1);

  const navLinks = [
    { label: 'Главная',           href: root + 'index.html' },
    { label: 'Ритмы жизни',       href: root + 'ritmy/index.html' },
    { label: 'Исследование',      href: root + 'issledovanie/index.html' },
    { label: 'MNIP',              href: root + 'mnip/index.html' },
    { label: 'Neiry',             href: root + 'neiry/index.html' },
    { label: 'Блог',              href: root + 'blog/index.html' },
    { label: 'Записаться',        href: root + 'zapisatsya/index.html' },
    { label: 'Как это работает',  href: root + 'kak-eto-rabotaet/index.html' },
    { label: 'ONTO NOTHING',      href: root + 'onto-nothing/index.html' },
  ];

  const legalLinks = [
    { label: 'Политика конфиденциальности',                  href: root + 'privacy/index.html' },
    { label: 'Согласие на обработку персональных данных',    href: '#' },
    { label: 'Пользовательское соглашение',                  href: '#' },
  ];

  const navHtml = navLinks.map(item =>
    `<li><a href="${item.href}">${item.label}</a></li>`
  ).join('');

  const legalHtml = legalLinks.map(item =>
    `<li><a href="${item.href}">${item.label}</a></li>`
  ).join('');

  const year = new Date().getFullYear();

  const footerHtml = `
<footer class="site-footer">
  <div class="footer-inner">

    <div class="footer-col footer-col--brand">
      <div class="footer-brand">RHYTHMS OF NOTHING × NEIRY</div>
      <p class="footer-desc">Исследование состояний сознания через технологии и практику.</p>
    </div>

    <div class="footer-col footer-col--nav">
      <div class="footer-col-title">Навигация</div>
      <ul class="footer-links">
        ${navHtml}
      </ul>
    </div>

    <div class="footer-col footer-col--legal-links">
      <div class="footer-col-title">Документы</div>
      <ul class="footer-links">
        ${legalHtml}
      </ul>
    </div>

  </div>

  <div class="footer-bottom">
    <div class="footer-bottom-inner">
      <div class="footer-copy-row">
        <p class="footer-copy">© ${year} Индивидуальный предприниматель Шель Константин. Проект RHYTHMS OF NOTHING × NEIRY. Все права защищены.</p>
        <a href="#" class="footer-neiry-badge">
          <span class="badge-label">Neurotech Partner</span>
          <span class="badge-name">NEIRY</span>
        </a>
      </div>
      <p class="footer-disclaimer">Информация, размещённая на сайте, носит ознакомительный характер и не является публичной офертой, определяемой положениями Статьи 437 ГК РФ.</p>
      <p class="footer-warning">Все материалы данного сайта (тексты, авторские методики, структура) являются объектами авторского права. Любое копирование, распространение или использование контента без письменного согласия правообладателя строго запрещено. Нарушение преследуется по закону (ст.&nbsp;1252, 1301 ГК РФ).</p>
    </div>
  </div>
</footer>`;

  document.body.insertAdjacentHTML('beforeend', footerHtml);
})();
