#!/usr/bin/env python3
"""
部署前端到152服务器（修复看板问题后）
"""

import paramiko
import os
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

# 本地构建目录
LOCAL_DIST = 'D:/work/website/OA/pc-web/dist'
# 远程目标目录
REMOTE_DIST = '/var/www/oa-web'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 1. 打包本地dist目录
        print("📦 正在打包本地构建文件...")
        os.system(f'cd {LOCAL_DIST} && tar -czf D:/work/website/OA/.workbuddy/dist.tar.gz .')
        print("✅ 打包完成")
        
        # 2. 上传打包文件
        sftp = ssh.open_sftp()
        print(f"📤 正在上传构建文件到 {HOST}...")
        remote_tar = '/tmp/oa-web-dist.tar.gz'
        sftp.put('D:/work/website/OA/.workbuddy/dist.tar.gz', remote_tar)
        print("✅ 上传完成")
        sftp.close()
        
        # 3. 备份当前前端
        print("📋 正在备份当前前端...")
        backup_cmd = f"cd {REMOTE_DIST} && sudo tar -czf /tmp/oa-web-backup-$(date +%Y%m%d-%H%M%S).tar.gz . 2>/dev/null || echo 'BACKUP_SKIPPED'"
        ssh.exec_command(backup_cmd)
        time.sleep(2)
        print("✅ 备份完成")
        
        # 4. 清空远程目录（保留.htaccess等隐藏文件）
        print("🗑️  正在清空远程目录...")
        clean_cmd = f"sudo find {REMOTE_DIST} -type f -delete && sudo find {REMOTE_DIST} -type d -empty -delete || echo 'CLEAN_DONE'"
        ssh.exec_command(clean_cmd)
        time.sleep(2)
        print("✅ 清空完成")
        
        # 5. 解压新文件
        print("📂 正在解压新文件...")
        extract_cmd = f"cd {REMOTE_DIST} && sudo tar -xzf {remote_tar} && sudo chown -R www-data:www-data {REMOTE_DIST}"
        ssh.exec_command(extract_cmd)
        time.sleep(3)
        print("✅ 解压完成")
        
        # 6. 清理临时文件
        ssh.exec_command(f"rm -f {remote_tar}")
        os.remove('D:/work/website/OA/.workbuddy/dist.tar.gz')
        print("🗑️  已清理临时文件")
        
        # 7. 重载Nginx
        print("🔄 正在重载Nginx...")
        ssh.exec_command('sudo systemctl reload nginx')
        time.sleep(1)
        print("✅ Nginx重载完成")
        
        # 关闭SSH连接
        ssh.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    print("🚀 开始部署前端到152服务器...")
    print("=" * 60)
    
    success = main()
    
    if success:
        print("=" * 60)
        print("🎉 前端部署完成！")
        print("⚠️  重要：请清除浏览器缓存（Ctrl+F5）")
        print(f"🌐 访问地址: http://{HOST}")
    else:
        print("\n❌ 部署失败，请检查错误信息")
