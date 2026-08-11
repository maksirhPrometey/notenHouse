/* NotenHaus — shared form validation (name / UA phone / email / password) */

(function (global) {
  var MSG = {
    required: 'Це поле обовʼязкове',
    name: 'Імʼя може містити лише літери, дефіс і апостроф',
    phoneInvalid: 'Введіть коректний український номер (+380…)',
    emailInvalid: 'Введіть коректний email',
    passwordShort: 'Пароль має містити щонайменше 8 символів',
    passwordMismatch: 'Паролі не збігаються',
  };

  var NAME_STRIP = /[^A-Za-zА-Яа-яІіЇїЄєҐґ'ʼʻ`\-]/g;
  var NAME_HAS_BAD = /[^A-Za-zА-Яа-яІіЇїЄєҐґ'ʼʻ`\-]/;
  var NAME_VALID = /^[A-Za-zА-Яа-яІіЇїЄєҐґ'ʼʻ`\-]*$/;
  var EMAIL_STRIP = /\s+/g;
  var EMAIL_HAS_SPACE = /\s/;
  var EMAIL_VALID =
    /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;

  function createUi(options) {
    var wrapSelector = (options && options.wrapSelector) || '.form-field';

    function clearErrors(form) {
      form.querySelectorAll('.invalid-feedback').forEach(function (el) {
        el.textContent = '';
      });
      form.querySelectorAll(wrapSelector).forEach(function (el) {
        el.classList.remove('is-invalid');
      });
      form.querySelectorAll('.is-invalid').forEach(function (el) {
        el.classList.remove('is-invalid');
      });
    }

    function clearFieldError(form, name) {
      var el = form.querySelector('[data-field="' + name + '"]');
      if (el) el.textContent = '';
      var field = form.querySelector('[name="' + name + '"]');
      if (field) {
        field.classList.remove('is-invalid');
        var wrap = field.closest(wrapSelector);
        if (wrap) wrap.classList.remove('is-invalid');
      }
    }

    function showFieldError(form, name, message) {
      var el = form.querySelector('[data-field="' + name + '"]');
      if (el) el.textContent = message || '';
      var field = form.querySelector('[name="' + name + '"]');
      if (field) {
        field.classList.add('is-invalid');
        var wrap = field.closest(wrapSelector);
        if (wrap) wrap.classList.add('is-invalid');
      }
    }

    function showErrors(form, errors) {
      Object.keys(errors || {}).forEach(function (name) {
        var msg = errors[name] && errors[name][0];
        if (msg) showFieldError(form, name, msg);
      });
    }

    return {
      clearErrors: clearErrors,
      clearFieldError: clearFieldError,
      showFieldError: showFieldError,
      showErrors: showErrors,
    };
  }

  function setFieldValueKeepCaret(input, next, preferEnd) {
    var prev = input.value;
    if (prev === next) return;
    var start = input.selectionStart;
    var end = input.selectionEnd;
    input.value = next;
    if (preferEnd || start == null || end == null) {
      try {
        var len = next.length;
        input.setSelectionRange(len, len);
      } catch (err) {}
      return;
    }
    var delta = next.length - prev.length;
    var nextStart = Math.max(0, Math.min(next.length, start + delta));
    var nextEnd = Math.max(0, Math.min(next.length, end + delta));
    try {
      input.setSelectionRange(nextStart, nextEnd);
    } catch (err) {}
  }

  function uaPhoneDigits(value) {
    var digits = String(value || '').replace(/\D/g, '');
    if (digits.indexOf('380') === 0) digits = digits.slice(3);
    if (digits.charAt(0) === '0') digits = digits.slice(1);
    return digits.slice(0, 9);
  }

  function formatUaPhone(digits) {
    var d = String(digits || '');
    var out = '+380';
    if (!d.length) return out;
    out += ' (' + d.slice(0, Math.min(2, d.length));
    if (d.length < 2) return out;
    out += ')';
    if (d.length > 2) out += ' ' + d.slice(2, Math.min(5, d.length));
    if (d.length > 5) out += '-' + d.slice(5, Math.min(7, d.length));
    if (d.length > 7) out += '-' + d.slice(7, 9);
    return out;
  }

  function normalizeUaPhone(value) {
    var digits = uaPhoneDigits(value);
    return digits.length === 9 ? '+380' + digits : '';
  }

  function sanitizeName(value) {
    return String(value || '').replace(NAME_STRIP, '');
  }

  function sanitizeEmail(value) {
    return String(value || '').replace(EMAIL_STRIP, '');
  }

  function validateName(value, required) {
    var v = String(value || '');
    if (!v) return required ? MSG.required : '';
    if (!NAME_VALID.test(v) || /\d|\s/.test(v)) return MSG.name;
    return '';
  }

  function validatePhone(value, required) {
    var digits = uaPhoneDigits(value);
    if (!digits.length) return required ? MSG.required : '';
    if (digits.length < 9) return MSG.phoneInvalid;
    return '';
  }

  function validateEmail(value, required) {
    var v = String(value || '').trim();
    if (!v) return required ? MSG.required : '';
    if (EMAIL_HAS_SPACE.test(v) || !EMAIL_VALID.test(v)) return MSG.emailInvalid;
    return '';
  }

  function validatePassword(value, required) {
    var v = String(value || '');
    if (!v) return required ? MSG.required : '';
    if (v.length < 8) return MSG.passwordShort;
    return '';
  }

  function validatePasswordMatch(password, confirm) {
    var p2 = String(confirm || '');
    if (!p2) return '';
    if (String(password || '') !== p2) return MSG.passwordMismatch;
    return '';
  }

  function firstErrorField(form, errors, order) {
    var list = order || Object.keys(errors || {});
    for (var i = 0; i < list.length; i += 1) {
      if (errors[list[i]]) {
        return form.querySelector('[name="' + list[i] + '"]');
      }
    }
    return null;
  }

  function bindNameField(form, input, ui, options) {
    if (!input || !ui) return;
    var required = !!(options && options.required);
    var fieldName = (options && options.fieldName) || input.getAttribute('name') || 'name';

    function apply() {
      var cleaned = sanitizeName(input.value);
      var blocked = cleaned !== input.value;
      setFieldValueKeepCaret(input, cleaned, false);
      var err = validateName(input.value, false);
      if (err || blocked) ui.showFieldError(form, fieldName, err || MSG.name);
      else ui.clearFieldError(form, fieldName);
    }

    input.setAttribute('autocomplete', 'name');
    input.setAttribute('spellcheck', 'false');
    input.addEventListener('beforeinput', function (e) {
      if (e.isComposing) return;
      if (e.inputType && e.inputType.indexOf('delete') === 0) return;
      var data = e.data;
      if (data == null) return;
      if (NAME_HAS_BAD.test(data)) {
        e.preventDefault();
        ui.showFieldError(form, fieldName, MSG.name);
      }
    });
    input.addEventListener('input', apply);
    input.addEventListener('blur', function () {
      var err = validateName(input.value, required);
      if (err) ui.showFieldError(form, fieldName, err);
      else ui.clearFieldError(form, fieldName);
    });
  }

  function bindPhoneField(form, input, ui, options) {
    if (!input || !ui) return;
    var required = !!(options && options.required);
    var fieldName = (options && options.fieldName) || 'phone';
    var PREFIX = '+380';
    var PREFIX_LEN = PREFIX.length;

    function ensurePrefix() {
      input.value = formatUaPhone(uaPhoneDigits(input.value));
    }

    function protectCaret() {
      var start = input.selectionStart;
      var end = input.selectionEnd;
      if (start == null || end == null) return;
      if (start < PREFIX_LEN || end < PREFIX_LEN) {
        try {
          input.setSelectionRange(
            Math.max(PREFIX_LEN, start),
            Math.max(PREFIX_LEN, end)
          );
        } catch (err) {}
      }
    }

    function apply(preferEnd) {
      var next = formatUaPhone(uaPhoneDigits(input.value));
      setFieldValueKeepCaret(input, next, preferEnd);
      protectCaret();
      var err = validatePhone(input.value, false);
      if (err) ui.showFieldError(form, fieldName, err);
      else ui.clearFieldError(form, fieldName);
    }

    input.setAttribute('inputmode', 'tel');
    input.setAttribute('autocomplete', 'tel');
    input.setAttribute('maxlength', '19');

    input.addEventListener('focus', function () {
      ensurePrefix();
      protectCaret();
    });
    input.addEventListener('click', protectCaret);
    input.addEventListener('keyup', protectCaret);
    input.addEventListener('select', protectCaret);

    input.addEventListener('beforeinput', function (e) {
      if (e.isComposing) return;
      var start = input.selectionStart;
      var end = input.selectionEnd;
      if (e.inputType && e.inputType.indexOf('delete') === 0) {
        if (start == null || end == null) return;
        if (start < PREFIX_LEN || (start === end && start <= PREFIX_LEN) || end <= PREFIX_LEN) {
          e.preventDefault();
          ensurePrefix();
          protectCaret();
        }
        return;
      }
      var data = e.data;
      if (data == null) return;
      if (start != null && start < PREFIX_LEN) {
        e.preventDefault();
        protectCaret();
        return;
      }
      if (/\D/.test(data) && data.indexOf('+') === -1) {
        e.preventDefault();
        ui.showFieldError(form, fieldName, MSG.phoneInvalid);
      }
    });

    input.addEventListener('input', function () {
      apply(true);
    });

    input.addEventListener('blur', function () {
      var digits = uaPhoneDigits(input.value);
      if (!digits.length) {
        input.value = '';
        if (required) ui.showFieldError(form, fieldName, MSG.required);
        else ui.clearFieldError(form, fieldName);
        return;
      }
      input.value = formatUaPhone(digits);
      var err = validatePhone(input.value, required);
      if (err) ui.showFieldError(form, fieldName, err);
      else ui.clearFieldError(form, fieldName);
    });

    input.addEventListener('keydown', function (e) {
      var start = input.selectionStart;
      var end = input.selectionEnd;
      if (e.key === 'ArrowLeft' || e.key === 'Home') {
        if (start != null && start <= PREFIX_LEN) {
          e.preventDefault();
          try {
            input.setSelectionRange(PREFIX_LEN, PREFIX_LEN);
          } catch (err) {}
        }
        return;
      }
      if (e.key !== 'Backspace' && e.key !== 'Delete') return;
      if (start == null || end == null) return;
      if (start !== end) {
        if (start < PREFIX_LEN) {
          e.preventDefault();
          var digits = uaPhoneDigits(
            (input.value || '').slice(0, PREFIX_LEN) +
              (input.value || '').slice(Math.max(end, PREFIX_LEN))
          );
          input.value = formatUaPhone(digits);
          protectCaret();
        }
        return;
      }
      if (e.key === 'Backspace' && start <= PREFIX_LEN) {
        e.preventDefault();
        ensurePrefix();
        protectCaret();
        return;
      }
      if (e.key === 'Delete' && start < PREFIX_LEN) {
        e.preventDefault();
        ensurePrefix();
        protectCaret();
      }
    });
  }

  function bindEmailField(form, input, ui, options) {
    if (!input || !ui) return;
    var required = !!(options && options.required);
    var fieldName = (options && options.fieldName) || 'email';

    function apply() {
      var cleaned = sanitizeEmail(input.value);
      var blocked = cleaned !== input.value;
      setFieldValueKeepCaret(input, cleaned, false);
      var err = validateEmail(input.value, false);
      if (err || blocked) ui.showFieldError(form, fieldName, err || MSG.emailInvalid);
      else ui.clearFieldError(form, fieldName);
    }

    input.setAttribute('inputmode', 'email');
    input.setAttribute('autocomplete', 'email');
    input.setAttribute('spellcheck', 'false');

    input.addEventListener('beforeinput', function (e) {
      if (e.isComposing) return;
      if (e.inputType && e.inputType.indexOf('delete') === 0) return;
      var data = e.data;
      if (data == null) return;
      if (EMAIL_HAS_SPACE.test(data)) {
        e.preventDefault();
        ui.showFieldError(form, fieldName, MSG.emailInvalid);
      }
    });
    input.addEventListener('input', apply);
    input.addEventListener('blur', function () {
      var err = validateEmail(input.value, required);
      if (err) ui.showFieldError(form, fieldName, err);
      else ui.clearFieldError(form, fieldName);
    });
  }

  function bindPasswordFields(form, passwordInput, confirmInput, ui) {
    if (!ui) return;

    function sync() {
      var p1 = passwordInput ? passwordInput.value : '';
      var p2 = confirmInput ? confirmInput.value : '';
      var err1 = validatePassword(p1, false);
      if (passwordInput) {
        if (err1) ui.showFieldError(form, 'password1', err1);
        else ui.clearFieldError(form, 'password1');
      }
      if (confirmInput) {
        var err2 = p2 ? validatePasswordMatch(p1, p2) : '';
        if (!p2 && confirmInput === document.activeElement) {
          ui.clearFieldError(form, 'password2');
        } else if (err2) {
          ui.showFieldError(form, 'password2', err2);
        } else if (p2) {
          ui.clearFieldError(form, 'password2');
        } else {
          ui.clearFieldError(form, 'password2');
        }
      }
    }

    if (passwordInput) {
      passwordInput.setAttribute('autocomplete', 'new-password');
      passwordInput.addEventListener('input', sync);
      passwordInput.addEventListener('blur', function () {
        var err = validatePassword(passwordInput.value, true);
        if (err) ui.showFieldError(form, 'password1', err);
        else ui.clearFieldError(form, 'password1');
        if (confirmInput && confirmInput.value) {
          var matchErr = validatePasswordMatch(passwordInput.value, confirmInput.value);
          if (matchErr) ui.showFieldError(form, 'password2', matchErr);
          else ui.clearFieldError(form, 'password2');
        }
      });
    }

    if (confirmInput) {
      confirmInput.setAttribute('autocomplete', 'new-password');
      confirmInput.addEventListener('input', sync);
      confirmInput.addEventListener('blur', function () {
        if (!confirmInput.value) {
          ui.showFieldError(form, 'password2', MSG.required);
          return;
        }
        var err = validatePasswordMatch(
          passwordInput ? passwordInput.value : '',
          confirmInput.value
        );
        if (err) ui.showFieldError(form, 'password2', err);
        else ui.clearFieldError(form, 'password2');
      });
    }
  }

  global.NotenHausFormValidation = {
    MSG: MSG,
    createUi: createUi,
    setFieldValueKeepCaret: setFieldValueKeepCaret,
    uaPhoneDigits: uaPhoneDigits,
    formatUaPhone: formatUaPhone,
    normalizeUaPhone: normalizeUaPhone,
    sanitizeName: sanitizeName,
    sanitizeEmail: sanitizeEmail,
    validateName: validateName,
    validatePhone: validatePhone,
    validateEmail: validateEmail,
    validatePassword: validatePassword,
    validatePasswordMatch: validatePasswordMatch,
    firstErrorField: firstErrorField,
    bindNameField: bindNameField,
    bindPhoneField: bindPhoneField,
    bindEmailField: bindEmailField,
    bindPasswordFields: bindPasswordFields,
  };
})(window);
