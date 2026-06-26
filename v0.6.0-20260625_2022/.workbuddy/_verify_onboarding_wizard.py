"""验证：117 入职档案 → 办理入职 3 步流程能完整走通（修复 form1Ref 冲突）"""
import paramiko
from playwright.sync_api import sync_playwright

API = 'http://192.168.3.117'
WEB = 'http://192.168.3.117'
USER = 'admin'
PASS = 'admin123'

# 1) 后端预热：登录拿 token
ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', username='nbcy', password='admin123', timeout=10)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 1366, 'height': 800})
    page = ctx.new_page()

    # 收集 console 错误
    errors = []
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'PAGEERROR: {e}'))

    print('[1] open login page...')
    page.goto(WEB, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(3000)
    page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_login.png')
    print('   current url:', page.url)
    print('   title:', page.title())
    # 只取可见的 input
    inps = page.locator('input:visible')
    print('   visible inputs found:', inps.count())
    inps.nth(0).click()
    inps.nth(0).fill(USER)
    inps.nth(1).click()
    inps.nth(1).fill(PASS)
    page.wait_for_timeout(500)
    page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_login_filled.png')
    # 用 keyboard Enter 提交
    page.keyboard.press('Enter')
    page.wait_for_load_state('networkidle', timeout=15000)
    page.wait_for_timeout(2000)
    print('   after login url:', page.url)

    print('[2] go to /employee/onboardings...')
    page.goto(f'{WEB}/employee/onboardings', wait_until='networkidle', timeout=20000)
    page.wait_for_timeout(1500)
    page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_onboard_step0.png')

    print('[3] click "办理入职" button...')
    # 找按钮：含"办理入职"或"新办入职"
    btn = None
    for sel in ['button:has-text("办理入职")', 'button:has-text("新办入职")', 'button:has-text("新 建")']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                break
        except Exception:
            continue
    if not btn:
        # 兜底：找顶部"+"或新建按钮
        page.locator('button.el-button--primary').first.click()

    page.wait_for_timeout(1000)
    page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_onboard_step1.png')

    print('[4] fill step1: 账号信息...')
    # 必填：登录账号、姓名 — 用 :visible
    inps = page.locator('.el-dialog input:visible')
    print('   dialog visible inputs:', inps.count())
    inps.nth(0).fill('test_wizard_001')   # 登录账号
    inps.nth(1).fill('测试向导')           # 姓名
    inps.nth(2).fill('13800138000')       # 手机号
    inps.nth(3).fill('wizard_test@oa.com') # 邮箱
    page.wait_for_timeout(300)
    page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_onboard_step1_filled.png')

    print('[5] click 下一步...')
    page.locator('.el-dialog button:has-text("下一步"):visible').click()
    page.wait_for_timeout(1500)
    page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_onboard_step2.png')

    # 验证 step2 是否出现
    step2_visible = page.locator('.el-dialog :text("入职日期")').first.is_visible(timeout=2000)
    print('   step2 入职日期 visible:', step2_visible)

    if not step2_visible:
        print('!! BUG STILL: 下一步没切到 step2 !!')
        print('   错误条数:', len(errors))
        for e in errors[:10]: print('   ERR:', e)
    else:
        print('[6] fill step2: 岗位信息...')
        # 入职日期
        page.locator('.el-dialog input[placeholder*="选择日期"]').first.fill('2026-07-01')
        page.keyboard.press('Enter')
        page.wait_for_timeout(300)

        # 部门
        page.locator('.el-dialog .el-select').first.click()
        page.wait_for_timeout(800)
        opts = page.locator('.el-select-dropdown__item:visible')
        if opts.count() > 0:
            opts.first.click()
        page.wait_for_timeout(500)

        # 岗位
        page.locator('.el-dialog .el-select').nth(1).click()
        page.wait_for_timeout(800)
        opts = page.locator('.el-select-dropdown__item:visible')
        if opts.count() > 0:
            opts.first.click()
        page.wait_for_timeout(500)
        page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_onboard_step2_filled.png')

        print('[7] click 下一步 → step3...')
        page.locator('.el-dialog button:has-text("下一步"):visible').click()
        page.wait_for_timeout(1500)
        page.screenshot(path='D:/work/website/OA/.workbuddy/_verify_onboard_step3.png')

        step3_visible = page.locator('.el-dialog :text("身份证号")').first.is_visible(timeout=2000)
        print('   step3 身份证号 visible:', step3_visible)

    print('=== console errors ===')
    for e in errors[:15]:
        print(' ', e)
    print('=== total errors:', len(errors), '===')

    browser.close()
print('DONE')
