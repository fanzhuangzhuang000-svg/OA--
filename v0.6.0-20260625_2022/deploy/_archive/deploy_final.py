import paramiko, os, sys, tarfile, tempfile

HOST, USER, PASS = '172.20.0.139', 'nbcy', 'admin123'
LOCAL_API = 'D:/work/website/OA/pc-api'
REMOTE_BASE = '/var/www/oa-api'

def log(m): print(f"  {m}")

def run(ssh, cmd, desc='', sudo=True, timeout=120):
    full = f"sudo bash -c '{cmd}'" if sudo else cmd
    log(f"▶ {desc or cmd[:60]}")
    stdin, stdout, stderr = ssh.exec_command(full, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    for l in (out + err).split('\n'):
        l = l.strip()
        if l: log(f"   {l[:150]}")
    return code == 0, out.strip(), err.strip()

def main():
    print("🚀 部署后端文件到 172.20.0.139...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)
    print("✅ SSH 连接成功")
    sftp = ssh.open_sftp()

    # Step 1: 上传并解压文件
    print("\n📦 步骤1: 上传后端文件...")
    log("  打包中（排除 vendor/ node_modules/）...")
    tmp_tar = os.path.join(tempfile.gettempdir(), 'oa-api.tar.gz')
    with tarfile.open(tmp_tar, 'w:gz') as tar:
        base_dir = os.path.dirname(LOCAL_API)
        for root, dirs, files in os.walk(LOCAL_API):
            dirs[:] = [d for d in dirs if d not in ('vendor','node_modules','.git','__pycache__')]
            for fn in files:
                fp = os.path.join(root, fn)
                arc = os.path.relpath(fp, base_dir)
                tar.add(fp, arcname=arc)
    log(f"  打包完成: {os.path.getsize(tmp_tar)//1024} KB")
    sftp.put(tmp_tar, '/tmp/oa-api.tar.gz')
    log("  上传完成！")
    os.remove(tmp_tar)

    print("\n📦 步骤2: 解压文件...")
    run(ssh, f"rm -rf {REMOTE_BASE}/*", "清理旧文件")
    run(ssh, f"tar -xzf /tmp/oa-api.tar.gz -C {REMOTE_BASE}/..", "解压")
    # 如果解压出来是 pc-api 目录，把内容移过去
    ok, out, _ = run(ssh, f"ls -d {REMOTE_BASE}/../pc-api 2>/dev/null && echo YES || echo NO", "检查目录名")
    if 'YES' in out:
        run(ssh, f"cp -r {REMOTE_BASE}/../pc-api/* {REMOTE_BASE}/ && rm -rf {REMOTE_BASE}/../pc-api", "移动文件")
    run(ssh, f"chown -R www-data:www-data {REMOTE_BASE}", "设置权限")
    run(ssh, "rm -f /tmp/oa-api.tar.gz", "删除临时文件")

    # Step 3: Composer install
    print("\n📦 步骤3: 安装 PHP 依赖...")
    run(ssh, f"cd {REMOTE_BASE} && sudo -u www-data composer install --no-dev --optimize-autoloader 2>&1 | tail -5", "Composer install", sudo=False)

    # Step 4: 写入 .env
    print("\n📦 步骤4: 写入 .env...")
    env_content = "\n".join([
        "APP_NAME=安防运维OA", "APP_ENV=production", "APP_KEY=",
        "APP_DEBUG=false", "APP_URL=http://172.20.0.139", "",
        "DB_CONNECTION=mysql", "DB_HOST=127.0.0.1", "DB_PORT=3306",
        "DB_DATABASE=oa_db", "DB_USERNAME=oa_user", "DB_PASSWORD=OaPass123!",
        "", "SANCTUM_STATEFUL_DOMAINS=172.20.0.139",
    ]) + "\n"
    import base64
    encoded = base64.b64encode(env_content.encode()).decode()
    run(ssh, f"echo '{encoded}' | base64 -d | sudo tee {REMOTE_BASE}/.env > /dev/null", "写入 .env")
    run(ssh, f"chown www-data:www-data {REMOTE_BASE}/.env", "设置 .env 权限")

    # Step 5: 生成 APP_KEY + 迁移
    print("\n📦 步骤5: 数据库迁移...")
    run(ssh, f"cd {REMOTE_BASE} && php artisan key:generate --force", "生成 APP_KEY")
    run(ssh, f"cd {REMOTE_BASE} && php artisan migrate --force", "运行迁移")
    run(ssh, f"cd {REMOTE_BASE} && php artisan db:seed --force", "运行种子")

    # Step 6: 测试
    print("\n📦 步骤6: 测试访问...")
    _, out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/", "测试 HTTP")
    log(f"  HTTP 状态码: {out}")

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
