#!/usr/bin/env python3
"""上传并运行修正后的测试数据生成脚本到152服务器"""
import paramiko
import time
import base64

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
        
        # 1. 读取本地修正后的PHP脚本
        print("=" * 60)
        print("1. 读取本地PHP脚本...")
        
        with open('D:/work/website/OA/.workbuddy/generate_test_data_correct.php', 'r') as f:
            php_script = f.read()
        
        print(f"✅ PHP脚本读取成功，大小: {len(php_script)} 字节")
        
        # 2. 上传PHP脚本到152服务器
        print("\n" + "=" * 60)
        print("2. 上传PHP脚本到152服务器...")
        
        # 使用base64编码上传
        encoded_script = base64.b64encode(php_script.encode()).decode()
        
        # 上传base64编码的脚本
        ssh.exec_command(f'echo "{encoded_script}" | base64 -d > /tmp/generate_test_data.php')
        time.sleep(3)
        
        # 检查文件是否上传成功
        stdin, stdout, stderr = ssh.exec_command('ls -lh /tmp/generate_test_data.php')
        file_info = stdout.read().decode().strip()
        print(f"✅ PHP脚本已上传: {file_info}")
        
        # 3. 运行PHP脚本
        print("\n" + "=" * 60)
        print("3. 运行测试数据生成脚本...")
        print("⏳ 这可能需要几分钟...")
        
        stdin, stdout, stderr = ssh.exec_command('php /tmp/generate_test_data.php')
        
        # 等待命令完成（最多5分钟）
        for i in range(150):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            if i % 15 == 0:  # 每30秒显示一次
                print(f"   生成中... ({i*2}s)")
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print("\n生成结果:")
        print(result)
        if error:
            print(f"\n⚠️ 错误输出: {error}")
        
        # 4. 检查生成的数据
        print("\n" + "=" * 60)
        print("4. 检查生成的数据...")
        
        # 创建一个简单的检查脚本
        check_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "数据量检查:\n";
echo "  考勤: " . DB::table('attendance_records')->count() . " 条\n";
echo "  报销: " . DB::table('expense_claims')->count() . " 条\n";
echo "  应收: " . DB::table('receivables')->count() . " 条\n";
echo "  应付: " . DB::table('payables')->count() . " 条\n";
echo "  消息: " . DB::table('notifications')->count() . " 条\n";
?>
"""
        
        # 上传检查脚本
        encoded_check = base64.b64encode(check_script.encode()).decode()
        ssh.exec_command(f'echo "{encoded_check}" | base64 -d > /tmp/check_data.php')
        time.sleep(2)
        
        # 运行检查脚本
        stdin, stdout, stderr = ssh.exec_command('php /tmp/check_data.php')
        time.sleep(5)
        
        check_result = stdout.read().decode()
        print(check_result)
        
        # 5. 清理临时文件
        ssh.exec_command('rm /tmp/generate_test_data.php /tmp/check_data.php')
        
        ssh.close()
        print("\n✅ 测试数据生成完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
