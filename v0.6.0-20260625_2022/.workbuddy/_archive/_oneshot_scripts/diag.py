import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=20)

def run(cmd):
    si, so, se = ssh.exec_command(cmd, timeout=20, get_pty=True)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    return out or err

print('--- .env DB ---')
print(run('grep -E "^DB_(DATABASE|HOST|USERNAME|PASSWORD)" /var/www/oa-api/.env'))

print('\n--- psql 列表 ---')
print(run('sudo -u postgres psql -l 2>&1 | head -25'))

print('\n--- 现有 migrations ---')
print(run('sudo -u postgres psql -d oa -c "SELECT migration FROM migrations ORDER BY id DESC LIMIT 10;" 2>&1 | head -20'))

ssh.close()
