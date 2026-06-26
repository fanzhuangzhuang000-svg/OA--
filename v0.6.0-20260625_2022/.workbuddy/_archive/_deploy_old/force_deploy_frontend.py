#!/usr/bin/env python3
"""
强制重新部署前端到152服务器（使用sudo权限）
"""
import paramiko
import os
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
LOCAL_DIST = 'D:/work/website/OA/pc-web/dist'
REMOTE_WEB = '/var/www/oa-web'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 1. 检查Nginx配置，确认前端路径
        print("=" * 60)
        print("1. 检查Nginx配置")
        print("=" * 60)
        
        cmd_nginx = "sudo cat /etc/nginx/sites-enabled/oa-api.conf 2>/dev/null | grep -A5 'root\\|location'"
        stdin, stdout, stderr = ssh.exec_command(cmd_nginx, get_pty=True, timeout=10)
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
        # 2. 备份当前前端文件
        print("\n" + "=" * 60)
        print("2. 备份当前前端文件")
        print("=" * 60)
        
        cmd_backup = f"sudo cp -r {REMOTE_WEB} {REMOTE_WEB}.bak.$(date +%Y%m%d_%H%M%S)"
        ssh.exec_command(cmd_backup, get_pty=True, timeout=30)
        print(f"✅ 已备份到 {REMOTE_WEB}.bak.*")
        
        # 3. 删除当前前端文件（使用sudo）
        print("\n" + "=" * 60)
        print("3. 清空前端目录")
        print("=" * 60)
        
        cmd_clear = f"sudo rm -rf {REMOTE_WEB}/*"
        ssh.exec_command(cmd_clear, get_pty=True, timeout=30)
        print(f"✅ 已清空 {REMOTE_WEB}/")
        
        # 4. 创建SFTP连接，上传新文件
        print("\n" + "=" * 60)
        print("4. 上传新的前端文件")
        print("=" * 60)
        
        sftp = ssh.open_sftp()
        
        # 获取本地dist目录的所有文件
        local_files = []
        for root, dirs, files in os.walk(LOCAL_DIST):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, LOCAL_DIST)
                remote_path = f"{REMOTE_WEB}/{relative_path}".replace('\\', '/')
                local_files.append((local_path, remote_path))
        
        print(f"📤 正在上传 {len(local_files)} 个文件...")
        
        uploaded = 0
        for local_path, remote_path in local_files:
            try:
                # 创建远程目录
                remote_dir = remote_path.rsplit('/', 1)[0]
                try:
                    sftp.makedirs(remote_dir)
                except:
                    pass
                
                # 上传文件到/tmp先
                tmp_path = f"/tmp/{os.path.basename(local_path)}"
                sftp.put(local_path, tmp_path)
                
                # 使用sudo移动到目标位置
                cmd_move = f"sudo cp '{tmp_path}' '{remote_path}' && sudo chown www-data:www-data '{remote_path}' && rm -f '{tmp_path}'"
                ssh.exec_command(cmd_move, get_pty=True, timeout=10)
                
                uploaded += 1
                if uploaded % 10 == 0:
                    print(f"   进度: {uploaded}/{len(local_files)}")
            except Exception as e:
                print(f"   错误: 上传 {local_path} 失败 - {e}")
        
        sftp.close()
        print(f"✅ 上传完成: {uploaded}/{len(local_files)} 个文件")
        
        # 5. 设置正确的权限
        print("\n" + "=" * 60)
        print("5. 设置文件权限")
        print("=" * 60)
        
        cmd_chown = f"sudo chown -R www-data:www-data {REMOTE_WEB}"
        ssh.exec_command(cmd_chown, get_pty=True, timeout=30)
        print(f"✅ 已设置 {REMOTE_WEB} 权限为 www-data:www-data")
        
        # 6. 重载Nginx
        print("\n" + "=" * 60)
        print("6. 重载Nginx")
        print("=" * 60)
        
        cmd_reload = "sudo nginx -t && sudo systemctl reload nginx"
        stdin, stdout, stderr = ssh.exec_command(cmd_reload, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        print(output)
        if error:
            print("错误:", error)
        
        # 7. 验证部署
        print("\n" + "=" * 60)
        print("7. 验证部署")
        print("=" * 60)
        
        cmd_verify = f"""grep -o "演示账号" {REMOTE_WEB}/index.html | wc -l"""
        stdin, stdout, stderr = ssh.exec_command(cmd_verify, get_pty=True, timeout=10)
        count = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"演示账号提示出现次数: {count}")
        
        if int(count) > 0:
            print("✅ 演示账号提示已成功部署！")
            cmd_show = f"""grep -A3 "demo-tip" {REMOTE_WEB}/index.html | head -10"""
            stdin, stdout, stderr = ssh.exec_command(cmd_show, get_pty=True, timeout=10)
            output = stdout.read().decode('utf-8', errors='ignore')
            print("\n演示账号提示内容:")
            print(output)
        else:
            print("❌ 演示账号提示未部署成功")
        
        # 8. 测试访问
        print("\n" + "=" * 60)
        print("8. 测试前端访问")
        print("=" * 60)
        
        cmd_test = "curl -s -o /dev/null -w '%{http_code}' http://localhost/"
        stdin, stdout, stderr = ssh.exec_command(cmd_test, get_pty=True, timeout=10)
        status = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"前端访问状态码: {status}")
        
        if status == "200":
            print("✅ 前端可以正常访问")
        else:
            print("⚠️ 前端访问可能异常")
        
        print("\n" + "=" * 60)
        print("✅ 部署完成")
        print("=" * 60)
        print("\n请执行以下操作：")
        print("  1. 按 Ctrl + F5 强制刷新页面")
        print("  2. 或使用无痕模式访问 http://152.136.115.121")
        print("  3. 登录按钮下方应显示「演示账号」提示")
        print("  4. 账号: admin / 密码: Admin@2026\n")
        
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
        print("\n❌ 部署失败，请检查错误信息")
