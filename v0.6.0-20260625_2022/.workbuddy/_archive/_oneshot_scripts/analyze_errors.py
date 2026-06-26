"""分析 laravel.log 错误类型"""
import paramiko
import re
from collections import Counter

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=15):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace')
    return out

log = run('sudo cat /var/www/oa-api/storage/logs/laravel.log 2>/dev/null', t=15)

# 提取 ERROR 信息
errors = re.findall(r'production\.ERROR: (.+?)(?=\s*\{|\s*$|\[stacktrace\])', log, re.MULTILINE)

# 截断为 100 字符作归类
def normalize(e):
    return re.sub(r'\d+', 'N', e)[:150]

norms = [normalize(e) for e in errors]
counter = Counter(norms)

print(f'共 {len(errors)} 条 ERROR')
print('=' * 80)
print('错误类型 Top 20:')
for err, n in counter.most_common(20):
    print(f'\n[{n:3d}] {err[:200]}')

# 看每个错误首次出现时间
print('\n' + '=' * 80)
print('第一次出现时间 + 完整信息:')
seen = set()
for line in log.split('\n'):
    if 'production.ERROR' in line:
        # 抽时间和消息
        m = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] production\.ERROR: (.+?)(?=\s*\{)', line)
        if m:
            ts, msg = m.group(1), m.group(2)[:150]
            if msg not in seen:
                seen.add(msg)
                print(f'\n[{ts}] {msg}')

ssh.close()
