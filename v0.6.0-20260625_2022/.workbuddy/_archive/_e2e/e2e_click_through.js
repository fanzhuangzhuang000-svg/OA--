#!/usr/bin/env node
/**
 * 模拟「点开列表 → 点进详情」真实点击路径
 */
const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const BASE = 'http://152.136.115.121';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SHOTS = 'D:/work/website/OA/.workbuddy/shots';
if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const errs = { console: [], page: [], failed: [] };
  page.on('console', m => { if (m.type() === 'error') errs.console.push(m.text()); });
  page.on('pageerror', e => errs.page.push(e.message));
  page.on('response', r => { if (r.status() >= 400 && !r.url().includes('favicon')) errs.failed.push(`HTTP ${r.status()} ${r.url()}`); });

  // 登录
  console.log('login...');
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(window.location.pathname), { timeout: 15000 });
  await sleep(1000);

  // 项目列表
  console.log('\n--- 项目列表 ---');
  errs.console = []; errs.page = []; errs.failed = [];
  await page.goto(BASE + '/project/list', { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(3000);
  await page.screenshot({ path: SHOTS + '/list_project.png' });
  // 找第一行 "查看" / "详情" 链接
  const projectLink = await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (!rows.length) return null;
    const firstRow = rows[0];
    const links = firstRow.querySelectorAll('a, button, .el-button');
    for (const a of links) {
      const t = (a.textContent || '').trim();
      if (t.includes('详情') || t.includes('查看') || t.includes('更多') || t.includes('...')) {
        return { text: t, tag: a.tagName };
      }
    }
    // 没找到 - 直接取第一行第一列的项目名
    return { text: 'NO_LINK', tag: 'none', firstCell: firstRow.querySelector('td')?.innerText || '' };
  });
  console.log('  first row link:', projectLink);
  console.log('  errs after list:', errs.failed.length, errs.failed.slice(0, 3));

  // 点击第一行的项目名（很多表格点击名字就进详情）
  console.log('\n--- 点击第一行项目名 ---');
  errs.console = []; errs.page = []; errs.failed = [];
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (rows[0]) {
      // 找第一行里带链接的元素
      const a = rows[0].querySelector('a') || rows[0].querySelector('.el-link') || rows[0].querySelector('[class*="link"]');
      if (a) { a.click(); return; }
      // 或者点 "查看" / "详情" 按钮
      const btns = rows[0].querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('详情') || b.textContent.includes('查看') || b.textContent.includes('更多')) { b.click(); return; }
      }
    }
  });
  await sleep(3000);
  console.log('  url after click:', page.url());
  await page.screenshot({ path: SHOTS + '/list_project_click.png' });
  const projectDetailBody = (await page.evaluate(() => document.body.innerText || '')).slice(0, 300).replace(/\n/g, ' | ');
  console.log('  body sample:', projectDetailBody);
  console.log('  errs:', errs.failed.length, errs.failed.slice(0, 5));
  console.log('  console errs:', errs.console.length, errs.console.slice(0, 3));
  console.log('  page errs:', errs.page.length, errs.page.slice(0, 3));

  // 维修工单列表
  console.log('\n--- 工单列表 ---');
  errs.console = []; errs.page = []; errs.failed = [];
  await page.goto(BASE + '/service/orders', { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(3000);
  await page.screenshot({ path: SHOTS + '/list_service.png' });
  const serviceLink = await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (!rows.length) return { count: 0 };
    return { count: rows.length, firstCell: rows[0].querySelector('td')?.innerText || '' };
  });
  console.log('  service rows:', serviceLink);
  console.log('  errs after service list:', errs.failed.length, errs.failed.slice(0, 5));

  // 点击第一行
  console.log('\n--- 点击工单第一行 ---');
  errs.console = []; errs.page = []; errs.failed = [];
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row');
    if (rows[0]) {
      const a = rows[0].querySelector('a') || rows[0].querySelector('.el-link');
      if (a) { a.click(); return; }
      const btns = rows[0].querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('详情') || b.textContent.includes('查看') || b.textContent.includes('更多')) { b.click(); return; }
      }
    }
  });
  await sleep(3000);
  console.log('  url after click:', page.url());
  await page.screenshot({ path: SHOTS + '/list_service_click.png' });
  const serviceDetailBody = (await page.evaluate(() => document.body.innerText || '')).slice(0, 300).replace(/\n/g, ' | ');
  console.log('  body sample:', serviceDetailBody);
  console.log('  errs:', errs.failed.length, errs.failed.slice(0, 5));
  console.log('  console errs:', errs.console.length, errs.console.slice(0, 3));
  console.log('  page errs:', errs.page.length, errs.page.slice(0, 3));

  // 汇总
  console.log('\n=== ALL FAILED RESOURCES (entire session) ===');
  // 重置收集
  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
