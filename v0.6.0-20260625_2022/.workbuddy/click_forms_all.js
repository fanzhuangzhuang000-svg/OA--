const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const fs = require('fs');

const SHOTS_DIR = 'D:/work/website/OA/.workbuddy/shots/forms';
fs.mkdirSync(SHOTS_DIR, { recursive: true });

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// 需要挨个点开 dialog 表单 + 提交的页面
// 范围: 各模块"新建/创建/录入"页 + 列表页"+"按钮
const PAGES_WITH_FORMS = [
  // 业务核心 — 创建类
  { path: '/customer/list', name: '客户列表-新建', btn: '新建客户|新增客户|创建客户' },
  { path: '/sales/leads', name: '线索池-新建', btn: '新建线索|创建线索|新增线索' },
  { path: '/sales/opps', name: '商机池-新建', btn: '新建商机|创建商机' },
  { path: '/maintenance/work-orders/create', name: '创建工单', btn: '' },
  { path: '/maintenance/repairs/create', name: '新建返修', btn: '' },
  { path: '/expense/apply', name: '申请报销', btn: '' },
  { path: '/project/create', name: '创建项目', btn: '' },
  { path: '/inventory/inbound-order', name: '入库单', btn: '新建|创建' },
  { path: '/inventory/outbound-order', name: '出库单', btn: '新建|创建' },
  { path: '/inventory/material-request', name: '领料单', btn: '新建|创建' },
  { path: '/purchase/requirement', name: '采购需求', btn: '新建|创建' },
  { path: '/purchase/plan', name: '采购计划', btn: '新建|创建' },
  { path: '/construction/commencement', name: '开工单', btn: '新建|创建' },
  { path: '/construction/rectification', name: '整改工单', btn: '新建|创建' },
  { path: '/vehicle/apply', name: '用车申请', btn: '' },
  { path: '/settings/user', name: '用户管理-新增', btn: '新增|新建' },
  { path: '/settings/role', name: '角色管理-新增', btn: '新增|新建' },
  { path: '/settings/dict', name: '数据字典-新增', btn: '新增|新建' },
  { path: '/finance/receipt', name: '收款单', btn: '新建|创建|录入' },
  { path: '/finance/payment', name: '付款单', btn: '新建|创建|录入' },
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const apiErrors = [];
  const pageErrors = [];
  page.on('response', r => {
    const u = r.url();
    if (u.includes('/api/') && r.status() >= 400) apiErrors.push({ status: r.status(), url: u.replace('http://192.168.3.117:8081','') });
  });
  page.on('pageerror', e => pageErrors.push(e.message));

  // 1. 登录
  console.log('[login]');
  await page.goto('http://192.168.3.117/login', { waitUntil: 'networkidle2' });
  await sleep(1500);
  await page.waitForSelector('input[placeholder*="用户名"]', { timeout: 10000 });
  const u = await page.$('input[placeholder*="用户名"]');
  const p = await page.$('input[placeholder*="密码"]');
  await u.click(); await u.type('admin1', { delay: 20 });
  await p.click(); await p.type('admin123', { delay: 20 });
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '登录' || b.textContent.includes('登 录'));
    if (btn) btn.click();
  });
  await page.waitForFunction(() => location.pathname !== '/login', { timeout: 20000 });
  await sleep(2000);

  const results = [];

  for (let i = 0; i < PAGES_WITH_FORMS.length; i++) {
    const p = PAGES_WITH_FORMS[i];
    const beforeApi = apiErrors.length;
    const beforePage = pageErrors.length;
    try {
      await page.goto('http://192.168.3.117' + p.path, { waitUntil: 'networkidle2', timeout: 20000 });
    } catch (e) {
      results.push({ path: p.path, name: p.name, status: 'NAV_FAIL', err: e.message });
      continue;
    }
    await sleep(1500);
    await page.screenshot({ path: SHOTS_DIR + '/' + (i+1).toString().padStart(2,'0') + '_' + p.name.replace(/[\\/:*?"<>|]/g,'_') + '.png' });

    // 找 "新建/创建/新增" 按钮
    let btnFound = false;
    let openedDialog = false;
    if (p.btn) {
      const re = new RegExp(p.btn);
      const btnInfo = await page.evaluate((regexStr) => {
        const re = new RegExp(regexStr);
        const btns = Array.from(document.querySelectorAll('button, a, .el-button'));
        for (const b of btns) {
          const t = (b.textContent || '').trim();
          if (re.test(t) && b.offsetParent !== null) {
            b.click();
            return { ok: true, text: t };
          }
        }
        return { ok: false };
      }, re.source.slice(1, -1));
      btnFound = btnInfo.ok;
      if (btnInfo.ok) {
        await sleep(1500);
        // 检查 dialog 出现
        const hasDialog = await page.evaluate(() => {
          return document.querySelectorAll('.el-dialog, .el-drawer, .el-message-box').length > 0;
        });
        openedDialog = hasDialog;
        if (hasDialog) {
          await page.screenshot({ path: SHOTS_DIR + '/' + (i+1).toString().padStart(2,'0') + '_' + p.name.replace(/[\\/:*?"<>|]/g,'_') + '_dialog.png' });
        }
        // 关闭 dialog
        await page.evaluate(() => {
          const closeBtn = document.querySelector('.el-dialog__close, .el-drawer__close-btn, .el-message-box__close, [aria-label*="close"]');
          if (closeBtn) closeBtn.click();
          // 兜底: 按 ESC
          document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
        });
        await sleep(800);
      }
    }

    const newApi = apiErrors.slice(beforeApi);
    const newPage = pageErrors.slice(beforePage);

    results.push({
      path: p.path, name: p.name,
      btn_found: btnFound, dialog_opened: openedDialog,
      api_err: newApi.length, page_err: newPage.length,
      api_errs: newApi.slice(0,3), page_errs: newPage.slice(0,3),
    });

    if (!btnFound && p.btn) console.log(`  ⚠ [${(i+1).toString().padStart(2,'0')}] ${p.path} 未找到按钮 "${p.btn}"`);
    else if (newApi.length || newPage.length) console.log(`  ✗ [${(i+1).toString().padStart(2,'0')}] ${p.path} api=${newApi.length} pageErr=${newPage.length}`);
    else if (btnFound && openedDialog) console.log(`  ✓ [${(i+1).toString().padStart(2,'0')}] ${p.path} 弹窗打开成功`);
    else if (btnFound) console.log(`  ✓ [${(i+1).toString().padStart(2,'0')}] ${p.path} 按钮找到`);
    else console.log(`  · [${(i+1).toString().padStart(2,'0')}] ${p.path} 直接表单页`);
  }

  // 汇总
  fs.writeFileSync(SHOTS_DIR + '/_report.json', JSON.stringify(results, null, 2));
  const ok = results.filter(r => !r.api_err && !r.page_err);
  const fail = results.filter(r => r.api_err || r.page_err);
  const noBtn = results.filter(r => r.btn_found === false);

  console.log('\n========= 表单弹窗测试报告 =========');
  console.log(`总页面: ${results.length}`);
  console.log(`通过: ${ok.length}, 失败: ${fail.length}, 未找到按钮: ${noBtn.length}`);
  if (fail.length) {
    console.log('\n[失败明细]');
    for (const r of fail) {
      console.log(`  ${r.path} (${r.name})`);
      r.api_errs.forEach(e => console.log(`    ${e.status} ${e.url}`));
      r.page_errs.forEach(e => console.log(`    ${e}`));
    }
  }
  if (noBtn.length) {
    console.log('\n[未找到新建按钮]');
    for (const r of noBtn) console.log(`  ${r.path} (${r.name})`);
  }

  await browser.close();
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
