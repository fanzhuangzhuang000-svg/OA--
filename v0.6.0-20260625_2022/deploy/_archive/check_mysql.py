import paramiko
import sys

host = '172.20.0.139'
user = 'nbcy'
password = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# 检查 MySQL 认证方式
cmds = [
    ("MySQL 用户认证方式", "sudo mysql -u root -e \"SELECT user, plugin FROM mysql.user WHERE user='root';\" 2>&1"),
    ("尝试 mysql -u root（无密码）", "mysql -u root -e 'SELECT 1' 2>&1 | head -3"),
    ("尝试 sudo mysql", "sudo mysql -e 'SELECT 1' 2>&1 | head -3"),
    ("检查 MySQL 是否有密码", "sudo grep -r 'password' /etc/mysql/ 2>/dev/null | head -5"),
]

for desc, cmd in cmds:
    print(f"\n🔍 {desc}:")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"   {out[:300]}")
    if err and 'Using a password' not in err:
        print(f"   ⚠️ {err[:200]}")

ssh.close()
print("\n✅ 检查完成")
