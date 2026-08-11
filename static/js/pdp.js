/* NotenHaus — PDP gallery, qty stepper, image lightbox */

(function () {
  function clampQty(input) {
    var min = parseInt(input.min || '1', 10);
    var max = parseInt(input.max || '999', 10);
    var value = parseInt(input.value, 10);
    if (isNaN(value) || value < min) value = min;
    if (!isNaN(max) && value > max) value = max;
    input.value = String(value);
    return value;
  }

  function initQty(root) {
    var groups = root.querySelectorAll('[data-pdp-qty]');
    for (var i = 0; i < groups.length; i += 1) {
      (function (group) {
        var input = group.querySelector('.pdp__qty-input');
        var dec = group.querySelector('[data-pdp-qty-dec]');
        var inc = group.querySelector('[data-pdp-qty-inc]');
        if (!input) return;

        if (dec) {
          dec.addEventListener('click', function () {
            var next = clampQty(input) - 1;
            input.value = String(next);
            clampQty(input);
            input.dispatchEvent(new Event('change', { bubbles: true }));
          });
        }

        if (inc) {
          inc.addEventListener('click', function () {
            var next = clampQty(input) + 1;
            input.value = String(next);
            clampQty(input);
            input.dispatchEvent(new Event('change', { bubbles: true }));
          });
        }

        input.addEventListener('change', function () {
          clampQty(input);
        });
        input.addEventListener('blur', function () {
          clampQty(input);
        });
      })(groups[i]);
    }
  }

  function setActiveThumb(thumbs, active) {
    for (var i = 0; i < thumbs.length; i += 1) {
      var on = thumbs[i] === active;
      thumbs[i].classList.toggle('is-active', on);
      thumbs[i].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
  }

  function initGallery(root) {
    var gallery = root.querySelector('[data-pdp-gallery]');
    if (!gallery) return;

    var mainImg = gallery.querySelector('[data-pdp-main]');
    var zoomBtn = gallery.querySelector('[data-pdp-zoom]');
    var thumbs = gallery.querySelectorAll('[data-pdp-thumb]');
    if (!mainImg || !thumbs.length) return;

    if (!gallery.querySelector('.pdp__thumb.is-active') && thumbs[0]) {
      setActiveThumb(thumbs, thumbs[0]);
    }

    for (var i = 0; i < thumbs.length; i += 1) {
      thumbs[i].addEventListener('click', function (ev) {
        var btn = ev.currentTarget;
        var src = btn.getAttribute('data-src');
        var alt = btn.getAttribute('data-alt') || '';
        if (!src) return;
        mainImg.src = src;
        mainImg.alt = alt;
        if (zoomBtn) {
          zoomBtn.setAttribute('data-src', src);
          zoomBtn.setAttribute('data-alt', alt);
        }
        setActiveThumb(thumbs, btn);
      });
    }
  }

  function initLightbox(root) {
    var dialog = document.querySelector('[data-pdp-lightbox]');
    var img = dialog ? dialog.querySelector('[data-pdp-lightbox-img]') : null;
    var closeBtn = dialog ? dialog.querySelector('[data-pdp-lightbox-close]') : null;
    if (!dialog || !img) return;

    function openLightbox(src, alt) {
      if (!src) return;
      img.src = src;
      img.alt = alt || '';
      if (typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        dialog.setAttribute('open', '');
      }
      if (closeBtn) closeBtn.focus();
    }

    function closeLightbox() {
      if (typeof dialog.close === 'function') {
        dialog.close();
      } else {
        dialog.removeAttribute('open');
      }
      img.removeAttribute('src');
      img.alt = '';
    }

    var zooms = root.querySelectorAll('[data-pdp-zoom]');
    for (var i = 0; i < zooms.length; i += 1) {
      zooms[i].addEventListener('click', function (ev) {
        var btn = ev.currentTarget;
        openLightbox(btn.getAttribute('data-src'), btn.getAttribute('data-alt'));
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', closeLightbox);
    }

    dialog.addEventListener('click', function (ev) {
      if (ev.target === dialog) closeLightbox();
    });

    dialog.addEventListener('cancel', function (ev) {
      ev.preventDefault();
      closeLightbox();
    });
  }

  function init() {
    var root = document.querySelector('[data-pdp]');
    if (!root) return;
    initQty(root);
    initGallery(root);
    initLightbox(root);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
