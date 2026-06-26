#!/usr/bin/env node
/**
 * 车辆保险 + 保养 真实点击 e2e
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

  // 登录
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(location.pathname), { timeout: 15000 });
  await sleep(1000);
  console.log('[login] ok');

  // 1) 保险页
  console.log('\n=== 保险记录 ===');
  apiCalls.length = 0;
  consoleErrs.length = 0;
  pageErrs.length = 0;
  failedRes.length = 0;
  await page.goto(BASE + '/vehicle/insurance', { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(3000);
  await page.screenshot({ path: path.join(SHOTS, '_vehicle_insurance.png'), fullPage: false });
  const body1 = (await page.evaluate(() => document.body.innerText)).slice(0, 400).replace(/\n/g, ' | ');
  console.log('  body:', body1);
  console.log('  API calls:', apiCalls.length, apiCalls.slice(0, 8));
  console.log('  console errs:', consoleErrs.length, consoleErrs.slice(0, 3));
  console.log('  page errs:', pageErrs.length, pageErrs.slice(0, 3));
  console.log('  failed res:', failedRes.length, failedRes.slice(0, 3));

  // 2) 保养页
  console.log('\n=== 保养记录 ===');
  apiCalls.length = 0;
  consoleErrs.length = 0;
  pageErrs.length = 0;
  failedRes.length = 0;
  await page.goto(BASE + '/vehicle/maintenance', { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(3000);
  await page.screenshot({ path: path.join(SHOTS, '_vehicle_maintenance.png'), fullPage: false });
  const body2 = (await page.evaluate(() => document.body.innerText)).slice(0, 400).replace(/\n/g, ' | ');
  console.log('  body:', body2);
  console.log('  API calls:', apiCalls.length, apiCalls.slice(0, 8));
  console.log('  console errs:', consoleErrs.length, consoleErrs.slice(0, 3));
  console.log('  page errs:', pageErrs.length, pageErrs.slice(0, 3));
  console.log('  failed res:', failedRes.length, failedRes.slice(0, 3));

  // 3) 打开新增保险对话框
  console.log('\n=== 点击新增保险 ===');
  apiCalls.length = 0;
  consoleErrs.length = 0;
  await page.goto(BASE + '/vehicle/insurance', { waitUntil: 'networkidle2' });
  await sleep(2000);
  // 找「新增保险」按钮
  const newBtn = await page.evaluateHandle(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('新增保险')) return b;
    }
    return null;
  });
  if (newBtn) {
    await newBtn.asElement().click();
    await sleep(1500);
    await page.screenshot({ path: path.join(SHOTS, '_insurance_dialog.png') });
    const dialogText = (await page.evaluate(() => {
      const dlg = document.querySelector('.el-dialog');
      return dlg ? dlg.innerText.slice(0, 200).replace(/\n/g, ' | ') : 'NO DIALOG';
    }));
    console.log('  dialog visible:', dialogText);
  } else {
    console.log('  ❌ NOT FOUND 新增保险 button');
  }

  console.log('\n=== ALL CONSOLE ERRORS ===');
  [...new Set(consoleErrs)].slice(0, 10).forEach(e => console.log('  •', e.slice(0, 150)));
  console.log('\n=== ALL FAILED RESOURCES ===');
  [...new Set(failedRes)].slice(0, 10).forEach(e => console.log('  •', e));

  await browser.close();
  console.log('\nDONE');
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
