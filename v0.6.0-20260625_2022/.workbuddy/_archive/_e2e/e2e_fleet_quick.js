#!/usr/bin/env node
const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');
const BASE = 'http://152.136.115.121';
const SHOTS = 'D:/work/website/OA/.workbuddy/shots';
if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push('PAGE: ' + e.message));

  // 登录
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2' });
  await page.waitForSelector('button.login-btn');
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(location.pathname), { timeout: 15000 });
  await sleep(1000);

  // 去车辆档案, 截图
  await page.goto(BASE + '/vehicle/fleet', { waitUntil: 'networkidle2' });
  await sleep(2000);
  await page.screenshot({ path: path.join(SHOTS, '_fleet_with_quick.png'), fullPage: false });
  console.log('url:', page.url());

  // 检查列表是否真的有 4 个新列
  const headers = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.el-table__header-wrapper th')).map(t => t.innerText.trim());
  });
  console.log('table headers:', headers);

  // 找第一行 "保险" 列的 "详情" 按钮
  const insuranceBtn = await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (!rows[0]) return null;
    const cells = rows[0].querySelectorAll('td');
    for (const c of cells) {
      const b = c.querySelector('button');
      if (b && c.previousElementSibling?.innerText?.includes('车牌号') === false) {
        // 找列标题
      }
    }
    return null;
  });

  // 直接点第一行的"保险"列按钮
  const clicked = await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (!rows[0]) return 'no row';
    // 找所有列, 找到标题是"保险"的那一列
    const headers = document.querySelectorAll('.el-table__header-wrapper th .cell');
    let insuranceColIdx = -1, maintenanceColIdx = -1, dispatchColIdx = -1, fuelCardColIdx = -1;
    headers.forEach((h, i) => {
      const t = h.innerText.trim();
      if (t === '保险') insuranceColIdx = i;
      else if (t === '保养') maintenanceColIdx = i;
      else if (t === '调度') dispatchColIdx = i;
      else if (t === '油卡') fuelCardColIdx = i;
    });
    console.log('col indexes:', { insuranceColIdx, maintenanceColIdx, dispatchColIdx, fuelCardColIdx });
    if (insuranceColIdx < 0) return 'no insurance col';

    const cells = rows[0].querySelectorAll('td');
    const insBtn = cells[insuranceColIdx]?.querySelector('button');
    if (insBtn) {
      insBtn.click();
      return 'clicked insurance col idx=' + insuranceColIdx;
    }
    return 'no button in col ' + insuranceColIdx;
  });
  console.log('click result:', clicked);
  await sleep(3000);
  await page.screenshot({ path: path.join(SHOTS, '_fleet_quickclick.png') });
  console.log('url after click:', page.url());
  const body = (await page.evaluate(() => document.body.innerText)).slice(0, 300).replace(/\n/g, ' | ');
  console.log('body:', body);

  console.log('errs:', errs.length, errs.slice(0, 5));
  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
