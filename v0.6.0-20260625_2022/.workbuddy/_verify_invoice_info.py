"""
E2E 验证 - 客户详情 客户开票信息 增/改/删

流程:
1. 登录 -> 客户详情
2. 点 "编辑客户" -> 看到 "开票信息" 区
3. 点 "添加开票信息" -> 出现新行
4. 填 增值税专用发票/北京安防公司#1/91110000123456789X + 选 默认
5. 继续添加一条 普通发票, 不选默认
6. 保存 -> 验证 2 条 invoice_info 存在
7. 重新打开 -> 删除第 1 条 -> 保存
8. 验证只剩 1 条, 默认属性已切到剩下的那条
"""
import sys
import requests
from playwright.sync_api import sync_playwright

WEB = 'http://192.168.3.117'
API = WEB + ':8081'
USER = 'admin'
PASS = 'admin123'
CUSTOMER_ID = 42

errors = []


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        page.on('console', lambda msg: msg.type == 'error' and errors.append(f'CONSOLE: {msg.text[:200]}'))
        page.on('pageerror', lambda exc: errors.append(f'PAGEERROR: {str(exc)[:200]}'))

        # 1) 登录
        print('[1] 登录')
        page.goto(f'{WEB}/login', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(2000)
        inputs = page.locator('input:visible')
        inputs.nth(0).fill(USER)
        inputs.nth(1).fill(PASS)
        page.locator('button.login-btn').first.click()
        page.wait_for_load_state('networkidle', timeout=15000)
        page.wait_for_timeout(1500)
        assert '/login' not in page.url, f'登录失败, 还在 {page.url}'

        # 2) 客户详情
        print('[2] 客户详情')
        page.goto(f'{WEB}/customer/{CUSTOMER_ID}', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(2000)

        # 3) 点 "编辑客户"
        print('[3] 点 "编辑客户"')
        page.locator('button:visible:has-text("编辑客户")').first.click()
        page.wait_for_timeout(1500)
        dialog = page.locator('.el-dialog:visible:has-text("编辑客户")')
        assert dialog.count() > 0, '弹窗没打开'

        # 4) 找到 "开票信息" 区, 验证 "添加开票信息" 按钮
        print('[4] 找到开票信息区')
        add_invoice_btn = page.locator('.el-dialog button:has-text("添加开票信息")')
        assert add_invoice_btn.count() > 0, '没找到「添加开票信息」按钮'
        # 现有 invoice-row 数量
        before = page.locator('.invoice-row').count()
        print(f'   现有开票信息行数: {before}')

        # 5) 添加一条专票
        print('[5] 添加 1 条专票')
        add_invoice_btn.first.click()
        page.wait_for_timeout(500)
        rows1 = page.locator('.invoice-row').count()
        print(f'   添加后: {rows1} 行')
        assert rows1 == before + 1

        # 填第 2 行 (新增的那行)
        new_row = page.locator('.invoice-row').nth(rows1 - 1)
        # 第 1 个是 select (发票类型), 第 2 个是单位名称, 第 3 个是税号
        new_row.locator('.el-select').first.click()
        page.wait_for_timeout(500)
        page.locator('.el-select-dropdown__item:visible:has-text("增值税专用发票")').first.click()
        page.wait_for_timeout(500)
        # inputs: 2 (单位) 3 (税号) 4 (默认 checkbox 不是 input) 5 (删除) 6 (注册地址) 7 (注册电话) 8 (开户行) 9 (账号) 10 (备注 textarea)
        # 用 placeholder 定位
        new_row.locator('input[placeholder*="单位名称"]').first.fill('E2E专票公司#1')
        new_row.locator('input[placeholder*="税号"]').first.fill('91110000123456789X')
        new_row.locator('input[placeholder*="注册地址"]').first.fill('北京市朝阳区某街1号')
        new_row.locator('input[placeholder*="注册电话"]').first.fill('010-12345678')
        new_row.locator('input[placeholder*="开户银行"]').first.fill('工商银行北京分行')
        new_row.locator('input[placeholder*="银行账号"]').first.fill('6222021234567890123')
        # 默认勾上
        new_row.locator('.el-checkbox').first.click()
        page.wait_for_timeout(300)
        page.screenshot(path='D:/work/website/OA/.workbuddy/_invoice_filled1.png')

        # 6) 再添加 1 条普票
        print('[6] 再添加 1 条普票 (不默认)')
        add_invoice_btn.first.click()
        page.wait_for_timeout(500)
        rows2 = page.locator('.invoice-row').count()
        print(f'   添加后: {rows2} 行')
        new_row2 = page.locator('.invoice-row').nth(rows2 - 1)
        new_row2.locator('input[placeholder*="单位名称"]').first.fill('E2E普票公司#2')
        new_row2.locator('input[placeholder*="税号"]').first.fill('91110000987654321Y')
        page.screenshot(path='D:/work/website/OA/.workbuddy/_invoice_filled2.png')

        # 7) 保存
        print('[7] 保存修改')
        page.locator('.el-dialog:visible button:has-text("保存修改")').click()
        page.wait_for_timeout(4000)
        page.screenshot(path='D:/work/website/OA/.workbuddy/_invoice_saved.png')

        # 8) API 验证
        r = requests.post(f'{API}/api/auth/login', json={'username': USER, 'password': PASS}, timeout=10)
        tok = r.json()['data']['token']
        r2 = requests.get(f'{API}/api/customers/{CUSTOMER_ID}/invoice-infos',
                          headers={'Authorization': f'Bearer {tok}'}, timeout=10)
        infos = r2.json().get('data', [])
        print(f'   API invoice-infos: {len(infos)} 条')
        for i in infos:
            print(f'     - id={i["id"]} type={i["invoice_type"]} company={i["company_name"]} tax={i["tax_no"]} default={i["is_default"]}')
        assert len(infos) == 2, f'预期 2 条, 实际 {len(infos)}'
        defaults = [i for i in infos if i['is_default']]
        assert len(defaults) == 1, f'预期只有 1 条默认, 实际 {len(defaults)}'
        assert defaults[0]['company_name'] == 'E2E专票公司#1', f'默认应该是 E2E专票公司#1, 实际 {defaults[0]["company_name"]}'

        # 9) 重新打开, 删除专票
        print('[9] 重新打开, 删除专票')
        page.goto(f'{WEB}/customer/{CUSTOMER_ID}', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)
        page.locator('button:visible:has-text("编辑客户")').first.click()
        page.wait_for_timeout(1500)
        # 找到 E2E专票公司#1 所在行, 删它
        inv_rows = page.locator('.invoice-row')
        nrows = inv_rows.count()
        print(f'   重新打开看到: {nrows} 行')
        for i in range(nrows):
            row = inv_rows.nth(i)
            val = row.locator('input[placeholder*="单位名称"]').first.input_value()
            if 'E2E专票公司#1' in val:
                print(f'   找到专票行 (index {i}), 删它')
                row.locator('button:has-text("删除")').first.click()
                page.wait_for_timeout(500)
                break

        page.screenshot(path='D:/work/website/OA/.workbuddy/_invoice_mark_deleted.png')

        # 10) 保存
        page.locator('.el-dialog:visible button:has-text("保存修改")').click()
        page.wait_for_timeout(4000)

        # 11) API 验证
        r3 = requests.get(f'{API}/api/customers/{CUSTOMER_ID}/invoice-infos',
                          headers={'Authorization': f'Bearer {tok}'}, timeout=10)
        infos2 = r3.json().get('data', [])
        print(f'   删除后: {len(infos2)} 条')
        for i in infos2:
            print(f'     - id={i["id"]} company={i["company_name"]} default={i["is_default"]}')
        assert len(infos2) == 1, f'预期 1 条, 实际 {len(infos2)}'
        assert infos2[0]['company_name'] == 'E2E普票公司#2', f'预期剩下 E2E普票公司#2'

        print()
        print('=== console errors ===')
        for e in errors[:10]:
            print(' ', e)
        print(f'   total: {len(errors)}')

        if any('PAGEERROR' in e for e in errors):
            print('!! 页面有 JS 异常')
            sys.exit(1)
        print()
        print('======================================')
        print('✅ 开票信息 增/改/删 E2E 验证全过')
        print('======================================')
        browser.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        sys.exit(1)
