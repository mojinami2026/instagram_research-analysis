#!/usr/bin/env node
/**
 * Smoke test for the Overthinking Suite.
 *
 * The suite has no build step, so there is nothing to typecheck or compile —
 * a broken app looks exactly like a working one until someone opens it. This
 * serves apps/ over HTTP with the real Cloudflare `_headers` applied and then,
 * for every page:
 *
 *   1. loads it and fails on any JS error or console error
 *   2. fails on any CSP violation (so `_headers` can't silently break the site)
 *   3. fails on any request to an external origin (the privacy claim, enforced)
 *   4. submits the form and fails if no result renders
 *   5. fails on "undefined"/"NaN" leaking into rendered output
 *   6. fails on horizontal overflow at 390px
 *   7. checks every index.html card link resolves to a real file
 *
 * Usage: node apps/tools/smoke-test.js
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const APPS = path.resolve(__dirname, '..');
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8' };

/** Minimal `_headers` parser: collects the rules under the `/*` catch-all. */
function globalHeaders() {
  const file = path.join(APPS, '_headers');
  if (!fs.existsSync(file)) return {};
  const out = {};
  let inGlobal = false;
  for (const raw of fs.readFileSync(file, 'utf8').split('\n')) {
    const line = raw.replace(/\s+$/, '');
    if (!line || line.trimStart().startsWith('#')) continue;
    if (!/^\s/.test(line)) { inGlobal = line.trim() === '/*'; continue; }
    if (!inGlobal) continue;
    const i = line.indexOf(':');
    if (i > 0) out[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return out;
}

function serve(headers) {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
    const file = path.join(APPS, rel);
    if (!file.startsWith(APPS) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404); return res.end('not found');
    }
    for (const [k, v] of Object.entries(headers)) res.setHeader(k, v);
    res.setHeader('Content-Type', MIME[path.extname(file)] || 'application/octet-stream');
    res.end(fs.readFileSync(file));
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

const SAMPLE_TEXT = [
  'them: hey! loved your talk today, we should grab drinks 😉 friday late?',
  'you: haha sure, what works',
  'them: humbled and thrilled to announce my new role — what a journey'
].join('\n');

(async () => {
  const headers = globalHeaders();
  console.log('applying _headers:', Object.keys(headers).join(', ') || '(none)');
  const server = await serve(headers);
  const base = `http://127.0.0.1:${server.address().port}`;

  // SMOKE_CHROME lets you point at an already-installed Chromium instead of
  // Playwright's own download (useful in sandboxes and prebaked images).
  const browser = await chromium.launch(
    process.env.SMOKE_CHROME ? { executablePath: process.env.SMOKE_CHROME, args: ['--no-sandbox'] } : {}
  );
  const files = fs.readdirSync(APPS).filter(f => f.endsWith('.html')).sort();
  let failed = 0;

  for (const file of files) {
    const page = await browser.newPage();
    const errs = [];

    page.on('pageerror', e => errs.push('JS ERROR: ' + e.message));
    page.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
    page.on('request', r => {
      if (!r.url().startsWith(base) && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) {
        errs.push('EXTERNAL REQUEST: ' + r.url());
      }
    });
    await page.addInitScript(() => {
      addEventListener('securitypolicyviolation', e =>
        console.error('CSP VIOLATION: ' + e.violatedDirective + ' blocked ' + e.blockedURI));
    });

    await page.goto(base + '/' + file, { waitUntil: 'load' });
    await page.waitForTimeout(150);

    let note = '';
    if (file === 'index.html') {
      const hrefs = await page.locator('a.card').evaluateAll(as => as.map(a => a.getAttribute('href')));
      for (const h of hrefs) if (!fs.existsSync(path.join(APPS, h))) errs.push('DEAD LINK: ' + h);
      if (hrefs.length === 0) errs.push('NO APP CARDS ON INDEX');
      note = `cards=${hrefs.length}`;
    } else {
      if (!(await page.locator('#quiz button[type=submit]').count())) errs.push('NO SUBMIT BUTTON');

      const textareas = page.locator('#quiz textarea');
      for (let i = 0; i < (await textareas.count()); i++) await textareas.nth(i).fill(SAMPLE_TEXT);

      await page.locator('#quiz button[type=submit]').click();
      await page.waitForSelector('#result.on', { timeout: 15000 })
        .catch(() => errs.push('NO RESULT RENDERED AFTER SUBMIT'));

      const out = await page.locator('#result').innerText().catch(() => '');
      if (!out.trim()) errs.push('EMPTY RESULT');
      // Answer labels legitimately contain the word "undefined", so only flag
      // the shapes that mean a bug: bare NaN, or "$NaN"/"undefined/10" splices.
      const bug = out.match(/(NaN|undefined)(\s*(\/|%|pts|points|mo\b|months))|[$]\s*NaN|\bNaN\b/);
      if (bug) errs.push('BAD VALUE IN OUTPUT: ' + bug[0]);

      await page.setViewportSize({ width: 390, height: 800 });
      await page.waitForTimeout(120);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (overflow > 2) errs.push(`H-OVERFLOW ${overflow}px at 390px wide`);

      const score = (await page.locator('#result .score__num').textContent().catch(() => '')) || '';
      note = `score=${score.trim()}`;
    }

    if (errs.length) { failed++; console.log(`✗ ${file}  ${note}`); errs.forEach(e => console.log('    ' + e)); }
    else console.log(`✓ ${file}  ${note}`);
    await page.close();
  }

  await browser.close();
  server.close();

  console.log(failed ? `\n${failed} of ${files.length} pages have problems` : `\nall ${files.length} pages OK`);
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
