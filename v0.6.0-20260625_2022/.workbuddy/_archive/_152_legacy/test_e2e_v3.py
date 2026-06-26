"""
Better E2E test - logs ALL network activity, uses form submit + Enter key.
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

  // Capture ALL responses
  page.on('response', async resp => {
    const url = resp.url();
    if (url.includes('152.136.115.121') || url.includes('/api')) {
      console.log('  [NET] ' + resp.request().method() + ' ' + url.replace('http://152.136.115.121', '') + ' -> ' + resp.status());
    }
  });
  page.on('pageerror', err => console.log('  [PAGEERROR] ' + err.message));
  page.on('console', msg => {
    if (msg.type() === 'error' || msg.type() === 'warning') {
      console.log('  [CONSOLE.' + msg.type() + '] ' + msg.text().substring(0, 200));
    }
  });

  console.log('[1/4] Navigating to http://152.136.115.121/login ...');
  await page.goto('http://152.136.115.121/login', {waitUntil: 'networkidle0', timeout: 30000});
  console.log('  Title: ' + await page.title());
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_01_login.png', fullPage: true});

  // The form has default values 'admin'/'admin123' so we can just press Enter
  console.log('[2/4] Pressing Enter in password field to submit...');
  const inputs = await page.$$('input');
  console.log('  Found ' + inputs.length + ' inputs');

  // Focus the password field and press Enter
  if (inputs.length >= 2) {
    await inputs[1].focus();
    await page.keyboard.press('Enter');
    console.log('  Pressed Enter');
  } else if (inputs.length >= 1) {
    await inputs[0].focus();
    await page.keyboard.press('Enter');
    console.log('  Pressed Enter on input 0');
  }

  // Wait for response
  await new Promise(r => setTimeout(r, 5000));
  console.log('  URL after submit: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_02_after_submit.png', fullPage: true});

  // Check storage
  const storage = await page.evaluate(() => {
    return {
      ls: Object.fromEntries(Object.entries(localStorage)),
      ss: Object.fromEntries(Object.entries(sessionStorage)),
      cookies: document.cookie
    };
  });
  console.log('  localStorage: ' + JSON.stringify(storage.ls).substring(0, 300));
  console.log('  sessionStorage: ' + JSON.stringify(storage.ss).substring(0, 300));
  console.log('  cookies: ' + storage.cookies);

  console.log('[3/4] Try clicking login button directly...');
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await page.evaluate(el => el.textContent.trim(), btn);
    if (text.includes('登录')) {
      console.log('  Clicking: "' + text + '"');
      // Click and wait for navigation/network
      await Promise.all([
        page.waitForResponse(r => r.url().includes('/api/') && r.url().includes('login'), {timeout: 10000}).catch(() => console.log('  No login response in 10s')),
        btn.click()
      ]);
      break;
    }
  }

  await new Promise(r => setTimeout(r, 4000));
  console.log('  URL after click: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_03_after_click.png', fullPage: true});

  const storage2 = await page.evaluate(() => {
    return {
      ls: Object.fromEntries(Object.entries(localStorage)),
      ss: Object.fromEntries(Object.entries(sessionStorage)),
    };
  });
  console.log('  localStorage after click: ' + JSON.stringify(storage2.ls).substring(0, 300));
  console.log('  sessionStorage after click: ' + JSON.stringify(storage2.ss).substring(0, 300));

  console.log('[4/4] Going to / dashboard...');
  await page.goto('http://152.136.115.121/', {waitUntil: 'networkidle0', timeout: 15000}).catch(e => console.log('  / Error: ' + e.message));
  await new Promise(r => setTimeout(r, 2000));
  console.log('  URL: ' + page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_04_dashboard.png', fullPage: true});

  // /up health
  const resp = await page.goto('http://152.136.115.121/up', {waitUntil: 'networkidle0', timeout: 10000});
  console.log('  /up status: ' + resp.status());

  await browser.close();
  console.log('');
  console.log('[DONE]');
})().catch(e => {
  console.error('ERROR: ' + e.message);
  console.error(e.stack);
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
    print(result.stderr[:3000])
print(f"Exit code: {result.returncode}")
