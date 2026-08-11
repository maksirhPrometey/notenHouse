/* NotenHaus — Contacts form validation adapter */

(function (global) {
  var V = global.NotenHausFormValidation;
  if (!V) return;

  var ui = V.createUi({ wrapSelector: '.contacts-float' });

  function validateFormFields(form) {
    var name = form.querySelector('[name="name"]');
    var phone = form.querySelector('[name="phone"]');
    var email = form.querySelector('[name="email"]');
    var errors = {};
    var nameErr = V.validateName(name ? name.value : '', false);
    var phoneErr = V.validatePhone(phone ? phone.value : '', true);
    var emailErr = V.validateEmail(email ? email.value : '', false);
    if (nameErr) errors.name = [nameErr];
    if (phoneErr) errors.phone = [phoneErr];
    if (emailErr) errors.email = [emailErr];
    return errors;
  }

  function bindFields(form) {
    if (!form) return;
    V.bindNameField(form, form.querySelector('[name="name"]'), ui, {
      required: false,
      fieldName: 'name',
    });
    V.bindPhoneField(form, form.querySelector('[name="phone"]'), ui, {
      required: true,
      fieldName: 'phone',
    });
    V.bindEmailField(form, form.querySelector('[name="email"]'), ui, {
      required: false,
      fieldName: 'email',
    });
  }

  global.NotenHausContactsForm = {
    bindFields: bindFields,
    clearErrors: ui.clearErrors,
    showErrors: ui.showErrors,
    validateFormFields: validateFormFields,
    firstErrorField: function (form, errors) {
      return V.firstErrorField(form, errors, ['name', 'phone', 'email']);
    },
    normalizeUaPhone: V.normalizeUaPhone,
  };
})(window);
