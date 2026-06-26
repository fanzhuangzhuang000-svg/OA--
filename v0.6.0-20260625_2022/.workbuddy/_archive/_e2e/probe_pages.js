#!/usr/bin/env node
/**
 * 探索前端 vue-router 实际路径 (通过 puppeteer 访问 + console 错误)
 */
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const BASE = 'http://172.20.0.139:3000';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SHOTS_DIR = 'D:/work/website/OA/.workbuddy/shots/v039p1';

const PATHS = [
  '/lead/list', '/lead/board', '/lead',
  '/opp/list', '/opp/board', '/opp',
  '/quote/list', '/quote', '/opp/32/quote',
  '/referrer/list', '/referrer',
  '/project/pool',
  '/sales/leads', '/sales/leads/board', '/sales/opps', '/sales/opps/board',
  '/sales/quotes', '/sales/referrers', '/sales/pool',
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await page.waitForSelector('button.login-btn', { timeout: 10000 });
  await page.click('button.login-btn');
  await new Promise(r => setTimeout(r, 3000));
  console.log('登录点击完成，URL=' + page.url());

  for (const p of PATHS) {
    const consoleErrs = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrs.push(msg.text());
    });
    await page.goto(BASE + p, { waitUntil: 'networkidle2', timeout: 15000 });
    await new Promise(r => setTimeout(r, 1500));
    const bodyText = await page.evaluate(() => document.body.innerText || '');
    const has404 = bodyText.includes('404') && (bodyText.includes('页面不存在') || bodyText.includes('抱歉'));
    const hasContent = bodyText.length > 50 && !has404;
    const safeName = p.replace(/[\/\:]/g, '_');
    const shotPath = path.join(SHOTS_DIR, `probe${safeName}.png`);
    await page.screenshot({ path: shotPath, fullPage: false });
    console.log(`${hasContent ? '✅' : '❌'} ${p.padEnd(28)} text=${bodyText.length.toString().padStart(4)} has404=${has404}  shot=${path.basename(shotPath)}`);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
