"""
Full E2E test: open http://152.136.115.121 in headless Chrome, login, navigate to dashboard.
Uses puppeteer-core with system Chrome.
"""
import time
import subprocess
import os

# Use puppeteer-core with system Chrome
CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'

print(f"Chrome path: {CHROME_PATH}")
print(f"Chrome exists: {os.path.exists(CHROME_PATH)}")

# Try the E2E pages script that already worked
script = r'''
const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setViewport({width: 1440, height: 900});

  console.log('[1/5] Navigating to http://152.136.115.121 ...');
  await page.goto('http://152.136.115.121', {waitUntil: 'networkidle0', timeout: 30000});

  console.log('  Title:', await page.title());
  console.log('  URL:', page.url());

  // Wait for login form
  console.log('[2/5] Filling login form...');
  await page.waitForSelector('input[placeholder*="账"], input[placeholder*="用"]', {timeout: 10000}).catch(() => console.log('  Login input not found, maybe already logged in'));
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_01_login.png', fullPage: true});
  console.log('  Screenshot: server_01_login.png');

  // Try to find username/password inputs
  const inputs = await page.$$('input');
  console.log(`  Found ${inputs.length} inputs`);

  // Fill username
  for (const inp of inputs) {
    const ph = await page.evaluate(el => el.placeholder, inp);
    const type = await page.evaluate(el => el.type, inp);
    if (type === 'text' || ph.includes('账') || ph.includes('用')) {
      await inp.type('admin');
      console.log(`  Typed admin in input (placeholder: ${ph})`);
      break;
    }
  }

  // Fill password
  for (const inp of inputs) {
    const type = await page.evaluate(el => el.type, inp);
    if (type === 'password') {
      await inp.type('admin123');
      console.log('  Typed admin123 in password');
      break;
    }
  }

  // Find and click login button
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_02_filled.png', fullPage: true});
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text.includes('登录') || text.includes('Login') || text.includes('登 录')) {
      console.log(`  Clicking button: "${text}"`);
      await btn.click();
      break;
    }
  }

  // Wait for navigation or dashboard
  console.log('[3/5] Waiting for login response...');
  await new Promise(r => setTimeout(r, 3000));
  console.log('  URL after login:', page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_03_after_login.png', fullPage: true});

  // Try to navigate to dashboard
  console.log('[4/5] Navigating to dashboard...');
  await page.goto('http://152.136.115.121/dashboard', {waitUntil: 'networkidle0', timeout: 30000}).catch(e => console.log('  Dashboard nav error:', e.message));
  await new Promise(r => setTimeout(r, 2000));
  console.log('  Dashboard URL:', page.url());
  await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/server_04_dashboard.png', fullPage: true});

  // Check API health
  console.log('[5/5] Checking /up health endpoint...');
  const resp = await page.goto('http://152.136.115.121/up', {waitUntil: 'networkidle0', timeout: 15000});
  console.log('  /up status:', resp.status());

  await browser.close();
  console.log('\n[DONE] E2E test complete.');
})().catch(e => {
  console.error('ERROR:', e);
  process.exit(1);
});
'''

# Write to a JS file and run with node
with open('.workbuddy/e2e_server.js', 'w', encoding='utf-8') as f:
    f.write(script)

# Run it
print("\n=== Running E2E test ===")
result = subprocess.run(
    ['node', '.workbuddy/e2e_server.js'],
    cwd='D:/work/website/OA',
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
