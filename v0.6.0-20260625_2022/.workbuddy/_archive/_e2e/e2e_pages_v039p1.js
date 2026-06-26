#!/usr/bin/env node
/**
 * v0.3.9 P1 前端 7 页面 puppeteer 验证 (v2 - 用实际可用路径)
 * 实际可用路径: /sales/leads, /sales/leads/board, /sales/opps, /sales/opps/board,
 *              /opp/:id/quote (报价单), /sales/referrers, /project/pool (项目池)
 */
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const BASE = 'http://172.20.0.139:3000';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SHOTS_DIR = 'D:/work/website/OA/.workbuddy/shots/v039p1';

if (!fs.existsSync(SHOTS_DIR)) {
  fs.mkdirSync(SHOTS_DIR, { recursive: true });
}

// 用实际存在的页面 (id 1 假定存在)
const PAGES = [
  { p: '/sales/leads', title: '线索池', buttons: ['新建线索', '转商机', '丢弃'] },
  { p: '/sales/leads/board', title: '线索看板', buttons: [] },
  { p: '/sales/opps', title: '商机池', buttons: ['新建商机', '成交', '战败'] },
  { p: '/sales/opps/board', title: '商机看板', buttons: [] },
  { p: '/opp/1/quote', title: '报价单 (opp=1)', buttons: ['新建版本', '提交审批', '客户接受'] },
  { p: '/sales/referrers', title: '推荐人', buttons: ['新增', '编辑', '删除'] },
  { p: '/project/pool', title: '项目池', buttons: ['转为施工项目'] },
];

async function login(page) {
  console.log('[login] navigating ...');
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await new Promise(r => setTimeout(r, 500));
  await page.click('button.login-btn');
  await new Promise(r => setTimeout(r, 3000));
  console.log('[login] done. url:', page.url());
}

async function clickButtonIfExists(page, text) {
  try {
    const clicked = await page.evaluate((t) => {
      const buttons = Array.from(document.querySelectorAll('button, .el-button, .btn, [role="button"]'));
      for (const btn of buttons) {
        const txt = (btn.innerText || btn.textContent || '').trim();
        if (txt === t || txt.includes(t)) {
          btn.click();
          return true;
        }
      }
      return false;
    }, text);
    return clicked;
  } catch (e) {
    return false;
  }
}

(async () => {
  console.log(`[start] launching chrome`);
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const consoleErrs = [];
  const pageErrs = [];
  const failedResources = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrs.push(msg.text());
  });
  page.on('pageerror', err => pageErrs.push(err.message));
  page.on('requestfailed', req => {
    const url = req.url();
    if (!url.includes('favicon') && !url.includes('sockjs')) {
      failedResources.push(`${req.failure().errorText} ${url}`);
    }
  });
  page.on('response', resp => {
    if (resp.status() >= 400 && !resp.url().includes('favicon') && !resp.url().includes('/dashboard/')) {
      failedResources.push(`HTTP ${resp.status()} ${resp.url()}`);
    }
  });

  try {
    await login(page);
  } catch (e) {
    console.error('[login] FAILED:', e.message);
    await browser.close();
    process.exit(1);
  }

  console.log(`\n=== 开始跑 ${PAGES.length} 个 P1 页面 ===\n`);
  const results = [];
  for (const item of PAGES) {
    const url = BASE + item.p;
    const consoleBefore = consoleErrs.length;
    const pageErrBefore = pageErrs.length;
    const failResBefore = failedResources.length;
    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
      await Promise.race([
        page.waitForFunction(
          () => {
            const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row, .el-table__body tr, .el-table tr, .kanban-card, .lead-card');
            return rows.length > 0;
          },
          { timeout: 4000 }
        ).catch(() => {}),
        new Promise(r => setTimeout(r, 4000)),
      ]);
      const bodyText = await page.evaluate(() => document.body.innerText || '');
      const debugInfo = await page.evaluate(() => {
        const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row, .el-table__body tr, .el-table tr');
        const cards = document.querySelectorAll('.kanban-card, .lead-card, .opportunity-card');
        return { rowCount: rows.length, cardCount: cards.length };
      });
      const safeName = item.p.replace(/[\/\:]/g, '_');
      const shotPath = path.join(SHOTS_DIR, safeName + '.png');
      await page.screenshot({ path: shotPath, fullPage: false });

      const buttonClicks = [];
      for (const btnText of item.buttons) {
        const clicked = await clickButtonIfExists(page, btnText);
        await new Promise(r => setTimeout(r, 500));
        if (clicked) {
          buttonClicks.push(btnText);
          await page.screenshot({ path: path.join(SHOTS_DIR, `${safeName}_click_${btnText.replace(/\W/g, '_')}.png`), fullPage: false });
          await page.evaluate(() => {
            const cancelBtns = document.querySelectorAll('.el-dialog__close, .el-message-box__close, .el-drawer__close-btn, .cancel-btn, .el-button--cancel, .el-message-box__btns .el-button--primary');
            cancelBtns.forEach(b => b.click());
          });
          await new Promise(r => setTimeout(r, 500));
        }
      }

      const newConsoleErrs = consoleErrs.slice(consoleBefore);
      const newPageErrs = pageErrs.slice(pageErrBefore);
      const newFailRes = failedResources.slice(failResBefore);
      const realErrs = [...newPageErrs, ...newFailRes];
      const consoleOk = newConsoleErrs.filter(e => !e.includes('favicon'));

      let status = '✅';
      let note = `渲染(${bodyText.length}字) rows=${debugInfo.rowCount} cards=${debugInfo.cardCount}`;
      const has404 = bodyText.includes('404') && (bodyText.includes('页面不存在') || bodyText.includes('抱歉'));
      if (has404) {
        status = '❌';
        note = '页面 404';
      } else if (bodyText.length < 50) {
        status = '❌';
        note = '页面内容过少';
      } else if (realErrs.length > 0) {
        status = '⚠️';
        note = `错误: ${realErrs.length}条 | ${realErrs[0].slice(0, 80)}`;
      } else if (consoleOk.length > 0) {
        status = '⚠️';
        note = `console: ${consoleOk[0].slice(0, 80)}`;
      }
      results.push({
        ...item, status, note,
        clicks: buttonClicks,
        errCount: realErrs.length,
        consoleCount: consoleOk.length,
      });
      console.log(`${status} ${item.p.padEnd(28)} clicks=[${buttonClicks.join(',')}] ${note}`);
    } catch (e) {
      results.push({ ...item, status: '❌', note: '加载失败: ' + e.message, clicks: [] });
      console.log(`❌ ${item.p.padEnd(28)} 加载失败: ${e.message.slice(0, 100)}`);
    }
  }

  // 汇总
  console.log('\n=== 汇总 ===');
  const ok = results.filter(r => r.status === '✅').length;
  const warn = results.filter(r => r.status === '⚠️').length;
  const fail = results.filter(r => r.status === '❌').length;
  console.log(`P1 页面: ✅ ${ok}  ⚠️ ${warn}  ❌ ${fail}  共 ${results.length}`);

  if (warn + fail > 0) {
    console.log('\n--- 详细问题清单 ---');
    for (const r of results) {
      if (r.status !== '✅') {
        console.log(`${r.status} ${r.p.padEnd(28)} clicks=[${(r.clicks || []).join(',')}] ${r.note}`);
      }
    }
  }

  const reportPath = path.join(SHOTS_DIR, 'pages_results.json');
  fs.writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    base: BASE,
    total: results.length, ok, warn, fail,
    pass_rate: (ok / results.length * 100).toFixed(1) + '%',
    results,
  }, null, 2));

  await browser.close();
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => {
  console.error('FATAL:', e);
  process.exit(1);
});
