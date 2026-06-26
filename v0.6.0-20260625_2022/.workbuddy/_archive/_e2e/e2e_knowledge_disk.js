const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  page.on('response', r => { if (r.status() >= 400 && !r.url().includes('favicon')) errs.push('HTTP ' + r.status() + ' ' + r.url()); });

  await page.goto('http://152.136.115.121/login', { waitUntil: 'networkidle2' });
  await page.waitForSelector('button.login-btn');
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(location.pathname), { timeout: 15000 });
  await sleep(1000);

  // 知识库
  errs.length = 0;
  await page.goto('http://152.136.115.121/knowledge/list', { waitUntil: 'networkidle2' });
  await sleep(3000);
  await page.screenshot({ path: 'D:/work/website/OA/.workbuddy/shots/_knowledge_list.png' });
  const body = (await page.evaluate(() => document.body.innerText)).slice(0, 400).replace(/\n/g, ' | ');
  console.log('knowledge body:', body);
  console.log('knowledge errs:', errs.length, errs.slice(0, 3));

  // 网盘
  errs.length = 0;
  await page.goto('http://152.136.115.121/disk', { waitUntil: 'networkidle2' });
  await sleep(3000);
  await page.screenshot({ path: 'D:/work/website/OA/.workbuddy/shots/_disk_list.png' });
  const body2 = (await page.evaluate(() => document.body.innerText)).slice(0, 300).replace(/\n/g, ' | ');
  console.log('\ndisk body:', body2);
  console.log('disk errs:', errs.length, errs.slice(0, 3));

  await browser.close();
  console.log('\nDONE');
})().catch(e => console.error(e));
