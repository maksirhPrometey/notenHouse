/* NotenHaus — Registration form client validation */

(function () {
  var V = window.NotenHausFormValidation;
  if (!V) return;

  var ui = V.createUi({ wrapSelector: '.form-field' });
  var FIELD_ORDER = ['display_name', 'email', 'phone', 'password1', 'password2'];

  function validateFormFields(form) {
    var name = form.querySelector('[name="display_name"]');
    var email = form.querySelector('[name="email"]');
    var phone = form.querySelector('[name="phone"]');
    var password1 = form.querySelector('[name="password1"]');
    var password2 = form.querySelector('[name="password2"]');
    var errors = {};

    var nameErr = V.validateName(name ? name.value : '', true);
    var emailErr = V.validateEmail(email ? email.value : '', true);
    var phoneErr = V.validatePhone(phone ? phone.value : '', false);
    var passErr = V.validatePassword(password1 ? password1.value : '', true);
    var confirmVal = password2 ? password2.value : '';
    var confirmErr = confirmVal
      ? V.validatePasswordMatch(password1 ? password1.value : '', confirmVal)
      : V.MSG.required;

    if (nameErr) errors.display_name = [nameErr];
    if (emailErr) errors.email = [emailErr];
    if (phoneErr) errors.phone = [phoneErr];
    if (passErr) errors.password1 = [passErr];
    if (confirmErr) errors.password2 = [confirmErr];
    return errors;
  }

  function init() {
    var form = document.querySelector('[data-register-form]');
    if (!form) return;

    var nameInput = form.querySelector('[name="display_name"]');
    var emailInput = form.querySelector('[name="email"]');
    var phoneInput = form.querySelector('[name="phone"]');
    var password1 = form.querySelector('[name="password1"]');
    var password2 = form.querySelector('[name="password2"]');

    V.bindNameField(form, nameInput, ui, {
      required: true,
      fieldName: 'display_name',
    });
    V.bindEmailField(form, emailInput, ui, {
      required: true,
      fieldName: 'email',
    });
    V.bindPhoneField(form, phoneInput, ui, {
      required: false,
      fieldName: 'phone',
    });
    V.bindPasswordFields(form, password1, password2, ui);

    form.addEventListener('submit', function (e) {
      ui.clearErrors(form);
      var errors = validateFormFields(form);
      if (Object.keys(errors).length) {
        e.preventDefault();
        ui.showErrors(form, errors);
        var focusEl = V.firstErrorField(form, errors, FIELD_ORDER);
        if (focusEl) focusEl.focus();
        return;
      }

      if (phoneInput) {
        var digits = V.uaPhoneDigits(phoneInput.value);
        if (!digits.length) {
          phoneInput.value = '';
        } else {
          var normalized = V.normalizeUaPhone(phoneInput.value);
          if (normalized) phoneInput.value = normalized;
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
