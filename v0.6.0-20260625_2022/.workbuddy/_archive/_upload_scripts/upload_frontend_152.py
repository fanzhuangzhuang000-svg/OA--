#!/usr/bin/env python3
"""
上传前端构建文件到152服务器
"""
import paramiko
import os
from scp import SCPClient

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
REMOTE_WEB_PATH = '/var/www/oa-web'

# 本地构建目录
LOCAL_DIST = 'D:/work/website/OA/pc-web/dist'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 先备份当前前端
        print("📦 正在备份当前前端...")
        backup_cmd = f"cd {REMOTE_WEB_PATH} && tar -czf /tmp/oa-web-backup-$(date +%Y%m%d-%H%M%S).tar.gz . 2>/dev/null || echo '备份跳过'"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        print("✅ 备份完成")
        
        # 清空前端目录（保留必要文件）
        print("🗑️  正在清理前端目录...")
        clean_cmd = f"cd {REMOTE_WEB_PATH} && find . -type f -delete && find . -type d -delete 2>/dev/null || echo '清理完成'"
        ssh.exec_command(clean_cmd)
        
        # 创建SCP客户端
        print("📤 正在上传前端构建文件...")
        
        # 使用sftp上传整个目录
        sftp = ssh.open_sftp()
        
        # 递归上传目录
        def upload_dir(local_path, remote_path):
            # 创建远程目录
            try:
                sftp.mkdir(remote_path)
            except:
                pass
            
            for item in os.listdir(local_path):
                local_item = os.path.join(local_path, item)
                remote_item = remote_path + '/' + item
                
                if os.path.isdir(local_item):
                    upload_dir(local_item, remote_item)
                else:
                    print(f"  上传: {item}")
                    sftp.put(local_item, remote_item)
        
        # 上传dist目录内容
        upload_dir(LOCAL_DIST, REMOTE_WEB_PATH)
        
        sftp.close()
        print("✅ 上传完成")
        
        # 设置权限
        print("🔐 正在设置文件权限...")
        chown_cmd = f"chown -R www-data:www-data {REMOTE_WEB_PATH}"
        ssh.exec_command(chown_cmd)
        print("✅ 权限设置完成")
        
        # 重载Nginx
        print("🔄 正在重载Nginx...")
        reload_cmd = "systemctl reload nginx"
        ssh.exec_command(reload_cmd)
        print("✅ Nginx重载完成")
        
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
