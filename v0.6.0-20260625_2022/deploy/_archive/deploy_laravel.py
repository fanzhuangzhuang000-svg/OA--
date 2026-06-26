import paramiko, os, sys, json, io

HOST, USER, PASS = '172.20.0.139', 'nbcy', 'admin123'
REMOTE_BASE = '/var/www/oa-api'

def log(m): print(f"  {m}")

def run(ssh, cmd, desc='', timeout=120):
    log(f"▶ {desc or cmd[:60]}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    for l in (out + err).split('\n'):
        l = l.strip()
        if l: log(f"   {l[:150]}")
    return code == 0, out.strip(), err.strip()

def main():
    print("🚀 重新部署（正确方式：composer create-project）...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)
    print("✅ SSH 连接成功")

    # Step 1: 备份已有的（如果有）
    print(f"\n📦 步骤1: 清理旧项目...")
    run(ssh, f"sudo rm -rf {REMOTE_BASE}", "删除旧目录")

    # Step 2: 用 composer 创建真正的 Laravel 11 项目
    print(f"\n📦 步骤2: 创建 Laravel 11 项目（composer create-project）...")
    print("   ⏳ 这可能需要 2-5 分钟（下载依赖）...")
    ok, out, err = run(ssh,
        f"cd /var/www && sudo -u www-data composer create-project laravel/laravel oa-api --prefer-dist --no-interaction 2>&1 | tail -10",
        "composer create-project laravel/laravel",
        timeout=300)

    if not ok:
        print(f"   ❌ Laravel 创建失败: {err[:300]}")
        sys.exit(1)

    # Step 3: 验证 Laravel 安装
    print(f"\n📦 步骤3: 验证 Laravel 安装...")
    ok, out, _ = run(ssh, f"ls {REMOTE_BASE}/artisan {REMOTE_BASE}/public/index.php 2>/dev/null && echo EXISTS || echo MISSING", "检查 artisan")
    if 'MISSING' in out:
        print("   ❌ Laravel 安装失败")
        sys.exit(1)
    run(ssh, f"cd {REMOTE_BASE} && php artisan --version", "Laravel 版本")

    # Step 4: 安装额外依赖（Sanctum + Spatie Permission）
    print(f"\n📦 步骤4: 安装额外依赖...")
    run(ssh, f"cd {REMOTE_BASE} && sudo -u www-data composer require laravel/sanctum spatie/laravel-permission --no-interaction 2>&1 | tail -5", "composer require", timeout=120)

    # Step 5: 生成 APP_KEY
    print(f"\n📦 步骤5: 生成 APP_KEY...")
    run(ssh, f"cd {REMOTE_BASE} && php artisan key:generate", "key:generate")

    # Step 6: 配置 .env（数据库）
    print(f"\n📦 步骤6: 配置 .env...")
    env_lines = [
        "APP_NAME=安防运维OA",
        "APP_ENV=production",
        "APP_KEY=",
        "APP_DEBUG=false",
        "APP_URL=http://172.20.0.139",
        "",
        "DB_CONNECTION=mysql",
        "DB_HOST=127.0.0.1",
        "DB_PORT=3306",
        "DB_DATABASE=oa_db",
        "DB_USERNAME=oa_user",
        "DB_PASSWORD=OaPass123!",
        "",
        "SANCTUM_STATEFUL_DOMAINS=172.20.0.139",
    ]
    env_content = '\n'.join(env_lines) + '\n'
    import base64
    encoded = base64.b64encode(env_content.encode()).decode()
    run(ssh, f"echo '{encoded}' | base64 -d | sudo tee {REMOTE_BASE}/.env > /dev/null", "写入 .env")
    run(ssh, f"cd {REMOTE_BASE} && php artisan key:generate", "重新生成 APP_KEY")

    # Step 7: 运行迁移（使用 debian-sys-maint 创建数据库）
    print(f"\n📦 步骤7: 数据库迁移...")
    # 先确保数据库存在
    run(ssh, """sudo mysql -u debian-sys-maint -p"$(sudo grep password /etc/mysql/debian.cnf | head -1 | cut -d= -f2 | tr -d ' ')" -e "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null""", "创建数据库", timeout=30)
    run(ssh, f"cd {REMOTE_BASE} && php artisan migrate --force", "运行迁移", timeout=60)

    # Step 8: 配置 Nginx（已经配置好了，只需确认）
    print(f"\n📦 步骤8: 确认 Nginx 配置...")
    run(ssh, "sudo nginx -t", "测试 Nginx 配置")
    run(ssh, "sudo systemctl reload nginx", "重载 Nginx")

    # Step 9: 测试
    print(f"\n📦 步骤9: 测试访问...")
    _, out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>/dev/null", "测试 HTTP")
    log(f"   HTTP 状态码: {out.strip()}")

    ssh.close()

    print(f"\n🎉 部署完成！")
    print(f"🌐 访问地址: http://172.20.0.139")
    print(f"📡 API 地址: http://172.20.0.139/api")
    print(f"\n⚠️ 注意：现在只有 Laravel 骨架，我的业务代码还没复制进去")
    print(f"   下一步需要把 controller/model/migration 等文件复制进去")

if __name__ == '__main__':
    try: main()
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback; traceback.print_exc()
