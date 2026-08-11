/* NotenHaus — catalog filters drawer (mobile) */

(function () {
  const toggle = document.getElementById('catalog-filter-toggle');
  const shell = document.getElementById('catalog-filters-panel');
  if (!toggle || !shell) return;

  const mq = window.matchMedia('(max-width: 1023px)');
  const form = document.getElementById('catalog-filter-form');

  function releaseFocusFromShell() {
    const active = document.activeElement;
    if (!active || typeof active.focus !== 'function') return;
    if (!shell.contains(active)) return;
    // Move focus out before aria-hidden/inert — avoids Chrome a11y warning
    toggle.focus({ preventScroll: true });
  }

  function syncA11y(open) {
    if (mq.matches) {
      if (!open) releaseFocusFromShell();
      shell.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open) {
        shell.removeAttribute('inert');
      } else {
        shell.setAttribute('inert', '');
      }
    } else {
      shell.setAttribute('aria-hidden', 'false');
      shell.removeAttribute('inert');
    }
  }

  function setOpen(open) {
    if (!mq.matches) {
      releaseFocusFromShell();
      shell.classList.remove('is-open');
      document.body.classList.remove('is-filters-open');
      toggle.setAttribute('aria-expanded', 'false');
      syncA11y(false);
      return;
    }
    shell.classList.toggle('is-open', open);
    document.body.classList.toggle('is-filters-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    syncA11y(open);
  }

  toggle.addEventListener('click', function () {
    setOpen(!shell.classList.contains('is-open'));
  });

  shell.querySelectorAll('[data-filter-close]').forEach(function (el) {
    el.addEventListener('click', function () {
      setOpen(false);
    });
  });

  if (form) {
    form.addEventListener('submit', function () {
      if (mq.matches) setOpen(false);
    });
  }

  document.body.addEventListener('htmx:afterRequest', function (event) {
    const source = event.detail && event.detail.elt;
    if (source && form && (source === form || form.contains(source)) && mq.matches) {
      setOpen(false);
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && shell.classList.contains('is-open')) {
      setOpen(false);
    }
  });

  function onViewportChange() {
    if (!mq.matches) setOpen(false);
    else syncA11y(shell.classList.contains('is-open'));
  }

  syncA11y(false);

  if (typeof mq.addEventListener === 'function') {
    mq.addEventListener('change', onViewportChange);
  } else if (typeof mq.addListener === 'function') {
    mq.addListener(onViewportChange);
  }
})();
