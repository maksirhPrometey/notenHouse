(() => {
  const resetBox = document.querySelector('[data-theme-reset]');
  const clearBox = document.querySelector('[data-theme-clear]');

  function applyColors(map) {
    Object.entries(map).forEach(([name, value]) => {
      const input = document.getElementById(`id_${name}`);
      if (!input) return;
      input.value = value;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  }

  function parseDefaults(el, attr) {
    if (!el) return null;
    try {
      return JSON.parse(el.getAttribute(attr) || '{}');
    } catch {
      return null;
    }
  }

  const originalDefaults = parseDefaults(resetBox, 'data-theme-defaults');
  const cssDefaults = parseDefaults(clearBox, 'data-theme-css-defaults');

  if (resetBox && originalDefaults) {
    resetBox.addEventListener('change', () => {
      if (!resetBox.checked) return;
      if (clearBox) clearBox.checked = false;
      applyColors(originalDefaults);
    });
  }

  if (clearBox && cssDefaults) {
    clearBox.addEventListener('change', () => {
      if (!clearBox.checked) return;
      if (resetBox) resetBox.checked = false;
      applyColors(cssDefaults);
    });
  }
})();
