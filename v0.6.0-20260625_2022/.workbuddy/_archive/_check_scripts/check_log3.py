import paramiko, re
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 看 ":id" 错误的 URL (生产日志里 context 部分)
stdin, stdout, stderr = ssh.exec_command('grep -B1 "invalid input syntax for type bigint: " /var/www/oa-api/storage/logs/laravel.log | grep -oE "GET /api/[^\" ]+|POST /api/[^\" ]+|PUT /api/[^\" ]+|DELETE /api/[^\" ]+" | sort -u | head -20')
print("=== affected endpoints ===")
print(stdout.read().decode('utf-8', errors='ignore'))
# 看 knowledge_category_id 上下文
stdin, stdout, stderr = ssh.exec_command('grep -B2 -A1 "knowledge_category_id" /var/www/oa-api/storage/logs/laravel.log | tail -20')
print("\n=== knowledge_category_id context ===")
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
