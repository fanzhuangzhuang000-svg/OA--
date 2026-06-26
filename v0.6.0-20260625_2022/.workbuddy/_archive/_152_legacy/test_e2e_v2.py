"""
Improved E2E test: properly clear fields, watch network requests.
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
  await page.setViewport({width: 1440, height: 900});

  const apiCalls = [];
  page.on('response', resp => {
    if (resp.url().includes('/api/')) {
      console.log('  [NET] ' + resp.request().method() + ' ' + resp.url().replace('http://152.136.115.121', '') + ' -> ' + resp.status());
      apiCalls.push({status: resp.status(), url: resp.url()});
    }
  });
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('  [CONSOLE.error] ' + msg.text());
    }
  });

  console.log('[1/5] Navigating to http://152.136.115.121 ...');
  await page.goto('http://152.136.115.121', {waitUntil: 'networkidle0', timeout: 30000});
  console.log('  Title: ' + await page.title());
  console.log('  URL: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_01_login.png', fullPage: true});

  await page.waitForSelector('input', {timeout: 10000});
  await new Promise(r => setTimeout(r, 1000));

  console.log('[2/5] Filling login form (clearing first)...');
  const inputs = await page.$$('input');
  console.log('  Found ' + inputs.length + ' inputs');

  if (inputs.length >= 1) {
    await inputs[0].focus();
    await page.keyboard.down('Control');
    await page.keyboard.press('A');
    await page.keyboard.up('Control');
    await page.keyboard.press('Backspace');
    await inputs[0].type('admin');
    const val1 = await page.evaluate(el => el.value, inputs[0]);
    console.log('  Username field value: "' + val1 + '"');
  }
  if (inputs.length >= 2) {
    await inputs[1].focus();
    await page.keyboard.down('Control');
    await page.keyboard.press('A');
    await page.keyboard.up('Control');
    await page.keyboard.press('Backspace');
    await inputs[1].type('admin123');
    const val2 = await page.evaluate(el => el.value, inputs[1]);
    console.log('  Password field value length: ' + val2.length);
  }
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_02_filled.png', fullPage: true});

  console.log('[3/5] Clicking login button...');
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await page.evaluate(el => el.textContent.trim(), btn);
    if (text.includes('登录')) {
      await btn.click();
      console.log('  Clicked: "' + text + '"');
      break;
    }
  }

  await new Promise(r => setTimeout(r, 5000));
  console.log('  URL after login: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_03_after_login.png', fullPage: true});

  const tokenInStorage = await page.evaluate(() => {
    return {
      localStorage: Object.fromEntries(Object.entries(localStorage)),
      sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),
    };
  });
  console.log('  localStorage: ' + JSON.stringify(tokenInStorage.localStorage).substring(0, 250));
  console.log('  sessionStorage: ' + JSON.stringify(tokenInStorage.sessionStorage).substring(0, 250));

  console.log('[4/5] Navigating to dashboard / ...');
  await page.goto('http://152.136.115.121/', {waitUntil: 'networkidle0', timeout: 15000}).catch(e => console.log('  Error: ' + e.message));
  await new Promise(r => setTimeout(r, 2000));
  console.log('  URL: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_04_dashboard.png', fullPage: true});

  await page.goto('http://152.136.115.121/dashboard', {waitUntil: 'networkidle0', timeout: 15000}).catch(e => console.log('  Error: ' + e.message));
  await new Promise(r => setTimeout(r, 2000));
  console.log('  Dashboard URL: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_05_dashboard2.png', fullPage: true});

  console.log('[5/5] /up health check...');
  const resp = await page.goto('http://152.136.115.121/up', {waitUntil: 'networkidle0', timeout: 10000});
  console.log('  /up status: ' + resp.status());

  console.log('');
  console.log('=== API call summary ===');
  apiCalls.forEach(c => console.log('  ' + c.status + ' ' + c.url.replace('http://152.136.115.121', '')));

  await browser.close();
  console.log('');
  console.log('[DONE]');
})().catch(e => {
  console.error('ERROR: ' + e.message);
  process.exit(1);
});
'''

with open('D:/work/website/OA/.workbuddy/e2e_server.js', 'w', encoding='utf-8') as f:
    f.write(script)

subprocess.run(['cp', 'D:/work/website/OA/.workbuddy/e2e_server.js', 'C:/Users/MRG/.workbuddy/binaries/node/workspace/e2e_server.js'])
result = subprocess.run(
    ['C:/Users/MRG/.workbuddy/binaries/node/versions/22.22.2/node.exe', 'e2e_server.js'],
    cwd='C:/Users/MRG/.workbuddy/binaries/node/workspace',
    capture_output=True,
    text=True,
    timeout=120
)
print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"Exit code: {result.returncode}")
