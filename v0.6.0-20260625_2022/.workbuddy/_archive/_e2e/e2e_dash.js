const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1080});

  const apiCalls = [];
  page.on('response', resp => {
    if (resp.url().includes('/api/')) {
      console.log('  [NET] ' + resp.request().method() + ' ' + resp.url().replace('http://152.136.115.121', '') + ' -> ' + resp.status());
      apiCalls.push({status: resp.status(), url: resp.url()});
    }
  });
  page.on('pageerror', err => console.log('  [PAGEERROR] ' + err.message));

  console.log('[1/4] Login first...');
  await page.goto('http://152.136.115.121/login', {waitUntil: 'networkidle0', timeout: 30000});
  await new Promise(r => setTimeout(r, 1000));

  // Login by pressing Enter
  const inputs = await page.$$('input');
  if (inputs.length >= 2) {
    await inputs[1].focus();
    await page.keyboard.press('Enter');
  }
  await new Promise(r => setTimeout(r, 4000));
  console.log('  URL: ' + page.url());

  console.log('[2/4] Navigating to data dashboard...');
  // Try different paths
  const paths = ['/dashboard/screen', '/screen', '/dataview', '/dashboard', '/'];
  for (const p of paths) {
    await page.goto('http://152.136.115.121' + p, {waitUntil: 'networkidle0', timeout: 15000}).catch(e => console.log('  ' + p + ' Error: ' + e.message));
    await new Promise(r => setTimeout(r, 2000));
    const url = page.url();
    const hasError = await page.evaluate(() => {
      return document.body.textContent.includes('Server Error') ||
             document.body.textContent.includes('500') ||
             document.body.textContent.includes('加载失败');
    });
    if (url.includes(p) && !hasError) {
      console.log('  ' + p + ' OK: ' + url);
    } else if (hasError) {
      console.log('  ' + p + ' HAS ERROR, URL: ' + url);
    } else {
      console.log('  ' + p + ' redirected to: ' + url);
    }
    await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/dash_' + p.replace(/\//g, '_') + '.png', fullPage: true});
  }

  console.log('[3/4] Final state...');
  console.log('  URL: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/dash_final.png', fullPage: true});

  console.log('[4/4] /up health check...');
  const resp = await page.goto('http://152.136.115.121/up', {waitUntil: 'networkidle0', timeout: 10000});
  console.log('  /up status: ' + resp.status());

  console.log('');
  console.log('=== API call summary ===');
  const errors = apiCalls.filter(c => c.status >= 400);
  if (errors.length === 0) {
    console.log('  No errors! All API calls returned < 400');
  } else {
    errors.forEach(c => console.log('  ERROR ' + c.status + ' ' + c.url.replace('http://152.136.115.121', '')));
  }

  await browser.close();
  console.log('');
  console.log('[DONE]');
})().catch(e => {
  console.error('ERROR: ' + e.message);
  process.exit(1);
});
