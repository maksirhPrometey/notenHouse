/* NotenHaus — Shipping & Payment FAQ accordion */

(function () {
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function setOpen(item, trigger, panel, open) {
    item.classList.toggle('is-open', open);
    trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      panel.removeAttribute('hidden');
    } else if (reducedMotion.matches) {
      panel.setAttribute('hidden', '');
    } else {
      window.setTimeout(function () {
        if (!item.classList.contains('is-open')) {
          panel.setAttribute('hidden', '');
        }
      }, 320);
    }
  }

  function initFaq() {
    var root = document.querySelector('[data-shipping-faq]');
    if (!root) return;

    var items = root.querySelectorAll('.faq-item');
    items.forEach(function (item) {
      var trigger = item.querySelector('[data-faq-trigger]');
      var panel = item.querySelector('[data-faq-panel]');
      if (!trigger || !panel) return;

      trigger.addEventListener('click', function () {
        var willOpen = trigger.getAttribute('aria-expanded') !== 'true';
        items.forEach(function (other) {
          var otherTrigger = other.querySelector('[data-faq-trigger]');
          var otherPanel = other.querySelector('[data-faq-panel]');
          if (!otherTrigger || !otherPanel) return;
          setOpen(other, otherTrigger, otherPanel, other === item ? willOpen : false);
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFaq);
  } else {
    initFaq();
  }
})();
