import paramiko
import time

print("🔍 快速测试 172.20.0.139 SSH 连接...")
print("=" * 50)

# 测试几个可能的凭据
credentials = [
    ('ubuntu', 'Aa782997781.'),
    ('root', 'admin123'),
    ('ubuntu', 'admin123'),
    ('root', 'Aa782997781.'),
]

for username, password in credentials:
    print(f"\n尝试: {username} / {password[:3]}***")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('172.20.0.139', username=username, password=password, timeout=5)
        print(f"  ✅ 连接成功！")
        
        # 快速验证
        stdin, stdout, stderr = ssh.exec_command('whoami')
        user = stdout.read().decode().strip()
        print(f"  当前用户: {user}")
        
        stdin, stdout, stderr = ssh.exec_command('ls /var/www/oa-api/artisan')
        output = stdout.read().decode().strip()
        if output:
            print(f"  ✅ Laravel 项目存在")
        else:
            print(f"  ⚠️  Laravel 项目不存在")
        
        ssh.close()
        print(f"\n✅ 正确凭据: {username} / {password}")
        break
        
    except paramiko.AuthenticationException:
        print(f"  ❌ 认证失败")
    except paramiko.SSHException as e:
        print(f"  ❌ SSH 错误: {e}")
    except Exception as e:
        print(f"  ❌ 其他错误: {e}")

print("\n" + "=" * 50)
print("测试完成")
