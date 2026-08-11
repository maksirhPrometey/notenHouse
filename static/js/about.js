/* NotenHaus — About page counters (Intersection Observer) */

(function () {
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function formatCount(value) {
    try {
      return new Intl.NumberFormat('uk-UA').format(value);
    } catch (err) {
      return String(value);
    }
  }

  function animateCount(el, target, suffix, duration) {
    var start = null;
    var from = 0;

    function frame(ts) {
      if (start === null) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.round(from + (target - from) * eased);
      el.textContent = formatCount(current) + suffix;
      if (progress < 1) {
        window.requestAnimationFrame(frame);
      } else {
        el.textContent = formatCount(target) + suffix;
      }
    }

    window.requestAnimationFrame(frame);
  }

  function initMilestones() {
    var root = document.querySelector('[data-about-milestones]');
    if (!root) return;

    var items = root.querySelectorAll('[data-milestone][data-count-target]');
    if (!items.length) return;

    function run(item) {
      if (item.classList.contains('is-counted')) return;
      item.classList.add('is-counted');
      var valueEl = item.querySelector('[data-milestone-value]');
      if (!valueEl) return;

      var target = parseInt(item.getAttribute('data-count-target'), 10);
      if (!Number.isFinite(target)) return;

      var suffix = item.getAttribute('data-count-suffix') || '';
      if (reducedMotion.matches) {
        valueEl.textContent = formatCount(target) + suffix;
        return;
      }
      animateCount(valueEl, target, suffix, target >= 100000 ? 1600 : 1100);
    }

    if (!('IntersectionObserver' in window)) {
      items.forEach(run);
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          run(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.35, rootMargin: '0px 0px -8% 0px' }
    );

    items.forEach(function (item) {
      observer.observe(item);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMilestones);
  } else {
    initMilestones();
  }
})();
