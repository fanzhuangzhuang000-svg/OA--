import paramiko
import sys

host = '172.20.0.139'
user = 'nbcy'
password = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, username=user, password=password, timeout=10)
    print("✅ SSH 连接成功！")

    commands = [
        ("PHP版本", "php -v 2>/dev/null || echo 'PHP未安装'"),
        ("Composer", "which composer 2>/dev/null || echo 'Composer未安装'"),
        ("MySQL", "mysql --version 2>/dev/null || echo 'MySQL未安装'"),
        ("Nginx", "nginx -v 2>&1 || echo 'Nginx未安装'"),
        ("系统信息", "uname -a && cat /etc/os-release | head -5"),
        ("磁盘空间", "df -h /"),
        ("Web目录", "ls /var/www/html/ 2>/dev/null || ls /www/ 2>/dev/null || echo '需确认web目录'"),
    ]

    for desc, cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        print(f"\n📌 {desc}:")
        print(output if output else error)

    ssh.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
    sys.exit(1)
