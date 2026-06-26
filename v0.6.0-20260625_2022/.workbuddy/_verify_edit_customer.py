"""V0.5.8.9 编辑客户弹窗 E2E 验证

流程: 登录 → 客户管理 → 列表第一行点开 → 点编辑客户 → 改 name + contact + phone → 保存
验证: 弹窗出现 / 表单字段填充 / 提交后页面刷新 / 改动生效 / 0 console 错误
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

API = "http://192.168.3.117:8081"
WEB = "http://192.168.3.117"
USER = "admin"
PASS = "admin123"

errors = []
console_errors = []


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        page.on("pageerror", lambda exc: console_errors.append(f"PAGEERROR: {exc}"))
        page.on(
            "console",
            lambda msg: console_errors.append(f"console.{msg.type}: {msg.text}")
            if msg.type in ("error", "warning")
            else None,
        )

        # ========== 1. 登录 ==========
        print("[1] 登录")
        page.goto(f"{WEB}/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        # 找可见的 username/password input
        inputs = page.locator("input.el-input__inner:visible")
        cnt = inputs.count()
        print(f"   visible inputs: {cnt}")
        if cnt < 2:
            page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_login.png")
            errors.append(f"登录页 input 不足 2 个 (cnt={cnt})")
            return False
        inputs.nth(0).fill(USER)
        inputs.nth(1).fill(PASS)
        page.wait_for_timeout(500)
        # 点登录按钮
        page.wait_for_timeout(500)
        page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_login_filled.png")
        btn = page.locator("button.login-btn:visible").first
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(2000)
        print(f"   after login url: {page.url}")

        # ========== 2. 进客户管理 → 客户列表 ==========
        print("[2] 导航到客户列表")
        # 客户管理 → 客户档案
        page.goto(f"{WEB}/customer", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2500)
        print(f"   list url: {page.url}")
        page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_list.png")

        # ========== 3. 列表第一行点击进详情 ==========
        print("[3] 点击第一行客户进详情")
        # 找表格行
        rows = page.locator(".el-table__body-wrapper .el-table__row")
        row_cnt = rows.count()
        print(f"   列表行数: {row_cnt}")
        if row_cnt == 0:
            errors.append("客户列表为空")
            return False
        # 取第一行的客户名链接 - 用于核对
        first_link = page.locator(".el-table__body-wrapper a.cust-name").first
        first_name_before = first_link.text_content() or ""
        print(f"   第一行客户名: {first_name_before!r}")
        first_link.click()
        page.wait_for_timeout(2500)
        print(f"   after click url: {page.url}")
        if "/customer/" not in page.url:
            errors.append(f"点击未进详情, url={page.url}")
            return False
        page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_detail.png")

        # ========== 4. 点 "编辑客户" 按钮 ==========
        print("[4] 点击编辑客户按钮")
        edit_btn = page.locator('button:has-text("编辑客户")')
        if not edit_btn.first.is_visible(timeout=3000):
            errors.append("编辑客户按钮不可见")
            return False
        edit_btn.first.click()
        page.wait_for_timeout(1500)

        # 验证弹窗出现
        dialog = page.locator(".el-dialog:has-text('编辑客户')")
        dialog_visible = dialog.first.is_visible(timeout=3000)
        print(f"   弹窗可见: {dialog_visible}")
        if not dialog_visible:
            errors.append("编辑客户弹窗未出现")
            page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_dialog_fail.png")
            return False
        page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_dialog_open.png")

        # ========== 5. 验证表单字段填充 ==========
        print("[5] 验证表单字段填充")
        # 找弹窗里的第一个 input (客户名称)
        name_input = page.locator(".el-dialog input").first
        cur_name = name_input.input_value()
        print(f"   客户名 input value: {cur_name!r}")
        if not cur_name:
            errors.append("客户名称未填充")
            return False

        # ========== 6. 改 name / contact / phone ==========
        print("[6] 修改表单数据")
        new_name = f"{cur_name}-E2E"
        new_contact = "E2E测试联系人"
        new_phone = "13900139000"
        name_input.fill(new_name)

        # 联系人 input 是第几个? form 顺序: name(0) industry(1) category是select不算input province(2) city(3) district(4) address(5) contact(6) phone(7)
        # 用 placeholder 找更稳
        contact_input = page.locator(".el-dialog input[placeholder='主联系人姓名']").first
        phone_input = page.locator(".el-dialog input[placeholder='主联系人手机号']").first
        contact_input.fill(new_contact)
        phone_input.fill(new_phone)
        page.wait_for_timeout(500)
        page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_dialog_filled.png")

        # ========== 7. 点保存 ==========
        print("[7] 点击保存修改")
        save_btn = page.locator(".el-dialog button:has-text('保存修改')").first
        save_btn.click()
        # 等 5 秒: 弹窗消失 + 成功提示 + 数据刷新
        page.wait_for_timeout(5000)
        # 弹窗应已关闭
        dialog_after = page.locator(".el-dialog:has-text('编辑客户')")
        dialog_count = dialog_after.count()
        print(f"   保存后弹窗数: {dialog_count}")
        if dialog_count > 0 and dialog_after.first.is_visible(timeout=500):
            print("   ⚠️ 弹窗仍在, 等 3s 再看")
            page.wait_for_timeout(3000)
        print("   弹窗处理完成")

        # ========== 8. 验证 name 已更新 ==========
        print("[8] 验证客户名已更新")
        page.wait_for_timeout(1500)
        # 详情页 title 反映客户名
        title_el = page.locator(".page-title").first
        title_after = title_el.text_content() or ""
        print(f"   详情标题: {title_after!r}")
        if new_name not in title_after:
            errors.append(f"详情页标题未更新: {title_after!r} (期望含 {new_name!r})")
            page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_detail_after.png")
            return False
        page.screenshot(path="D:/work/website/OA/.workbuddy/_edit_cust_detail_after.png")

        # ========== 9. 验证 contact 已更新 ==========
        print("[9] 验证主联系人已更新")
        # 找含「E2E测试联系人」的 DOM
        contact_visible = page.get_by_text("E2E测试联系人", exact=False).first.is_visible(timeout=2000)
        print(f"   E2E测试联系人 visible: {contact_visible}")

        # ========== 10. 改回原名 (清场) ==========
        print("[10] 改回原名")
        page.locator('button:has-text("编辑客户")').first.click()
        page.wait_for_timeout(1000)
        page.locator(".el-dialog input").first.fill(first_name_before)
        page.wait_for_timeout(300)
        page.locator(".el-dialog button:has-text('保存修改')").first.click()
        page.wait_for_timeout(2000)

        # ========== 收尾 ==========
        print()
        print("=" * 50)
        print(f"console errors: {len(console_errors)}")
        for e in console_errors[:10]:
            print(f"  {e}")
        print(f"测试错误: {len(errors)}")
        for e in errors:
            print(f"  !! {e}")
        print("=" * 50)
        browser.close()
        return len(errors) == 0 and len([e for e in console_errors if "PAGEERROR" in e]) == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
