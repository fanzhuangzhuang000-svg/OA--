#!/usr/bin/env node
/**
 * 项目详情 + 工单详情 真实点击 e2e
 * 1) 登录拿 token
 * 2) GET /api/projects 拿真实 ID
 * 3) GET /api/service-orders 拿真实 ID
 * 4) 启动浏览器，去详情页，捕获所有 console error / 500
 */
const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const BASE = 'http://152.136.115.121';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SHOTS = 'D:/work/website/OA/.workbuddy/shots';

if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, { recursive: true });

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function api(token, path) {
  const r = await fetch(BASE + path, { headers: { Authorization: 'Bearer ' + token, Accept: 'application/json' } });
  return r.json();
}

async function loginToken() {
  const r = await fetch(BASE + '/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'admin123' })
  });
  const j = await r.json();
  if (!j.data || !j.data.token) throw new Error('login: ' + JSON.stringify(j).slice(0, 200));
  return j.data.token;
}

(async () => {
  console.log('[1] login ...');
  const token = await loginToken();
  console.log('    token ok:', token.slice(0, 20) + '...');

  console.log('[2] fetch real project id and service order id ...');
  const projects = await api(token, '/api/projects?per_page=1');
  console.log('    projects response sample:', JSON.stringify(projects).slice(0, 200));
  const projList = (projects.data && projects.data.data) || projects.data || [];
  const projId = Array.isArray(projList) ? projList[0]?.id : null;
  console.log('    first project id =', projId, 'name =', projList[0]?.name || projList[0]?.project_name);

  const services = await api(token, '/api/service-orders?per_page=1');
  console.log('    service-orders response sample:', JSON.stringify(services).slice(0, 200));
  const svcList = (services.data && services.data.data) || services.data || [];
  const svcId = Array.isArray(svcList) ? svcList[0]?.id : null;
  console.log('    first service order id =', svcId, 'title =', svcList[0]?.title || svcList[0]?.order_no);

  // 同时直接试一下详情 API，看是否后端 500
  console.log('\n[3] direct API test on detail endpoints ...');
  if (projId) {
    const r = await fetch(BASE + '/api/projects/' + projId, { headers: { Authorization: 'Bearer ' + token } });
    console.log('    GET /api/projects/' + projId + ' → HTTP', r.status);
    const text = await r.text();
    console.log('    body sample:', text.slice(0, 400));
  }
  if (svcId) {
    const r = await fetch(BASE + '/api/service-orders/' + svcId, { headers: { Authorization: 'Bearer ' + token } });
    console.log('    GET /api/service-orders/' + svcId + ' → HTTP', r.status);
    const text = await r.text();
    console.log('    body sample:', text.slice(0, 400));
  }

  // 浏览器
  console.log('\n[4] launching chrome ...');
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const consoleErrs = [];
  const pageErrs = [];
  const failedRes = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrs.push(m.text()); });
  page.on('pageerror', e => pageErrs.push(e.message));
  page.on('response', r => { if (r.status() >= 400 && !r.url().includes('favicon')) failedRes.push(`HTTP ${r.status()} ${r.url()}`); });

  // 登录
  console.log('[5] browser login ...');
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => window.location.pathname === '/' || window.location.pathname === '/dashboard', { timeout: 15000 }).catch(() => {});
  await sleep(1000);
  console.log('    logged in, url =', page.url());

  // 项目详情
  if (projId) {
    console.log('\n[6] navigate to /project/' + projId);
    const before = { c: consoleErrs.length, p: pageErrs.length, r: failedRes.length };
    try {
      await page.goto(BASE + '/project/' + projId, { waitUntil: 'networkidle2', timeout: 20000 });
      await sleep(3000);
      const shot = path.join(SHOTS, '_detail_project_' + projId + '.png');
      await page.screenshot({ path: shot, fullPage: false });
      const bodyText = (await page.evaluate(() => document.body.innerText || '')).slice(0, 500);
      console.log('    shot:', shot);
      console.log('    body sample:', bodyText.slice(0, 300).replace(/\n/g, ' | '));
      const newC = consoleErrs.slice(before.c);
      const newP = pageErrs.slice(before.p);
      const newR = failedRes.slice(before.r);
      console.log('    new console errors:', newC.length, newC.slice(0, 3));
      console.log('    new page errors:', newP.length, newP.slice(0, 3));
      console.log('    new failed res:', newR.length, newR.slice(0, 5));
    } catch (e) {
      console.log('    FAILED:', e.message);
    }
  }

  // 工单详情
  if (svcId) {
    console.log('\n[7] navigate to /service/' + svcId);
    const before = { c: consoleErrs.length, p: pageErrs.length, r: failedRes.length };
    try {
      await page.goto(BASE + '/service/' + svcId, { waitUntil: 'networkidle2', timeout: 20000 });
      await sleep(3000);
      const shot = path.join(SHOTS, '_detail_service_' + svcId + '.png');
      await page.screenshot({ path: shot, fullPage: false });
      const bodyText = (await page.evaluate(() => document.body.innerText || '')).slice(0, 500);
      console.log('    shot:', shot);
      console.log('    body sample:', bodyText.slice(0, 300).replace(/\n/g, ' | '));
      const newC = consoleErrs.slice(before.c);
      const newP = pageErrs.slice(before.p);
      const newR = failedRes.slice(before.r);
      console.log('    new console errors:', newC.length, newC.slice(0, 3));
      console.log('    new page errors:', newP.length, newP.slice(0, 3));
      console.log('    new failed res:', newR.length, newR.slice(0, 5));
    } catch (e) {
      console.log('    FAILED:', e.message);
    }
  }

  console.log('\n=== ALL CONSOLE ERRORS ===');
  [...new Set(consoleErrs)].slice(0, 20).forEach(e => console.log('  •', e.slice(0, 200)));
  console.log('\n=== ALL PAGE ERRORS ===');
  [...new Set(pageErrs)].slice(0, 20).forEach(e => console.log('  •', e.slice(0, 200)));
  console.log('\n=== ALL FAILED RESOURCES ===');
  [...new Set(failedRes)].slice(0, 30).forEach(e => console.log('  •', e.slice(0, 200)));

  await browser.close();
  console.log('\nDONE');
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
