(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function closest(el, sel) {
    return el && el.closest ? el.closest(sel) : null;
  }

  function bumpQtyDisplay(display) {
    if (!display || reducedMotion) return;
    display.classList.remove('is-changing');
    void display.offsetWidth;
    display.classList.add('is-changing');
    window.setTimeout(function () {
      display.classList.remove('is-changing');
    }, 170);
  }

  function submitQtyForm(form, nextQty) {
    var input = form.querySelector('[data-cart-qty-input]');
    var display = form.querySelector('[data-cart-qty-display]');
    if (!input) return;
    input.value = String(nextQty);
    if (display) {
      bumpQtyDisplay(display);
      display.textContent = String(nextQty);
    }
    if (typeof form.requestSubmit === 'function') {
      form.requestSubmit();
    } else {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      if (window.htmx) {
        window.htmx.trigger(form, 'submit');
      } else {
        form.submit();
      }
    }
  }

  function onClick(event) {
    var dec = closest(event.target, '[data-cart-qty-dec]');
    var inc = closest(event.target, '[data-cart-qty-inc]');
    if (dec || inc) {
      event.preventDefault();
      var form = closest(event.target, '[data-cart-qty-form]');
      if (!form) return;
      var input = form.querySelector('[data-cart-qty-input]');
      var current = parseInt((input && input.value) || '1', 10) || 1;
      var next = dec ? Math.max(1, current - 1) : current + 1;
      if (next === current) return;
      submitQtyForm(form, next);
      return;
    }
  }

  function onSubmit(event) {
    var form = closest(event.target, '[data-cart-remove-form]');
    if (!form || reducedMotion) return;
    var item = closest(form, '[data-cart-item]');
    if (!item || item.classList.contains('is-removing')) return;
    item.classList.add('is-removing');
  }

  document.addEventListener('click', onClick);
  document.addEventListener('submit', onSubmit, true);
})();
