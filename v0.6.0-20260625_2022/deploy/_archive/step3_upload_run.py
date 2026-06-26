#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""上传PHP文件到服务器并执行"""
import paramiko, requests

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S {cmd}', timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

# 上传
print("上传 seed_demo.php...")
run('chown nbcy:nbcy /var/www/oa-api')
sftp = ssh.open_sftp()
sftp.put('D:/work/website/OA/deploy/seed_demo.php', '/var/www/oa-api/seed_demo.php')
sftp.close()
print("上传完成")

# 语法检查
print("\n语法检查...")
out = run("php -l /var/www/oa-api/seed_demo.php 2>&1")
print(out)
if 'Errors' in out:
    print("语法错误，停止执行")
    ssh.close()
    exit(1)

# 执行
print("\n执行 seed...")
out = run("bash -c 'cd /var/www/oa-api && php seed_demo.php 2>&1'", timeout=120)
print(out)

# 恢复权限
run('chown www-data:www-data /var/www/oa-api')
ssh.close()

# 验证
print("\n" + "="*55)
print("验证数据:")
print("="*55)
r = requests.post('http://172.20.0.139:3001/api/auth/login', json={'username':'admin','password':'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['data']['token']
    headers = {'Authorization': f'Bearer {token}'}
    for m, p, n in [('GET','/api/employees/departments','部门'),('GET','/api/employees','员工'),('GET','/api/customers','客户'),('GET','/api/projects','项目'),('GET','/api/service/orders','售后'),('GET','/api/expenses','报销'),('GET','/api/vehicles','车辆'),('GET','/api/inventory','库存'),('GET','/api/finance/receivables','应收'),('GET','/api/finance/payables','应付'),('GET','/api/attendance/records?month=2026-06','考勤'),('GET','/api/disk/folders','网盘'),('GET','/api/knowledge/categories','知识库'),('GET','/api/system-logs','日志')]:
        try:
            r2 = requests.get(f'http://172.20.0.139:3001{p}', headers=headers, timeout=10)
            if r2.status_code == 200:
                d = r2.json().get('data', {})
                if isinstance(d, list):
                    cnt = len(d)
                elif isinstance(d, dict):
                    cnt = d.get('total', d.get('items', d.get('count', len(d.get('list', [])))))
                    if cnt is None: cnt = '?'
                else:
                    cnt = '?'
                print(f"  {n:<8} 200   {cnt}")
            else:
                print(f"  {n:<8} {r2.status_code}")
        except Exception as e:
            print(f"  {n:<8} ERR {e}")
print("\n完成!")
