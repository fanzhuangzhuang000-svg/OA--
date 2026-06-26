#!/usr/bin/env python
"""从172服务器复制Concerns目录到152服务器"""
import paramiko
import os
import sys

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

LOCAL_CONCERNS = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\Concerns'
REMOTE_TMP = '/tmp/Concerns'
REMOTE_TARGET = '/var/www/oa-api/app/Http/Controllers/Api/Concerns'

print(f"[1/4] 本地Concerns目录: {LOCAL_CONCERNS}")
if not os.path.exists(LOCAL_CONCERNS):
    print(f"[FAIL] 本地目录不存在: {LOCAL_CONCERNS}")
    sys.exit(1)

local_files = os.listdir(LOCAL_CONCERNS)
print(f"      本地文件数: {len(local_files)}")
for f in local_files:
    print(f"      - {f}")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)
print(f"\n[2/4] SSH连接成功: {HOST}")

# 创建远程临时目录并上传
sftp = ssh.open_sftp()
try:
    sftp.mkdir(REMOTE_TMP)
except OSError:
    pass

print(f"[3/4] 上传 {len(local_files)} 个文件到 {REMOTE_TMP}")
for f in local_files:
    local_path = os.path.join(LOCAL_CONCERNS, f).replace('\\', '/')
    remote_path = f"{REMOTE_TMP}/{f}"
    sftp.put(local_path, remote_path)
    print(f"      [OK] {f}")
sftp.close()

# 远程复制到目标位置
print(f"[4/4] 部署到 {REMOTE_TARGET}")
cmd = f"""sudo mkdir -p {REMOTE_TARGET} && \
sudo cp -r {REMOTE_TMP}/* {REMOTE_TARGET}/ && \
sudo chown -R www-data:www-data {REMOTE_TARGET} && \
sudo rm -rf {REMOTE_TMP} && \
echo '[OK] Concerns部署完成' && \
ls -la {REMOTE_TARGET}/"""

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='ignore'))
err = stderr.read().decode('utf-8', errors='ignore')
if err:
    print(f"[STDERR] {err}")

# 重启PHP-FPM
print("\n[BONUS] 重启PHP-FPM")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart php8.3-fpm && echo "[OK] PHP-FPM重启完成"')
print(stdout.read().decode('utf-8', errors='ignore'))

# 测试API
print("\n[TEST] 测试API")
stdin, stdout, stderr = ssh.exec_command('sleep 2 && curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:3001/api/health')
print(f"Health: {stdout.read().decode('utf-8', errors='ignore')}")

ssh.close()
print("\n[DONE] 全部完成")
