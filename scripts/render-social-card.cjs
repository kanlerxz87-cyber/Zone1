// Development-only renderer. Uses only local reviewed fonts/imagery and closes its
// temporary asset server/browser before exiting. No public site or analytics config changes.
const { chromium } = require('playwright');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '..');
const MIME = { '.woff2': 'font/woff2', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg' };

(async () => {
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://local.invalid').pathname;
    const file = path.resolve(ROOT, '.' + pathname);
    if (!pathname.startsWith('/assets/') || !file.startsWith(ROOT + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      res.writeHead(404); res.end(); return;
    }
    res.setHeader('Content-Type', MIME[path.extname(file)] || 'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
  await new Promise(resolve => server.listen(0, '0.0.0.0', resolve));
  let browser;
  try {
    const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
    browser = await chromium.launch({ ...(executablePath ? { executablePath, args: ['--no-sandbox', '--disable-dev-shm-usage'] } : {}) });
    const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
    const base = `http://127.0.0.1:${server.address().port}/`;
    const template = fs.readFileSync(path.join(ROOT, 'publication/social-card.html.tpl'), 'utf8').replaceAll('{{BASE_URL}}', base);
    await page.setContent(template, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(ROOT, 'assets/og-card.png') });
    console.log('Rendered assets/og-card.png (1200×630), using local publication assets only.');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
