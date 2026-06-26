"""
E2E 验证 - 客户详情 编辑客户 对话框的联系人管理

流程:
1. 登录 -> 客户列表 -> 进入客户详情
2. 点 "编辑客户" 打开弹窗
3. 验证 "联系人" 区有初始主联系人行
4. 点 "添加联系人" -> 出现新行 (姓名/职务/电话 3 个 input)
5. 填新联系人 -> 保存
6. 验证: 联系人数量从 1 变 2, 详情页面显示新联系人
7. 再点编辑 -> 删除新联系人 -> 保存
8. 验证: 联系人数量变 1
"""
import sys
from playwright.sync_api import sync_playwright, expect

WEB = 'http://192.168.3.117'
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
        print('   登录后 url:', page.url)

        # 2) 直接进客户详情 (id=42)
        print('[2] 客户详情 (id=42)')
        page.goto(f'{WEB}/customer/{CUSTOMER_ID}', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(2000)

        # 记录保存前联系人数量 (从主页面 BasicInfoTab 抓, 跳过 — 我们用 API 验证)

        # 3) 点 "编辑客户"
        print('[3] 点 "编辑客户" 按钮')
        page.locator('button:visible:has-text("编辑客户")').first.click()
        page.wait_for_timeout(1500)
        # 验证弹窗
        dialog = page.locator('.el-dialog:visible:has-text("编辑客户")')
        assert dialog.count() > 0, '编辑客户弹窗没打开'
        print('   弹窗已打开')

        # 4) 验证 "联系人" 区有行
        print('[4] 验证联系人行 (姓名/职务/电话)')
        contact_rows = page.locator('.contact-row')
        row_count = contact_rows.count()
        print(f'   联系人行数: {row_count}')
        assert row_count >= 1, f'联系人行数 {row_count} < 1'

        # 5) 点 "添加联系人" -> 多出一行
        print('[5] 点 "添加联系人" 按钮')
        page.locator('button:visible:has-text("添加联系人")').first.click()
        page.wait_for_timeout(500)
        new_count = page.locator('.contact-row').count()
        print(f'   添加后行数: {new_count}')
        assert new_count == row_count + 1, f'行数没增加 ({row_count} -> {new_count})'

        # 6) 填新行
        print('[6] 填新联系人数据')
        new_row = page.locator('.contact-row').nth(new_count - 1)
        # 第 1 个 input=姓名, 第 2 个=职务, 第 3 个=电话
        new_row_inputs = new_row.locator('input')
        print(f'   新行 input 数: {new_row_inputs.count()}')
        new_row_inputs.nth(0).fill('E2E新增联系人')
        new_row_inputs.nth(1).fill('E2E测试经理')
        new_row_inputs.nth(2).fill('13900005555')
        page.wait_for_timeout(500)
        page.screenshot(path='D:/work/website/OA/.workbuddy/_add_contact_filled.png')

        # 7) 截图 + 保存
        print('[7] 保存修改')
        page.locator('.el-dialog:visible button:has-text("保存修改")').click()
        page.wait_for_timeout(3000)
        page.screenshot(path='D:/work/website/OA/.workbuddy/_add_contact_saved.png')

        # 8) 验证联系人列表里出现新联系人
        print('[8] 验证新联系人已保存')
        page.wait_for_timeout(2000)
        # API 验证更可靠
        import requests
        r = requests.post(f'{WEB}:8081/api/auth/login', json={'username': USER, 'password': PASS}, timeout=10)
        tok = r.json()['data']['token']
        r2 = requests.get(f'{WEB}:8081/api/customers/{CUSTOMER_ID}/contacts',
                          headers={'Authorization': f'Bearer {tok}'}, timeout=10)
        contacts = r2.json().get('data', [])
        names = [c.get('name') for c in contacts]
        print(f'   API contacts names: {names}')
        assert any('E2E新增联系人' in n for n in names), f'新联系人没保存: {names}'

        # 9) 再编辑 + 删除新联系人
        print('[9] 再编辑, 删除新增的联系人')
        page.goto(f'{WEB}/customer/{CUSTOMER_ID}', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)
        page.locator('button:visible:has-text("编辑客户")').first.click()
        page.wait_for_timeout(1500)
        # 应该看到 2 行 (主 + 新增)
        rows = page.locator('.contact-row')
        nrows = rows.count()
        print(f'   编辑时联系人行数: {nrows}')
        assert nrows == 2, f'预期 2 行, 实际 {nrows}'

        # 找 E2E新增联系人 那一行, 点它的删除按钮
        for i in range(nrows):
            row = rows.nth(i)
            name_input = row.locator('input').first
            val = name_input.input_value()
            if 'E2E新增联系人' in val:
                print(f'   找到 E2E 行 (index {i})')
                row.locator('button:has-text("删除")').click()
                page.wait_for_timeout(500)
                break

        page.screenshot(path='D:/work/website/OA/.workbuddy/_add_contact_deleted.png')

        # 10) 保存
        print('[10] 保存删除')
        page.locator('.el-dialog:visible button:has-text("保存修改")').click()
        page.wait_for_timeout(3000)

        # 11) 验证 API
        r3 = requests.get(f'{WEB}:8081/api/customers/{CUSTOMER_ID}/contacts',
                          headers={'Authorization': f'Bearer {tok}'}, timeout=10)
        contacts2 = r3.json().get('data', [])
        names2 = [c.get('name') for c in contacts2]
        print(f'   删除后 contacts names: {names2}')
        assert not any('E2E新增联系人' in n for n in names2), f'联系人没删掉: {names2}'

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
        print('✅ 联系人增删功能 E2E 验证全过')
        print('======================================')
        browser.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        sys.exit(1)
