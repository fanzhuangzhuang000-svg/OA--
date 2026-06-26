"""Task 2: 172 前端路由 Puppeteer 测试"""
import asyncio
from playwright.async_api import async_playwright
import os, json, time

ROUTES = [
    ('/dashboard', '工作台'),
    ('/attendance', '考勤管理'),
    ('/employee', '员工管理'),
    ('/customer', '客户管理'),
    ('/project', '项目管理'),
    ('/project/board', '项目看板'),
    ('/project/calendar', '项目日历'),
    ('/service', '售后服务'),
    ('/finance', '财务概览'),
    ('/finance/receivable', '应收账款'),
    ('/finance/payable', '应付账款'),
    ('/vehicle', '车辆管理'),
    ('/inventory', '库存管理'),
    ('/training', '培训管理'),
    ('/approval/center', '审批中心'),
    ('/approval/finance', '财务审批'),
    ('/approval/operation', '运营审批'),
    ('/approval/project', '项目审批'),
    ('/purchase', '采购管理'),
    ('/purchase/requirement', '采购需求'),
    ('/purchase/plan', '采购计划'),
    ('/purchase/approval', '采购审批'),
    ('/purchase/payment-request', '付款申请'),
    ('/purchase/payment', '付款管理'),
    ('/purchase/contract', '采购合同'),
    ('/purchase/shipment', '发货管理'),
    ('/purchase/logistics', '物流跟踪'),
    ('/disk', '公司网盘'),
    ('/knowledge', '知识库'),
    ('/message', '消息中心'),
    ('/vehicle-usage', '用车管理'),
    ('/settings', '系统设置'),
]

SHOT_DIR = r'D:\work\website\OA\.workbuddy\shots\qa-2026-06-19'
os.makedirs(SHOT_DIR, exist_ok=True)

BASE = 'http://172.20.0.139:18080'
API = 'http://172.20.0.139:3001'

async def main():
    results = []
    console_errors_total = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()

        console_errors = []
        page.on('console', lambda msg: console_errors.append(f'{msg.type}:{msg.text}') if msg.type == 'error' else None)

        # 登录（API 在 3001 端口，跨域所以用 Playwright request）
        try:
            await page.goto(f'{BASE}/', timeout=15000)
            await page.wait_for_timeout(1000)
            # Playwright 跨域请求
            api_resp = await ctx.request.post(f'{API}/api/auth/login', data={'username': 'admin', 'password': 'admin123'})
            j = await api_resp.json()
            token = j.get('data', {}).get('token') if j.get('data') else None
            if token:
                # 写到 localStorage（前端用 token 做认证）
                await page.evaluate(f'localStorage.setItem("token", "{token}")')
                # 同时尝试常见 key
                for k in ['oa_token', 'auth_token', 'access_token']:
                    await page.evaluate(f'localStorage.setItem("{k}", "{token}")')
                print(f'Token: {token[:30]}...')
            else:
                print(f'NO TOKEN: {j}')
        except Exception as e:
            print(f'Login error: {e}')
            await browser.close()
            return

        # 测每个路由
        for path, name in ROUTES:
            url = f'{BASE}{path}'
            errors_before = len(console_errors)
            try:
                resp = await page.goto(url, timeout=15000, wait_until='networkidle')
                status = resp.status if resp else 0
                await page.wait_for_timeout(500)
                # 检查关键内容
                content = await page.content()
                has_content = len(content) > 1000
                title = await page.title()
                # 截图
                shot_name = path.replace('/', '_').strip('_') or 'root'
                shot_path = f'{SHOT_DIR}\\{shot_name}.png'
                await page.screenshot(path=shot_path, full_page=False)

                ok = status == 200 and has_content
                results.append({
                    'path': path,
                    'name': name,
                    'status': status,
                    'has_content': has_content,
                    'title': title,
                    'shot': shot_path,
                    'console_errors': len(console_errors) - errors_before,
                    'ok': ok,
                })
                mark = '✅' if ok else '❌'
                print(f'{mark} {path} → {status} (errors: {len(console_errors) - errors_before})')
            except Exception as e:
                results.append({
                    'path': path,
                    'name': name,
                    'status': 0,
                    'has_content': False,
                    'error': str(e)[:100],
                    'ok': False,
                })
                print(f'❌ {path} → EXCEPTION: {str(e)[:80]}')

        console_errors_total = len(console_errors)
        await browser.close()

    passed = sum(1 for r in results if r['ok'])
    print(f'\n=== 路由测试结果 ===')
    print(f'总路由: {len(ROUTES)}')
    print(f'通过: {passed}')
    print(f'失败: {len(ROUTES) - passed}')
    print(f'通过率: {passed/len(ROUTES)*100:.1f}%')
    print(f'console 错误总数: {console_errors_total}')
    if console_errors:
        print(f'错误样本: {console_errors[:5]}')

    # 写报告
    with open(r'D:\work\website\OA\.workbuddy\qa-route-2026-06-19.md', 'w', encoding='utf-8') as f:
        f.write(f'# 172 前端路由 QA 测试报告\n\n')
        f.write(f'**测试时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f'**总路由**: {len(ROUTES)}\n')
        f.write(f'**通过**: {passed}\n')
        f.write(f'**失败**: {len(ROUTES) - passed}\n')
        f.write(f'**通过率**: {passed/len(ROUTES)*100:.1f}%\n')
        f.write(f'**Console 错误**: {console_errors_total}\n\n')
        f.write(f'## 详细结果\n\n')
        f.write(f'| 路由 | 名称 | 状态 | 内容 | Console 错误 | 通过 |\n')
        f.write(f'|------|------|------|------|------|------|\n')
        for r in results:
            mark = '✅' if r['ok'] else '❌'
            f.write(f"| {r['path']} | {r['name']} | {r.get('status', 'EXCEPTION')} | {'Y' if r.get('has_content') else 'N'} | {r.get('console_errors', '-')} | {mark} |\n")
        f.write(f'\n## 失败路由\n\n')
        for r in results:
            if not r['ok']:
                f.write(f"- **{r['path']}** ({r['name']}): {r.get('error', 'status=' + str(r.get('status')))[:120]}\n")
    print('Report saved: .workbuddy/qa-route-2026-06-19.md')

asyncio.run(main())
