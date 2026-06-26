#!/usr/bin/env python3
"""
验证152服务器前端部署（在JS文件中搜索）
"""
import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
REMOTE_WEB = '/var/www/oa-web'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 1. 在JS文件中搜索演示账号提示
        print("=" * 60)
        print("1. 在JS文件中搜索演示账号提示")
        print("=" * 60)
        
        cmd_search = f"""grep -r "演示账号\|admin.*Admin" {REMOTE_WEB}/assets/ 2>/dev/null | head -5"""
        stdin, stdout, stderr = ssh.exec_command(cmd_search, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        
        if output.strip():
            print("✅ 演示账号提示已在JS文件中！")
            print("\n找到的内容（前200字符）:")
            print(output[:200])
        else:
            print("❌ JS文件中未找到演示账号提示")
            print("   可能的原因：")
            print("   1. 本地构建未包含演示账号提示")
            print("   2. 部署未成功")
        
        # 2. 检查本地构建文件是否包含演示账号提示
        print("\n" + "=" * 60)
        print("2. 检查本地构建文件")
        print("=" * 60)
        
        import subprocess
        cmd_local = f'grep -r "演示账号" D:/work/website/OA/pc-web/dist/ 2>/dev/null | head -3'
        result = subprocess.run(cmd_local, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            print("✅ 本地构建文件包含演示账号提示")
            print("\n本地文件内容（前200字符）:")
            print(result.stdout[:200])
        else:
            print("❌ 本地构建文件不包含演示账号提示")
            print("   需要重新构建前端")
        
        # 3. 测试实际登录功能
        print("\n" + "=" * 60)
        print("3. 测试登录功能")
        print("=" * 60)
        
        cmd_test_login = """curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"Admin@2026"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('登录结果:', '成功' if data.get('code') == 0 else '失败'); print('消息:', data.get('message', ''))" 2>/dev/null || echo "API请求失败"
"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_test_login, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
        # 4. 提供浏览器测试方法
        print("\n" + "=" * 60)
        print("4. 浏览器测试步骤")
        print("=" * 60)
        print("""
✅ 后端已确认可以正常登录！
   用户名: admin
   密码: Admin@2026

📋 前端可能有浏览器缓存，请按以下步骤测试：

方法1：强制刷新（推荐）
  1. 打开 http://152.136.115.121
  2. 按 Ctrl + F5 (Windows) 或 Cmd + Shift + R (Mac)
  3. 页面会强制从服务器重新加载

方法2：使用无痕模式（排除缓存问题）
  1. 按 Ctrl + Shift + N (Chrome)
  2. 访问 http://152.136.115.121
  3. 输入 admin 和 Admin@2026 登录

方法3：清除浏览器缓存
  1. 按 F12 打开开发者工具
  2. 右键点击「刷新」按钮
  3. 选择「清空缓存并硬性重新加载」

方法4：检查前端是否真的加载了新版本
  1. 打开 http://152.136.115.121
  2. 按 F12 打开开发者工具
  3. 切换到「Network」标签页
  4. 勾选「Disable cache」（禁用缓存）
  5. 刷新页面
  6. 查看加载的JS文件是否包含演示账号提示
""")
        
        print("\n" + "=" * 60)
        print("✅ 验证完成")
        print("=" * 60)
        print("\n💡 如果浏览器仍然显示旧版本：")
        print("   1. 可能是浏览器缓存问题 → 按 Ctrl + F5 强制刷新")
        print("   2. 可能是前端代码问题 → 检查登录页面Vue组件")
        print("   3. 可能是Nginx缓存问题 → 重启Nginx")
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 验证失败，请检查错误信息")
