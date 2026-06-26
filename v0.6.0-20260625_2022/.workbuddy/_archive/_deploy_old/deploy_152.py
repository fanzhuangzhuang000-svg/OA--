"""部署脚本：本地 pc-api + pc-web → 152 展示平台"""
import paramiko, os, sys, time

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

LOCAL_API = 'D:/work/website/OA/pc-api'
LOCAL_WEB = 'D:/work/website/OA/pc-web'
REMOTE_API = '/var/www/oa-api'
REMOTE_WEB = '/var/www/oa-web'
STAGE_API = '/tmp/oa-api-staging'
STAGE_WEB = '/tmp/oa-web-staging'

def ssh():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS)
    return c

def run(c, cmd, timeout=120):
    print('>>>', cmd)
    si, so, se = c.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    if out.strip(): print(out[:1500])
    if err.strip() and 'arning' not in err and 'No such' not in err: print('ERR:', err[:600])
    return out, err

def upload_dir(sftp, local, remote):
    try: sftp.mkdir(remote)
    except IOError: pass
    for name in os.listdir(local):
        lp = os.path.join(local, name)
        rp = remote + '/' + name
        if os.path.isdir(lp):
            upload_dir(sftp, lp, rp)
        else:
            try: sftp.put(lp, rp)
            except Exception as e: print('FAIL', rp, e)

def main():
    c = ssh()
    sftp = c.open_sftp()

    # === 1. 同步 pc-api（后端） ===
    print('\n========== 1. 同步 pc-api 后端 ==========')
    run(c, f'rm -rf {STAGE_API} && mkdir -p {STAGE_API}')
    upload_dir(sftp, LOCAL_API, STAGE_API)
    print('API uploaded')

    # 复制到目标 + 设置 owner
    run(c, f'sudo rm -rf {REMOTE_API}.bak && sudo mv {REMOTE_API} {REMOTE_API}.bak')
    run(c, f'sudo mkdir -p {REMOTE_API}')
    run(c, f'sudo cp -r {STAGE_API}/. {REMOTE_API}/')
    run(c, f'sudo chown -R www-data:www-data {REMOTE_API}')
    run(c, f'sudo rm -rf {STAGE_API}')

    # composer install（如有 vendor）
    run(c, f'cd {REMOTE_API} && [ -f composer.json ] && sudo -u www-data composer install --no-dev --no-security-blocking --no-interaction 2>&1 | tail -10', timeout=300)

    # 数据库迁移
    run(c, f'cd {REMOTE_API} && sudo -u www-data php artisan migrate --force 2>&1 | tail -20', timeout=120)

    # 缓存清理 + php-fpm 重启
    run(c, f'cd {REMOTE_API} && sudo -u www-data php artisan route:clear && sudo -u www-data php artisan config:clear && sudo -u www-data php artisan cache:clear')

    # === 2. 同步 pc-web（前端） ===
    print('\n========== 2. 同步 pc-web 前端 ==========')
    run(c, f'rm -rf {STAGE_WEB} && mkdir -p {STAGE_WEB}')
    upload_dir(sftp, LOCAL_WEB + '/dist', STAGE_WEB)
    print('Web dist uploaded')

    # 备份 + 替换
    run(c, f'sudo rm -rf {REMOTE_WEB}.bak && sudo mv {REMOTE_WEB} {REMOTE_WEB}.bak')
    run(c, f'sudo mkdir -p {REMOTE_WEB}')
    run(c, f'sudo cp -r {STAGE_WEB}/. {REMOTE_WEB}/')
    run(c, f'sudo chown -R www-data:www-data {REMOTE_WEB}')
    run(c, f'rm -rf {STAGE_WEB}')

    # nginx 配置（如果需要）
    # 假设 nginx 已配置 /var/www/oa-web → SPA fallback + /api → 3001

    # === 3. 重启服务 ===
    print('\n========== 3. 重启服务 ==========')
    run(c, 'sudo systemctl restart php8.3-fpm 2>&1 | tail -3')
    run(c, 'sudo systemctl reload nginx 2>&1 | tail -3')

    sftp.close()
    c.close()
    print('\n========== 部署完成 ==========')

if __name__ == '__main__':
    main()
