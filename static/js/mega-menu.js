/* NotenHaus — mega-menu open/close + sidebar tabs */

(function () {
  const root = document.getElementById('catalog-panel');
  const triggers = document.querySelectorAll('[data-mega-toggle]');
  if (!root || !triggers.length) return;

  const body = document.body;
  const tabs = root.querySelectorAll('[data-mega-tab]');
  const panes = root.querySelectorAll('[data-mega-pane]');
  let lastFocus = null;

  function setOpen(open) {
    if (open) {
      lastFocus = document.activeElement;
      root.hidden = false;
      // force reflow for enter animation
      void root.offsetWidth;
      root.classList.add('is-open');
      body.classList.add('is-mega-open');
      triggers.forEach(function (btn) {
        btn.setAttribute('aria-expanded', 'true');
      });
      const firstTab = root.querySelector('.mega-menu__cat.is-active') || tabs[0];
      if (firstTab) firstTab.focus();
    } else {
      root.classList.remove('is-open');
      body.classList.remove('is-mega-open');
      triggers.forEach(function (btn) {
        btn.setAttribute('aria-expanded', 'false');
      });
      window.setTimeout(function () {
        if (!root.classList.contains('is-open')) {
          root.hidden = true;
        }
      }, 300);
      if (lastFocus && typeof lastFocus.focus === 'function') {
        lastFocus.focus();
      }
    }
  }

  function isOpen() {
    return root.classList.contains('is-open');
  }

  function activateTab(key) {
    tabs.forEach(function (tab) {
      const active = tab.getAttribute('data-mega-tab') === key;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
      tab.setAttribute('tabindex', active ? '0' : '-1');
    });
    panes.forEach(function (pane) {
      const active = pane.getAttribute('data-mega-pane') === key;
      pane.classList.toggle('is-active', active);
      if (active) {
        pane.removeAttribute('hidden');
      } else {
        pane.setAttribute('hidden', '');
      }
    });
  }

  triggers.forEach(function (btn) {
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      if (typeof window.notenHausCloseMobileNav === 'function') {
        window.notenHausCloseMobileNav();
      }
      setOpen(!isOpen());
    });
  });

  root.querySelectorAll('[data-mega-close]').forEach(function (el) {
    el.addEventListener('click', function () {
      setOpen(false);
    });
  });

  tabs.forEach(function (tab) {
    tab.setAttribute('tabindex', tab.classList.contains('is-active') ? '0' : '-1');
    tab.addEventListener('click', function () {
      activateTab(tab.getAttribute('data-mega-tab'));
    });
    tab.addEventListener('keydown', function (event) {
      const list = Array.prototype.slice.call(tabs);
      const index = list.indexOf(tab);
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
        event.preventDefault();
        const next = list[(index + 1) % list.length];
        activateTab(next.getAttribute('data-mega-tab'));
        next.focus();
      } else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault();
        const prev = list[(index - 1 + list.length) % list.length];
        activateTab(prev.getAttribute('data-mega-tab'));
        prev.focus();
      } else if (event.key === 'Home') {
        event.preventDefault();
        activateTab(list[0].getAttribute('data-mega-tab'));
        list[0].focus();
      } else if (event.key === 'End') {
        event.preventDefault();
        activateTab(list[list.length - 1].getAttribute('data-mega-tab'));
        list[list.length - 1].focus();
      }
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && isOpen()) {
      setOpen(false);
    }
  });
})();
