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

  // 去车辆档案
  await page.goto(BASE + '/vehicle/fleet', { waitUntil: 'networkidle2' });
  await sleep(2000);

  // 遍历每行, 抓"查看"按钮点开看 tab 计数
  const rowsInfo = await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    const data = [];
    rows.forEach((row, i) => {
      const plate = row.querySelector('td:nth-child(1)')?.innerText?.trim();
      const btns = row.querySelectorAll('button');
      let viewBtn = null;
      for (const b of btns) if (b.innerText.includes('查看')) viewBtn = b;
      data.push({ i, plate, hasView: !!viewBtn });
    });
    return data;
  });
  console.log('rows:', rowsInfo);

  for (const info of rowsInfo) {
    // 重新点查看 (因为 dialog 是单例, 之前打开要关)
    await page.goto(BASE + '/vehicle/fleet', { waitUntil: 'networkidle2' });
    await sleep(1500);
    const opened = await page.evaluate((i) => {
      const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
      if (!rows[i]) return false;
      const btns = rows[i].querySelectorAll('button');
      for (const b of btns) {
        if (b.innerText.includes('查看')) { b.click(); return true; }
      }
      return false;
    }, info.i);
    if (!opened) { console.log('skip', info.plate); continue; }
    await sleep(2500);
    // 抓所有 tab 标题
    const tabInfo = await page.evaluate(() => {
      const tabs = document.querySelectorAll('.el-tabs__item');
      return Array.from(tabs).map(t => t.innerText.trim());
    });
    console.log(info.plate, '→ tabs:', tabInfo);
    // 切到每个 tab 截图
    for (let t = 0; t < tabInfo.length; t++) {
      await page.evaluate((idx) => {
        const tabs = document.querySelectorAll('.el-tabs__item');
        if (tabs[idx]) tabs[idx].click();
      }, t);
      await sleep(1500);
      const tabBody = await page.evaluate(() => {
        const pane = document.querySelector('.el-tab-pane:not([style*="display: none"])');
        return pane ? pane.innerText.slice(0, 200).replace(/\n/g, ' | ') : '(empty pane)';
      });
      const safeName = (info.plate || 'row').replace(/[\s\/]/g, '_');
      await page.screenshot({ path: path.join(SHOTS, `_detail_${safeName}_tab${t}.png`) });
      console.log(`  tab${t} (${tabInfo[t]}):`, tabBody);
    }
  }
  console.log('all errs:', errs.length, errs.slice(0, 5));
  await browser.close();
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
