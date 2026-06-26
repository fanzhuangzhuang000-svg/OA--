const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const fs = require('fs');

const SHOTS_DIR = 'D:/work/website/OA/.workbuddy/shots/submissions';
fs.mkdirSync(SHOTS_DIR, { recursive: true });

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// 直接对每个有"提交/保存"按钮的表单页, 点提交看后端 validation
const PAGES = [
  { path: '/project/create', name: '创建项目' },
  { path: '/expense/apply', name: '申请报销' },
  { path: '/maintenance/work-orders/create', name: '创建工单' },
  { path: '/maintenance/repairs/create', name: '新建返修' },
  { path: '/vehicle/apply', name: '用车申请' },
  { path: '/construction/commencement', name: '开工单' },
  { path: '/construction/rectification', name: '整改工单' },
  { path: '/purchase/requirement', name: '采购需求' },
  { path: '/purchase/plan', name: '采购计划' },
  { path: '/inventory/inbound-order', name: '入库单' },
  { path: '/inventory/outbound-order', name: '出库单' },
  { path: '/inventory/material-request', name: '领料单' },
  { path: '/finance/receipt', name: '收款单' },
  { path: '/finance/payment', name: '付款单' },
  { path: '/attendance/leave', name: '请假申请' },
  { path: '/attendance/overtime', name: '加班申请' },
  { path: '/settings/wizard', name: '系统初始化-step1' },
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
  const apiSuccess = [];
  const pageErrors = [];
  page.on('response', r => {
    const u = r.url();
    if (u.includes('/api/') && !u.includes('route:list')) {
      if (r.status() >= 400) apiErrors.push({ status: r.status(), url: u.replace('http://192.168.3.117:8081',''), method: r.request().method() });
      else if (r.request().method() !== 'GET' && (u.includes('store') || u.includes('create') || u.includes('submit') || u.includes('apply'))) {
        apiSuccess.push({ status: r.status(), url: u.replace('http://192.168.3.117:8081',''), method: r.request().method() });
      }
    }
  });
  page.on('pageerror', e => pageErrors.push(e.message));

  console.log('[login]');
  await page.goto('http://192.168.3.117/login', { waitUntil: 'networkidle2' });
  await sleep(1500);
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

  for (let i = 0; i < PAGES.length; i++) {
    const target = PAGES[i];
    const beforeApi = apiErrors.length;
    const beforeOk = apiSuccess.length;
    const beforePage = pageErrors.length;

    try {
      await page.goto('http://192.168.3.117' + target.path, { waitUntil: 'networkidle2', timeout: 20000 });
    } catch (e) {
      results.push({ path: target.path, name: target.name, status: 'NAV_FAIL', err: e.message });
      continue;
    }
    await sleep(1500);

    // 找"保存"/"提交"/"申请"/"保存草稿"/"确定"按钮
    const clickResult = await page.evaluate(() => {
      // 宽松匹配: 包含"保存" / "提交" / "申请" / "确定" / "完成" / "新增提交" 等
      const re = /(保存|提交|申请|确定|完成|开始使用|保存配置|保存草稿)/;
      const btns = Array.from(document.querySelectorAll('button'));
      const candidates = [];
      for (const b of btns) {
        const t = (b.textContent || '').trim();
        // 排除取消/重置/关闭
        if (/(取消|重置|关闭|返回|删除|清空|导出|导入|搜索|刷新|查询)/.test(t)) continue;
        if (re.test(t) && b.offsetParent !== null && !b.disabled) {
          candidates.push(b);
        }
      }
      if (candidates.length) {
        candidates[0].click();
        return { ok: true, text: candidates[0].textContent.trim() };
      }
      return { ok: false };
    });

    await sleep(2500); // 等后端响应 + 弹错误提示

    await page.screenshot({ path: SHOTS_DIR + '/' + (i+1).toString().padStart(2,'0') + '_' + target.name.replace(/[\\/:*?"<>|]/g,'_') + '.png' });

    // 抓 body 关键错信息
    const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 1500));
    const validationMsg = /[\u4e00-\u9fa5]+/.test(bodyText) ? bodyText.match(/(必填|不能为空|格式错误|已存在|失败|错误|success|成功|已创建|已保存|提交成功)[\u4e00-\u9fa5\w]*/g)?.slice(0, 3) : null;

    const newApi = apiErrors.slice(beforeApi);
    const newOk = apiSuccess.slice(beforeOk);
    const newPage = pageErrors.slice(beforePage);

    results.push({
      path: target.path,
      name: target.name,
      btn_clicked: clickResult.ok,
      btn_text: clickResult.text,
      api_err: newApi.length,
      api_ok: newOk.length,
      api_errs: newApi.slice(0, 3),
      api_oks: newOk.slice(0, 3),
      page_err: newPage.length,
      page_errs: newPage.slice(0, 3),
      validation_msg: validationMsg,
    });

    if (clickResult.ok) {
      if (newApi.length) console.log(`  ✗ [${(i+1).toString().padStart(2,'0')}] ${target.path} (${target.name}) 提交: ${clickResult.text}, api_err=${newApi.length}`);
      else if (newOk.length) console.log(`  ✓ [${(i+1).toString().padStart(2,'0')}] ${target.path} 提交成功: ${newOk[0].method} ${newOk[0].url}`);
      else console.log(`  · [${(i+1).toString().padStart(2,'0')}] ${target.path} 点了 ${clickResult.text}, 无 API 调用 (前端校验拦住)`);
    } else {
      console.log(`  ⚠ [${(i+1).toString().padStart(2,'0')}] ${target.path} 没找到保存/提交按钮`);
    }
  }

  fs.writeFileSync(SHOTS_DIR + '/_report.json', JSON.stringify(results, null, 2));
  const realFails = results.filter(r => r.api_err);
  console.log('\n========= 提交按钮测试报告 =========');
  console.log(`总页面: ${results.length}`);
  console.log(`提交触发 API 错 (前端 bug): ${realFails.length}`);
  if (realFails.length) {
    console.log('\n[真实错误]');
    for (const r of realFails) {
      console.log(`  ${r.path} (${r.name})`);
      r.api_errs.forEach(e => console.log(`    ${e.status} ${e.method} ${e.url}`));
    }
  }

  await browser.close();
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
