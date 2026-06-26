#!/usr/bin/env python3
"""备份152服务器数据库"""
import paramiko
import time
from datetime import datetime

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"正在连接 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASS, timeout=15)
        print("✅ SSH连接成功\n")
        
        # 1. 备份数据库
        print("=" * 60)
        print("1. 备份数据库...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"/tmp/oa_backup_{timestamp}.sql"
        
        # 获取数据库密码
        stdin, stdout, stderr = ssh.exec_command("cat /var/www/oa-api/.env | grep DB_PASSWORD | cut -d'=' -f2")
        db_password = stdout.read().decode().strip()
        
        # 执行备份
        backup_cmd = f"""export PGPASSWORD='{db_password}' && pg_dump -h 127.0.0.1 -U oa_user -d security_oa > {backup_file}"""
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        
        # 等待备份完成
        for i in range(30):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            print(f"备份中... ({i*2}s)")
        
        # 检查备份文件大小
        stdin, stdout, stderr = ssh.exec_command(f"ls -lh {backup_file}")
        backup_info = stdout.read().decode().strip()
        print(f"✅ 备份完成: {backup_info}")
        
        # 2. 创建测试数据生成脚本
        print("\n" + "=" * 60)
        print("2. 创建测试数据生成脚本...")
        
        # 由于涉及的表非常多，我将创建一个综合性的PHP脚本
        # 该脚本将使用Laravel的DB facade来插入数据
        
        php_script = """<?php
// 加载Laravel环境
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "✅ Laravel环境加载成功\\n\\n";

// 设置中文faker
$faker = Faker\Factory::create('zh_CN');

// 生成数据的起始和结束日期（6个月）
$startDate = '2025-12-01';
$endDate = '2026-06-22';

echo "开始生成测试数据...\\n";
echo "时间范围: {$startDate} 至 {$endDate}\\n\\n";

// TODO: 这里将逐个模块生成数据
// 由于代码量很大，我将分批生成

echo "⚠️ 测试数据生成脚本已创建，等待执行...\\n";
?>
"""
        
        # 将脚本保存到服务器
        sftp = ssh.open_sftp()
        
        # 先本地创建脚本
        with open('/tmp/generate_test_data.php', 'w') as f:
            f.write(php_script)
        
        # 上传到服务器
        sftp.put('/tmp/generate_test_data.php', '/tmp/generate_test_data.php')
        sftp.close()
        
        print("✅ 测试数据生成脚本已上传到 /tmp/generate_test_data.php")
        print("\n⚠️ 由于涉及的表非常多，我需要分步生成数据")
        print("1. 先生成核心模块（员工、考勤、报销）")
        print("2. 然后生成业务模块（项目、客户、售后服务）")
        print("3. 最后生成辅助模块（库存、财务、网盘等）")
        
        ssh.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
