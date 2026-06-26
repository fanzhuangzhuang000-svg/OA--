#!/usr/bin/env python3
"""
使用tar.gz打包并部署前端到152服务器
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
LOCAL_TAR = 'D:/work/website/OA/.workbuddy/dist.tar.gz'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 1. 本地打包
        print("=" * 60)
        print("1. 本地打包前端文件")
        print("=" * 60)
        
        import tarfile
        print(f"📦 正在打包 {LOCAL_DIST} -> {LOCAL_TAR}...")
        with tarfile.open(LOCAL_TAR, "w:gz") as tar:
            tar.add(LOCAL_DIST, arcname="dist")
        print(f"✅ 打包完成: {LOCAL_TAR}")
        
        # 2. 上传打包文件
        print("\n" + "=" * 60)
        print("2. 上传打包文件到152服务器")
        print("=" * 60)
        
        sftp = ssh.open_sftp()
        remote_tar = "/tmp/dist.tar.gz"
        
        print(f"📤 正在上传 {LOCAL_TAR} -> {remote_tar}...")
        sftp.put(LOCAL_TAR, remote_tar)
        print("✅ 上传完成")
        sftp.close()
        
        # 3. 备份当前前端
        print("\n" + "=" * 60)
        print("3. 备份当前前端文件")
        print("=" * 60)
        
        cmd_backup = f"sudo cp -r {REMOTE_WEB} {REMOTE_WEB}.bak.$(date +%Y%m%d_%H%M%S)"
        ssh.exec_command(cmd_backup, get_pty=True, timeout=30)
        print(f"✅ 已备份")
        
        # 4. 清空前端目录
        print("\n" + "=" * 60)
        print("4. 清空前端目录")
        print("=" * 60)
        
        cmd_clear = f"sudo rm -rf {REMOTE_WEB}/*"
        ssh.exec_command(cmd_clear, get_pty=True, timeout=30)
        print(f"✅ 已清空 {REMOTE_WEB}/")
        
        # 5. 解压新文件
        print("\n" + "=" * 60)
        print("5. 解压新文件")
        print("=" * 60)
        
        cmd_extract = f"sudo tar -xzf {remote_tar} -C {REMOTE_WEB} --strip-components=1 && sudo chown -R www-data:www-data {REMOTE_WEB}"
        stdin, stdout, stderr = ssh.exec_command(cmd_extract, get_pty=True, timeout=60)
        
        output = ""
        while True:
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                print(chunk, end='')
                output += chunk
            elif stderr.channel.recv_ready():
                chunk = stderr.channel.recv(4096).decode('utf-8', errors='ignore')
                print(chunk, end='')
                output += chunk
            else:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
        
        print("✅ 解压完成")
        
        # 6. 清理临时文件
        print("\n" + "=" * 60)
        print("6. 清理临时文件")
        print("=" * 60)
        
        ssh.exec_command(f"rm -f {remote_tar}", get_pty=True, timeout=10)
        print(f"✅ 已清理临时文件")
        
        # 7. 重载Nginx
        print("\n" + "=" * 60)
        print("7. 重载Nginx")
        print("=" * 60)
        
        cmd_reload = "sudo nginx -t && sudo systemctl reload nginx"
        stdin, stdout, stderr = ssh.exec_command(cmd_reload, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
        # 8. 验证部署
        print("\n" + "=" * 60)
        print("8. 验证部署")
        print("=" * 60)
        
        # 检查index.html引用的JS文件是否存在
        cmd_check_js = f"""grep -o 'assets/index-[^"]*.js' {REMOTE_WEB}/index.html | head -1"""
        stdin, stdout, stderr = ssh.exec_command(cmd_check_js, get_pty=True, timeout=10)
        js_file = stdout.read().decode('utf-8', errors='ignore').strip()
        
        if js_file:
            cmd_check_exist = f"ls -lh {REMOTE_WEB}/{js_file} 2>&1"
            stdin, stdout, stderr = ssh.exec_command(cmd_check_exist, get_pty=True, timeout=10)
            output = stdout.read().decode('utf-8', errors='ignore')
            print(f"JS文件: {js_file}")
            print(output)
            
            # 检查JS文件是否包含演示账号
            cmd_check_demo = f"""grep -o "演示账号" {REMOTE_WEB}/{js_file} | wc -l"""
            stdin, stdout, stderr = ssh.exec_command(cmd_check_demo, get_pty=True, timeout=10)
            count = stdout.read().decode('utf-8', errors='ignore').strip()
            print(f"\n演示账号提示出现次数: {count}")
            
            if int(count) > 0:
                print("✅ 演示账号提示已成功部署！")
            else:
                print("⚠️ JS文件已部署，但可能演示账号提示在其它文件中")
        else:
            print("⚠️ 未找到JS文件引用")
        
        # 9. 测试访问
        print("\n" + "=" * 60)
        print("9. 测试访问")
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
        print("\n⚠️ 重要：请清除浏览器缓存！")
        print("   方法1：按 Ctrl + F5 强制刷新")
        print("   方法2：使用无痕模式访问")
        print("   方法3：F12 -> Network -> 勾选 Disable cache -> 刷新\n")
        
        # 关闭SSH连接
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
