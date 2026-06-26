#!/usr/bin/env python3
"""在152服务器上创建并运行测试数据生成脚本"""
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
        
        # 1. 在服务器上创建PHP脚本
        print("=" * 60)
        print("1. 在服务器上创建测试数据生成脚本...")
        
        php_script = '''<?php
// 加载Laravel环境
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "✅ Laravel环境加载成功\\n\\n";

// 使用Laravel的DB facade
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

// 设置中文faker
$faker = Faker\Factory::create('zh_CN');

// 生成数据的起始和结束日期（6个月）
$startDate = '2025-12-01';
$endDate = '2026-06-22';

echo "开始生成测试数据...\\n";
echo "时间范围: {$startDate} 至 {$endDate}\\n\\n";

// 获取现有用户ID
$userIds = DB::table('users')->pluck('id')->toArray();
if (count($userIds) == 0) {
    echo "❌ 没有用户数据，无法生成测试数据\\n";
    exit(1);
}
echo "✅ 找到 " . count($userIds) . " 个用户\\n";

// 获取现有客户ID
$customerIds = DB::table('customers')->pluck('id')->toArray();
echo "✅ 找到 " . count($customerIds) . " 个客户\\n";

// 1. 生成考勤数据
echo "\\n1. 生成考勤数据...\\n";
$attendanceCount = 0;
for ($i = 0; $i < 500; $i++) {
    try {
        $date = $faker->dateTimeBetween($startDate, $endDate)->format('Y-m-d');
        $userId = $faker->randomElement($userIds);
        
        // 检查是否已存在
        $exists = DB::table('attendance_records')
            ->where('user_id', $userId)
            ->where('date', $date)
            ->exists();
        
        if (!$exists) {
            DB::table('attendance_records')->insert([
                'user_id' => $userId,
                'date' => $date,
                'check_in' => $date . ' ' . $faker->time('H:i:s', '09:00:00'),
                'check_out' => $date . ' ' . $faker->time('H:i:s', '18:00:00'),
                'status' => $faker->randomElement(['normal', 'late', 'early_leave', 'absent']),
                'created_at' => now(),
                'updated_at' => now(),
            ]);
            $attendanceCount++;
        }
    } catch (Exception $e) {
        // 忽略重复错误
    }
}
echo "   ✅ 生成了 {$attendanceCount} 条考勤记录\\n";

// 2. 生成报销数据
echo "\\n2. 生成报销数据...\\n";
$expenseCount = 0;
for ($i = 0; $i < 100; $i++) {
    try {
        $expenseId = DB::table('expense_claims')->insertGetId([
            'user_id' => $faker->randomElement($userIds),
            'amount' => $faker->randomFloat(2, 100, 5000),
            'type' => $faker->randomElement(['travel', 'meal', 'office', 'other']),
            'description' => $faker->sentence,
            'status' => $faker->randomElement(['pending', 'approved', 'rejected']),
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $expenseCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$expenseCount} 条报销记录\\n";

// 3. 生成应收数据
echo "\\n3. 生成应收数据...\\n";
$receivableCount = 0;
if (count($customerIds) > 0) {
    for ($i = 0; $i < 50; $i++) {
        try {
            DB::table('receivables')->insert([
                'customer_id' => $faker->randomElement($customerIds),
                'amount' => $faker->randomFloat(2, 1000, 50000),
                'due_date' => $faker->dateTimeBetween($startDate, $endDate)->format('Y-m-d'),
                'status' => $faker->randomElement(['pending', 'partial', 'paid']),
                'created_at' => $faker->dateTimeBetween($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $receivableCount++;
        } catch (Exception $e) {
            // 忽略错误
        }
    }
}
echo "   ✅ 生成了 {$receivableCount} 条应收记录\\n";

// 4. 生成应付数据
echo "\\n4. 生成应付数据...\\n";
$payableCount = 0;
for ($i = 0; $i < 50; $i++) {
    try {
        DB::table('payables')->insert([
            'supplier_id' => null, // 可能为null
            'amount' => $faker->randomFloat(2, 1000, 50000),
            'due_date' => $faker->dateTimeBetween($startDate, $endDate)->format('Y-m-d'),
            'status' => $faker->randomElement(['pending', 'partial', 'paid']),
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $payableCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$payableCount} 条应付记录\\n";

// 5. 生成消息数据
echo "\\n5. 生成消息数据...\\n";
$notificationCount = 0;
for ($i = 0; $i < 200; $i++) {
    try {
        DB::table('notifications')->insert([
            'user_id' => $faker->randomElement($userIds),
            'type' => $faker->randomElement(['info', 'warning', 'error', 'success']),
            'title' => $faker->sentence,
            'content' => $faker->paragraph,
            'is_read' => $faker->boolean,
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $notificationCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$notificationCount} 条消息记录\\n";

echo "\\n✅ 第一阶段测试数据生成完成！\\n";
echo "⚠️ 注意: 还需要为其他模块生成数据（售后服务、采购、销售等）\\n";
?>
'''
        
        # 将PHP脚本写入服务器
        # 使用echo命令创建文件，避免转义问题
        # 先创建临时文件
        with open('/tmp/generate_data.php', 'w') as f:
            f.write(php_script)
        
        # 上传文件
        sftp = ssh.open_sftp()
        sftp.put('/tmp/generate_data.php', '/tmp/generate_data.php')
        sftp.close()
        
        print("✅ PHP脚本已上传到 /tmp/generate_data.php")
        
        # 2. 运行PHP脚本
        print("\n" + "=" * 60)
        print("2. 运行测试数据生成脚本...")
        stdin, stdout, stderr = ssh.exec_command('php /tmp/generate_data.php')
        
        # 等待命令完成
        for i in range(30):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            print(f"生成中... ({i*2}s)")
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print("\n生成结果:")
        print(result)
        if error:
            print(f"\n错误: {error}")
        
        # 3. 清理临时文件
        ssh.exec_command('rm /tmp/generate_data.php')
        
        ssh.close()
        print("\n✅ 测试数据生成完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
