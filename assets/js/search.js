(function () {
  var I18N = window.SITE_I18N || {};
  var switcher = document.getElementById('lang-switcher');

  function known(l) { return I18N.hasOwnProperty(l); }

  function setHidden(elements, hidden) {
    Array.prototype.forEach.call(elements, function (el) { el.hidden = hidden; });
  }

  function applyLocaleToSection(sec, lang) {
    var useLocal = sec.getAttribute('data-city-locale') === lang;
    Array.prototype.forEach.call(sec.querySelectorAll('.t-en, .d-en'), function (en) {
      hideEnglishSpanIfLocalized(en, useLocal);
    });
    setHidden(sec.querySelectorAll('.t-local, .d-local'), !useLocal);
  }

  function hideEnglishSpanIfLocalized(en, useLocal) {
    var localClass = en.classList.contains('t-en') ? '.t-local' : '.d-local';
    var hasLocal = en.parentNode.querySelector(localClass) !== null;
    en.hidden = useLocal && hasLocal;
  }

  function applyLang(lang) {
    var dict = I18N[lang] || I18N.en || {};
    document.documentElement.lang = lang;
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n]'), function (el) {
      var k = el.getAttribute('data-i18n');
      if (dict[k] != null) el.textContent = dict[k];
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n-placeholder]'), function (el) {
      var k = el.getAttribute('data-i18n-placeholder');
      if (dict[k] != null) el.setAttribute('placeholder', dict[k]);
    });
    var citySections = document.querySelectorAll('[data-city-section]');
    for (var i = 0; i < citySections.length; i++) {
      applyLocaleToSection(citySections[i], lang);
    }
  }

  var stored = localStorage.getItem('lang');
  var initial = known(stored) ? stored : 'en';

  if (switcher) {
    switcher.value = initial;
    switcher.addEventListener('change', function () {
      localStorage.setItem('lang', switcher.value);
      applyLang(switcher.value);
    });
  }

  applyLang(initial);

  var input = document.getElementById('city-search');
  if (!input) return;
  var sections = Array.prototype.slice.call(document.querySelectorAll('[data-city-section]'));
  var noResults = document.querySelector('.no-results');

  function apply() {
    var q = input.value.trim().toLowerCase();
    var anyVisible = false;
    sections.forEach(function (s) {
      var name = (s.getAttribute('data-city-name') || '').toLowerCase();
      var id = (s.getAttribute('data-city-id') || '').toLowerCase();
      var match = q === '' || name.indexOf(q) !== -1 || id.indexOf(q) !== -1;
      s.hidden = !match;
      if (match) anyVisible = true;
    });
    if (noResults) noResults.hidden = anyVisible;
  }

  input.addEventListener('input', apply);
})();
