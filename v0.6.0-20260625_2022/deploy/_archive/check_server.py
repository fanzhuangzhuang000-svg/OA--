import paramiko, json, sys

host, user, password = '172.20.0.139', 'nbcy', 'admin123'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

cmds = [
    ("互联网访问", "curl -s --max-time 5 https://repo.packagist.org 2>&1 | head -1"),
    ("Packagist 可达", "ping -c 1 repo.packagist.org 2>&1 | head -2"),
    ("Composer 版本", "composer --version"),
    ("PHP 版本", "php --version | head -1"),
]

for desc, cmd in cmds:
    print(f"\n🔍 {desc}:")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"   {out[:200]}")
    if err and 'Using a password' not in err: print(f"   ⚠️ {err[:200]}")

# 验证服务器上的 composer.json
print("\n🔍 验证服务器上的 composer.json:")
stdin, stdout, stderr = ssh.exec_command(f"cat /var/www/oa-api/composer.json 2>/dev/null || echo 'NOT_FOUND'", timeout=5)
content = stdout.read().decode().strip()
if content == 'NOT_FOUND':
    print("   ❌ /var/www/oa-api/composer.json 不存在")
else:
    try:
        json.loads(content)
        print("   ✅ composer.json 是有效 JSON")
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON 无效: {e}")
        print(f"   内容前200字: {content[:200]}")

ssh.close()
print("\n✅ 检查完成")
