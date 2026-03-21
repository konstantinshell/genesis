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

  const footerLinks = [
    { label: 'Главная',         href: root + 'index.html' },
    { label: 'Ритмы жизни',     href: root + 'ritmy/index.html' },
    { label: 'Исследование',    href: root + 'issledovanie/index.html' },
    { label: 'MNIP',            href: root + 'mnip/index.html' },
    { label: 'Neiry',           href: root + 'neiry/index.html' },
    { label: 'Блог',            href: root + 'blog/index.html' },
    { label: 'Записаться',      href: root + 'zapisatsya/index.html' },
    { label: 'Как это работает',href: root + 'kak-eto-rabotaet/index.html' },
  ];

  const linksHtml = footerLinks.map(item =>
    `<li><a href="${item.href}">${item.label}</a></li>`
  ).join('');

  const year = new Date().getFullYear();

  const footerHtml = `
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <div class="footer-brand">ONTO NOTHING</div>
      <p class="footer-desc">Исследование состояний сознания через технологии и практику.</p>
    </div>
    <ul class="footer-links">
      ${linksHtml}
    </ul>
    <div class="footer-copy">© ${year} ONTO NOTHING. Все права защищены.</div>
  </div>
</footer>`;

  document.body.insertAdjacentHTML('beforeend', footerHtml);
})();
