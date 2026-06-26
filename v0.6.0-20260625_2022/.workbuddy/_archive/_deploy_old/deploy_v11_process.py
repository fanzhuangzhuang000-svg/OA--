"""
V1.1 工序验收 - 部署到 172.20.0.139
流程：sftp put → /tmp/ → sudo cp → oa-api → chown www-data → migrate → GRANT → seed → restart php-fpm
"""
import paramiko, time, re, os

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
API = '/var/www/oa-api'

FILES = [
    (r'D:\work\website\OA\pc-api\database\migrations\2026_06_22_130000_create_process_tables.php',
     f'{API}/database/migrations/2026_06_22_130000_create_process_tables.php'),
    (r'D:\work\website\OA\pc-api\app\Models\OtherModels.php',
     f'{API}/app/Models/OtherModels.php'),
    (r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\ProcessController.php',
     f'{API}/app/Http/Controllers/Api/ProcessController.php'),
    (r'D:\work\website\OA\pc-api\routes\api.php',
     f'{API}/routes/api.php'),
    (r'D:\work\website\OA\pc-api\database\seeders\ProcessTemplateSeeder.php',
     f'{API}/database/seeders/ProcessTemplateSeeder.php'),
]

def run(ssh, cmd, label='', echo=True, timeout=120, get_pty=True):
    if label and echo:
        print(f'  [{label}] $ {cmd[:90]}')
    if get_pty:
        si, so, se = ssh.exec_command(cmd, timeout=timeout, get_pty=True)
    else:
        si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    if echo and (out or err):
        for line in (out or err).split('\n')[:20]:
            print(f'    {line}')
    return out, err, rc

def main():
    print('=' * 60)
    print('  V1.1 工序验收 → 部署 172.20.0.139')
    print('=' * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    print(f'  [SSH] OK  {HOST}')

    # 1) 上传：先 put 到 /tmp/，再 sudo cp 到目标
    print('\n  [1/8] 上传 5 个文件 (tmp → sudo cp)')
    sftp = ssh.open_sftp()
    for local, remote in FILES:
        name = os.path.basename(local)
        tmp = f'/tmp/upload_{name}'
        sftp.put(local, tmp)
        # sudo cp + chown
        run(ssh, f'sudo cp {tmp} {remote} && sudo chown www-data:www-data {remote} && sudo rm {tmp}',
            label=remote.split('/')[-1], echo=True, timeout=30)
    sftp.close()

    # 2) migrate 只跑我新加的那个文件 (--path 避免重跑已存在的旧表)
    print('\n  [2/8] php artisan migrate --path=2026_06_22_130000_create_process_tables.php --force')
    run(ssh, f'cd {API} && sudo -u www-data php artisan migrate --path=database/migrations/2026_06_22_130000_create_process_tables.php --force 2>&1 | tail -25',
        label='migrate v1.1', timeout=120)

    # 3) GRANT (用 oa_user 真实身份，不用 postgres)
    print('\n  [3/8] GRANT 5 张新表权限')
    DB = 'security_oa'
    DB_USER = 'oa_user'
    DB_PWD = 'oa_pg_pwd_782997781'
    export = f'PGPASSWORD={DB_PWD}'
    for tbl in ['process_templates', 'process_instances', 'process_inspections', 'process_images', 'process_signatures']:
        run(ssh,
            f'{export} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -c "GRANT ALL PRIVILEGES ON TABLE {tbl} TO {DB_USER}; GRANT USAGE, SELECT ON SEQUENCE {tbl}_id_seq TO {DB_USER};" 2>&1 | tail -3',
            label=f'grant {tbl}', echo=True, timeout=30)

    # 4) seeder
    print('\n  [4/8] php artisan db:seed ProcessTemplateSeeder --force')
    run(ssh, f'cd {API} && sudo -u www-data php artisan db:seed --class=ProcessTemplateSeeder --force 2>&1 | tail -20',
        label='seed', timeout=120)

    # 5) clear
    print('\n  [5/8] route:clear + config:clear')
    run(ssh, f'cd {API} && sudo -u www-data php artisan route:clear && sudo -u www-data php artisan config:clear',
        label='clear')

    # 6) restart php-fpm
    print('\n  [6/8] restart php8.3-fpm')
    run(ssh, 'sudo systemctl restart php8.3-fpm', label='restart fpm')
    time.sleep(2)

    # 7) 路由存在性验证
    print('\n  [7/8] 验证路由表 (route:list)')
    run(ssh, f'cd {API} && sudo -u www-data php artisan route:list 2>&1 | grep -i "process" | head -20',
        label='route:list process', timeout=30)

    # 8) API端点验证 (带 token)
    print('\n  [8/8] 端到端验证 (login → GET /api/process/templates)')
    login_cmd = '''curl -s -X POST http://127.0.0.1:3001/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' '''
    out, _, _ = run(ssh, login_cmd, label='login', timeout=30, get_pty=False)
    print(f'    login body: {out[:200]}')
    m = re.search(r'"token"\s*:\s*"([^"]+)"', out) or re.search(r'"access_token"\s*:\s*"([^"]+)"', out)
    if m:
        token = m.group(1)
        print(f'    ✓ token={token[:30]}...')
        for ep in ['/api/process/industries', '/api/process/templates', '/api/process/instances', '/api/process/inspections']:
            tpl_cmd = f'curl -s -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1:3001{ep} 2>&1'
            tpl_out, _, _ = run(ssh, tpl_cmd, label=f'GET {ep}', echo=False, timeout=30, get_pty=False)
            print(f'    {ep}')
            print(f'      → {tpl_out[:250]}')
    else:
        print(f'    ⚠️  没拿到 token，跳过 endpoint 测试')

    ssh.close()
    print('\n' + '=' * 60)
    print('  ✅ V1.1 部署 + 验证完成')
    print('=' * 60)

if __name__ == '__main__':
    main()
