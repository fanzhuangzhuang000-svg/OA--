import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 看 knowledge_articles 真实字段
cmds = [
    'PGPASSWORD=nbcy psql -h 127.0.0.1 -U nbcy -d oa -c "\\d knowledge_articles" 2>&1 | head -40',
    'PGPASSWORD=nbcy psql -h 127.0.0.1 -U nbcy -d oa -c "\\d knowledge_categories" 2>&1 | head -30',
    'sudo -u www-data grep -rn "knowledge_category_id" /var/www/oa-api/app/ 2>/dev/null | head -10',
]
for c in cmds:
    print("=== " + c)
    stdin, stdout, stderr = ssh.exec_command(c)
    print(stdout.read().decode('utf-8', errors='ignore'))
    e = stderr.read().decode('utf-8', errors='ignore')
    if e: print('STDERR:', e)
ssh.close()
