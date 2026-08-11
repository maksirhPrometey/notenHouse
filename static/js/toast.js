/* NotenHaus — toast auto-dismiss (~3s) */

(function () {
  var DISMISS_MS = 3000;
  var LEAVE_MS = 280;

  function dismissToast(el) {
    if (!el || el.dataset.toastLeaving === '1') return;
    el.dataset.toastLeaving = '1';
    el.classList.add('is-leaving');
    window.setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, LEAVE_MS);
  }

  function initToast(el) {
    if (!el || el.dataset.toastInit === '1') return;
    el.dataset.toastInit = '1';
    window.setTimeout(function () {
      dismissToast(el);
    }, DISMISS_MS);
  }

  function initAll(root) {
    var scope = root && root.querySelectorAll ? root : document;
    var nodes = scope.querySelectorAll
      ? scope.querySelectorAll('[data-toast]')
      : [];
    for (var i = 0; i < nodes.length; i += 1) {
      initToast(nodes[i]);
    }
    if (scope !== document && scope.matches && scope.matches('[data-toast]')) {
      initToast(scope);
    }
  }

  function onReady() {
    initAll(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }

  document.body.addEventListener('htmx:oobAfterSwap', function () {
    initAll(document);
  });

  document.body.addEventListener('htmx:afterSettle', function (event) {
    var target = event.target;
    if (target) {
      initAll(target);
      if (target.parentNode) initAll(target.parentNode);
    }
    initAll(document.getElementById('toasts'));
  });

  if (typeof MutationObserver === 'function') {
    var observer = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i += 1) {
        var added = mutations[i].addedNodes;
        for (var j = 0; j < added.length; j += 1) {
          var node = added[j];
          if (!node || node.nodeType !== 1) continue;
          if (node.matches && node.matches('[data-toast]')) {
            initToast(node);
          }
          if (node.querySelectorAll) {
            initAll(node);
          }
        }
      }
    });
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  }
})();
