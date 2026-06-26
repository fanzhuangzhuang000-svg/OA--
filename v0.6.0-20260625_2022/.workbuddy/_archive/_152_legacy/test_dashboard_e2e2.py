"""
Open the data dashboard via the menu navigation, not direct URL.
The actual path is /screen (no /dashboard prefix).
"""
import subprocess

script = r'''const puppeteer = require('puppeteer-core');

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

  console.log('[1/4] Login...');
  await page.goto('http://152.136.115.121/login', {waitUntil: 'networkidle0', timeout: 30000});
  await new Promise(r => setTimeout(r, 1000));
  const inputs = await page.$$('input');
  if (inputs.length >= 2) {
    await inputs[1].focus();
    await page.keyboard.press('Enter');
  }
  await new Promise(r => setTimeout(r, 4000));
  console.log('  URL: ' + page.url());

  console.log('[2/4] Navigate to data dashboard...');
  await page.goto('http://152.136.115.121/screen', {waitUntil: 'networkidle0', timeout: 15000});
  await new Promise(r => setTimeout(r, 3000));
  console.log('  URL: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/dash_screen.png', fullPage: true});

  console.log('[3/4] Check for error messages...');
  const hasError = await page.evaluate(() => {
    const text = document.body.textContent;
    return {
      hasServerError: text.includes('Server Error'),
      has500: text.includes('500'),
      hasLoadFailed: text.includes('加载失败'),
      title: document.title,
      bodyText: text.substring(0, 500)
    };
  });
  console.log('  Has errors: ' + JSON.stringify(hasError));

  console.log('[4/4] /up health...');
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
'''

with open('D:/work/website/OA/.workbuddy/e2e_dash2.js', 'w', encoding='utf-8') as f:
    f.write(script)

import shutil
shutil.copy('D:/work/website/OA/.workbuddy/e2e_dash2.js', 'C:/Users/MRG/.workbuddy/binaries/node/workspace/e2e_dash2.js')

result = subprocess.run(
    ['C:/Users/MRG/.workbuddy/binaries/node/versions/22.22.2/node.exe', 'e2e_dash2.js'],
    cwd='C:/Users/MRG/.workbuddy/binaries/node/workspace',
    capture_output=True,
    text=True,
    timeout=120
)
print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr[:3000])
print(f"Exit code: {result.returncode}")
