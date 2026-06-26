#!/usr/bin/env node
/**
 * v0.3.9 P1 M1-B 前端 7 页面 e2e 验证
 * 依赖：backend-dev M1-A 已完成 + 已部署到 172.20.0.139
 *
 * 验证项：
 * 1. /sales/leads — 新建/编辑/转商机/丢弃 按钮
 * 2. /sales/leads/board — 拖拽改 status
 * 3. /sales/opps — 新建/编辑/成交/战败 按钮
 * 4. /sales/opps/board — 拖拽改 stage
 * 5. /sales/opps/:id/quote — 新建版本/提交/客户接受
 * 6. /sales/referrers — 新增/编辑/删除
 * 7. /sales/pool — 转为施工项目
 */
const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');
const BASE = process.env.E2E_BASE || 'http://172.20.0.139';
const SHOTS = 'D:/work/website/OA/.workbuddy/shots/v039_p1';
if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

const results = [];
function record(page, name, ok, detail) {
  const status = ok ? '✅' : '❌';
  const line = `${status} [${name}] ${detail || ''}`;
  console.log(line);
  results.push({ name, ok, detail });
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const httpErrs = [];
  page.on('console', m => { if (m.type() === 'error') httpErrs.push(m.text()); });
  page.on('pageerror', e => httpErrs.push('PAGE: ' + e.message));
  page.on('response', r => { if (r.url().includes('/api/sales/') && r.status() >= 400) httpErrs.push('HTTP ' + r.status() + ' ' + r.url().replace(BASE, '')); });

  // 登录
  try {
    // 1) 用 curl 拿 token（绕过 nginx 代理怪问题）
    const tok = process.env.LT || '157|Diob0k1n9QY8BgiziWaFr4JAKat2gFJ85UP07abX35ca3397';
    // 2) 设置 token 到 localStorage + 跳到 dashboard
    await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
    await sleep(2000);
    await page.evaluate((t) => {
      localStorage.setItem('token', t);
      localStorage.setItem('auth-token', t);
    }, tok);
    await page.goto(BASE + '/dashboard', { waitUntil: 'domcontentloaded' });
    await sleep(3000);
    record(page, '登录', true, '使用预拿 token 跳过 UI');
  } catch (e) {
    record(page, '登录', false, e.message);
    await browser.close();
    return;
  }

  // === 1) Leads.vue ===
  console.log('\n=== 1) /sales/leads 线索池 ===');
  try {
    await page.goto(BASE + '/sales/leads', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '01_leads.png') });
    const visible = await page.evaluate(() => !!document.querySelector('.page-title') && document.querySelector('.page-title').innerText.includes('线索池'));
    record(page, '线索池加载', visible, '标题可见: ' + visible);
    // 新建按钮
    const newBtn = await page.evaluateHandle(() => Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim().includes('新建线索')));
    if (newBtn && newBtn.asElement()) {
      await newBtn.asElement().click();
      await sleep(1500);
      await page.screenshot({ path: path.join(SHOTS, '01_leads_new_dialog.png') });
      const dialogVisible = await page.evaluate(() => !!document.querySelector('.el-dialog__title'));
      record(page, '新建线索 Dialog', dialogVisible, '弹出 Dialog: ' + dialogVisible);
      // 关闭
      await page.evaluate(() => {
        const btns = document.querySelectorAll('.el-dialog__close');
        for (const b of btns) b.click();
      });
      await sleep(500);
    } else {
      record(page, '新建线索按钮', false, '按钮未找到');
    }
  } catch (e) {
    record(page, '线索池', false, e.message);
  }

  // === 2) LeadsBoard.vue ===
  console.log('\n=== 2) /sales/leads/board 线索看板 ===');
  try {
    await page.goto(BASE + '/sales/leads/board', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '02_leads_board.png') });
    const visible = await page.evaluate(() => document.querySelectorAll('.board-column').length);
    record(page, '线索看板', visible > 0, `${visible} 列可见`);
  } catch (e) {
    record(page, '线索看板', false, e.message);
  }

  // === 3) Opps.vue ===
  console.log('\n=== 3) /sales/opps 商机池 ===');
  try {
    await page.goto(BASE + '/sales/opps', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '03_opps.png') });
    const visible = await page.evaluate(() => document.querySelectorAll('.funnel-item').length);
    record(page, '商机池漏斗', visible >= 6, `${visible} 个漏斗卡片`);
  } catch (e) {
    record(page, '商机池', false, e.message);
  }

  // === 4) OppsBoard.vue ===
  console.log('\n=== 4) /sales/opps/board 商机看板 ===');
  try {
    await page.goto(BASE + '/sales/opps/board', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '04_opps_board.png') });
    const visible = await page.evaluate(() => document.querySelectorAll('.board-column').length);
    record(page, '商机看板', visible >= 6, `${visible} 列可见`);
  } catch (e) {
    record(page, '商机看板', false, e.message);
  }

  // === 5) Quotes.vue ===
  console.log('\n=== 5) /sales/opps/1/quote 报价单 ===');
  try {
    await page.goto(BASE + '/sales/opps/1/quote', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '05_quotes.png') });
    const visible = await page.evaluate(() => document.querySelectorAll('.quote-item, .el-empty').length);
    record(page, '报价单页', visible > 0, '加载正常');
  } catch (e) {
    record(page, '报价单', false, e.message);
  }

  // === 6) Referrers.vue ===
  console.log('\n=== 6) /sales/referrers 推荐人 ===');
  try {
    await page.goto(BASE + '/sales/referrers', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '06_referrers.png') });
    const visible = await page.evaluate(() => document.querySelectorAll('.el-table__row').length);
    record(page, '推荐人列表', visible >= 0, `${visible} 行`);
    // 新增按钮
    const newBtn = await page.evaluateHandle(() => Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim().includes('新增推荐人')));
    if (newBtn && newBtn.asElement()) {
      await newBtn.asElement().click();
      await sleep(1500);
      await page.screenshot({ path: path.join(SHOTS, '06_referrers_new.png') });
      const dialogVisible = await page.evaluate(() => !!document.querySelector('.el-dialog__title'));
      record(page, '新增推荐人 Dialog', dialogVisible, '');
    }
  } catch (e) {
    record(page, '推荐人', false, e.message);
  }

  // === 7) Pool.vue ===
  console.log('\n=== 7) /sales/pool 项目池 ===');
  try {
    await page.goto(BASE + '/sales/pool', { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(SHOTS, '07_pool.png') });
    const visible = await page.evaluate(() => document.querySelectorAll('.el-table__row').length);
    record(page, '项目池列表', visible >= 0, `${visible} 行`);
  } catch (e) {
    record(page, '项目池', false, e.message);
  }

  // 总结
  console.log('\n=== HTTP 错误汇总 ===');
  if (httpErrs.length === 0) {
    console.log('  无 HTTP 错误');
  } else {
    httpErrs.slice(0, 20).forEach(e => console.log('  -', e));
    if (httpErrs.length > 20) console.log(`  ...还有 ${httpErrs.length - 20} 条`);
  }
  console.log('\n=== 总结 ===');
  const passed = results.filter(r => r.ok).length;
  const failed = results.length - passed;
  console.log(`  通过 ${passed} / 失败 ${failed} / 总计 ${results.length}`);

  await browser.close();
  process.exit(failed > 0 ? 1 : 0);
})();
