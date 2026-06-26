#!/usr/bin/env node
const puppeteer = require('puppeteer-core');
const path = require('path');

const BASE = 'http://172.20.0.139:3000';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  await page.goto(BASE + '/login', { waitUntil: 'networkidle2' });
  await page.waitForSelector('button.login-btn');
  await page.click('button.login-btn');
  await new Promise(r => setTimeout(r, 3000));
  console.log('login url:', page.url());

  const PATHS = ['/opp/48/quote', '/opp/47/quote', '/opp/43/quote', '/opp/32/quote', '/opp/30/quote',
    '/quote/18', '/quote/17', '/quote/16', '/quote/list'];
  for (const p of PATHS) {
    await page.goto(BASE + p, { waitUntil: 'networkidle2', timeout: 15000 });
    await new Promise(r => setTimeout(r, 2000));
    const txt = await page.evaluate(() => document.body.innerText || '');
    const has404 = txt.includes('404') && txt.includes('页面不存在');
    const safe = p.replace(/[\/\:]/g, '_');
    await page.screenshot({ path: `D:/work/website/OA/.workbuddy/shots/v039p1/probe${safe}.png` });
    console.log(`${has404 ? '❌' : '✅'} ${p.padEnd(25)} text=${txt.length.toString().padStart(4)}`);
  }
  await browser.close();
})();
