"""抓剩余 3 个 POST 错 + 列日志错误"""
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

print('=== 最近 30 行 laravel.log ===')
si, so, se = ssh.exec_command('sudo -n tail -50 /var/www/oa-api/storage/logs/laravel.log 2>&1', timeout=10)
print(so.read().decode('utf-8', 'replace'))

ssh.close()
