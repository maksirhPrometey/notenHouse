/* NotenHaus — musical note micro-interactions for .btn */

(function () {
  var NOTES = ['\u2669', '\u266A', '\u266B', '\u266C', '\uD834\uDD1E'];
  var HOVER_COUNT = 8;
  var BURST_COUNT = 10;
  var TAP_NOTES_MS = 1200;
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var coarsePointer = window.matchMedia('(hover: none), (pointer: coarse)');

  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function pickNote() {
    return NOTES[Math.floor(Math.random() * NOTES.length)];
  }

  function randomizeHover(layer) {
    var particles = layer.querySelectorAll('.btn-notes__particle--hover');
    for (var i = 0; i < particles.length; i += 1) {
      var p = particles[i];
      p.textContent = pickNote();
      p.style.setProperty('--nx', rand(12, 88).toFixed(1) + '%');
      p.style.setProperty('--ny', rand(28, 55).toFixed(1) + '%');
      p.style.setProperty('--drift-x', rand(-15, 15).toFixed(1) + 'px');
      p.style.setProperty('--rot', rand(-20, 20).toFixed(1) + 'deg');
      p.style.setProperty('--scale', rand(0.7, 1.4).toFixed(2));
      p.style.setProperty('--delay', String(i * 100) + 'ms');
      p.style.setProperty('--dur', rand(0.95, 1.35).toFixed(2) + 's');
    }
  }

  function spawnBurst(btn) {
    var i;
    var isTouchViewport = window.matchMedia('(max-width: 1023px)').matches;
    var isGhost = btn.classList.contains('btn--ghost');

    btn.classList.add('is-btn-pressed');
    window.setTimeout(function () {
      btn.classList.remove('is-btn-pressed');
    }, 160);

    /* Touch/tablet: portal on body so HTMX cart swap does not kill the burst */
    if (isTouchViewport) {
      var rect = btn.getBoundingClientRect();
      var portal = document.createElement('div');
      portal.className = 'btn-notes-burst-portal';
      portal.setAttribute('aria-hidden', 'true');
      portal.style.left = (rect.left + rect.width / 2).toFixed(1) + 'px';
      portal.style.top = (rect.top + rect.height / 2).toFixed(1) + 'px';
      document.body.appendChild(portal);

      var remaining = BURST_COUNT;
      function removeParticle(event) {
        var node = event.currentTarget;
        if (node && node.parentNode) node.parentNode.removeChild(node);
        remaining -= 1;
        if (remaining <= 0 && portal.parentNode) {
          portal.parentNode.removeChild(portal);
        }
      }

      for (i = 0; i < BURST_COUNT; i += 1) {
        var angle = (i / BURST_COUNT) * Math.PI * 2 + rand(-0.25, 0.25);
        var dist = rand(180, 260);
        var p = document.createElement('span');
        p.className = 'btn-notes__particle btn-notes__particle--burst';
        p.setAttribute('aria-hidden', 'true');
        p.textContent = pickNote();
        p.style.setProperty('--burst-x', (Math.cos(angle) * dist).toFixed(1) + 'px');
        p.style.setProperty('--burst-y', (Math.sin(angle) * dist).toFixed(1) + 'px');
        p.style.setProperty('--rot', rand(-45, 45).toFixed(1) + 'deg');
        p.style.setProperty('--scale', rand(0.9, 1.35).toFixed(2));
        if (isGhost || i % 3 === 0) {
          p.style.color = 'var(--jwp-color-maroon-accent, #8c0d30)';
        }
        p.addEventListener('animationend', removeParticle);
        portal.appendChild(p);
      }

      window.setTimeout(function () {
        if (portal.parentNode) portal.parentNode.removeChild(portal);
      }, 3500);
      return;
    }

    var layer = btn.querySelector('.btn-notes');
    if (!layer) return;

    btn.classList.add('is-notes-bursting');
    if (btn._notesBurstTimer) {
      window.clearTimeout(btn._notesBurstTimer);
    }
    btn._notesBurstTimer = window.setTimeout(function () {
      btn.classList.remove('is-notes-bursting');
      btn._notesBurstTimer = null;
    }, 340);

    for (i = 0; i < BURST_COUNT; i += 1) {
      var dAngle = (i / BURST_COUNT) * Math.PI * 2 + rand(-0.2, 0.2);
      var dDist = rand(30, 56);
      var particle = document.createElement('span');
      particle.className = 'btn-notes__particle btn-notes__particle--burst';
      particle.setAttribute('aria-hidden', 'true');
      particle.textContent = pickNote();
      particle.style.setProperty('--nx', '50%');
      particle.style.setProperty('--ny', '50%');
      particle.style.setProperty('--burst-x', (Math.cos(dAngle) * dDist).toFixed(1) + 'px');
      particle.style.setProperty('--burst-y', (Math.sin(dAngle) * dDist).toFixed(1) + 'px');
      particle.style.setProperty('--rot', rand(-45, 45).toFixed(1) + 'deg');
      particle.style.setProperty('--scale', rand(0.9, 1.35).toFixed(2));
      if (i % 3 === 0) {
        particle.style.color = 'var(--jwp-color-maroon-accent, #8c0d30)';
      }
      particle.addEventListener('animationend', function onEnd(event) {
        var node = event.currentTarget;
        if (node && node.parentNode) node.parentNode.removeChild(node);
      });
      layer.appendChild(particle);
    }
  }

  function isTouchLike(event) {
    if (event && (event.pointerType === 'touch' || event.pointerType === 'pen')) {
      return true;
    }
    return coarsePointer.matches;
  }

  function activateTapNotes(btn, layer) {
    randomizeHover(layer);
    btn.classList.add('is-notes-active');
    if (btn._notesTapTimer) {
      window.clearTimeout(btn._notesTapTimer);
    }
    btn._notesTapTimer = window.setTimeout(function () {
      btn.classList.remove('is-notes-active');
      btn._notesTapTimer = null;
    }, TAP_NOTES_MS);
  }

  function enhance(btn) {
    if (!btn || btn.getAttribute('data-notes-ready') === '1') return;
    btn.setAttribute('data-notes-ready', '1');

    if (!btn.getAttribute('aria-label') && !btn.getAttribute('aria-labelledby')) {
      var labelText = (btn.textContent || '').replace(/\s+/g, ' ').trim();
      if (labelText) btn.setAttribute('aria-label', labelText);
    }

    var layer = document.createElement('span');
    layer.className = 'btn-notes';
    layer.setAttribute('aria-hidden', 'true');

    var i;
    for (i = 0; i < HOVER_COUNT; i += 1) {
      var p = document.createElement('span');
      p.className = 'btn-notes__particle btn-notes__particle--hover';
      p.textContent = NOTES[i % NOTES.length];
      p.style.setProperty('--nx', (12 + i * (76 / (HOVER_COUNT - 1))).toFixed(1) + '%');
      p.style.setProperty('--ny', '40%');
      p.style.setProperty('--delay', String(i * 100) + 'ms');
      p.style.setProperty('--dur', (1 + (i % 3) * 0.1).toFixed(2) + 's');
      p.style.setProperty('--drift-x', ((i % 2 === 0 ? -1 : 1) * (6 + i)).toFixed(1) + 'px');
      p.style.setProperty('--rot', ((i - 3) * 4).toFixed(1) + 'deg');
      p.style.setProperty('--scale', (0.75 + (i % 4) * 0.15).toFixed(2));
      layer.appendChild(p);
    }

    btn.insertBefore(layer, btn.firstChild);

    btn.addEventListener('pointerenter', function () {
      if (reducedMotion.matches) return;
      randomizeHover(layer);
    });

    btn.addEventListener('pointerdown', function (event) {
      if (reducedMotion.matches) return;
      if (event.button != null && event.button !== 0) return;

      if (isTouchLike(event)) {
        activateTapNotes(btn, layer);
        spawnBurst(btn);
        return;
      }

      /* Desktop mouse: burst on real <button> only (anchors navigate immediately) */
      if (btn.tagName === 'BUTTON') {
        spawnBurst(btn);
      }
    });
  }

  function init(root) {
    if (reducedMotion.matches) return;
    var scope = root && root.querySelectorAll ? root : document;
    var buttons = scope.querySelectorAll('.btn');
    for (var i = 0; i < buttons.length; i += 1) {
      enhance(buttons[i]);
    }
  }

  function onReady() {
    init(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }

  document.body.addEventListener('htmx:afterSettle', function (event) {
    init(event.target);
  });

  if (typeof reducedMotion.addEventListener === 'function') {
    reducedMotion.addEventListener('change', function () {
      if (!reducedMotion.matches) init(document);
    });
  }
})();
