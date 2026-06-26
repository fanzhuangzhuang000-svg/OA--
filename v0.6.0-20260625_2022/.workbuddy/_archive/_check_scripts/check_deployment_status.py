#!/usr/bin/env python3
"""
检查152服务器前端部署状态
"""
import paramiko

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 1. 检查前端文件是否包含演示账号提示
        print("=" * 60)
        print("1. 检查前端文件中的演示账号提示")
        print("=" * 60)
        
        cmd_check_demo = """grep -o "演示账号" /var/www/oa-web/index.html | wc -l"""
        stdin, stdout, stderr = ssh.exec_command(cmd_check_demo, timeout=10)
        count = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"演示账号提示出现次数: {count}")
        
        if int(count) > 0:
            print("✅ 演示账号提示已部署")
            cmd_show_demo = """grep -A3 "demo-tip" /var/www/oa-web/index.html | head -15"""
            stdin, stdout, stderr = ssh.exec_command(cmd_show_demo, timeout=10)
            output = stdout.read().decode('utf-8', errors='ignore')
            print("\n演示账号提示内容:")
            print(output)
        else:
            print("❌ 演示账号提示未部署")
        
        # 2. 检查版本号
        print("\n" + "=" * 60)
        print("2. 检查前端版本号")
        print("=" * 60)
        
        cmd_check_version = """grep -o "v1.0.[0-9]*" /var/www/oa-web/index.html | tail -1"""
        stdin, stdout, stderr = ssh.exec_command(cmd_check_version, timeout=10)
        version = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"前端版本号: {version if version else '未找到'}")
        
        # 3. 检查后端状态
        print("\n" + "=" * 60)
        print("3. 检查后端API状态")
        print("=" * 60)
        
        cmd_check_api = """curl -s -o /dev/null -w "%{http_code}" http://localhost/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"Admin@2026"}' """
        stdin, stdout, stderr = ssh.exec_command(cmd_check_api, timeout=10)
        status = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"登录API状态码: {status}")
        
        if status == "200":
            print("✅ 后端API正常")
        else:
            print("⚠️ 后端API可能异常")
        
        # 4. 提供清除缓存的命令
        print("\n" + "=" * 60)
        print("4. 如何清除浏览器缓存")
        print("=" * 60)
        print("""
方法1：强制刷新（最简单，推荐）
  - Windows: Ctrl + F5 或 Ctrl + Shift + R
  - Mac: Cmd + Shift + R

方法2：手动清除缓存
  1. 按 F12 打开开发者工具
  2. 右键点击「刷新」按钮
  3. 选择「清空缓存并硬性重新加载」

方法3：完全清除缓存
  1. 按 Ctrl + Shift + Delete
  2. 选择「缓存的图片和文件」
  3. 点击「清除数据」

方法4：使用无痕模式（排除缓存问题）
  - 按 Ctrl + Shift + N (Chrome)
  - 访问 http://152.136.115.121
""")
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    main()
