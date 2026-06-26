const puppeteer = require('C:/Users/MRG/.workbuddy/binaries/node/workspace/node_modules/puppeteer-core');
const fs = require('fs');
const path = require('path');

const SHOTS_DIR = 'D:/work/website/OA/.workbuddy/shots/click-through';
fs.mkdirSync(SHOTS_DIR, { recursive: true });

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// 完整路由表 (从 router/index.ts 抓出来的真实路径)
const ROUTES = [
  // 工作台
  { path: '/dashboard', name: '工作台' },
  { path: '/project-overview', name: '总览看板' },
  // 考勤
  { path: '/attendance/overview', name: '考勤总览' },
  { path: '/attendance/record', name: '打卡记录' },
  { path: '/attendance/leave', name: '请假管理' },
  { path: '/attendance/overtime', name: '加班管理' },
  { path: '/attendance/report', name: '考勤报表' },
  { path: '/attendance/shifts', name: '班次配置' },
  { path: '/attendance/groups', name: '班组管理' },
  { path: '/attendance/schedule', name: '排班计划' },
  { path: '/attendance/my-schedule', name: '我的排班' },
  // 员工
  { path: '/employee/list', name: '员工列表' },
  { path: '/employee/org', name: '组织架构' },
  { path: '/employee/onboardings', name: '入职档案' },
  { path: '/employee/resignations', name: '离职管理' },
  { path: '/employee/skill', name: '技能标签' },
  // 客户
  { path: '/customer/list', name: '客户列表' },
  { path: '/customer/health', name: '客户健康度' },
  { path: '/customer/pipeline', name: '销售漏斗' },
  { path: '/customer/follow-calendar', name: '跟进日历' },
  { path: '/customer/map', name: '客户地图' },
  // 销售
  { path: '/sales/leads', name: '线索池' },
  { path: '/sales/leads/board', name: '线索看板' },
  { path: '/sales/opps', name: '商机池' },
  { path: '/sales/opps/board', name: '商机看板' },
  { path: '/sales/referrers', name: '推荐人' },
  { path: '/sales/settlements', name: '居间费结算' },
  { path: '/sales/external-quote', name: '对外报价看板' },
  // 项目
  { path: '/project/pool', name: '项目池' },
  { path: '/project/list', name: '项目列表' },
  { path: '/project/board', name: '项目看板' },
  { path: '/project/calendar', name: '付款日历' },
  { path: '/project/create', name: '创建项目' },
  // 质保
  { path: '/project/warranty/list', name: '质保期列表' },
  { path: '/project/warranty/expiring', name: '即将到期' },
  { path: '/project/warranty/service-order', name: '服务工单' },
  { path: '/project/warranty/deposit', name: '质保金' },
  // 采购
  { path: '/purchase/requirement', name: '采购需求' },
  { path: '/purchase/plan', name: '采购计划' },
  { path: '/purchase/approval', name: '采购审批' },
  { path: '/purchase/payment-request', name: '付款申请' },
  { path: '/purchase/payment', name: '财务付款' },
  { path: '/purchase/contract', name: '采购合同' },
  { path: '/purchase/shipment', name: '供应商发货' },
  { path: '/purchase/logistics', name: '物流跟踪' },
  // 施工
  { path: '/construction/team', name: '施工团队' },
  { path: '/construction/commencement', name: '开工单' },
  { path: '/construction/log', name: '施工日志' },
  { path: '/construction/log/daily', name: '每日上报' },
  { path: '/construction/rectification', name: '整改工单' },
  { path: '/construction/work-process', name: '工序字典' },
  { path: '/construction/external-work', name: '施工发包' },
  { path: '/construction/process/templates', name: '工序模板' },
  { path: '/construction/process/instances', name: '工序实例' },
  { path: '/construction/process/inspections', name: '验收记录' },
  // 维修中心
  { path: '/maintenance/work-orders', name: '维修工单' },
  { path: '/maintenance/work-orders/create', name: '创建工单' },
  { path: '/maintenance/repairs', name: '返修管理' },
  { path: '/maintenance/repairs/create', name: '新建返修' },
  { path: '/maintenance/stats', name: '维修统计' },
  { path: '/maintenance/kanban', name: '维修看板' },
  { path: '/maintenance/portal-repair', name: '返修进度查询' },
  // 报销
  { path: '/expense/list', name: '报销列表' },
  { path: '/expense/apply', name: '申请报销' },
  { path: '/expense/approval', name: '审批管理' },
  // 车辆
  { path: '/vehicle/fleet', name: '车辆档案' },
  { path: '/vehicle/apply', name: '用车申请' },
  { path: '/vehicle/dispatch', name: '调度管理' },
  { path: '/vehicle/insurance', name: '保险记录' },
  { path: '/vehicle/maintenance', name: '保养记录' },
  { path: '/vehicle/fuel-card', name: '油卡管理' },
  // 库存
  { path: '/inventory', name: '库存总览' },
  { path: '/inventory/inout', name: '出入库明细' },
  { path: '/inventory/inbound-order', name: '入库单' },
  { path: '/inventory/outbound-order', name: '出库单' },
  { path: '/inventory/material-request', name: '领料单' },
  { path: '/inventory/material-return', name: '领料归还单' },
  // 财务
  { path: '/finance/overview', name: '财务概览' },
  { path: '/finance/receipt', name: '收款单' },
  { path: '/finance/payment', name: '付款单' },
  { path: '/finance/receivable', name: '应收账款' },
  { path: '/finance/payable', name: '应付账款' },
  { path: '/finance/supplier-ledger', name: '供应商总账' },
  { path: '/finance/customer-ledger', name: '客户总账' },
  { path: '/finance/repair-cost', name: '售后成本报表' },
  // 供应商
  { path: '/supplier/list', name: '供应商列表' },
  // 审批
  { path: '/approval/finance', name: '财务审批' },
  { path: '/approval/operation', name: '运营审批' },
  { path: '/approval/project', name: '项目审批' },
  // 网盘/知识/大屏/消息
  { path: '/disk', name: '公司网盘' },
  { path: '/knowledge/list', name: '知识列表' },
  { path: '/screen', name: '数据大屏' },
  { path: '/message/list', name: '消息列表' },
  // 系统设置
  { path: '/settings/profile', name: '个人信息' },
  { path: '/settings/password', name: '修改密码' },
  { path: '/settings/my-permissions', name: '我的权限' },
  { path: '/settings/organization', name: '组织权限' },
  { path: '/settings/role', name: '角色管理' },
  { path: '/settings/role/matrix', name: '权限矩阵' },
  { path: '/settings/user', name: '用户管理' },
  { path: '/settings/field-mask', name: '字段脱敏' },
  { path: '/settings/permission-log', name: '权限变更历史' },
  { path: '/settings/approval', name: '审批引擎' },
  { path: '/settings/log', name: '系统日志' },
  { path: '/settings/backup', name: '数据管理' },
  { path: '/settings/wizard', name: '系统初始化' },
  { path: '/settings/dict', name: '数据字典' },
  { path: '/settings/monitor', name: '系统监控' },
];

const PAGE = (p) => p.replace(/[/\\:*?"<>|]/g, '_').replace(/^_+/, '');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const apiErrors = [];
  const consoleErrors = [];
  const pageErrors = [];
  const failedReqs = [];

  page.on('response', r => {
    const u = r.url();
    if (u.includes('/api/') && r.status() >= 400) {
      apiErrors.push({ status: r.status(), url: u.replace('http://192.168.3.117:8081', '') });
    }
  });
  page.on('console', m => {
    if (m.type() === 'error') {
      const text = m.text();
      // 过滤已知噪音
      if (text.includes('Failed to load resource') && text.includes('favicon')) return;
      consoleErrors.push(text);
    }
  });
  page.on('pageerror', e => pageErrors.push(e.message));
  page.on('requestfailed', req => {
    const f = req.failure();
    if (f && !req.url().includes('favicon')) {
      failedReqs.push({ url: req.url().replace('http://192.168.3.117:8081', ''), err: f.errorText });
    }
  });

  // 1. 登录 — el-input 实际是 div 包裹 input, 用真实 input element
  console.log('[login] 打开 /login');
  await page.goto('http://192.168.3.117/login', { waitUntil: 'networkidle2' });
  await sleep(1500);

  // 找所有 input[type=text] 和 input[type=password]
  await page.waitForSelector('input', { timeout: 10000 });

  // 通过 input 元素 type 拿
  const uHandle = await page.$('input[placeholder*="用户名"]');
  const pHandle = await page.$('input[placeholder*="密码"]');
  if (uHandle && pHandle) {
    await uHandle.click();
    await uHandle.type('admin1', { delay: 30 });
    await pHandle.click();
    await pHandle.type('admin123', { delay: 30 });
  } else {
    // 兜底: 用 evaluate 找
    const ok = await page.evaluate(() => {
      const all = document.querySelectorAll('input');
      let u = null, p = null;
      for (const i of all) {
        if (i.type === 'text' && i.offsetParent !== null) u = i;
        if (i.type === 'password' && i.offsetParent !== null) p = i;
      }
      if (!u || !p) return false;
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(u, 'admin1');
      u.dispatchEvent(new Event('input', { bubbles: true }));
      setter.call(p, 'admin123');
      p.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    });
    if (!ok) {
      console.error('[login] 找不到用户名/密码输入框');
      await browser.close();
      process.exit(1);
    }
  }
  await sleep(500);

  // 点登录按钮
  const loginClicked = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent.trim() === '登录' || b.textContent.includes('登 录'));
    if (btn) { btn.click(); return true; }
    return false;
  });
  console.log('[login] button clicked:', loginClicked);
  try {
    await page.waitForFunction(() => location.pathname !== '/login', { timeout: 20000 });
  } catch (e) {
    console.error('[login] failed:', e.message);
    await page.screenshot({ path: SHOTS_DIR + '/_login_failed.png' });
    const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 500));
    console.log('login body text:', bodyText);
    await browser.close();
    process.exit(1);
  }
  await sleep(2000);
  console.log('[login] ok, path=', page.url());

  // 2. 逐个点
  const results = [];
  for (let i = 0; i < ROUTES.length; i++) {
    const r = ROUTES[i];
    // 重置错误收集
    const beforeApi = apiErrors.length;
    const beforeConsole = consoleErrors.length;
    const beforePage = pageErrors.length;
    const beforeFailed = failedReqs.length;

    try {
      await page.goto('http://192.168.3.117' + r.path, { waitUntil: 'networkidle2', timeout: 20000 });
    } catch (e) {
      results.push({ path: r.path, name: r.name, status: 'NAV_FAIL', err: e.message });
      continue;
    }
    await sleep(1500);

    // 截图
    const shotPath = SHOTS_DIR + '/' + (i+1).toString().padStart(2,'0') + '_' + PAGE(r.path) + '.png';
    try {
      await page.screenshot({ path: shotPath, fullPage: false });
    } catch {}

    // 抓页面 body 关键错误提示 (精准匹配, 避免 ¥ 15,500,000 误判)
    const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 1500));
    const hasErr = /目标不存在|资源错误|404 Not Found|500 Internal|页面加载失败|资源加载失败/.test(bodyText);

    // 抓本路径新增错误
    const newApi = apiErrors.slice(beforeApi);
    const newConsole = consoleErrors.slice(beforeConsole);
    const newPage = pageErrors.slice(beforePage);
    const newFailed = failedReqs.slice(beforeFailed);

    results.push({
      path: r.path,
      name: r.name,
      url_after: page.url().replace('http://192.168.3.117', ''),
      api_err: newApi.length,
      console_err: newConsole.length,
      page_err: newPage.length,
      failed_req: newFailed.length,
      body_has_err: hasErr,
      api_errs: newApi.slice(0, 3),
      page_errs: newPage.slice(0, 3),
      console_errs: newConsole.slice(0, 3),
      failed_reqs: newFailed.slice(0, 3),
    });

    if (newApi.length || newPage.length || hasErr) {
      console.log(`  ✗ [${(i+1).toString().padStart(2,'0')}] ${r.path} api=${newApi.length} pageErr=${newPage.length} bodyErr=${hasErr}`);
    } else {
      console.log(`  ✓ [${(i+1).toString().padStart(2,'0')}] ${r.path} (${r.name})`);
    }
  }

  // 3. 汇总报告
  const summary = {
    total: ROUTES.length,
    visited: results.filter(r => r.status !== 'NAV_FAIL').length,
    nav_fail: results.filter(r => r.status === 'NAV_FAIL').length,
    has_issue: results.filter(r => r.api_err || r.page_err || r.body_has_err).length,
    results,
  };
  fs.writeFileSync(SHOTS_DIR + '/_report.json', JSON.stringify(summary, null, 2));

  // 4. 详细错误
  console.log('\n\n========= 报告 =========');
  console.log(`总路由: ${summary.total}, 访问成功: ${summary.visited}, 导航失败: ${summary.nav_fail}, 有问题: ${summary.has_issue}`);

  // 按错误类型分组
  const problematic = results.filter(r => r.api_err || r.page_err || r.body_has_err);
  if (problematic.length) {
    console.log(`\n[有问题 ${problematic.length} 个]`);
    for (const r of problematic) {
      console.log(`\n--- ${r.path} (${r.name}) ---`);
      console.log(`  最终 URL: ${r.url_after}`);
      console.log(`  body 含错误提示: ${r.body_has_err}`);
      if (r.api_errs.length) {
        console.log(`  API 错误 (${r.api_err}):`);
        r.api_errs.forEach(e => console.log(`    ${e.status} ${e.url}`));
      }
      if (r.page_errs.length) {
        console.log(`  Page 错误 (${r.page_err}):`);
        r.page_errs.forEach(e => console.log(`    ${e}`));
      }
      if (r.console_errs.length) {
        console.log(`  Console 错误 (${r.console_err}):`);
        r.console_errs.forEach(e => console.log(`    ${e}`));
      }
      if (r.failed_reqs.length) {
        console.log(`  Failed 请求 (${r.failed_req}):`);
        r.failed_reqs.forEach(e => console.log(`    ${e.err} ${e.url}`));
      }
    }
  }

  await browser.close();
})().catch(e => {
  console.error('FATAL:', e);
  process.exit(1);
});
