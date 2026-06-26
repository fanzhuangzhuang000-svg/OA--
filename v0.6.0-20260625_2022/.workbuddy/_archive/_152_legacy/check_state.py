"""Quick check of server state for Enums and composer.json."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

cmds = [
    'ls -la /var/www/oa-api/app/Enums/',
    'cat /var/www/oa-api/composer.json | head -40',
    'grep -c "^enum" /var/www/oa-api/app/Enums/index.php',
    'ls /var/www/oa-api/app/Models/',
    'sudo -u www-data php -r "require \\"/var/www/oa-api/vendor/autoload.php\\"; var_dump(class_exists(\\"App\\\\\\\\Enums\\\\\\\\UserStatus\\"));" 2>&1 | head -5',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err.strip():
        print(f"STDERR: {err}")

client.close()
