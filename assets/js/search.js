(function () {
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
