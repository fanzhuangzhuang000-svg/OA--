// E2E压力测试: 跑遍所有菜单, 截图+记录错误
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const BASE = 'http://172.20.0.139:3000';
const SHOTS = path.join(__dirname, 'shots');
if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, {recursive: true});

const errors = [];
const success = [];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({width: 1440, height: 900});
  
  // 捕获console错误和网络错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push({type: 'console', url: page.url(), text: msg.text()});
    }
  });
  page.on('pageerror', err => {
    errors.push({type: 'pageerror', url: page.url(), text: err.message});
  });
  page.on('response', resp => {
    if (resp.status() >= 400) {
      errors.push({type: 'http', url: page.url(), api: resp.url(), status: resp.status()});
    }
  });
  
  // 1. 登录
  console.log('登录中...');
  await page.goto(BASE, {waitUntil: 'networkidle0', timeout: 30000}).catch(e => errors.push({type: 'nav', text: e.message}));
  await page.screenshot({path: path.join(SHOTS, '01_login.png')});
  
  // 输入账号密码
  await page.waitForSelector('input[placeholder*="账号"], input[type="text"]', {timeout: 10000}).catch(() => {});
  const inputs = await page.$$('input');
  if (inputs.length >= 2) {
    await inputs[0].click({clickCount: 3});
    await inputs[0].type('admin');
    await inputs[1].click({clickCount: 3});
    await inputs[1].type('admin123');
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const txt = await page.evaluate(el => el.textContent, btn);
      if (txt && txt.includes('登录')) { await btn.click(); break; }
    }
  }
  await new Promise(r => setTimeout(r, 3000));
  await page.screenshot({path: path.join(SHOTS, '02_after_login.png')});
  
  // 2. 遍历所有菜单
  const menuItems = await page.$$('.el-menu-item, .menu-item, [class*="menu"] li, aside a');
  console.log(`发现 ${menuItems.length} 个菜单项`);
  
  for (let i = 0; i < Math.min(menuItems.length, 50); i++) {
    try {
      const txt = await page.evaluate(el => el.textContent.trim(), menuItems[i]).catch(() => '');
      if (!txt || txt.length > 20) continue;
      await menuItems[i].click().catch(() => {});
      await new Promise(r => setTimeout(r, 1500));
      await page.screenshot({path: path.join(SHOTS, `menu_${i}_${txt}.png`)});
      success.push(txt);
      console.log(`✓ ${txt}`);
    } catch (e) {
      errors.push({type: 'menu', text: e.message});
    }
  }
  
  console.log(`\n成功访问: ${success.length} 个菜单`);
  console.log(`错误数: ${errors.length}`);
  
  // 输出错误报告
  fs.writeFileSync(path.join(__dirname, 'e2e_errors.json'), JSON.stringify(errors, null, 2));
  
  await browser.close();
})().catch(e => console.error('FATAL:', e));
