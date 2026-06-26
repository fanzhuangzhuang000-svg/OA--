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

  // 关键: 监听所有 API 请求，打印 URL
  page.on('request', req => {
    if (req.url().includes('/api/')) {
      console.log('  REQ:', req.method(), req.url());
    }
  });
  page.on('response', r => {
    if (r.url().includes('/api/') && r.status() >= 400) {
      console.log('  RESP ERR:', r.status(), r.url());
    }
  });

  await page.goto('http://152.136.115.121/login', { waitUntil: 'networkidle2' });
  await page.waitForSelector('button.login-btn');
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(location.pathname), { timeout: 15000 });
  await sleep(1000);

  // 模拟用户的真实点击路径: 项目列表 → 详情
  console.log('\n=== 项目列表 ===');
  await page.goto('http://152.136.115.121/project/list', { waitUntil: 'networkidle2' });
  await sleep(2000);

  console.log('\n=== 点击「查看」按钮 ===');
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (rows[0]) {
      const btns = rows[0].querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('查看') || b.textContent.includes('详情')) { b.click(); break; }
      }
    }
  });
  await sleep(3000);

  // 服务: 列表 → 详情
  console.log('\n=== 工单列表 ===');
  await page.goto('http://152.136.115.121/service/orders', { waitUntil: 'networkidle2' });
  await sleep(2000);

  console.log('\n=== 点击工单查看 ===');
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (rows[0]) {
      const btns = rows[0].querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('查看') || b.textContent.includes('详情')) { b.click(); break; }
      }
    }
  });
  await sleep(3000);

  await browser.close();
  console.log('\nDONE');
})().catch(e => console.error(e));
