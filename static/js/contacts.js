/* NotenHaus — Contacts page: schedule, form AJAX, note micro-interactions */

(function () {
  var NOTES = ['\u2669', '\u266A', '\u266B', '\u266C', '\u266F'];
  var HOVER_COUNT = 10;
  var BURST_COUNT = 12;
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function pickNote() {
    return NOTES[Math.floor(Math.random() * NOTES.length)];
  }

  function parseTime(value) {
    var parts = String(value || '').split(':');
    var h = parseInt(parts[0], 10);
    var m = parseInt(parts[1] || '0', 10);
    if (isNaN(h) || isNaN(m)) return null;
    return h * 60 + m;
  }

  function getZonedParts(timeZone) {
    try {
      var fmt = new Intl.DateTimeFormat('en-GB', {
        timeZone: timeZone || 'Europe/Kyiv',
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      });
      var parts = fmt.formatToParts(new Date());
      var map = {};
      for (var i = 0; i < parts.length; i += 1) {
        map[parts[i].type] = parts[i].value;
      }
      var weekdayMap = {
        Mon: 1,
        Tue: 2,
        Wed: 3,
        Thu: 4,
        Fri: 5,
        Sat: 6,
        Sun: 7,
      };
      return {
        day: weekdayMap[map.weekday] || 0,
        minutes: parseTime((map.hour || '0') + ':' + (map.minute || '0')),
      };
    } catch (err) {
      var now = new Date();
      var jsDay = now.getDay();
      return {
        day: jsDay === 0 ? 7 : jsDay,
        minutes: now.getHours() * 60 + now.getMinutes(),
      };
    }
  }

  function isOpenNow(schedule) {
    if (!schedule || typeof schedule !== 'object') return false;
    var days = Array.isArray(schedule.days) ? schedule.days : [1, 2, 3, 4, 5];
    var open = parseTime(schedule.open || '10:00');
    var close = parseTime(schedule.close || '18:00');
    if (open == null || close == null) return false;
    var zoned = getZonedParts(schedule.timezone);
    if (days.indexOf(zoned.day) === -1) return false;
    return zoned.minutes >= open && zoned.minutes < close;
  }

  function updateOpenStatus() {
    var el = document.querySelector('[data-open-status]');
    var script = document.getElementById('contacts-schedule-data');
    if (!el || !script) return;
    var schedule = {};
    try {
      schedule = JSON.parse(script.textContent || '{}');
    } catch (err) {
      schedule = {};
    }
    var open = isOpenNow(schedule);
    el.textContent = open ? 'Зараз відчинено' : 'Зачинено';
    el.classList.toggle('is-open', open);
    el.classList.toggle('is-closed', !open);
  }

  function randomizeHover(layer) {
    var particles = layer.querySelectorAll('.contacts-submit__particle--hover');
    for (var i = 0; i < particles.length; i += 1) {
      var p = particles[i];
      p.textContent = pickNote();
      p.style.setProperty('--nx', rand(10, 90).toFixed(1) + '%');
      p.style.setProperty('--ny', rand(30, 58).toFixed(1) + '%');
      p.style.setProperty('--drift-x', rand(-16, 16).toFixed(1) + 'px');
      p.style.setProperty('--rot', rand(-22, 22).toFixed(1) + 'deg');
      p.style.setProperty('--scale', rand(0.7, 1.35).toFixed(2));
      p.style.setProperty('--delay', String(i * 90) + 'ms');
      p.style.setProperty('--dur', rand(0.9, 1.3).toFixed(2) + 's');
    }
  }

  function spawnBurst(btn) {
    var layer = btn.querySelector('[data-submit-notes]');
    if (!layer) return;
    for (var i = 0; i < BURST_COUNT; i += 1) {
      var angle = (i / BURST_COUNT) * Math.PI * 2 + rand(-0.2, 0.2);
      var dist = rand(28, 58);
      var p = document.createElement('span');
      p.className = 'contacts-submit__particle contacts-submit__particle--burst';
      p.setAttribute('aria-hidden', 'true');
      p.textContent = pickNote();
      p.style.setProperty('--nx', '50%');
      p.style.setProperty('--ny', '50%');
      p.style.setProperty('--burst-x', (Math.cos(angle) * dist).toFixed(1) + 'px');
      p.style.setProperty('--burst-y', (Math.sin(angle) * dist).toFixed(1) + 'px');
      p.style.setProperty('--rot', rand(-45, 45).toFixed(1) + 'deg');
      p.style.setProperty('--scale', rand(0.85, 1.35).toFixed(2));
      if (i % 3 === 0) {
        p.style.color = 'var(--jwp-color-maroon-accent, #8c0d30)';
      }
      p.addEventListener('animationend', function (event) {
        var node = event.currentTarget;
        if (node && node.parentNode) node.parentNode.removeChild(node);
      });
      layer.appendChild(p);
    }
  }

  function enhanceSubmit(btn) {
    if (!btn || btn.getAttribute('data-notes-ready') === '1') return;
    btn.setAttribute('data-notes-ready', '1');
    var layer = btn.querySelector('[data-submit-notes]');
    if (!layer) return;
    if (reducedMotion.matches) return;

    for (var i = 0; i < HOVER_COUNT; i += 1) {
      var p = document.createElement('span');
      p.className = 'contacts-submit__particle contacts-submit__particle--hover';
      p.setAttribute('aria-hidden', 'true');
      p.textContent = NOTES[i % NOTES.length];
      p.style.setProperty('--nx', (10 + i * (80 / (HOVER_COUNT - 1))).toFixed(1) + '%');
      p.style.setProperty('--ny', '42%');
      p.style.setProperty('--delay', String(i * 90) + 'ms');
      p.style.setProperty('--dur', (1 + (i % 3) * 0.1).toFixed(2) + 's');
      p.style.setProperty('--drift-x', ((i % 2 === 0 ? -1 : 1) * (5 + i)).toFixed(1) + 'px');
      p.style.setProperty('--rot', ((i - 4) * 4).toFixed(1) + 'deg');
      p.style.setProperty('--scale', (0.75 + (i % 4) * 0.12).toFixed(2));
      layer.appendChild(p);
    }

    btn.addEventListener('pointerenter', function () {
      if (reducedMotion.matches || btn.classList.contains('is-success')) return;
      randomizeHover(layer);
    });

    btn.addEventListener('pointerdown', function (event) {
      if (reducedMotion.matches || btn.classList.contains('is-success')) return;
      if (event.button != null && event.button !== 0) return;
      spawnBurst(btn);
    });
  }

  function setSuccessState(btn, successEl, message) {
    if (btn) {
      btn.classList.add('is-success');
      btn.disabled = true;
      var label = btn.querySelector('[data-submit-label]');
      if (label) label.textContent = (message || 'Повідомлення надіслано!') + ' ✓';
    }
    if (successEl) {
      successEl.hidden = false;
      successEl.textContent = (message || 'Повідомлення надіслано!') + ' ✓';
    }
  }

  function initForm() {
    var form = document.querySelector('[data-contacts-form]');
    if (!form) return;
    var success = document.getElementById('contact-success');
    var submitBtn = form.querySelector('[data-contacts-submit]');
    var phoneInput = form.querySelector('[name="phone"]');
    var validation = window.NotenHausContactsForm;

    enhanceSubmit(submitBtn);
    if (validation) validation.bindFields(form);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (submitBtn && submitBtn.classList.contains('is-success')) return;

      if (validation) validation.clearErrors(form);
      var errors = validation ? validation.validateFormFields(form) : {};
      if (Object.keys(errors).length) {
        validation.showErrors(form, errors);
        var focusEl = validation.firstErrorField(form, errors);
        if (focusEl) focusEl.focus();
        return;
      }

      if (submitBtn) submitBtn.disabled = true;
      var fd = new FormData(form);
      if (validation && phoneInput) {
        var normalized = validation.normalizeUaPhone(phoneInput.value);
        if (normalized) fd.set('phone', normalized);
      }

      fetch(form.action, {
        method: 'POST',
        body: fd,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(function (r) {
          return r.json().then(function (data) {
            return { ok: r.ok, data: data };
          });
        })
        .then(function (res) {
          if (!res.ok) {
            if (submitBtn) submitBtn.disabled = false;
            if (validation) {
              validation.showErrors(form, (res.data && res.data.errors) || {});
            }
            return;
          }
          form.reset();
          var firstTopic = form.querySelector('input[name="topic"]');
          if (firstTopic) firstTopic.checked = true;
          setSuccessState(
            submitBtn,
            success,
            (res.data && res.data.message) || 'Повідомлення надіслано!'
          );
        })
        .catch(function () {
          if (submitBtn) submitBtn.disabled = false;
          if (success) {
            success.hidden = false;
            success.textContent = 'Помилка відправки. Спробуйте пізніше.';
            success.style.color = 'var(--jwp-color-error-red)';
          }
        });
    });
  }

  function onReady() {
    updateOpenStatus();
    initForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
