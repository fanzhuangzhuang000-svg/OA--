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
    const url = resp.url();
    if (url.includes('152.136.115.121/api/') && resp.status() < 400) {
      apiCalls.push({status: resp.status(), url: url.replace('http://152.136.115.121', '')});
    } else if (url.includes('152.136.115.121/api/') && resp.status() >= 400) {
      console.log('  [ERROR] ' + resp.status() + ' ' + url.replace('http://152.136.115.121', ''));
    }
  });
  page.on('pageerror', err => console.log('  [PAGEERROR] ' + err.message));

  console.log('[1/16] Login...');
  await page.goto('http://152.136.115.121/login', {waitUntil: 'networkidle0', timeout: 30000});
  await new Promise(r => setTimeout(r, 1000));
  const inputs = await page.$$('input');
  if (inputs.length >= 2) {
    await inputs[1].focus();
    await page.keyboard.press('Enter');
  }
  await new Promise(r => setTimeout(r, 4000));
  console.log('  URL: ' + page.url());

  // Test each module
  const modules = [
    { name: '工作台 (Dashboard)',   path: '/dashboard',          wait: 3000 },
    { name: '数据大屏 (Screen)',     path: '/screen',             wait: 3000 },
    { name: '考勤 (Attendance)',     path: '/attendance/overview',wait: 2000 },
    { name: '员工 (Employees)',      path: '/employee/list',      wait: 2000 },
    { name: '客户 (Customers)',      path: '/customer/list',      wait: 2000 },
    { name: '项目 (Projects)',       path: '/project/list',       wait: 2000 },
    { name: '售后 (Service Orders)', path: '/service/orders',     wait: 2000 },
    { name: '报销 (Expenses)',       path: '/expense/list',       wait: 2000 },
    { name: '车辆 (Vehicles)',       path: '/vehicle/list',       wait: 2000 },
    { name: '库存 (Inventory)',      path: '/inventory/list',     wait: 2000 },
    { name: '财务 (Finance)',        path: '/finance/receivables',wait: 2000 },
    { name: '网盘 (Disk)',           path: '/disk/list',          wait: 2000 },
    { name: '知识库 (Knowledge)',    path: '/knowledge/list',     wait: 2000 },
    { name: '消息 (Messages)',       path: '/message',            wait: 2000 },
    { name: '系统设置 (Settings)',   path: '/settings/organization', wait: 2000 },
  ];

  console.log('');
  console.log('[2/16] Testing all modules...');
  for (const m of modules) {
    apiCalls.length = 0;
    try {
      await page.goto('http://152.136.115.121' + m.path, {waitUntil: 'networkidle0', timeout: 15000});
      await new Promise(r => setTimeout(r, m.wait));

      // Check for empty data
      const stats = await page.evaluate(() => {
        const text = document.body.textContent;
        return {
          hasError: text.includes('Server Error') || text.includes('500'),
          hasLoadFailed: text.includes('加载失败'),
          hasEmptyState: text.includes('暂无') || text.includes('没有数据') || text.includes('共 0'),
          bodyLength: text.length,
          bodyText: text.substring(0, 200)
        };
      });

      const errorCount = apiCalls.filter(c => c.status >= 400).length;
      const dataCount = apiCalls.filter(c => c.status < 400).length;
      const status = (stats.hasError || errorCount > 0) ? 'FAIL' :
                     (!stats.hasEmptyState && dataCount > 0) ? 'OK' : 'EMPTY';
      console.log('  ' + status + ' | ' + m.name + ' | API: ' + dataCount + ' ok, ' + errorCount + ' err | ' + stats.bodyText.substring(0, 80).replace(/\\s+/g, ' '));

      await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/e2e_' + m.path.replace(/[\\/:]/g, '_') + '.png', fullPage: false});
    } catch (e) {
      console.log('  NAV_FAIL | ' + m.name + ' | ' + e.message);
    }
  }

  await browser.close();
  console.log('');
  console.log('[DONE]');
})().catch(e => {
  console.error('ERROR: ' + e.message);
  process.exit(1);
});
