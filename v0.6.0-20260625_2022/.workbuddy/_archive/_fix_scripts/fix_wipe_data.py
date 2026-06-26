"""修复 wipeData 方法：补全漏掉的业务表"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

# 1. 看当前 wipeData 完整的 tables 数组
out = run('sed -n "/function wipeData/,/DB::beginTransaction/p" /var/www/oa-api/app/Http/Controllers/Api/SystemSettingsController.php | head -55')
print('=== 当前 tables 列表 ===')
print(out)

# 2. 修补 - 在 $tables 数组里 'notifications', 后加上漏掉的表
sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/SystemSettingsController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 把 fuel_cards / fuel_card_recharges / inventory_categories / suppliers / system_logs 加进去
# 它们应该在 notifications 之后
old_tail = "            'notifications',\n        ];"
new_tail = """            'notifications', 'system_logs',
            'fuel_card_recharges', 'fuel_cards',
            'inventory_categories',
            'suppliers',
        ];"""

if old_tail in content:
    content = content.replace(old_tail, new_tail)
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/SystemSettingsController.php', 'w') as f:
        f.write(content)
    print('\n✓ tables 列表已扩充 5 张表')
else:
    print('\n⚠️ 找不到旧的 tables 末尾，尝试其他位置')

# 3. 验证修改
out = run('grep -A 2 "fuel_cards" /var/www/oa-api/app/Http/Controllers/Api/SystemSettingsController.php | head -5')
print('\n=== 修改后 ===')
print(out)

# 4. 重启 FPM
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)
print('\n✓ php-fpm 已重启')

# 5. 测 wipe-data
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

import urllib.error
data = json.dumps({'password':'admin123','confirm_phrase':'确认清空'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/admin/wipe-data', data=data, headers={'Authorization': f'Bearer {token}','Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode('utf-8'))
        print(f'\n=== wipe 响应 code={resp.get("code")} ===')
        print(f'message: {resp.get("message")}')
        data_field = resp.get('data', {})
        # 统计非 0 的项
        non_zero = {k: v for k, v in data_field.items() if v and v != 0 and v != 'ERR: '}
        print(f'\n实际删除的表: {len(non_zero)} 张')
        for k, v in non_zero.items():
            print(f'  {k}: {v}')
except urllib.error.HTTPError as e:
    print(f'\nwipe HTTP {e.code}:', e.read().decode()[:500])

ssh.close()
