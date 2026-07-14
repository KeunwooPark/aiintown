(function () {
  var root = document.querySelector('[data-ask]');
  if (!root) return;

  var I18N = window.SITE_I18N || {};
  var endpoint = root.getAttribute('data-endpoint') || '';
  var form = root.querySelector('[data-ask-form]');
  var input = root.querySelector('[data-ask-input]');
  var submit = root.querySelector('[data-ask-submit]');
  var statusEl = root.querySelector('[data-ask-status]');
  var answerEl = root.querySelector('[data-ask-answer]');
  var eventsEl = root.querySelector('[data-ask-events]');

  function currentLang() {
    var sw = document.getElementById('lang-switcher');
    if (sw && sw.value) return sw.value;
    return document.documentElement.lang || 'en';
  }

  function t(key, fallback) {
    var dict = I18N[currentLang()] || I18N.en || {};
    return dict[key] != null ? dict[key] : fallback;
  }

  function setStatus(message) {
    if (!message) {
      statusEl.hidden = true;
      statusEl.textContent = '';
      return;
    }
    statusEl.hidden = false;
    statusEl.textContent = message;
  }

  function clearOutput() {
    answerEl.textContent = '';
    eventsEl.textContent = '';
  }

  // Render plain-text answer safely: paragraphs on blank lines, <br> on
  // single newlines. Everything goes through textContent — no HTML injection.
  function renderAnswer(text) {
    answerEl.textContent = '';
    var paragraphs = text.split(/\n\s*\n/);
    paragraphs.forEach(function (para) {
      if (!para.trim()) return;
      var p = document.createElement('p');
      var lines = para.split('\n');
      lines.forEach(function (line, i) {
        if (i > 0) p.appendChild(document.createElement('br'));
        p.appendChild(document.createTextNode(line));
      });
      answerEl.appendChild(p);
    });
  }

  function renderEvents(events) {
    eventsEl.textContent = '';
    if (!events || !events.length) return;

    events.forEach(function (e) {
      var card = document.createElement('article');
      card.className = 'ask-event-card';

      if (e.date && e.date_status !== 'unknown') {
        var time = document.createElement('time');
        time.setAttribute('datetime', e.date);
        time.textContent = e.date;
        card.appendChild(time);
      }

      var h = document.createElement('h4');
      if (e.url) {
        var a = document.createElement('a');
        a.href = e.url;
        a.rel = 'noopener';
        a.target = '_blank';
        a.textContent = e.title;
        h.appendChild(a);
      } else {
        h.textContent = e.title;
      }
      card.appendChild(h);

      if (e.venue) {
        var v = document.createElement('p');
        v.className = 'venue';
        v.textContent = e.venue;
        card.appendChild(v);
      }
      eventsEl.appendChild(card);
    });
  }

  function ask(question) {
    if (!endpoint) {
      setStatus(t('ask_error', 'The assistant is not configured yet.'));
      return;
    }
    clearOutput();
    setStatus(t('ask_loading', 'Thinking…'));
    submit.disabled = true;

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question, lang: currentLang() })
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (r) {
        if (!r.ok) {
          setStatus((r.data && r.data.error) || t('ask_error', 'Something went wrong. Please try again.'));
          return;
        }
        setStatus('');
        renderAnswer(r.data.answer || t('ask_empty', 'No answer.'));
        renderEvents(r.data.events);
      })
      .catch(function () {
        setStatus(t('ask_error', 'Something went wrong. Please try again.'));
      })
      .then(function () {
        submit.disabled = false;
      });
  }

  form.addEventListener('submit', function (evt) {
    evt.preventDefault();
    var q = (input.value || '').trim();
    if (!q) return;
    ask(q);
  });

  // Submit on Enter (Shift+Enter for newline).
  input.addEventListener('keydown', function (evt) {
    if (evt.key === 'Enter' && !evt.shiftKey) {
      evt.preventDefault();
      form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  });
})();
