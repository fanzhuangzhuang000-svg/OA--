#!/usr/bin/env node
/**
 * v0.3.8 全量页面浏览器自动化 E2E 测试
 * 用系统的 Chrome + puppeteer-core，访问每个页面、截图、检查控制台错误
 */
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const BASE = 'http://172.20.0.139:3000';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SHOTS_DIR = 'D:/work/website/OA/.workbuddy/shots';

// 完整页面路径清单
const PATHS = [
  { p: '/login', title: '登录页', auth: false },
  { p: '/', title: '工作台', auth: true },
  { p: '/dashboard', title: '工作台', auth: true },
  // 考勤
  { p: '/attendance', title: '考勤总览', auth: true },
  { p: '/attendance/overview', title: '考勤总览', auth: true },
  { p: '/attendance/record', title: '打卡记录', auth: true },
  { p: '/attendance/leave', title: '请假管理', auth: true },
  { p: '/attendance/overtime', title: '加班管理', auth: true },
  { p: '/attendance/report', title: '考勤报表', auth: true },
  // 员工
  { p: '/employee', title: '员工列表', auth: true },
  { p: '/employee/list', title: '员工列表', auth: true },
  { p: '/employee/org', title: '组织架构', auth: true },
  { p: '/employee/skill', title: '技能标签', auth: true },
  // 客户
  { p: '/customer', title: '客户列表', auth: true },
  { p: '/customer/list', title: '客户列表', auth: true },
  { p: '/customer/map', title: '客户地图', auth: true },
  { p: '/customer/1', title: '客户详情', auth: true },
  // 项目
  { p: '/project', title: '项目列表', auth: true },
  { p: '/project/list', title: '项目列表', auth: true },
  { p: '/project/create', title: '创建项目', auth: true },
  { p: '/project/123', title: '项目详情', auth: true },
  { p: '/project/123/gantt', title: '施工甘特图', auth: true },
  // 售后
  { p: '/service', title: '维修工单', auth: true },
  { p: '/service/orders', title: '维修工单', auth: true },
  { p: '/service/create', title: '创建工单', auth: true },
  { p: '/service/45', title: '工单详情', auth: true },
  { p: '/service/contract', title: '维保合同', auth: true },
  { p: '/service/stats', title: '服务统计', auth: true },
  // 报销
  { p: '/expense', title: '报销列表', auth: true },
  { p: '/expense/list', title: '报销列表', auth: true },
  { p: '/expense/apply', title: '申请报销', auth: true },
  { p: '/expense/approval', title: '审批管理', auth: true },
  // 车辆
  { p: '/vehicle', title: '车辆档案', auth: true },
  { p: '/vehicle/fleet', title: '车辆档案', auth: true },
  { p: '/vehicle/apply', title: '用车申请', auth: true },
  { p: '/vehicle/dispatch', title: '调度管理', auth: true },
  // 库存
  { p: '/inventory', title: '库存总览', auth: true },
  { p: '/inventory/stock', title: '库存总览', auth: true },
  { p: '/inventory/inout', title: '出入库明细', auth: true },
  { p: '/inventory/inbound-order', title: '入库单', auth: true },
  { p: '/inventory/outbound-order', title: '出库单', auth: true },
  { p: '/inventory/material-request', title: '领料单', auth: true },
  { p: '/inventory/material-return', title: '领料归还单', auth: true },
  // 财务
  { p: '/finance', title: '财务概览', auth: true },
  { p: '/finance/overview', title: '财务概览', auth: true },
  { p: '/finance/receipt', title: '收款单', auth: true },
  { p: '/finance/payment', title: '付款单', auth: true },
  { p: '/finance/receivable', title: '应收账款', auth: true },
  { p: '/finance/payable', title: '应付账款', auth: true },
  // P1
  { p: '/disk', title: '公司网盘', auth: true },
  { p: '/knowledge', title: '知识列表', auth: true },
  { p: '/knowledge/list', title: '知识列表', auth: true },
  // P2
  { p: '/screen', title: '数据大屏', auth: true },
  // 消息
  { p: '/message', title: '消息列表', auth: true },
  { p: '/message/list', title: '消息列表', auth: true },
  // 设置
  { p: '/settings', title: '组织权限', auth: true },
  { p: '/settings/profile', title: '个人信息', auth: true },
  { p: '/settings/password', title: '修改密码', auth: true },
  { p: '/settings/organization', title: '组织权限', auth: true },
  { p: '/settings/role', title: '角色管理', auth: true },
  { p: '/settings/approval', title: '审批引擎', auth: true },
  { p: '/settings/log', title: '系统日志', auth: true },
  { p: '/settings/backup', title: '数据管理', auth: true },
  // 404 期望
  { p: '/totally-invalid-route-xyz', title: '404', auth: true, expect404: true },
];

if (!fs.existsSync(SHOTS_DIR)) {
  fs.mkdirSync(SHOTS_DIR, { recursive: true });
}

async function login(page) {
  console.log('[login] navigating to /login ...');
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  // 表单已经预填 admin/admin123（见 views/login/index.vue:95-97）
  // 直接点登录按钮
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await new Promise(r => setTimeout(r, 500));
  // 截图核对
  await page.screenshot({ path: path.join(SHOTS_DIR, '_login_filled.png') });
  // 点击登录
  await page.click('button.login-btn');
  // 等跳转到 /
  try {
    await page.waitForFunction(
      () => window.location.pathname === '/',
      { timeout: 15000 }
    );
  } catch (e) {
    // 退路：手动检查
    const cur = page.url();
    console.log('[login] post-click url:', cur);
    if (!cur.endsWith(':3000/') && !cur.endsWith(':3000/dashboard')) {
      throw new Error('login failed, still at ' + cur);
    }
  }
  await new Promise(r => setTimeout(r, 1500));
  // 验证 token 存进去了
  const token = await page.evaluate(() => {
    for (const k of Object.keys(localStorage)) {
      if (k.includes('token') || k.includes('Token')) {
        return localStorage.getItem(k);
      }
    }
    for (const k of Object.keys(sessionStorage)) {
      if (k.includes('token') || k.includes('Token')) {
        return sessionStorage.getItem(k);
      }
    }
    return null;
  });
  console.log('[login] done. url:', page.url(), 'token:', token ? token.slice(0, 25) + '...' : 'NONE');
  if (!token) throw new Error('token not saved');
}

(async () => {
  console.log(`[start] launching chrome: ${CHROME}`);
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  // 收 console / pageerror / 404 资源
  const consoleErrs = [];
  const pageErrs = [];
  const failedResources = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrs.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    pageErrs.push(err.message);
  });
  page.on('requestfailed', req => {
    const url = req.url();
    if (!url.includes('favicon') && !url.includes('sockjs')) {
      failedResources.push(`${req.failure().errorText} ${url}`);
    }
  });
  page.on('response', resp => {
    if (resp.status() >= 400 && !resp.url().includes('favicon')) {
      failedResources.push(`HTTP ${resp.status()} ${resp.url()}`);
    }
  });

  // 登录
  try {
    await login(page);
  } catch (e) {
    console.error('[login] FAILED:', e.message);
    await browser.close();
    process.exit(1);
  }

  // 跑全部页面
  console.log(`\n=== 开始跑 ${PATHS.length} 个页面 ===\n`);
  const results = [];
  for (const item of PATHS) {
    const tag = item.expect404 ? '[404-期望]' : '[期望 200]';
    const url = BASE + item.p;
    const consoleBefore = consoleErrs.length;
    const pageErrBefore = pageErrs.length;
    const failResBefore = failedResources.length;
    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
      // 等真实数据回来 - 等到表格行数 > 0 或 4s 超时
      await Promise.race([
        page.waitForFunction(
          () => {
            const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row, .el-table__body tr, .el-table tr');
            const empty = document.querySelector('.el-empty, [class*="empty"]');
            // 行数 > 0 或页面有非空状态显示
            return rows.length > 0;
          },
          { timeout: 4000 }
        ).catch(() => {}),
        new Promise(r => setTimeout(r, 4000))
      ]);
      // 检查是否真的渲染（页面 div 有内容）
      const bodyText = await page.evaluate(() => document.body.innerText || '');
      // 调试输出: 列表行数 / total
      const debugInfo = await page.evaluate(() => {
        const rows = document.querySelectorAll('.el-table__body-wrapper .el-table__row, .el-table__body tr, .el-table tr');
        const pagination = document.querySelector('.el-pagination__total');
        return { rowCount: rows.length, paginationText: pagination?.innerText || '' };
      });
      console.log(`  [debug ${item.p}] rows=${debugInfo.rowCount} pagination="${debugInfo.paginationText}"`);
      const is404Page = bodyText.includes('404') && (bodyText.includes('页面不存在') || bodyText.includes('未找到') || bodyText.includes('Not Found'));
      // 截图
      const safeName = item.p.replace(/[\/\:]/g, '_');
      const shotPath = path.join(SHOTS_DIR, safeName + '.png');
      await page.screenshot({ path: shotPath, fullPage: false });
      const newConsoleErrs = consoleErrs.slice(consoleBefore);
      const newPageErrs = pageErrs.slice(pageErrBefore);
      const newFailRes = failedResources.slice(failResBefore);
      const realErrs = [...newPageErrs, ...newFailRes];
      const consoleOk = newConsoleErrs.filter(e => !e.includes('favicon'));
      let status = '✅';
      let note = `渲染(${bodyText.length}字)`;
      if (item.expect404) {
        if (is404Page) {
          status = '✅';
          note = 'NotFound 页面已渲染';
        } else {
          status = '❌';
          note = `未跳到 404 页面 (bodyText: ${bodyText.slice(0, 50)}...)`;
        }
      } else {
        if (bodyText.length < 50) {
          status = '⚠️';
          note = '页面内容过少';
        }
        if (realErrs.length > 0) {
          status = '⚠️';
          note = `错误: ${realErrs.length}条 | ${realErrs[0].slice(0, 80)}`;
        }
        if (consoleOk.length > 0 && status === '✅') {
          status = '⚠️';
          note = `console: ${consoleOk[0].slice(0, 80)}`;
        }
        // 列表页空数据检测 - 只在有表格但分页 total > 0 + 行数 = 0 时报警
        if (status === '✅' && debugInfo && debugInfo.rowCount <= 1 && debugInfo.paginationText && !debugInfo.paginationText.includes('共 0')) {
          status = '⚠️';
          note = `分页有 total (${debugInfo.paginationText}) 但无数据行`;
        }
      }
      results.push({ ...item, status, note, errCount: realErrs.length, consoleCount: consoleOk.length });
      console.log(`${status} ${tag} ${item.p.padEnd(40)} ${note}`);
    } catch (e) {
      results.push({ ...item, status: '❌', note: '加载失败: ' + e.message });
      console.log(`❌ ${tag} ${item.p.padEnd(40)} 加载失败: ${e.message.slice(0, 100)}`);
    }
  }

  // 汇总
  console.log('\n=== 汇总 ===');
  const ok200 = results.filter(r => !r.expect404 && r.status === '✅').length;
  const warn = results.filter(r => !r.expect404 && r.status === '⚠️').length;
  const fail = results.filter(r => r.status === '❌').length;
  const exp404 = results.filter(r => r.expect404);
  const exp404Ok = exp404.filter(r => r.status === '✅').length;
  const exp404Fail = exp404.filter(r => r.status === '❌').length;
  console.log(`业务路由 期望 200: ✅ ${ok200}  ⚠️ ${warn}  ❌ ${fail}`);
  console.log(`期望 404 路由: ✅ ${exp404Ok}  ❌ ${exp404Fail}`);

  // 详细警告/失败
  if (warn + fail + exp404Fail > 0) {
    console.log('\n--- 详细问题清单 ---');
    for (const r of results) {
      if (r.status !== '✅') {
        console.log(`${r.status} ${r.p.padEnd(40)} ${r.note}`);
      }
    }
  }

  // 收集所有问题
  console.log('\n--- 所有 pageerror 汇总 ---');
  const uniqPageErrs = [...new Set(pageErrs)];
  uniqPageErrs.forEach(e => console.log('  • ' + e.slice(0, 200)));

  console.log('\n--- 所有 failed resource 汇总 ---');
  const uniqFail = [...new Set(failedResources)];
  uniqFail.forEach(e => console.log('  • ' + e.slice(0, 200)));

  await browser.close();
})().catch(e => {
  console.error('FATAL:', e);
  process.exit(1);
});
