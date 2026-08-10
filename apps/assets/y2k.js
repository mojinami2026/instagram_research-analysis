/* ============================================================
   y2k.js — tiny app engine for the Overthinking Suite™
   Declare a spec, get a whole website. No build step, no deps.
   ============================================================ */
(function () {
  'use strict';

  const $ = (sel, root) => (root || document).querySelector(sel);
  const el = (tag, attrs, html) => {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (html != null) n.innerHTML = html;
    return n;
  };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
  const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
  const round = (n, d) => { const p = Math.pow(10, d || 0); return Math.round(n * p) / p; };
  const money = (n) => '$' + Math.round(n).toLocaleString('en-US');
  const pick = (arr, score) => arr[clamp(Math.floor((score / 100) * arr.length), 0, arr.length - 1)];

  const TICKER = [
    'welcome 2 the overthinking suite',
    'no data leaves ur computer, pinky swear',
    'this is entertainment, not therapy',
    'sign my guestbook',
    'best viewed at 800x600',
    'ur browser is a diary now',
  ];

  /* ---------- decorative chrome ---------- */
  function ticker(extra) {
    const msgs = (extra ? [extra] : []).concat(TICKER);
    const bar = el('div', { class: 'tickerbar' });
    bar.appendChild(el('span', null, '★ ' + msgs.join(' ★ ') + ' ★'));
    document.body.insertBefore(bar, document.body.firstChild);
  }

  function sparkles() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const chars = ['✦', '✧', '·', '✩', '❀', '☆'];
    let last = 0;
    addEventListener('pointermove', (e) => {
      const now = Date.now();
      if (now - last < 70) return;
      last = now;
      const s = el('div', { class: 'sparkle' }, chars[Math.floor(Math.random() * chars.length)]);
      s.style.left = e.clientX + 'px';
      s.style.top = e.clientY + 'px';
      s.style.color = ['#ff1e9c', '#6ef3ff', '#fff97a', '#b57edc'][Math.floor(Math.random() * 4)];
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 900);
    }, { passive: true });
  }

  function hitCounter(key) {
    let n;
    try {
      n = parseInt(localStorage.getItem('hits:' + key) || '0', 10) + 1;
      localStorage.setItem('hits:' + key, String(n));
    } catch (_) { n = 1; }
    const total = 31337 + n * 7;
    return String(total).padStart(6, '0').split('').map((d) => '<b>' + d + '</b>').join('');
  }

  function win(title, bodyHTML, cls) {
    return '<section class="win ' + (cls || '') + '">' +
      '<div class="win__bar"><b>' + title + '</b>' +
      '<div class="win__btns"><i>_</i><i>□</i><i>×</i></div></div>' +
      '<div class="win__body">' + bodyHTML + '</div></section>';
  }

  /* ---------- field rendering ---------- */
  function fieldHTML(f) {
    const hint = f.hint ? '<span class="field__hint">' + f.hint + '</span>' : '';
    const id = 'f_' + f.id;

    if (f.type === 'slider') {
      const def = f.default != null ? f.default : Math.round(((f.min || 0) + (f.max || 10)) / 2);
      return '<div class="field"><label for="' + id + '">' + f.label + hint + '</label>' +
        '<div class="slider"><input type="range" id="' + id + '" data-id="' + f.id + '" data-kind="slider" ' +
        'min="' + (f.min || 0) + '" max="' + (f.max != null ? f.max : 10) + '" step="' + (f.step || 1) + '" value="' + def + '">' +
        '<output>' + def + '</output></div>' +
        (f.ticks ? '<div class="ticks"><span>' + f.ticks[0] + '</span><span>' + f.ticks[1] + '</span></div>' : '') +
        '</div>';
    }
    if (f.type === 'num') {
      return '<div class="field"><label for="' + id + '">' + f.label + hint + '</label>' +
        '<div class="inputrow">' + (f.prefix ? '<span class="affix">' + f.prefix + '</span>' : '') +
        '<input type="number" id="' + id + '" data-id="' + f.id + '" data-kind="num" inputmode="decimal" ' +
        'value="' + (f.default != null ? f.default : 0) + '" min="' + (f.min != null ? f.min : 0) + '"' +
        (f.max != null ? ' max="' + f.max + '"' : '') + ' step="' + (f.step || 1) + '">' +
        (f.suffix ? '<span class="affix">' + f.suffix + '</span>' : '') + '</div></div>';
    }
    if (f.type === 'choice') {
      const opts = f.options.map((o, i) => {
        const checked = (f.default != null ? f.default === o.v : i === 0) ? ' checked' : '';
        return '<label><input type="radio" name="' + id + '" data-id="' + f.id + '" data-kind="choice" ' +
          'value="' + o.v + '"' + checked + '>' + o.label + '</label>';
      }).join('');
      return '<div class="field"><span class="field__legend">' + f.label + hint + '</span>' +
        '<div class="choices">' + opts + '</div></div>';
    }
    if (f.type === 'checks') {
      const opts = f.options.map((o) =>
        '<label><input type="checkbox" data-id="' + f.id + '" data-kind="checks" value="' + o.v + '">' +
        '<span>' + o.label + '</span></label>').join('');
      return '<div class="field"><span class="field__legend">' + f.label + hint + '</span>' +
        '<div class="checks">' + opts + '</div></div>';
    }
    if (f.type === 'text') {
      return '<div class="field"><label for="' + id + '">' + f.label + hint + '</label>' +
        '<input type="text" id="' + id + '" data-id="' + f.id + '" data-kind="text" placeholder="' +
        (f.placeholder || '') + '" value="' + (f.default || '') + '"></div>';
    }
    if (f.type === 'textarea') {
      return '<div class="field"><label for="' + id + '">' + f.label + hint + '</label>' +
        '<textarea id="' + id + '" data-id="' + f.id + '" data-kind="text" placeholder="' +
        (f.placeholder || '') + '">' + (f.default || '') + '</textarea></div>';
    }
    if (f.type === 'html') return f.html;
    return '';
  }

  function readValues(form) {
    const v = {};
    form.querySelectorAll('[data-id]').forEach((n) => {
      const id = n.dataset.id, kind = n.dataset.kind;
      if (kind === 'slider' || kind === 'num') v[id] = parseFloat(n.value) || 0;
      else if (kind === 'choice') { if (n.checked) v[id] = isNaN(+n.value) ? n.value : +n.value; }
      else if (kind === 'checks') { (v[id] = v[id] || []); if (n.checked) v[id].push(n.value); }
      else v[id] = n.value;
    });
    return v;
  }

  /* ---------- fake dial-up analysis ---------- */
  const BOOT = [
    'DIALING 1-800-OVERTHINK ...',
    'HANDSHAKE ... kshhhh-BEEDLE-DEEP-kshhh',
    'CONNECTED @ 56.6 kbps',
  ];
  function runLoader(box, lines, done) {
    const log = $('.loader__log', box), bar = $('.loader__bar i', box);
    box.classList.add('on');
    log.textContent = '';
    bar.style.width = '0%';
    const all = BOOT.concat(lines, ['DONE. brace yourself.']);
    let i = 0;
    (function step() {
      if (i >= all.length) { setTimeout(() => { box.classList.remove('on'); done(); }, 420); return; }
      log.textContent += (i ? '\n' : '') + '> ' + all[i];
      log.scrollTop = log.scrollHeight;
      bar.style.width = Math.round(((i + 1) / all.length) * 100) + '%';
      i++;
      setTimeout(step, 190 + Math.random() * 200);
    })();
  }

  /* ---------- results ---------- */
  function renderResult(box, r, app) {
    const stats = (r.stats || []).map((s) =>
      '<div class="stat"><b>' + esc(s.v) + '</b><span>' + esc(s.k) + '</span></div>').join('');
    const receipts = (r.receipts || []).map((x) => {
      const t = typeof x === 'string' ? { t: x } : x;
      return '<li class="is-' + (t.vibe || 'mid') + '">' + t.t + '</li>';
    }).join('');

    box.innerHTML =
      '<div class="verdict">' +
        '<div class="verdict__label">◄ THE VERDICT ►</div>' +
        '<h2 class="verdict__title">' + r.title + '</h2>' +
        '<p class="verdict__blurb">' + r.blurb + '</p>' +
      '</div>' +
      '<div class="score vibe-' + (r.vibe || 'mid') + '">' +
        '<div class="score__num">' + (r.scoreText != null ? r.scoreText : Math.round(r.score)) + '</div>' +
        '<div class="meter"><i></i></div>' +
      '</div>' +
      '<div class="meterlbl">' + (app.meterLabel || 'the number') + '</div>' +
      (stats ? '<div class="stats">' + stats + '</div>' : '') +
      (receipts ? '<div class="subhead">✂ the receipts</div><ul class="receipts">' + receipts + '</ul>' : '') +
      (r.extra || '') +
      '<div class="subhead">✎ what now</div>' +
      '<p style="font-size:14.5px;margin:0 0 14px">' + (r.advice || 'Sit with it.') + '</p>' +
      '<div class="btnrow">' +
        '<button class="btn btn--ghost" data-act="copy">📋 copy my results</button>' +
        '<button class="btn btn--ghost" data-act="again">↺ change my answers</button>' +
        '<a class="btn btn--ghost" href="index.html">🏠 back to the suite</a>' +
      '</div>';

    box.classList.add('on');
    requestAnimationFrame(() => { $('.meter i', box).style.width = clamp(r.score, 2, 100) + '%'; });

    box.querySelector('[data-act="copy"]').addEventListener('click', function () {
      const txt = app.title + '\n' + (r.scoreText != null ? r.scoreText : Math.round(r.score)) +
        ' — ' + r.title.replace(/<[^>]+>/g, '') + '\n' + r.blurb.replace(/<[^>]+>/g, '') +
        '\n\n' + (r.receipts || []).map((x) => '• ' + (typeof x === 'string' ? x : x.t).replace(/<[^>]+>/g, '')).join('\n');
      const btn = this;
      const ok = () => { btn.textContent = '✓ copied!'; setTimeout(() => { btn.textContent = '📋 copy my results'; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(ok, ok); else ok();
    });
    box.querySelector('[data-act="again"]').addEventListener('click', () => {
      box.classList.remove('on');
      document.querySelector('#quiz').scrollIntoView({ block: 'start' });
    });
    box.scrollIntoView({ block: 'start' });
  }

  /* ---------- the app builder ---------- */
  function app(spec) {
    document.title = spec.title + ' — Overthinking Suite™';
    ticker(spec.ticker);

    const fields = (spec.fields || []).map(fieldHTML).join('');
    const wrap = el('div', { class: 'wrap stack' });
    wrap.innerHTML =
      win('C:\\overthinking\\' + (spec.file || 'app') + '.exe',
        '<div class="hero">' +
          '<div class="hero__emoji">' + spec.emoji + '</div>' +
          '<h1>' + spec.title + '</h1>' +
          '<p class="hero__sub">' + spec.sub + '</p>' +
          '<div class="glitterline"></div>' +
          '<p class="hero__sub" style="font-size:13.5px">' + (spec.intro || '') + '</p>' +
        '</div>') +
      win('☞ the interrogation', '<form id="quiz" novalidate>' + fields +
        '<div class="btnrow"><button type="submit" class="btn">' + (spec.button || '✧ TELL ME THE TRUTH ✧') + '</button>' +
        '<span class="blink" style="font-size:13px">&lt;-- click it, coward</span></div>' +
        '</form>' +
        '<div class="loader" id="loader"><div class="loader__log"></div><div class="loader__bar"><i></i></div></div>') +
      win('★ results.html', '<div class="result" id="result"></div>' +
        '<p id="placeholder" style="text-align:center;font-size:14px;opacity:.7;margin:6px 0">' +
        'answer the questions and this window will fill up with things you already knew.</p>');
    document.body.appendChild(wrap);

    const footer = el('div', { class: 'wrap footer' });
    footer.innerHTML =
      '<div class="glitterline"></div>' +
      '<div class="badges"><span class="badge">MADE ON A COMPUTER</span>' +
      '<span class="badge">100% CLIENT-SIDE</span>' +
      '<span class="badge">NOT A DIAGNOSIS</span>' +
      '<span class="badge">Y2K COMPLIANT</span></div>' +
      '<p>you are visitor <span class="counter">' + hitCounter(spec.file || spec.title) + '</span> ' +
      'to this page · <a href="index.html">« back to the suite</a></p>' +
      '<p style="opacity:.7">everything is calculated in your browser. nothing is uploaded. ' +
      'this is a toy — please do not end a relationship over a number a website made up.</p>';
    document.body.appendChild(footer);

    sparkles();

    const form = $('#quiz'), loader = $('#loader'), result = $('#result'), ph = $('#placeholder');

    form.addEventListener('input', (e) => {
      if (e.target.dataset.kind === 'slider') {
        const out = e.target.parentNode.querySelector('output');
        if (out) out.textContent = e.target.value;
      }
    });

    if (spec.onMount) spec.onMount(form);

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const v = readValues(form);
      if (spec.collect) Object.assign(v, spec.collect(form) || {});
      let r;
      try { r = spec.compute(v); } catch (err) { console.error(err); return; }
      if (!r) return;
      if (ph) ph.style.display = 'none';
      result.classList.remove('on');
      runLoader(loader, spec.loaderLines || ['CRUNCHING FEELINGS ...', 'CROSS-REFERENCING RED FLAGS ...'],
        () => renderResult(result, r, spec));
    });
  }

  window.Y2K = { app, el, esc, clamp, round, money, pick, win, sparkles, hitCounter, ticker };
})();
