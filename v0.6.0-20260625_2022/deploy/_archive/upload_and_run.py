import paramiko, sys

HOST, USER, PASS = '172.20.0.139', 'nbcy', 'admin123'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)
print("✅ SSH 连接成功")

# 上传部署脚本
sftp = ssh.open_sftp()
print("📦 上传 deploy_full.sh...")
sftp.put('D:/work/website/OA/deploy/deploy_full.sh', '/tmp/deploy_full.sh')
ssh.exec_command("chmod +x /tmp/deploy_full.sh")
print("  ✅ 上传完成")

# 执行部署脚本
print("🚀 开始执行服务器端部署（约 3-5 分钟）...")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("sudo bash /tmp/deploy_full.sh 2>&1", timeout=600)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("⚠️ 错误输出:")
    print(err[:500])

sftp.close()
ssh.close()
print("\n🎉 部署脚本执行完成！")
