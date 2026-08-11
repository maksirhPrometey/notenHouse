/* NotenHaus front-end — header nav + search expand + newsletter stub + width lock */

(function () {
  var body = document.body;
  var header = document.querySelector('[data-site-header]');
  var burger = document.getElementById('header-burger');
  var nav = document.getElementById('header-nav');
  var backdrop = document.getElementById('header-backdrop');
  var closeBtn = document.getElementById('header-nav-close');
  var searchToggle = document.getElementById('header-search-toggle');
  var searchForm = document.getElementById('header-search');
  var searchInput = document.getElementById('header-q');

  function lockHorizontalScroll() {
    if (window.scrollX !== 0) {
      window.scrollTo(0, window.scrollY);
    }
    if (document.documentElement.scrollLeft !== 0) {
      document.documentElement.scrollLeft = 0;
    }
    if (document.body.scrollLeft !== 0) {
      document.body.scrollLeft = 0;
    }
  }

  lockHorizontalScroll();
  window.addEventListener('scroll', lockHorizontalScroll, { passive: true });
  document.body.addEventListener('scroll', lockHorizontalScroll, { passive: true });
  window.addEventListener('resize', lockHorizontalScroll, { passive: true });
  window.addEventListener('orientationchange', lockHorizontalScroll, { passive: true });

  function setSearchOpen(open) {
    if (!header || !searchToggle) return;
    header.classList.toggle('is-search-open', open);
    searchToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open && searchInput) {
      window.setTimeout(function () {
        searchInput.focus();
      }, 10);
    }
  }

  function setNavOpen(open) {
    if (!nav || !burger) return;
    body.classList.toggle('is-nav-open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'Закрити меню' : 'Відкрити меню');
    if (open) {
      setSearchOpen(false);
      nav.removeAttribute('hidden');
      if (backdrop) backdrop.removeAttribute('hidden');
    } else {
      nav.setAttribute('hidden', '');
      if (backdrop) backdrop.setAttribute('hidden', '');
    }
    lockHorizontalScroll();
  }

  window.notenHausCloseMobileNav = function () {
    setNavOpen(false);
  };

  window.notenHausCloseMobileSearch = function () {
    setSearchOpen(false);
  };

  if (burger) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') !== 'true';
      setNavOpen(open);
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      setNavOpen(false);
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', function () {
      setNavOpen(false);
    });
  }

  if (searchToggle) {
    searchToggle.addEventListener('click', function () {
      var open = searchToggle.getAttribute('aria-expanded') !== 'true';
      if (open) setNavOpen(false);
      setSearchOpen(open);
    });
  }

  document.addEventListener('pointerdown', function (event) {
    if (!header || !header.classList.contains('is-search-open')) return;
    var target = event.target;
    if (!target) return;
    if (searchForm && searchForm.contains(target)) return;
    if (searchToggle && searchToggle.contains(target)) return;
    setSearchOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (header && header.classList.contains('is-search-open')) {
      setSearchOpen(false);
      if (searchToggle) searchToggle.focus();
      return;
    }
    setNavOpen(false);
  });

  if (nav) {
    nav.addEventListener('click', function (event) {
      var link = event.target && event.target.closest ? event.target.closest('a') : null;
      if (link) setNavOpen(false);
    });
  }

  window.addEventListener('resize', function () {
    if (window.matchMedia('(min-width: 768px)').matches) {
      setSearchOpen(false);
      setNavOpen(false);
    }
  }, { passive: true });

  var newsletter = document.getElementById('newsletter-form');
  var newsletterMsg = document.getElementById('newsletter-msg');
  if (newsletter) {
    newsletter.addEventListener('submit', function (event) {
      event.preventDefault();
      if (newsletterMsg) newsletterMsg.hidden = false;
    });
  }
})();
