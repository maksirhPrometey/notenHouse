/* NotenHaus — custom dropdown + HTMX (shop_design §6.5 / ERR-82) */

(function () {
  const OPEN_CLASS = 'is-open';
  const SELECTED_CLASS = 'is-selected';

  function closeDropdown(dropdown) {
    dropdown.classList.remove(OPEN_CLASS);
    const trigger = dropdown.querySelector('[data-dropdown-trigger]');
    const menu = dropdown.querySelector('[data-dropdown-menu]');
    if (trigger) trigger.setAttribute('aria-expanded', 'false');
    if (menu) menu.setAttribute('aria-hidden', 'true');
  }

  function openDropdown(dropdown) {
    document.querySelectorAll('[data-custom-dropdown].' + OPEN_CLASS).forEach(function (item) {
      if (item !== dropdown) closeDropdown(item);
    });
    dropdown.classList.add(OPEN_CLASS);
    const trigger = dropdown.querySelector('[data-dropdown-trigger]');
    const menu = dropdown.querySelector('[data-dropdown-menu]');
    if (trigger) trigger.setAttribute('aria-expanded', 'true');
    if (menu) menu.setAttribute('aria-hidden', 'false');
  }

  function syncLinkedTarget(dropdown, value) {
    const syncSelector = dropdown.dataset.syncTarget;
    if (!syncSelector) return;
    const syncEl = document.querySelector(syncSelector);
    if (syncEl) syncEl.value = value;
  }

  function getDropdownForm(dropdown) {
    const input = dropdown.querySelector('[data-dropdown-input]');
    if (input && input.form) return input.form;
    return dropdown.closest('form');
  }

  function submitDropdownForm(dropdown) {
    const form = getDropdownForm(dropdown);
    if (!form || !window.htmx) return;

    const hxGet = form.getAttribute('hx-get');
    if (!hxGet) return;

    const config = {
      source: form,
      target: form.getAttribute('hx-target'),
      swap: form.getAttribute('hx-swap') || 'innerHTML',
    };

    if (form.getAttribute('hx-push-url') === 'true') {
      config.pushUrl = 'true';
    }

    window.htmx.ajax('GET', hxGet, config);
  }

  function setSelectedOption(dropdown, option) {
    const label = dropdown.querySelector('[data-dropdown-label]');
    const input = dropdown.querySelector('[data-dropdown-input]');
    const options = dropdown.querySelectorAll('[data-dropdown-option]');
    const value = option.dataset.value;
    const textNode = option.querySelector('[data-dropdown-option-label]');
    const text = textNode
      ? textNode.textContent.trim()
      : option.textContent.trim();

    options.forEach(function (item) {
      const selected = item === option;
      item.classList.toggle(SELECTED_CLASS, selected);
      item.setAttribute('aria-selected', selected ? 'true' : 'false');
    });

    if (label) label.textContent = text;
    if (!input || input.value === value) return;

    input.value = value;
    input.dispatchEvent(new Event('change', { bubbles: true }));
    syncLinkedTarget(dropdown, value);
    submitDropdownForm(dropdown);
  }

  function bindDropdown(dropdown) {
    if (dropdown.dataset.customDropdownInit === 'true') return;
    dropdown.dataset.customDropdownInit = 'true';

    const trigger = dropdown.querySelector('[data-dropdown-trigger]');
    const menu = dropdown.querySelector('[data-dropdown-menu]');
    const options = Array.prototype.slice.call(
      dropdown.querySelectorAll('[data-dropdown-option]')
    );
    if (!trigger || !menu || !options.length) return;

    trigger.addEventListener('click', function () {
      if (dropdown.classList.contains(OPEN_CLASS)) {
        closeDropdown(dropdown);
        return;
      }
      openDropdown(dropdown);
    });

    options.forEach(function (option, index) {
      option.addEventListener('click', function () {
        setSelectedOption(dropdown, option);
        closeDropdown(dropdown);
        trigger.focus();
      });

      option.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          options[Math.min(index + 1, options.length - 1)].focus();
        }
        if (event.key === 'ArrowUp') {
          event.preventDefault();
          options[Math.max(index - 1, 0)].focus();
        }
        if (event.key === 'Home') {
          event.preventDefault();
          options[0].focus();
        }
        if (event.key === 'End') {
          event.preventDefault();
          options[options.length - 1].focus();
        }
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          setSelectedOption(dropdown, option);
          closeDropdown(dropdown);
          trigger.focus();
        }
      });
    });

    trigger.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openDropdown(dropdown);
        const selected =
          options.find(function (item) {
            return item.classList.contains(SELECTED_CLASS);
          }) || options[0];
        selected.focus();
      }
      if (event.key === 'Escape') closeDropdown(dropdown);
    });

    menu.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeDropdown(dropdown);
        trigger.focus();
      }
    });
  }

  function handleDocumentClick(event) {
    document.querySelectorAll('[data-custom-dropdown].' + OPEN_CLASS).forEach(function (dropdown) {
      if (!dropdown.contains(event.target)) closeDropdown(dropdown);
    });
  }

  let documentBound = false;

  function bindDocumentListeners() {
    if (documentBound) return;
    document.addEventListener('click', handleDocumentClick);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        document.querySelectorAll('[data-custom-dropdown].' + OPEN_CLASS).forEach(closeDropdown);
      }
    });
    documentBound = true;
  }

  function initCustomDropdown(root) {
    const scope = root instanceof Element ? root : document;
    const dropdowns = scope.querySelectorAll('[data-custom-dropdown]');
    dropdowns.forEach(bindDropdown);
    if (dropdowns.length) bindDocumentListeners();
  }

  window.initCustomDropdown = initCustomDropdown;

  document.addEventListener('DOMContentLoaded', function () {
    initCustomDropdown();
  });

  document.body.addEventListener('htmx:afterSwap', function (event) {
    initCustomDropdown(event.detail && event.detail.target ? event.detail.target : event.target);
  });
})();
