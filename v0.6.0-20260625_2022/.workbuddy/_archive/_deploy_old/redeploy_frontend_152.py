#!/usr/bin/env python3
"""
彻底重新部署前端到152服务器（强制覆盖）
"""
import paramiko
import os
import tarfile
import time

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
        
        # 3. 彻底清空前端目录并解压（使用rm -rf 然后 mkdir）
        print("\n🗑️  正在清空并重新部署前端文件...")
        
        # 删除整个目录然后重建
        deploy_cmd = f"""
        cd /tmp &&
        rm -rf {REMOTE_WEB_PATH} &&
        mkdir -p {REMOTE_WEB_PATH} &&
        tar -xzf {remote_tar} -C {REMOTE_WEB_PATH} &&
        chown -R www-data:www-data {REMOTE_WEB_PATH} &&
        ls -la {REMOTE_WEB_PATH}/ | head -10
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
                time.sleep(0.1)
        
        print("\n✅ 部署完成")
        
        # 4. 验证部署
        print("\n🔍 验证部署结果...")
        verify_cmd = f"""
        grep -r '演示账号' {REMOTE_WEB_PATH}/assets/ 2>/dev/null | wc -l &&
        grep -o 'v1.0.[0-9]' {REMOTE_WEB_PATH}/index.html 2>/dev/null | head -1
        """
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        result = stdout.read().decode('utf-8').strip()
        print(f"   演示账号提示: {result.split(chr(10))[0]} 个文件包含")
        if len(result.split(chr(10))) > 1:
            print(f"   版本号: {result.split(chr(10))[1]}")
        
        # 5. 修改Nginx配置添加缓存控制
        print("\n⚙️ 配置Nginx缓存控制...")
        nginx_conf = f"""
        location / {{
            root {REMOTE_WEB_PATH};
            index index.html;
            try_files $uri $uri/ /index.html;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
            add_header Expires "0";
        }}
        
        location /assets/ {{
            root {REMOTE_WEB_PATH};
            expires 7d;
            add_header Cache-Control "public, max-age=604800";
        }}
        """
        
        # 读取当前Nginx配置
        cat_cmd = "cat /etc/nginx/sites-enabled/oa-api.conf 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null"
        stdin, stdout, stderr = ssh.exec_command(cat_cmd)
        nginx_config = stdout.read().decode('utf-8')
        
        if 'Cache-Control' not in nginx_config:
            print("   需要更新Nginx配置...")
            # 这里需要更新Nginx配置，但为了安全，先手动检查
            print("   ⚠️ 请手动更新Nginx配置添加缓存控制")
        else:
            print("   ✅ Nginx缓存控制已配置")
        
        # 6. 重载Nginx
        print("\n🔄 正在重载Nginx...")
        reload_cmd = "systemctl reload nginx"
        ssh.exec_command(reload_cmd)
        print("✅ Nginx重载完成")
        
        # 7. 清理临时文件
        ssh.exec_command(f"rm -f {remote_tar}")
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
        print("   2. 或使用无痕模式访问测试")
        print("   3. 版本号应为 v1.0.2")
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
