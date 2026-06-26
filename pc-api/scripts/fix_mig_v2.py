#!/usr/bin/env python3
"""重新部署 110003+110005 + migrate"""
import os
import sys
import paramiko

HOST = os.environ.get('OA172_HOST', '172.20.0.139')
USER = os.environ.get('OA172_USER', 'nbcy')
PWD = os.environ.get('OA172_PWD', '')

if not PWD:
    print("ERROR: 环境变量 OA172_PWD 未设置", file=sys.stderr)
    print("请设置: export OA172_PWD='your_password'", file=sys.stderr)
    sys.exit(2)

LOCAL_BASE = r'D:\work\website\OA\pc-api'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PWD, allow_agent=False, look_for_keys=False)


def run(c, check=False):
    s = ssh.exec_command(c)
    o = s[1].read().decode()
    e = s[2].read().decode()
    rc = s[1].channel.recv_exit_status()
    return rc, o, e


# 重新 put 2 个文件
sftp = ssh.open_sftp()
for name in [
    "2026_06_19_110003_create_purchase_contracts_table.php",
    "2026_06_19_110005_create_purchase_payment_requests_table.php",
]:
    local = os.path.join(LOCAL_BASE, "database", "migrations", name)
    sftp.put(local, "/tmp/" + name)
    print(f"  ✓ put {name}")
sftp.close()

# cp 覆盖
run("sudo -n cp -f /tmp/2026_06_19_110003_create_purchase_contracts_table.php /var/www/oa-api/database/migrations/2026_06_19_110003_create_purchase_contracts_table.php")
run("sudo -n cp -f /tmp/2026_06_19_110005_create_purchase_payment_requests_table.php /var/www/oa-api/database/migrations/2026_06_19_110005_create_purchase_payment_requests_table.php")

# 验证
rc, o, e = run("head -16 /var/www/oa-api/database/migrations/2026_06_19_110003_create_purchase_contracts_table.php | grep 'Schema::create'")
print(f"  110003 → {o.strip()}")
rc, o, e = run("head -16 /var/www/oa-api/database/migrations/2026_06_19_110005_create_purchase_payment_requests_table.php | grep 'Schema::create'")
print(f"  110005 → {o.strip()}")

# 跑 migrate
print("\n=== migrate --force ===")
rc, o, e = run("cd /var/www/oa-api && sudo -n -u www-data php artisan migrate --force 2>&1")
print(f"rc={rc}")
print(o)
print(e)

ssh.close()
