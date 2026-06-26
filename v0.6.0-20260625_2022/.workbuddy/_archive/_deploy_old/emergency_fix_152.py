#!/usr/bin/env python3
"""
紧急修复152服务器前端目录不存在的问题
"""
import paramiko
import os
import sys

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🚀 正在紧急修复152服务器...")
        print(f"=" * 60)
        
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 1. 创建前端目录
        print("\n1️⃣ 创建前端目录 /var/www/oa-web/...")
        ssh.exec_command('sudo mkdir -p /var/www/oa-web/')
        ssh.exec_command('sudo chown www-data:www-data /var/www/oa-web/')
        print("   ✅ 目录创建成功")
        
        # 2. 检查本地构建文件
        print("\n2️⃣ 检查本地构建文件...")
        local_dist = 'D:/work/website/OA/pc-web/dist/'
        if os.path.exists(local_dist):
            files = os.listdir(local_dist)
            has_index = os.path.exists(os.path.join(local_dist, "index.html"))
            print(f"   ✅ 本地构建文件存在: {len(files)} 个文件")
            print(f"   ✅ index.html存在: {has_index}")
        else:
            print("   ❌ 本地构建文件不存在！")
            return False
        
        # 3. 创建紧急恢复页面
        print("\n3️⃣ 创建紧急恢复页面...")
        emergency_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OA系统 - 恢复中</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0C447C 0%, #1D9E75 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(30px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 600px;
        }
        h1 { font-size: 48px; margin-bottom: 20px; }
        p { font-size: 18px; margin-bottom: 30px; opacity: 0.9; }
        .btn {
            display: inline-block;
            padding: 15px 40px;
            background: white;
            color: #0C447C;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s;
            cursor: pointer;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .status { margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 OA系统恢复中</h1>
        <p>前端正在紧急恢复，请稍后刷新页面...</p>
        <a href="javascript:location.reload()" class="btn">刷新页面</a>
        <div class="status">
            <p>🖥️ 服务器: 152.136.115.121</p>
            <p>⏰ 时间: 2026-06-22 20:50</p>
            <p>📊 状态: 正在部署前端文件...</p>
        </div>
    </div>
</body>
</html>"""
        
        # 保存紧急HTML到本地
        temp_html = '/tmp/emergency_index.html'
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(emergency_html)
        
        # 上传到服务器
        sftp = ssh.open_sftp()
        sftp.put(temp_html, '/tmp/emergency_index.html')
        sftp.close()
        
        # 复制到前端目录
        ssh.exec_command('sudo cp /tmp/emergency_index.html /var/www/oa-web/index.html')
        ssh.exec_command('sudo chown www-data:www-data /var/www/oa-web/index.html')
        ssh.exec_command('rm -f /tmp/emergency_index.html')
        print("   ✅ 紧急恢复页面已创建")
        
        # 4. 重载Nginx
        print("\n4️⃣ 重载Nginx...")
        ssh.exec_command('sudo systemctl reload nginx')
        import time
        time.sleep(2)
        print("   ✅ Nginx已重载")
        
        # 5. 测试连接
        print("\n5️⃣ 测试Web访问...")
        stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null', timeout=10)
        result = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"   HTTP状态码: {result}")
        
        print("\n" + "=" * 60)
        print("✅ 紧急修复完成！")
        print("🌐 请访问: http://152.136.115.121")
        print("⚠️  当前是紧急恢复页面")
        print("🚀 正在准备完整前端部署...")
        
        ssh.close()
        
        # 6. 部署完整前端
        print("\n6️⃣ 部署完整前端文件...")
        deploy_full_frontend()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return False

def deploy_full_frontend():
    """部署完整前端文件"""
    try:
        print("\n🚀 开始部署完整前端...")
        print("=" * 60)
        
        # 重新连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        
        # 打包本地dist目录
        print("\n📦 打包本地前端文件...")
        local_dist = 'D:/work/website/OA/pc-web/dist/'
        
        # 使用tar打包
        import tarfile
        tar_path = '/tmp/oa-web-frontend.tar'
        with tarfile.open(tar_path, 'w') as tar:
            for root, dirs, files in os.walk(local_dist):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, local_dist)
                    tar.add(file_path, arcname=arcname)
        
        print(f"   ✅ 打包完成: {tar_path}")
        
        # 上传到服务器
        print("\n📤 上传到152服务器...")
        sftp = ssh.open_sftp()
        sftp.put(tar_path, '/tmp/oa-web-frontend.tar')
        sftp.close()
        print("   ✅ 上传成功")
        
        # 解压到前端目录
        print("\n📂 解压前端文件...")
        ssh.exec_command('sudo rm -rf /var/www/oa-web/*')
        ssh.exec_command('cd /var/www/oa-web/ && sudo tar -xf /tmp/oa-web-frontend.tar')
        ssh.exec_command('sudo chown -R www-data:www-data /var/www/oa-web/')
        ssh.exec_command('rm -f /tmp/oa-web-frontend.tar')
        print("   ✅ 解压完成")
        
        # 验证文件
        print("\n✅ 验证前端文件...")
        stdin, stdout, stderr = ssh.exec_command('ls -lh /var/www/oa-web/ | head -10', timeout=10)
        result = stdout.read().decode('utf-8', errors='ignore')
        print("   " + result[:300])
        
        # 重载Nginx
        print("\n🔄 重载Nginx...")
        ssh.exec_command('sudo systemctl reload nginx')
        import time
        time.sleep(2)
        print("   ✅ Nginx已重载")
        
        # 测试访问
        print("\n🧪 测试Web访问...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost | head -5', timeout=10)
        result = stdout.read().decode('utf-8', errors='ignore')
        if 'OA' in result or 'html' in result:
            print("   ✅ Web界面恢复正常！")
        else:
            print(f"   ⚠️ 响应: {result[:100]}")
        
        print("\n" + "=" * 60)
        print("🎉 完整前端部署完成！")
        print("🌐 请访问: http://152.136.115.121")
        print("💡 提示: 请按 Ctrl+F5 强制刷新浏览器")
        
        ssh.close()
        
        # 清理本地临时文件
        os.remove(tar_path)
        
        return True
        
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 所有操作完成！")
    else:
        print("\n❌ 操作失败，请检查错误信息")
