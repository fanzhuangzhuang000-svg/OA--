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

    # 测试 sudo 是否需要密码
    stdin, stdout, stderr = ssh.exec_command('sudo -n echo "sudo_ok" 2>&1')
    result = stdout.read().decode().strip()
    if "sudo_ok" in result:
        print("✅ sudo 无需密码")
        sudo_needs_pwd = False
    else:
        print("⚠️ sudo 需要密码")
        sudo_needs_pwd = True

    # 检查是否可以用 root 直接登录
    try:
        ssh_root = paramiko.SSHClient()
        ssh_root.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_root.connect(host, username='root', password='admin123', timeout=5)
        print("✅ root 用户可直接登录")
        ssh_root.close()
        use_root = True
    except:
        print("❌ root 用户不可直接登录，将使用 nbcy+sudo")
        use_root = False

    ssh.close()
    print("\n📋 部署方案：")
    if use_root:
        print("   使用 root 用户直接部署（推荐）")
    else:
        print("   使用 nbcy 用户 + sudo 部署")
        if sudo_needs_pwd:
            print("   ⚠️ 需要交互式输入 sudo 密码，建议使用 root 登录")

except Exception as e:
    print(f"❌ 连接失败: {e}")
    sys.exit(1)
