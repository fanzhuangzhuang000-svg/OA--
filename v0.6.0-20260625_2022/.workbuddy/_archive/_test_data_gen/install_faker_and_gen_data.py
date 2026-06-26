#!/usr/bin/env python3
"""在152服务器上安装faker并生成测试数据"""
import paramiko
import time

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
        
        # 1. 安装faker库
        print("=" * 60)
        print("1. 安装faker库...")
        
        # 使用composer安装faker
        stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data composer require fakerphp/faker --no-interaction')
        
        # 等待安装完成（最多5分钟）
        for i in range(150):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            if i % 15 == 0:  # 每30秒显示一次
                print(f"   安装中... ({i*2}s)")
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        if 'error' in result.lower() or 'error' in error.lower():
            print(f"❌ 安装失败: {error}")
            print("尝试继续...")
        else:
            print("✅ faker库安装完成")
        
        # 2. 重新运行测试数据生成脚本
        print("\n" + "=" * 60)
        print("2. 重新运行测试数据生成脚本...")
        
        # 先检查faker是否可用
        check_faker = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
echo "✅ autoload加载成功\\n";

// 尝试加载faker
if (class_exists('Faker\\Factory')) {
    echo "✅ Faker库可用\\n";
    $faker = Faker\Factory::create('zh_CN');
    echo "✅ Faker创建成功: " . $faker->name . "\\n";
} else {
    echo "❌ Faker库不可用\\n";
}
?>
"""
        
        # 上传检查脚本
        import base64
        encoded_check = base64.b64encode(check_faker.encode()).decode()
        ssh.exec_command(f'echo "{encoded_check}" | base64 -d > /tmp/check_faker.php')
        time.sleep(2)
        
        # 运行检查脚本
        stdin, stdout, stderr = ssh.exec_command('php /tmp/check_faker.php')
        time.sleep(5)
        
        check_result = stdout.read().decode()
        check_error = stderr.read().decode()
        
        print("Faker检查结果:")
        print(check_result)
        if check_error:
            print(f"错误: {check_error}")
        
        # 如果faker可用，运行测试数据生成脚本
        if 'Faker库可用' in check_result:
            print("\n" + "=" * 60)
            print("3. 运行测试数据生成脚本...")
            
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
        else:
            print("\n❌ Faker库不可用，无法生成测试数据")
            print("尝试使用不需要faker的方法生成数据...")
            
            # 创建一个不需要faker的脚本
            simple_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "✅ Laravel环境加载成功\\n\\n";

// 使用Laravel的Str辅助函数生成随机数据
use Illuminate\Support\Str;

// 获取现有用户ID
$userIds = DB::table('users')->pluck('id')->toArray();
echo "✅ 找到 " . count($userIds) . " 个用户\\n";

// 生成简单的测试数据
echo "\\n生成考勤数据...\\n";
$count = 0;
for ($i = 0; $i < 100; $i++) {
    try {
        $date = date('Y-m-d', strtotime('-' . rand(0, 180) . ' days'));
        $userId = $userIds[array_rand($userIds)];
        
        $exists = DB::table('attendance_records')
            ->where('user_id', $userId)
            ->where('date', $date)
            ->exists();
        
        if (!$exists) {
            DB::table('attendance_records')->insert([
                'user_id' => $userId,
                'date' => $date,
                'check_in' => $date . ' 09:00:00',
                'check_out' => $date . ' 18:00:00',
                'status' => ['normal', 'late', 'early_leave'][rand(0, 2)],
                'created_at' => now(),
                'updated_at' => now(),
            ]);
            $count++;
        }
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$count} 条考勤记录\\n";

echo "\\n✅ 简单测试数据生成完成！\\n";
?>
"""
            
            # 上传简单脚本
            encoded_simple = base64.b64encode(simple_script.encode()).decode()
            ssh.exec_command(f'echo "{encoded_simple}" | base64 -d > /tmp/generate_simple_data.php')
            time.sleep(2)
            
            # 运行简单脚本
            stdin, stdout, stderr = ssh.exec_command('php /tmp/generate_simple_data.php')
            time.sleep(10)
            
            simple_result = stdout.read().decode()
            print(simple_result)
        
        # 3. 清理临时文件
        ssh.exec_command('rm /tmp/check_faker.php /tmp/generate_test_data.php /tmp/generate_simple_data.php')
        
        ssh.close()
        print("\n✅ 操作完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
