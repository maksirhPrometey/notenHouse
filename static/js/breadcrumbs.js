/* NotenHaus — breadcrumbs mobile expand */

(function () {
  function bindBreadcrumbs(root) {
    if (!root || root.dataset.breadcrumbsBound === '1') return;
    root.dataset.breadcrumbsBound = '1';

    var btn = root.querySelector('.breadcrumbs__expand');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var expanded = root.classList.toggle('is-expanded');
      btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      if (expanded) {
        btn.setAttribute('aria-label', 'Згорнути шлях');
      } else {
        btn.setAttribute('aria-label', 'Показати повний шлях');
      }
    });
  }

  function init() {
    document.querySelectorAll('[data-breadcrumbs]').forEach(bindBreadcrumbs);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  document.body.addEventListener('htmx:afterSettle', init);
})();
