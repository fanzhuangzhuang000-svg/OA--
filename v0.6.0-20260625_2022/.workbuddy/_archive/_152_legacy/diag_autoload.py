"""Diagnose why the Enums autoload is failing."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

cmds = [
    # Check the autoload_static.php to see if our files are listed
    'grep -n "Enums" /var/www/oa-api/vendor/composer/autoload_files.php 2>/dev/null',
    'grep -n "Enums" /var/www/oa-api/vendor/composer/autoload_static.php 2>/dev/null',
    'cat /var/www/oa-api/vendor/composer/autoload_files.php 2>/dev/null | head -30',
    # Check vendor/composer/installed.json for the files
    'cat /var/www/oa-api/vendor/composer/installed.php 2>/dev/null | grep -i "files" -A 3 | head -10',
    # Verify file path is correct
    'ls -la /var/www/oa-api/app/Enums/index.php',
    'head -5 /var/www/oa-api/app/Enums/index.php',
    # Run composer dump-autoload with -o (no warnings)
    'cd /var/www/oa-api && sudo -u www-data composer dump-autoload --no-dev 2>&1 | tail -10',
    # After dump, check the file list again
    'grep -c "index.php" /var/www/oa-api/vendor/composer/autoload_files.php 2>/dev/null',
    # Try loading the class directly (maybe it works despite bool(false))
    'cd /var/www/oa-api && sudo -u www-data php -r "require \\"/var/www/oa-api/vendor/autoload.php\\"; require_once \\"/var/www/oa-api/app/Enums/index.php\\"; var_dump(enum_exists(\'UserStatus\'));" 2>&1',
    'cd /var/www/oa-api && sudo -u www-data php -r "require \\"/var/www/oa-api/vendor/autoload.php\\"; var_dump(enum_exists(\'App\\\\Enums\\\\UserStatus\'));" 2>&1',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(f"OUT: {out}")
    if err.strip():
        print(f"ERR: {err}")

client.close()
