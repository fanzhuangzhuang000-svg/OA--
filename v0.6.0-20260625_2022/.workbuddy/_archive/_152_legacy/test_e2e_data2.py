"""
Final E2E test: visit each module and capture screenshot + data summary.
"""
import subprocess
import shutil

script = r'''const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1080});

  const errors = [];
  page.on('response', resp => {
    const url = resp.url();
    if (url.includes('152.136.115.121/api/') && resp.status() >= 400) {
      errors.push({status: resp.status(), url: url.replace('http://152.136.115.121', '')});
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

  const modules = [
    { name: '工作台',     path: '/dashboard',          screenshot: 'dash_01_work' },
    { name: '数据大屏',   path: '/screen',             screenshot: 'dash_02_screen' },
    { name: '考勤',       path: '/attendance/overview',screenshot: 'dash_03_attendance' },
    { name: '员工',       path: '/employee/list',      screenshot: 'dash_04_employee' },
    { name: '客户',       path: '/customer/list',      screenshot: 'dash_05_customer' },
    { name: '项目',       path: '/project/list',       screenshot: 'dash_06_project' },
    { name: '售后工单',   path: '/service/orders',     screenshot: 'dash_07_service' },
    { name: '维保合同',   path: '/service/contract',   screenshot: 'dash_08_maintenance' },
    { name: '报销',       path: '/expense/list',       screenshot: 'dash_09_expense' },
    { name: '车辆',       path: '/vehicle/fleet',      screenshot: 'dash_10_vehicle' },
    { name: '库存',       path: '/inventory/stock',    screenshot: 'dash_11_inventory' },
    { name: '财务',       path: '/finance/receivable', screenshot: 'dash_12_finance' },
    { name: '网盘',       path: '/disk/list',          screenshot: 'dash_13_disk' },
    { name: '知识库',     path: '/knowledge/list',     screenshot: 'dash_14_knowledge' },
    { name: '消息',       path: '/message',            screenshot: 'dash_15_message' },
    { name: '系统设置',   path: '/settings/organization', screenshot: 'dash_16_settings' },
  ];

  console.log('');
  console.log('[2/16] Testing ' + modules.length + ' modules...');
  for (const m of modules) {
    errors.length = 0;
    try {
      await page.goto('http://152.136.115.121' + m.path, {waitUntil: 'networkidle0', timeout: 15000});
      await new Promise(r => setTimeout(r, 2000));

      const stats = await page.evaluate(() => {
        const text = document.body.textContent;
        const isEmpty = text.includes('暂无') || text.includes('没有数据') || text.includes('共 0');
        const hasError = text.includes('Server Error') || text.includes('500');
        return { isEmpty, hasError, bodyLen: text.length };
      });

      const ok = !stats.hasError && errors.length === 0;
      const status = !ok ? 'FAIL' : (stats.isEmpty ? 'EMPTY' : 'OK');
      console.log('  ' + status + ' | ' + m.name + ' (' + m.path + ')');

      await page.screenshot({path: 'D:/work/website/OA/.workbuddy/screenshots/' + m.screenshot + '.png', fullPage: false});
    } catch (e) {
      console.log('  NAV_FAIL | ' + m.name + ' | ' + e.message);
    }
  }

  console.log('');
  console.log('[DONE] Total API errors: ' + errors.length);
  if (errors.length > 0) {
    errors.forEach(e => console.log('  ' + e.status + ' ' + e.url));
  }

  await browser.close();
})().catch(e => {
  console.error('ERROR: ' + e.message);
  process.exit(1);
});
'''

with open('D:/work/website/OA/.workbuddy/e2e_data2.js', 'w', encoding='utf-8') as f:
    f.write(script)

import shutil
shutil.copy('D:/work/website/OA/.workbuddy/e2e_data2.js', 'C:/Users/MRG/.workbuddy/binaries/node/workspace/e2e_data2.js')

result = subprocess.run(
    ['C:/Users/MRG/.workbuddy/binaries/node/versions/22.22.2/node.exe', 'e2e_data2.js'],
    cwd='C:/Users/MRG/.workbuddy/binaries/node/workspace',
    capture_output=True,
    text=True,
    timeout=300
)
print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr[:3000])
