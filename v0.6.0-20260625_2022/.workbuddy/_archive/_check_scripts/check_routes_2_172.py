"""查172 purchase 路由 + approval 路由"""
import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

cmds = [
    "cd /var/www/oa-api && php artisan route:list 2>&1 | grep -iE 'purchase|approval|finance/(invoice|receivables/.*/pay|transfer)|workbench|sales/(products|opps/.*/(quot|win|move|pool))|leads/.*convert' | head -80",
    "cd /var/www/oa-api && php artisan route:list 2>&1 | wc -l",
    "cd /var/www/oa-api && php artisan route:list 2>&1 | grep -iE 'POST' | head -40",
]
for cmd in cmds:
    print(f'=== {cmd[:80]} ===')
    si, so, se = c.exec_command(cmd, timeout=30)
    out = so.read().decode('utf-8', errors='ignore')
    print(out[:4000])
    print()
c.close()
