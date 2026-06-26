#!/usr/bin/env node
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
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push('PAGE: ' + e.message));
  page.on('response', r => { if (r.url().includes('/api/') && r.status() >= 400) errs.push('HTTP ' + r.status() + ' ' + r.url().replace(BASE, '')); });

  // 登录
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2' });
  await page.waitForSelector('button.login-btn');
  await sleep(500);
  await page.click('button.login-btn');
  await page.waitForFunction(() => ['/', '/dashboard'].includes(location.pathname), { timeout: 15000 });
  await sleep(1000);

  // 1) 分类管理页
  console.log('=== 分类管理 ===');
  await page.goto(BASE + '/inventory/category', { waitUntil: 'networkidle2' });
  await sleep(3000);
  await page.screenshot({ path: path.join(SHOTS, '_inv_category_expand.png'), fullPage: false });
  // 抓 tree 节点
  const treeInfo = await page.evaluate(() => {
    const nodes = document.querySelectorAll('.el-tree-node');
    const data = [];
    nodes.forEach(n => {
      const label = n.querySelector('.tree-name')?.innerText?.trim();
      const code = n.querySelector('.tree-code')?.innerText?.trim();
      const count = n.querySelector('.tree-count')?.innerText?.trim();
      data.push({ label, code, count });
    });
    return data;
  });
  console.log('  tree nodes:', treeInfo.length);
  treeInfo.forEach(n => console.log('  -', n.label, n.code || '', n.count || ''));

  // 2) 新增顶级分类
  console.log('\n=== 新增顶级分类 ===');
  const newBtn = await page.evaluateHandle(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) if (b.innerText.trim().includes('新增顶级分类')) return b;
    return null;
  });
  if (newBtn && newBtn.asElement()) {
    await newBtn.asElement().click();
    await sleep(1000);
    // 填名字
    await page.evaluate(() => {
      const inputs = document.querySelectorAll('.el-dialog .el-input__inner');
      for (const inp of inputs) {
        if (inp.placeholder?.includes('监控设备')) {
          inp.value = '测试分类A'; inp.dispatchEvent(new Event('input', {bubbles:true}));
        }
      }
    });
    await sleep(500);
    await page.screenshot({ path: path.join(SHOTS, '_inv_category_dialog.png') });
    await page.evaluate(() => {
      const btns = document.querySelectorAll('.el-dialog .el-button');
      for (const b of btns) if (b.innerText.trim() === '保存') { b.click(); break; }
    });
    await sleep(2000);
    // 重新看 tree
    const afterAdd = await page.evaluate(() => {
      const nodes = document.querySelectorAll('.el-tree-node .tree-name');
      return Array.from(nodes).map(n => n.innerText.trim());
    });
    console.log('  after add tree:', afterAdd);
  } else {
    console.log('  ❌ NOT FOUND 新增顶级分类 button');
  }

  // 3) 全部折叠
  console.log('\n=== 全部折叠 ===');
  const collapseBtn = await page.evaluateHandle(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) if (b.innerText.trim().includes('全部折叠')) return b;
    return null;
  });
  if (collapseBtn && collapseBtn.asElement()) {
    await collapseBtn.asElement().click();
    await sleep(1000);
    await page.screenshot({ path: path.join(SHOTS, '_inv_category_collapse.png') });
    // 查可见节点 (折叠后应该只看得到根)
    const collapsed = await page.evaluate(() => {
      const visible = document.querySelectorAll('.el-tree-node:not(.is-leaf)');
      return Array.from(visible).map(n => n.querySelector('.tree-name')?.innerText?.trim()).filter(Boolean);
    });
    console.log('  visible after collapse:', collapsed);
  }

  // 4) 删除测试分类A
  console.log('\n=== 删除测试分类A ===');
  await page.evaluate(() => {
    const buttons = document.querySelectorAll('button');
    for (const b of buttons) {
      if (b.innerText.trim().includes('全部展开')) { b.click(); break; }
    }
  });
  await sleep(1000);
  const delBtn = await page.evaluateHandle(() => {
    const nodes = document.querySelectorAll('.el-tree-node');
    for (const n of nodes) {
      if (n.innerText.includes('测试分类A')) {
        const btns = n.querySelectorAll('button');
        for (const b of btns) if (b.innerText.trim() === '删除') return b;
      }
    }
    return null;
  });
  if (delBtn && delBtn.asElement()) {
    await delBtn.asElement().click();
    await sleep(800);
    // 确认 popconfirm
    await page.evaluate(() => {
      const btns = document.querySelectorAll('.el-popconfirm .el-button--primary');
      for (const b of btns) if (b.innerText.trim() === '确定') { b.click(); break; }
    });
    await sleep(2000);
    const afterDel = await page.evaluate(() => {
      const nodes = document.querySelectorAll('.el-tree-node .tree-name');
      return Array.from(nodes).map(n => n.innerText.trim());
    });
    console.log('  after delete tree:', afterDel);
  } else {
    console.log('  ❌ NOT FOUND 测试分类A delete button');
  }

  console.log('\nall errs:', errs.length, errs.slice(0, 5));
  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
