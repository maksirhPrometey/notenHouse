/* NotenHaus — checkout: NP, validation, step checks, submit loading */

(function () {
  var form = document.getElementById('checkout-form');
  if (!form) return;

  var citiesUrl = form.getAttribute('data-np-cities-url');
  var warehousesUrl = form.getAttribute('data-np-warehouses-url');
  var methodInputs = form.querySelectorAll('[data-shipping-method]');
  var paymentInputs = form.querySelectorAll('[data-payment-method]');
  var npBlock = form.querySelector('[data-np-block]');
  var pickupBlock = form.querySelector('[data-pickup-block]');
  var citySearch = form.querySelector('[data-np-city-search]');
  var cityResults = form.querySelector('[data-np-city-results]');
  var warehouseSearch = form.querySelector('[data-np-warehouse-search]');
  var warehouseResults = form.querySelector('[data-np-warehouse-results]');
  var cityRef = form.querySelector('[name="np_city_ref"]');
  var cityName = form.querySelector('[name="np_city_name"]');
  var warehouseRef = form.querySelector('[name="np_warehouse_ref"]');
  var warehouseName = form.querySelector('[name="np_warehouse_name"]');
  var areaRef = form.querySelector('[name="np_area_ref"]');
  var npError = form.querySelector('[data-np-error]');
  var submitBtns = document.querySelectorAll('[data-checkout-submit]');
  var cityTimer = null;
  var whTimer = null;
  var locale = (document.documentElement.lang || 'uk').slice(0, 2);
  var msg = {
    required: locale === 'en' ? 'This field is required' : 'Обовʼязкове поле',
    email: locale === 'en' ? 'Enter a valid email' : 'Введіть коректний email',
    phone: locale === 'en' ? 'Enter a valid phone number' : 'Введіть коректний номер телефону',
    np: locale === 'en'
      ? 'Select a Nova Poshta city and branch'
      : 'Оберіть місто та відділення Нової Пошти',
    processing: locale === 'en' ? 'Processing…' : 'Оформлюємо…',
  };

  function selectedMethod() {
    var checked = form.querySelector('[data-shipping-method]:checked');
    return checked ? checked.value : '';
  }

  function syncMethodCards(inputs) {
    (inputs || methodInputs).forEach(function (input) {
      var card = input.closest('.checkout-method');
      if (!card) return;
      card.classList.toggle('is-selected', input.checked);
      input.setAttribute('aria-checked', input.checked ? 'true' : 'false');
    });
  }

  function isPickup() {
    return selectedMethod() === 'pickup';
  }

  function toggleNp() {
    syncMethodCards(methodInputs);
    var pickup = isPickup();
    if (npBlock) {
      npBlock.hidden = pickup;
    }
    if (pickupBlock) {
      pickupBlock.hidden = !pickup;
    }
    if (pickup && npError) {
      npError.hidden = true;
      npError.textContent = '';
    }
  }

  function syncPaymentCards() {
    syncMethodCards(paymentInputs);
  }

  function hideList(ul) {
    if (!ul) return;
    ul.innerHTML = '';
    ul.hidden = true;
  }

  function renderList(ul, items, onPick) {
    if (!ul) return;
    ul.innerHTML = '';
    if (!items.length) {
      ul.hidden = true;
      return;
    }
    items.forEach(function (item) {
      var li = document.createElement('li');
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = item.name;
      btn.addEventListener('click', function () {
        onPick(item);
        hideList(ul);
      });
      li.appendChild(btn);
      ul.appendChild(li);
    });
    ul.hidden = false;
  }

  function setFieldError(fieldEl, message) {
    if (!fieldEl) return;
    var wrap = fieldEl.closest('.form-field');
    if (!wrap) return;
    var err = wrap.querySelector('[data-field-error]');
    if (!err) {
      err = document.createElement('div');
      err.className = 'invalid-feedback';
      err.setAttribute('data-field-error', '');
      wrap.appendChild(err);
    }
    if (message) {
      wrap.classList.add('is-invalid');
      err.hidden = false;
      err.textContent = message;
    } else {
      wrap.classList.remove('is-invalid');
      err.hidden = true;
      err.textContent = '';
    }
  }

  function validateEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function validatePhone(value) {
    return /^\+?[0-9\s\-]{10,20}$/.test(value);
  }

  function validateContact() {
    var name = form.querySelector('[name="customer_name"]');
    var email = form.querySelector('[name="customer_email"]');
    var phone = form.querySelector('[name="customer_phone"]');
    var ok = true;

    if (!name || !name.value.trim()) {
      setFieldError(name, msg.required);
      ok = false;
    } else {
      setFieldError(name, '');
    }

    if (!email || !email.value.trim()) {
      setFieldError(email, msg.required);
      ok = false;
    } else if (!validateEmail(email.value.trim())) {
      setFieldError(email, msg.email);
      ok = false;
    } else {
      setFieldError(email, '');
    }

    if (!phone || !phone.value.trim()) {
      setFieldError(phone, msg.required);
      ok = false;
    } else if (!validatePhone(phone.value.trim())) {
      setFieldError(phone, msg.phone);
      ok = false;
    } else {
      setFieldError(phone, '');
    }

    return ok;
  }

  function validateShipping() {
    if (!selectedMethod()) return false;
    if (isPickup()) {
      if (npError) {
        npError.hidden = true;
        npError.textContent = '';
      }
      return true;
    }
    if (!cityRef || !cityRef.value || !warehouseRef || !warehouseRef.value) {
      if (npError) {
        npError.hidden = false;
        npError.textContent = msg.np;
      }
      return false;
    }
    if (npError) {
      npError.hidden = true;
      npError.textContent = '';
    }
    return true;
  }

  function setStepComplete(stepName, complete) {
    var step = form.querySelector('[data-checkout-step="' + stepName + '"]');
    if (!step) return;
    var check = step.querySelector('[data-step-check]');
    step.classList.toggle('is-complete', complete);
    if (check) {
      if (complete) check.removeAttribute('hidden');
      else check.setAttribute('hidden', '');
    }
  }

  function refreshSteps() {
    var contactOk = validateContactSoft();
    var shippingOk = validateShippingSoft();
    setStepComplete('contact', contactOk);
    setStepComplete('shipping', shippingOk);
    setStepComplete('payment', true);
  }

  function validateContactSoft() {
    var name = form.querySelector('[name="customer_name"]');
    var email = form.querySelector('[name="customer_email"]');
    var phone = form.querySelector('[name="customer_phone"]');
    return Boolean(
      name &&
        name.value.trim() &&
        email &&
        validateEmail(email.value.trim()) &&
        phone &&
        validatePhone(phone.value.trim())
    );
  }

  function validateShippingSoft() {
    if (!selectedMethod()) return false;
    if (isPickup()) return true;
    return Boolean(
      cityRef && cityRef.value && warehouseRef && warehouseRef.value
    );
  }

  function setLoading(isLoading) {
    submitBtns.forEach(function (btn) {
      btn.classList.toggle('is-loading', isLoading);
      btn.disabled = isLoading;
      if (isLoading) {
        if (!btn.querySelector('.checkout-submit__spinner')) {
          var spin = document.createElement('span');
          spin.className = 'checkout-submit__spinner';
          spin.setAttribute('aria-hidden', 'true');
          spin.textContent = '\u266A';
          btn.appendChild(spin);
        }
        btn.setAttribute('aria-busy', 'true');
      } else {
        var existing = btn.querySelector('.checkout-submit__spinner');
        if (existing) existing.remove();
        btn.removeAttribute('aria-busy');
      }
    });
  }

  methodInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      toggleNp();
      refreshSteps();
    });
  });
  paymentInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      syncPaymentCards();
      refreshSteps();
    });
  });
  toggleNp();
  syncPaymentCards();

  if (citySearch) {
    citySearch.addEventListener('input', function () {
      clearTimeout(cityTimer);
      var q = citySearch.value.trim();
      cityTimer = setTimeout(function () {
        if (q.length < 2) {
          hideList(cityResults);
          return;
        }
        fetch(citiesUrl + '?q=' + encodeURIComponent(q), {
          headers: { Accept: 'application/json' },
        })
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (!data.ok) return;
            renderList(cityResults, data.results || [], function (item) {
              cityRef.value = item.ref;
              cityName.value = item.name;
              if (areaRef) areaRef.value = item.area_ref || '';
              citySearch.value = item.name;
              warehouseRef.value = '';
              warehouseName.value = '';
              warehouseSearch.value = '';
              refreshSteps();
            });
          })
          .catch(function () {});
      }, 300);
    });
  }

  if (warehouseSearch) {
    warehouseSearch.addEventListener('input', function () {
      clearTimeout(whTimer);
      var q = warehouseSearch.value.trim();
      whTimer = setTimeout(function () {
        if (!cityRef.value) return;
        fetch(
          warehousesUrl +
            '?city_ref=' +
            encodeURIComponent(cityRef.value) +
            '&q=' +
            encodeURIComponent(q),
          { headers: { Accept: 'application/json' } }
        )
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (!data.ok) return;
            renderList(warehouseResults, data.results || [], function (item) {
              warehouseRef.value = item.ref;
              warehouseName.value = item.name;
              warehouseSearch.value = item.name;
              refreshSteps();
            });
          })
          .catch(function () {});
      }, 300);
    });
  }

  ['customer_name', 'customer_email', 'customer_phone'].forEach(function (name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (!el) return;
    el.addEventListener('blur', function () {
      validateContact();
      refreshSteps();
    });
    el.addEventListener('input', function () {
      refreshSteps();
    });
  });

  document.addEventListener('click', function (event) {
    if (
      cityResults &&
      !cityResults.hidden &&
      !cityResults.contains(event.target) &&
      event.target !== citySearch
    ) {
      hideList(cityResults);
    }
    if (
      warehouseResults &&
      !warehouseResults.hidden &&
      !warehouseResults.contains(event.target) &&
      event.target !== warehouseSearch
    ) {
      hideList(warehouseResults);
    }
  });

  form.addEventListener('submit', function (event) {
    var contactOk = validateContact();
    var shippingOk = validateShipping();
    refreshSteps();
    if (!contactOk || !shippingOk) {
      event.preventDefault();
      var firstInvalid = form.querySelector('.form-field.is-invalid .checkout-input, [data-np-error]:not([hidden])');
      if (firstInvalid && firstInvalid.focus) firstInvalid.focus();
      else if (npError && !npError.hidden && citySearch) citySearch.focus();
      return;
    }
    setLoading(true);
  });

  refreshSteps();
})();
