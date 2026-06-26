import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
script = r'''
echo "=== :id context (where) ==="
grep -B0 -A3 'invalid input syntax for type bigint: ":id"' /var/www/oa-api/storage/logs/laravel.log | grep -oE 'where "id" =[^,]+|SQL: [^,]{0,150}' | sort -u | head -20

echo ""
echo "=== :id 请求路径 ==="
grep -B0 -A1 'invalid input syntax for type bigint: ":id"' /var/www/oa-api/storage/logs/laravel.log | grep -oE '"[A-Z]+ /api/[^ "]+' | sort -u | head -20

echo ""
echo "=== NaN 表 ==="
grep -B0 -A1 'invalid input syntax for type bigint: "NaN"' /var/www/oa-api/storage/logs/laravel.log | grep -oE 'select [^f]*from "[^"]+"' | sort -u | head -20

echo ""
echo "=== NaN 请求路径 ==="
grep -B0 -A1 'invalid input syntax for type bigint: "NaN"' /var/www/oa-api/storage/logs/laravel.log | grep -oE '"[A-Z]+ /api/[^ "]+' | sort -u | head -20
'''
stdin, stdout, stderr = ssh.exec_command(script)
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
