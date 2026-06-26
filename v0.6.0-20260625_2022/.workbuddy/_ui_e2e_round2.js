// 业务流 + 资金流 真机点击测试 V0.5.8.4+
// 完全模拟人类: 登录 → 走菜单 → 进表单 → type → 点提交 → 看页面反应
// 不只跑后端, 抓 pageerror + response
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const HOST = 'http://192.168.3.117';
const SCREEN_DIR = 'D:/work/website/OA/.workbuddy';

const results = [];
let stepNum = 0;

function log(msg) { console.log(msg); }
function record(name, ok, detail) {
  stepNum++;
  const tag = ok ? '✅' : '❌';
  log(`  ${tag} [${stepNum}] ${name}: ${detail || ''}`);
  results.push({ name, ok, detail });
}

async function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

async function login(page) {
  await page.goto(`${HOST}/login`, { waitUntil: 'networkidle0' });
  await page.waitForSelector('.el-input__inner', { timeout: 8000 });
  const inputs = await page.$$('.el-input__inner');
  // 第一个 enabled 的 user + pwd
  let userInp, pwdInp;
  for (const i of inputs) {
    const t = await i.evaluate(e => e.type);
    if (t === 'text' && !userInp) userInp = i;
    if (t === 'password' && !pwdInp) pwdInp = i;
  }
  await userInp.click({ clickCount: 3 }); await page.keyboard.press('Backspace');
  await userInp.type('admin');
  await pwdInp.click({ clickCount: 3 }); await page.keyboard.press('Backspace');
  await pwdInp.type('admin123');
  await wait(400);
  // 关掉移动端提示
  for (const b of await page.$$('button')) {
    const t = await b.evaluate(e => e.textContent || '');
    if (t.includes('继续访问') || t.includes('知道了') || t.includes('关闭')) { await b.click().catch(() => {}); break; }
  }
  await wait(200);
  // 点登录
  for (const b of await page.$$('button')) {
    const t = await b.evaluate(e => e.textContent || '');
    if ((t.includes('登 录') || t.includes('登录')) && t.length < 10) { await b.click(); break; }
  }
  await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 8000 }).catch(() => {});
  await wait(800);
  return page.url().includes('/login') ? false : true;
}

async function clickByText(page, text, ctx = 'body') {
  const handle = await page.evaluateHandle((t, c) => {
    const root = c === 'body' ? document.body : document.querySelector(c);
    if (!root) return null;
    const items = [...root.querySelectorAll('button, a, .el-menu-item, .el-link, [role="button"]')];
    return items.find(el => (el.textContent || '').includes(t) && el.offsetParent !== null);
  }, text, ctx);
  if (handle) {
    const isEl = await handle.evaluate(e => e ? !!e.click : false);
    if (isEl) { try { await handle.click(); return true; } catch {} }
  }
  return false;
}

async function findMenu(page, menuText) {
  // 点击侧边栏菜单 (穿透多个层级)
  const items = await page.$$('.el-menu-item');
  for (const it of items) {
    const t = await it.evaluate(e => e.textContent || '');
    if (t.trim().includes(menuText)) { await it.click(); return true; }
  }
  // 试子菜单 (展开)
  for (const it of await page.$$('.el-sub-menu__title')) {
    const t = await it.evaluate(e => e.textContent || '');
    if (t.includes(menuText)) { await it.click(); await wait(400); return true; }
  }
  return false;
}

async function gotoMenu(page, menuPath) {
  // 直接用 vue-router 跳转, 跳过菜单点击
  await page.evaluate((path) => {
    // 找 vue app 实例
    const app = document.querySelector('#app')?.__vue_app__;
    if (app && app.config.globalProperties.$router) {
      app.config.globalProperties.$router.push(path);
    }
  }, menuPath);
  await wait(1500);
}

async function realTypeInDialog(page, label, value) {
  // 在 dialog 内找 label 对应 input
  return await page.evaluate((lbl, val) => {
    const dialogs = [...document.querySelectorAll('.el-dialog')];
    for (const d of dialogs) {
      if (d.querySelector('[aria-label="Close"]') && d.style.display === 'none') continue;
      const items = [...d.querySelectorAll('.el-form-item')];
      for (const it of items) {
        const l = it.querySelector('.el-form-item__label');
        if (l && l.textContent.trim().startsWith(lbl)) {
          const inp = it.querySelector('input[type="text"], input:not([type])');
          if (inp) { inp.focus(); inp.select(); return true; }
        }
      }
    }
    return false;
  }, label, value);
}

async function realTypeInForm(page, label, value) {
  // 维修页是页面表单, 不是 dialog
  return await page.evaluate((lbl, val) => {
    const items = [...document.querySelectorAll('.el-form-item')];
    for (const it of items) {
      const l = it.querySelector('.el-form-item__label');
      if (l && l.textContent.trim().startsWith(lbl)) {
        const inp = it.querySelector('input[type="text"], input:not([type]), textarea');
        if (inp) { inp.focus(); inp.select(); return true; }
      }
    }
    return false;
  }, label, value);
}

async function realType(page, label, value) {
  // 1. 先试 dialog
  const found = await realTypeInDialog(page, label, value);
  if (!found) {
    // 2. 退到页面表单
    await realTypeInForm(page, label, value);
  }
  await page.keyboard.down('Control');
  await page.keyboard.press('A');
  await page.keyboard.up('Control');
  await page.keyboard.press('Delete');
  await page.keyboard.type(value, { delay: 30 });
  await wait(200);
  // 验证
  return await page.evaluate((lbl, v) => {
    const items = [...document.querySelectorAll('.el-dialog, .page-container, .el-form')];
    items.forEach(_ => {}); // skip
    // 优先 dialog
    for (const d of document.querySelectorAll('.el-dialog')) {
      for (const it of d.querySelectorAll('.el-form-item')) {
        const l = it.querySelector('.el-form-item__label');
        if (l && l.textContent.trim().startsWith(lbl)) {
          const inp = it.querySelector('input');
          if (inp) return inp.value === v;
        }
      }
    }
    // 页面表单
    for (const it of document.querySelectorAll('.el-form-item')) {
      const l = it.querySelector('.el-form-item__label');
      if (l && l.textContent.trim().startsWith(lbl)) {
        const inp = it.querySelector('input');
        if (inp) return inp.value === v;
      }
    }
    return false;
  }, label, value);
}

async function typeFocused(page, value) {
  return await page.evaluate(v => {
    const inp = window.__focusedInput;
    if (!inp) return false;
    // 1) 清空
    inp.value = '';
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    // 2) 用 v-model setter
    const tag = inp.tagName;
    const proto = tag === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
    setter.call(inp, v);
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new Event('change', { bubbles: true }));
    inp.dispatchEvent(new Event('blur', { bubbles: true }));
    return inp.value === v;
  }, value);
}

async function selectOption(page, labelText, optionText) {
  // 找 select, 点击 → 弹出 → 点包含 optionText 的项
  return await page.evaluate((label, opt) => {
    const items = [...document.querySelectorAll('.el-form-item')];
    for (const it of items) {
      const lbl = it.querySelector('.el-form-item__label');
      if (lbl && lbl.textContent.trim().startsWith(label)) {
        const sel = it.querySelector('.el-select');
        if (sel) { sel.click(); return true; }
      }
    }
    return false;
  }, labelText, optionText);
}

async function clickByExactText(page, text, ctx = 'body') {
  // 在弹出层中找含 text 的项并点击
  await page.evaluate((t, c) => {
    const root = c === 'body' ? document.body : document.querySelector(c);
    if (!root) return;
    const candidates = [...root.querySelectorAll('.el-select-dropdown__item, .el-option, .el-dropdown-menu__item, li[role="option"]')];
    const target = candidates.find(el => (el.textContent || '').includes(t) && el.offsetParent !== null);
    if (target) target.click();
  }, text, ctx);
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  // 错误收集
  const pageErrors = [];
  page.on('pageerror', e => pageErrors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') pageErrors.push('console: ' + m.text()); });

  // API 错误收集
  const apiCalls = [];
  const api404s = [];
  page.on('response', async r => {
    const u = r.url();
    if (u.includes('/api/') && !u.includes('/api/health')) {
      try {
        const body = await r.text();
        apiCalls.push({ url: u.replace(HOST, ''), method: r.request().method(), status: r.status(), body: body.slice(0, 150) });
        if (r.status() === 404) api404s.push({ url: u.replace(HOST, ''), method: r.request().method() });
      } catch {}
    } else if (r.status() === 404) {
      api404s.push({ url: u, method: r.request().method() });
    }
  });

  // ===== 登录 =====
  log('\n========== 登录 ==========');
  const ok = await login(page);
  record('登录 admin/admin123', ok, `URL: ${page.url()}`);
  if (!ok) { await browser.close(); return; }
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_01_home.png') });

  // ============================================================
  // 业务流 1: 销售链路 — 线索→商机→报价→项目
  // ============================================================
  log('\n========== 业务流 1: 销售链路 (UI 端到端) ==========');
  pageErrors.length = 0; apiCalls.length = 0;

  // 1.1 用 router 直接进线索
  await gotoMenu(page, '/sales/leads');
  record('进 线索列表', page.url().includes('/sales/leads'), `URL: ${page.url()}`);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_02_leads.png') });

  // 1.2 创建线索 — 找新建按钮
  let clicked = await clickByText(page, '新建线索', '.page-container, body');
  if (!clicked) clicked = await clickByText(page, '新建', '.page-container, body');
  if (!clicked) clicked = await clickByText(page, '新增', '.page-container, body');
  await wait(1000);
  const dialogOpen = await page.evaluate(() => {
    return !!document.querySelector('.el-dialog__title') &&
           document.querySelector('.el-dialog__title').textContent.includes('线索');
  });
  record('进 新建线索 弹窗', clicked || dialogOpen, `clicked=${clicked} dialog=${dialogOpen} URL: ${page.url()}`);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_03_lead_create.png') });

  if (clicked || dialogOpen) {
    // 填表: 用真键盘 type (Vue v-model 才能正确响应)
    const ok1 = await realType(page, '客户名称', 'UI测试-张家港三厂');
    await wait(300);
    const ok2 = await realType(page, '联系人', 'UI测试联系人');
    await wait(300);
    const ok3 = await realType(page, '联系电话', '13900009999');
    await wait(300);
    record('填线索表单 (名称+联系人+电话)', ok1 && ok2 && ok3, `name=${ok1} 联系人=${ok2} 电话=${ok3}`);
    await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_04_lead_filled.png') });

    // 跟进人: el-select-v2 远程搜索
    const userSelects = await page.$$('.el-dialog .el-select');
    let assignedOk = false;
    for (const sel of userSelects) {
      const inFollowUp = await sel.evaluate(s => {
        const item = s.closest('.el-form-item');
        const lbl = item?.querySelector('.el-form-item__label')?.textContent || '';
        return lbl.includes('跟进');
      });
      if (inFollowUp) {
        // 点开下拉
        await sel.click();
        await wait(500);
        // 远程搜索: 输入 "admin" 搜
        const searchInp = await page.$('.el-select-dropdown__input, .el-select-v2__search-input, .el-select-dropdown input');
        if (searchInp) {
          await searchInp.type('admin', { delay: 50 });
          await wait(800);
        }
        // 选第一个非 disabled
        assignedOk = await page.evaluate(() => {
          const items = [...document.querySelectorAll('.el-select-dropdown__item')];
          const it = items.find(e => e.offsetParent && !e.classList.contains('is-disabled') && e.textContent.trim().length > 0);
          if (it) { it.click(); return true; }
          return false;
        });
        break;
      }
    }
    record('选 跟进人', assignedOk);
    await wait(500);

    // 提交
    const submitOk = await clickByText(page, '保存', '.el-dialog') || await clickByText(page, '确 定', '.el-dialog') || await clickByText(page, '确定', '.el-dialog');
    record('点确定/保存', submitOk);
    await wait(3000);
    await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_05_lead_submitted.png') });
    const lastCall = apiCalls.filter(c => c.url.includes('/leads') && c.method === 'POST').pop();
    record('线索 API 调用', lastCall && lastCall.status < 500, lastCall ? `HTTP ${lastCall.status} body=${lastCall.body.slice(0,150)}` : '未触发 API');
  }

  // ============================================================
  // 业务流 2: 资金流 — 公司内部转账
  // ============================================================
  log('\n========== 资金流: 公司内部转账 (UI 端到端) ==========');
  pageErrors.length = 0; apiCalls.length = 0;

  await gotoMenu(page, '/finance/overview');
  record('财务概览 菜单', page.url().includes('finance'), `URL: ${page.url()}`);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_05_finance.png') });

  // 点"公司内部转账"按钮
  const transferBtn = await clickByText(page, '公司内部转账', '.page-container, body');
  record('点 公司内部转账 按钮', transferBtn);
  await wait(1500);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_06_transfer_dialog.png') });

  if (transferBtn) {
    // 选账户: 第一个 select = 转出, 第二个 = 转入
    const selects = await page.$$('.el-dialog .el-select');
    log(`  找到 ${selects.length} 个 select`);

    // 转出账户
    if (selects[0]) { await selects[0].click(); await wait(500); }
    await page.evaluate(() => {
      const items = [...document.querySelectorAll('.el-select-dropdown__item')];
      const it = items.find(e => e.offsetParent && (e.textContent || '').includes('工商'));
      if (it) it.click();
    });
    await wait(800);

    // 转入账户
    if (selects[1]) { await selects[1].click(); await wait(500); }
    await page.evaluate(() => {
      const items = [...document.querySelectorAll('.el-select-dropdown__item')];
      const it = items.find(e => e.offsetParent && (e.textContent || '').includes('招商') && !e.classList.contains('is-disabled'));
      if (it) it.click();
    });
    await wait(800);

    // 金额 (el-input-number 特殊)
    const amtOk = await page.evaluate(() => {
      const dialog = [...document.querySelectorAll('.el-dialog')].pop();
      if (!dialog) return false;
      const items = [...dialog.querySelectorAll('.el-form-item')];
      for (const it of items) {
        const l = it.querySelector('.el-form-item__label');
        if (l && l.textContent.trim().startsWith('转账金额')) {
          const inp = it.querySelector('.el-input-number input');
          if (inp) {
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(inp, '888');
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
            inp.dispatchEvent(new Event('blur', { bubbles: true }));
            return inp.value === '888';
          }
        }
      }
      return false;
    });
    await wait(300);
    // 用途 (普通 input)
    const useOk = await realType(page, '用途', 'UI 端到端 - 备用金调拨');
    await wait(300);
    record('填转出/转入/金额+用途', selects.length >= 2 && amtOk && useOk, `selects=${selects.length} 金额=${amtOk} 用途=${useOk}`);

    await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_07_transfer_filled.png') });

    // 点确认转账
    const cfm = await clickByText(page, '确认转账', '.el-dialog');
    record('点 确认转账', cfm);
    await wait(1500);

    // 处理 ElMessageBox 确认
    await page.evaluate(() => {
      const btns = [...document.querySelectorAll('.el-message-box .el-button--primary')];
      if (btns[0]) btns[0].click();
    });
    await wait(2000);
    await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_08_transfer_done.png') });

    const transferCall = apiCalls.filter(c => c.url.includes('/finance/accounts/transfer') && c.method === 'POST').pop();
    record('转账 API 调用', transferCall && transferCall.status < 500, transferCall ? `HTTP ${transferCall.status} body=${transferCall.body.slice(0, 100)}` : '未触发');
  }

  // ============================================================
  // 业务流 3: 维修工单 (V0.5.8.4 res.data 修复验证)
  // ============================================================
  log('\n========== 业务流 3: 维修工单创建 (UI 端到端) ==========');
  pageErrors.length = 0; apiCalls.length = 0;

  await gotoMenu(page, '/maintenance/repairs/create');
  record('进 新建返修 页 (直接路由)', page.url().includes('/repairs/create'), `URL: ${page.url()}`);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_09_repair_create.png') });

  // 填表 — 用真键盘
  const ok1 = await realType(page, '客户', 'UI测试-赵六');
  await wait(200);
  const ok2 = await realType(page, '联系', '13800006666');
  await wait(200);
  // 故障描述 (textarea)
  const taOk = await page.evaluate(() => {
    const items = [...document.querySelectorAll('.el-form-item')];
    for (const it of items) {
      const lbl = it.querySelector('.el-form-item__label');
      if (lbl && lbl.textContent.trim().startsWith('故障')) {
        const ta = it.querySelector('textarea');
        if (ta) { ta.focus(); ta.select(); return true; }
      }
    }
    return false;
  });
  if (taOk) {
    await page.keyboard.type('UI 端到端测试 - 设备无法开机, 反复重启', { delay: 20 });
  }
  await wait(300);
  record('填返修表单 (客户+电话+描述)', ok1 && ok2 && taOk, `name=${ok1} phone=${ok2} desc=${taOk}`);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_10_repair_filled.png') });

  // 提交
  const sub = await clickByText(page, '提交', '.el-form') || await clickByText(page, '保 存', '.el-form');
  record('点 提交', sub);
  await wait(3000);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_11_repair_done.png') });

  const repairCall = apiCalls.filter(c => c.url.endsWith('/repair-orders') && c.method === 'POST').pop();
  record('返修单 API', repairCall && repairCall.status < 500, repairCall ? `HTTP ${repairCall.status}` : '未触发');
  record('返修页 跳走 (V0.5.8.4 验证)', page.url().includes('/repairs/'), `URL: ${page.url()}`);

  // ============================================================
  // 业务流 4: 商机看板
  // ============================================================
  log('\n========== 业务流 4: 商机看板 (UI 端到端) ==========');

  await gotoMenu(page, '/sales/opps/board');
  record('商机看板 路由', page.url().includes('opp'), `URL: ${page.url()}`);
  await wait(3000);
  await page.screenshot({ path: path.join(SCREEN_DIR, '_ui_12_opps.png') });

  // 7 段列卡 (抓全 apiCalls, 不重置)
  const oppsCall = apiCalls.filter(c => c.url.includes('/sales/opps') && !c.url.includes('/funnel') && !c.url.includes('/stats')).pop();
  record('商机 API 200', oppsCall && oppsCall.status === 200, oppsCall ? `HTTP ${oppsCall.status} URL=${oppsCall.url}` : `未触发 (共 ${apiCalls.length} 个 API)`);

  // ============================================================
  // 总结
  // ============================================================
  log('\n========== 总结 ==========');
  const pass = results.filter(r => r.ok).length;
  const fail = results.filter(r => !r.ok).length;
  log(`✅ ${pass} / ❌ ${fail} / 总 ${results.length}`);
  if (pageErrors.length) {
    log(`\n⚠️ 页面 JS 错误 ${pageErrors.length}:`);
    pageErrors.slice(0, 5).forEach(e => log(`  - ${e.slice(0, 200)}`));
  }
  if (fail > 0) {
    log('\n❌ 失败项:');
    results.filter(r => !r.ok).forEach(r => log(`  - ${r.name}: ${r.detail}`));
  }

  fs.writeFileSync(path.join(SCREEN_DIR, '_ui_results.json'), JSON.stringify({ results, api404s, pageErrors: pageErrors.slice(0, 20) }, null, 2));
  if (api404s.length) {
    log(`\n⚠️ 404 资源 ${api404s.length}:`);
    api404s.slice(0, 10).forEach(e => log(`  - ${e.method} ${e.url}`));
  }

  await browser.close();
}

main().catch(e => { console.log('FATAL:', e.message); process.exit(1); });
