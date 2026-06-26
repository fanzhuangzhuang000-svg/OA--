#!/usr/bin/env python3
"""
上传前端构建文件到152服务器（使用Python打包）
"""
import paramiko
import os
import tarfile
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
REMOTE_WEB_PATH = '/var/www/oa-web'

# 本地构建目录
LOCAL_DIST = 'D:/work/website/OA/pc-web/dist'
LOCAL_TAR = 'D:/work/website/OA/.workbuddy/oa-web-dist.tar.gz'

def create_tar_gz(source_dir, output_filename):
    """创建tar.gz压缩包"""
    print(f"📦 正在打包前端构建文件...")
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=".")
    print(f"✅ 打包完成: {output_filename}")

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 1. 打包本地dist目录
        create_tar_gz(LOCAL_DIST, LOCAL_TAR)
        
        # 2. 备份当前前端
        print("📦 正在备份当前前端...")
        backup_cmd = f"cd {REMOTE_WEB_PATH} && tar -czf /tmp/oa-web-backup-$(date +%Y%m%d-%H%M%S).tar.gz . 2>/dev/null || echo '备份跳过'"
        ssh.exec_command(backup_cmd)
        print("✅ 备份完成")
        
        # 3. 上传压缩包
        print("📤 正在上传前端构建文件...")
        sftp = ssh.open_sftp()
        remote_tar = '/tmp/oa-web-dist.tar.gz'
        sftp.put(LOCAL_TAR, remote_tar)
        sftp.close()
        print("✅ 上传完成")
        
        # 4. 清空前端目录并解压
        print("🗑️  正在部署前端文件...")
        deploy_cmd = f"""
        cd {REMOTE_WEB_PATH} && 
        find . -type f -delete && 
        tar -xzf {remote_tar} -C {REMOTE_WEB_PATH} && 
        chown -R www-data:www-data {REMOTE_WEB_PATH}
        """
        stdin, stdout, stderr = ssh.exec_command(deploy_cmd, get_pty=True)
        
        # 等待命令完成
        output = ""
        while True:
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                output += chunk
            elif stderr.channel.recv_ready():
                chunk = stderr.channel.recv(4096).decode('utf-8', errors='ignore')
                output += chunk
            else:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
        
        print("✅ 部署完成")
        
        # 5. 重载Nginx
        print("🔄 正在重载Nginx...")
        reload_cmd = "systemctl reload nginx"
        ssh.exec_command(reload_cmd)
        print("✅ Nginx重载完成")
        
        # 6. 清理临时文件
        ssh.exec_command(f"rm -f {remote_tar}")
        os.remove(LOCAL_TAR)
        print("🗑️  已清理临时文件")
        
        # 关闭SSH连接
        ssh.close()
        
        print("\n" + "="*60)
        print("🎉 前端部署完成！")
        print("="*60)
        print(f"🌐 访问地址: http://{HOST}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 所有操作完成！")
    else:
        print("\n❌ 操作失败，请检查错误信息")
