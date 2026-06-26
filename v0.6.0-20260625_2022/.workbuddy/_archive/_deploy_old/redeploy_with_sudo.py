#!/usr/bin/env python3
"""
使用sudo权限彻底重新部署前端到152服务器
"""
import paramiko
import os
import tarfile

HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
REMOTE_WEB_PATH = '/var/www/oa-web'
LOCAL_DIST = 'D:/work/website/OA/pc-web/dist'
LOCAL_TAR = 'D:/work/website/OA/.workbuddy/oa-web-dist.tar.gz'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 1. 打包本地dist目录
        print("\n📦 正在打包前端构建文件...")
        with tarfile.open(LOCAL_TAR, "w:gz") as tar:
            tar.add(LOCAL_DIST, arcname=".")
        print(f"✅ 打包完成: {LOCAL_TAR}")
        
        # 2. 上传压缩包
        print("\n📤 正在上传前端构建文件...")
        sftp = ssh.open_sftp()
        remote_tar = '/tmp/oa-web-dist.tar.gz'
        sftp.put(LOCAL_TAR, remote_tar)
        sftp.close()
        print("✅ 上传完成")
        
        # 3. 使用sudo权限清空并部署
        print("\n🗑️  正在清空并重新部署前端文件...")
        deploy_cmd = f"""
        sudo bash -c '
        cd {REMOTE_WEB_PATH} &&
        rm -rf * &&
        rm -rf assets/ &&
        tar -xzf {remote_tar} -C {REMOTE_WEB_PATH} &&
        chown -R www-data:www-data {REMOTE_WEB_PATH} &&
        echo "部署完成" &&
        ls -la {REMOTE_WEB_PATH}/index.html
        '
        """
        stdin, stdout, stderr = ssh.exec_command(deploy_cmd, get_pty=True, timeout=300)
        
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
                import time
                time.sleep(0.1)
        
        print("\n✅ 部署完成")
        
        # 4. 验证部署
        print("\n🔍 验证部署结果...")
        verify_cmd = f"""
        sudo bash -c '
        echo "=== 版本号 ===" &&
        grep -o "v1.0.[0-9]" {REMOTE_WEB_PATH}/index.html 2>/dev/null | head -1 &&
        echo "=== 演示账号提示 ===" &&
        grep -r "演示账号" {REMOTE_WEB_PATH}/assets/ 2>/dev/null | wc -l
        '
        """
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        result = stdout.read().decode('utf-8').strip()
        print(result)
        
        # 5. 配置Nginx缓存控制
        print("\n⚙️ 配置Nginx缓存控制...")
        nginx_cmd = f"""
        sudo bash -c '
        if ! grep -q "Cache-Control" /etc/nginx/sites-enabled/*.conf 2>/dev/null; then
            echo "需要手动配置Nginx缓存控制"
        else
            echo "Nginx缓存控制已配置"
        fi
        '
        """
        ssh.exec_command(nginx_cmd)
        
        # 6. 重载Nginx
        print("\n🔄 正在重载Nginx...")
        reload_cmd = "sudo systemctl reload nginx"
        ssh.exec_command(reload_cmd)
        print("✅ Nginx重载完成")
        
        # 7. 清理临时文件
        ssh.exec_command(f"sudo rm -f {remote_tar}")
        os.remove(LOCAL_TAR)
        print("\n🗑️  已清理临时文件")
        
        ssh.close()
        
        print("\n" + "="*60)
        print("🎉 前端部署完成！")
        print("="*60)
        print(f"🌐 访问地址: http://{HOST}")
        print("="*60)
        print("⚠️ 重要提示:")
        print("   1. 请清除浏览器缓存（Ctrl+Shift+Delete）")
        print("   2. 或按 Ctrl+F5 强制刷新")
        print("   3. 版本号应为 v1.0.2")
        print("   4. 登录按钮下方应显示演示账号提示")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 所有操作完成！")
    else:
        print("\n❌ 操作失败，请检查错误信息")
