/* NotenHaus — /poshuk/ refine search (clear button, history-friendly) */
(function () {
  'use strict';

  var root = document.querySelector('[data-search-page]');
  if (!root) return;

  var input = root.querySelector('[data-search-input]');
  var clearBtn = root.querySelector('[data-search-clear]');
  if (!input || !clearBtn) return;

  function syncClear() {
    var hasValue = Boolean((input.value || '').trim());
    clearBtn.classList.toggle('is-hidden', !hasValue);
  }

  input.addEventListener('input', syncClear);
  input.addEventListener('search', syncClear);

  clearBtn.addEventListener('click', function () {
    input.value = '';
    syncClear();
    input.focus();
  });

  syncClear();
})();
