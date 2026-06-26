"""查172实际路由名"""
import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

cmds = [
    "cd /var/www/oa-api && grep -E 'Route::(get|post|put|patch|delete)' routes/api.php | grep -iE 'sales|leads|opps|quotations|attendance|leave|purchase|finance|approval' | head -100",
    "cd /var/www/oa-api && php artisan route:list 2>&1 | grep -iE 'sales|attendance|purchase|finance|approval|knowledge' | head -80",
]
for cmd in cmds:
    print(f'=== {cmd[:80]} ===')
    si, so, se = c.exec_command(cmd, timeout=30)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    print(out[:3000])
    if err.strip():
        print('STDERR:', err[:500])
c.close()
