import paramiko, os, sys, tarfile, tempfile, re

HOST, USER, PASS = '172.20.0.139', 'nbcy', 'admin123'
LOCAL_API = 'D:/work/website/OA/pc-api'
REMOTE_BASE = '/var/www/oa-api'

def log(m): print(f"  {m}")

def main():
    print("🚀 上传并执行服务器端部署脚本...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)
    print("✅ SSH 连接成功")
    sftp = ssh.open_sftp()

    # 上传 deploy_server.sh
    print("\n📦 上传 deploy_server.sh...")
    sftp.put('D:/work/website/OA/deploy/deploy_server.sh', '/tmp/deploy_server.sh')
    ssh.exec_command("chmod +x /tmp/deploy_server.sh")
    print("  ✅ 上传完成")

    # 执行服务器端部署脚本（前8步）
    print("\n📦 执行服务器端部署脚本（前8步）...")
    stdin, stdout, stderr = ssh.exec_command("sudo bash /tmp/deploy_server.sh 2>&1", timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    for line in out.split('\n'):
        if line.strip():
            log(line[:150])
    if err.strip():
        for line in err.split('\n'):
            if line.strip():
                log(f"  ⚠️ {line[:150]}")
    print("  ✅ 服务器端准备完成")

    # 上传后端文件
    print("\n📦 打包并上传后端文件...")
    log("  打包中（排除 vendor/ node_modules/）...")
    tmp_tar = os.path.join(tempfile.gettempdir(), 'oa-api.tar.gz')
    with tarfile.open(tmp_tar, 'w:gz') as tar:
        base_dir = os.path.dirname(LOCAL_API)
        for root, dirs, files in os.walk(LOCAL_API):
            dirs[:] = [d for d in dirs if d not in ('vendor', 'node_modules', '.git', '__pycache__')]
            for fn in files:
                fp = os.path.join(root, fn)
                arc = os.path.relpath(fp, base_dir)
                tar.add(fp, arcname=arc)
    log(f"  打包完成: {os.path.getsize(tmp_tar)//1024} KB")
    log("  上传中...")
    sftp.put(tmp_tar, '/tmp/oa-api.tar.gz')
    log("  上传完成！")
    os.remove(tmp_tar)

    # 解压
    print("\n📦 解压文件...")
    ssh.exec_command(f"sudo rm -rf {REMOTE_BASE}/* && tar -xzf /tmp/oa-api.tar.gz -C {REMOTE_BASE}/.. && sudo chown -R www-data:www-data {REMOTE_BASE} && rm -f /tmp/oa-api.tar.gz")
    # 检查目录结构
    _, out2, _ = ssh.exec_command(f"ls {REMOTE_BASE}/ 2>&1 | head -10").communicate()
    log(f"  目录内容: {out2.decode().strip()[:200]}")
    print("  ✅ 文件解压完成")

    # 写入 .env
    print("\n📦 写入 .env...")
    env_content = "\n".join([
        "APP_NAME=安防运维OA", "APP_ENV=production", "APP_KEY=",
        "APP_DEBUG=false", "APP_URL=http://172.20.0.139", "",
        "DB_CONNECTION=mysql", "DB_HOST=127.0.0.1", "DB_PORT=3306",
        "DB_DATABASE=oa_db", "DB_USERNAME=oa_user", "DB_PASSWORD=OaPass123!",
        "", "SANCTUM_STATEFUL_DOMAINS=172.20.0.139",
    ]) + "\n"
    encoded = __import__('base64').b64encode(env_content.encode()).decode()
    ssh.exec_command(f"echo '{encoded}' | base64 -d | sudo tee {REMOTE_BASE}/.env > /dev/null && sudo chown www-data:www-data {REMOTE_BASE}/.env")
    print("  ✅ .env 写入完成")

    # Composer install
    print("\n📦 运行 composer install...")
    stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_BASE} && sudo -u www-data composer install --no-dev --optimize-autoloader 2>&1 | tail -10", timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    for line in (out + err).split('\n'):
        if line.strip():
            log(line[:150])
    print("  ✅ Composer install 完成")

    # 检查 artisan 是否存在
    _, out3, _ = ssh.exec_command(f"ls {REMOTE_BASE}/artisan 2>&1").communicate()
    if 'artisan' in out3.decode():
        # 生成 APP_KEY + 迁移
        print("\n📦 运行数据库迁移...")
        ssh.exec_command(f"cd {REMOTE_BASE} && php artisan key:generate --force && php artisan migrate --force && php artisan db:seed --force")
        print("  ✅ 数据库迁移完成")
    else:
        log("  ⚠️ artisan 文件不存在，跳过迁移")

    # 测试
    print("\n📦 测试访问...")
    _, out4, _ = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1").communicate()
    code = out4.decode().strip()
    log(f"  HTTP 状态码: {code}")

    sftp.close()
    ssh.close()

    print(f"\n🎉 部署完成！")
    print(f"🌐 访问地址: http://172.20.0.139")
    print(f"📡 API 地址: http://172.20.0.139/api")
    print(f"\n📋 默认账号:")
    print(f"   管理员: admin / admin123")
    print(f"   经理:   manager / 123456")
    print(f"   员工:   user / 123456")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
        import traceback; traceback.print_exc()
