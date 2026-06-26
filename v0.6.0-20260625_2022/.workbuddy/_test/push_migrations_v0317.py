"""v0.3.17 — 推送 3 个幂等性加固的 stock_records migration 到 172"""
import sys, os
import paramiko
import posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
REMOTE_API = '/var/www/oa-api'

LOCAL_FILES = [
    r'D:\work\website\OA\pc-api\database\migrations\2024_01_07_000003_create_stock_records_table.php',
    r'D:\work\website\OA\pc-api\database\migrations\2026_06_21_130000_add_party_fields_to_stock_records.php',
    r'D:\work\website\OA\pc-api\database\migrations\2026_06_21_140000_add_logistics_to_stock_records.php',
]

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    sftp = ssh.open_sftp()

    for lf in LOCAL_FILES:
        fn = os.path.basename(lf)
        remote_tmp = f'/tmp/{fn}'
        remote_final = f'{REMOTE_API}/database/migrations/{fn}'
        sftp.put(lf, remote_tmp)
        print(f'  ✓ uploaded {fn} → {remote_tmp}')

        for cmd, label in [
            (f'sudo -n cp {remote_tmp} {remote_final}', 'cp'),
            (f'sudo -n chown www-data:www-data {remote_final}', 'chown'),
            (f'sudo -n chmod 644 {remote_final}', 'chmod'),
        ]:
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
            rc = stdout.channel.recv_exit_status()
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            print(f'    {label} rc={rc} {out} {err[:200] if err else ""}')
            if rc != 0:
                return 1

    sftp.close()
    ssh.close()
    print('\n✅ 3 个 migration 已推送到 172')
    return 0

if __name__ == '__main__':
    sys.exit(main())
