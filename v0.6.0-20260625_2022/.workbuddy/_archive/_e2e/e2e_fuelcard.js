#!/usr/bin/env node
/**
 * 油卡 + 车辆详情整合 e2e
 */
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

  const consoleErrs = [];
  const pageErrs = [];
  const failedRes = [];
  const apiCalls = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrs.push(m.text()); });
  page.on('pageerror', e => pageErrs.push(e.message));
  page.on('request', req => { if (req.url().includes('/api/') && !req.url().includes('auth/login')) apiCalls.push(req.method() + ' ' + req.url().replace(BASE, '')); });
  page.on('response', r => { if (r.url().includes('/api/') && r.status() >= 400) failedRes.push(`HTTP ${r.status()} ${r.url().replace(BASE, '')}`); });

  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(location.pathname), { timeout: 15000 });
  await sleep(1000);
  console.log('[login] ok');

  // 1) 油卡管理页
  console.log('\n=== 油卡管理 ===');
  apiCalls.length = 0;
  consoleErrs.length = 0; pageErrs.length = 0; failedRes.length = 0;
  await page.goto(BASE + '/vehicle/fuel-card', { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(3000);
  await page.screenshot({ path: path.join(SHOTS, '_vehicle_fuelcard.png'), fullPage: false });
  const body1 = (await page.evaluate(() => document.body.innerText)).slice(0, 500).replace(/\n/g, ' | ');
  console.log('  body:', body1);
  console.log('  API calls:', apiCalls.length, apiCalls.slice(0, 10));
  console.log('  console errs:', consoleErrs.length, consoleErrs.slice(0, 3));
  console.log('  page errs:', pageErrs.length, pageErrs.slice(0, 3));
  console.log('  failed res:', failedRes.length, failedRes.slice(0, 3));

  // 2) 车辆档案 → 点击查看 (打开整合详情)
  console.log('\n=== 车辆档案 → 详情对话框 ===');
  apiCalls.length = 0;
  consoleErrs.length = 0; pageErrs.length = 0; failedRes.length = 0;
  await page.goto(BASE + '/vehicle/fleet', { waitUntil: 'networkidle2' });
  await sleep(2000);
  // 找「查看」按钮
  const viewBtn = await page.evaluateHandle(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (rows[0]) {
      const btns = rows[0].querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('查看')) return b;
      }
    }
    return null;
  });
  if (viewBtn && viewBtn.asElement()) {
    await viewBtn.asElement().click();
    await sleep(3000);
    await page.screenshot({ path: path.join(SHOTS, '_vehicle_detail_insurance.png') });
    console.log('  dialog opened, url =', page.url());
    // 切到油卡 tab
    const fuelTab = await page.evaluateHandle(() => {
      const tabs = document.querySelectorAll('.el-tabs__item');
      for (const t of tabs) {
        if (t.textContent.includes('油卡')) return t;
      }
      return null;
    });
    if (fuelTab && fuelTab.asElement()) {
      await fuelTab.asElement().click();
      await sleep(2000);
      await page.screenshot({ path: path.join(SHOTS, '_vehicle_detail_fuelcard.png') });
      const tabBody = (await page.evaluate(() => document.body.innerText)).slice(0, 600).replace(/\n/g, ' | ');
      console.log('  fuel tab body:', tabBody);
    } else {
      console.log('  ❌ NOT FOUND 油卡 tab');
    }
    console.log('  API calls:', apiCalls.length, apiCalls.slice(0, 10));
    console.log('  console errs:', consoleErrs.length, consoleErrs.slice(0, 3));
    console.log('  page errs:', pageErrs.length, pageErrs.slice(0, 3));
    console.log('  failed res:', failedRes.length, failedRes.slice(0, 3));
  } else {
    console.log('  ❌ NOT FOUND 查看 button');
  }

  console.log('\n=== ALL CONSOLE ERRORS ===');
  [...new Set(consoleErrs)].slice(0, 10).forEach(e => console.log('  •', e.slice(0, 150)));
  console.log('\n=== ALL FAILED RESOURCES ===');
  [...new Set(failedRes)].slice(0, 10).forEach(e => console.log('  •', e));

  await browser.close();
  console.log('\nDONE');
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
