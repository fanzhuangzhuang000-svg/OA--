#!/usr/bin/env python3
"""上传并运行修正后的测试数据生成脚本到152服务器（v2）"""
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
        print("1. 读取本地修正后的PHP脚本...")
        
        with open('D:/work/website/OA/.workbuddy/generate_correct_data_v2.php', 'r', encoding='utf-8') as f:
            php_script = f.read()
        
        print(f"✅ PHP脚本读取成功，大小: {len(php_script)} 字节")
        
        # 2. 上传PHP脚本到152服务器
        print("\n" + "=" * 60)
        print("2. 上传PHP脚本到152服务器...")
        
        # 使用base64编码上传
        encoded_script = base64.b64encode(php_script.encode()).decode()
        
        # 上传base64编码的脚本
        ssh.exec_command(f'echo "{encoded_script}" | base64 -d > /tmp/generate_correct_data_v2.php')
        time.sleep(3)
        
        # 检查文件是否上传成功
        stdin, stdout, stderr = ssh.exec_command('ls -lh /tmp/generate_correct_data_v2.php')
        file_info = stdout.read().decode().strip()
        print(f"✅ PHP脚本已上传: {file_info}")
        
        # 3. 运行PHP脚本
        print("\n" + "=" * 60)
        print("3. 运行测试数据生成脚本...")
        print("⏳ 这可能需要几分钟...")
        
        stdin, stdout, stderr = ssh.exec_command('php /tmp/generate_correct_data_v2.php')
        
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
        
        # 创建一个全面的数据检查脚本
        check_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "数据量检查:\n";

// 核心模块
echo "【核心模块】\n";
echo "  用户: " . DB::table('users')->count() . " 个\n";
echo "  客户: " . DB::table('customers')->count() . " 个\n";
echo "  项目: " . DB::table('projects')->count() . " 个\n";
echo "  考勤: " . DB::table('attendance_records')->count() . " 条\n";
echo "  报销: " . DB::table('expense_claims')->count() . " 条\n";
echo "  应收: " . DB::table('receivables')->count() . " 条\n";
echo "  应付: " . DB::table('payables')->count() . " 条\n";
echo "  消息: " . DB::table('notifications')->count() . " 条\n";

// 业务模块
echo "\n【业务模块】\n";
echo "  服务工单: " . DB::table('service_orders')->count() . " 条\n";
echo "  采购订单: " . DB::table('purchase_orders')->count() . " 条\n";
echo "  销售机会: " . DB::table('opportunities')->count() . " 条\n";
echo "  供应商: " . DB::table('suppliers')->count() . " 个\n";

// 其他模块
echo "\n【其他模块】\n";
echo "  车辆: " . DB::table('vehicles')->count() . " 辆\n";
echo "  库存物品: " . DB::table('inventory_items')->count() . " 个\n";
echo "  财务账户: " . DB::table('finance_accounts')->count() . " 个\n";
echo "  网盘文件夹: " . DB::table('disk_folders')->count() . " 个\n";
echo "  知识库文章: " . DB::table('knowledge_articles')->count() . " 篇\n";

// 检查数据时间跨度
echo "\n【数据时间跨度】\n";
try {
    $projectStats = DB::table('projects')
        ->selectRaw('MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total')
        ->first();
    echo "  项目: {$projectStats->total} 条\n";
    echo "    最早: {$projectStats->earliest}\n";
    echo "    最新: {$projectStats->latest}\n";
} catch (Exception $e) {
    echo "  项目: 无数据\n";
}

try {
    $attendanceStats = DB::table('attendance_records')
        ->selectRaw('MIN(date) as earliest, MAX(date) as latest, COUNT(*) as total')
        ->first();
    echo "  考勤: {$attendanceStats->total} 条\n";
    echo "    最早: {$attendanceStats->earliest}\n";
    echo "    最新: {$attendanceStats->latest}\n";
} catch (Exception $e) {
    echo "  考勤: 无数据\n";
}
?>
"""
        
        # 上传检查脚本
        encoded_check = base64.b64encode(check_script.encode()).decode()
        ssh.exec_command(f'echo "{encoded_check}" | base64 -d > /tmp/check_all_data_v2.php')
        time.sleep(2)
        
        # 运行检查脚本
        stdin, stdout, stderr = ssh.exec_command('php /tmp/check_all_data_v2.php')
        time.sleep(5)
        
        check_result = stdout.read().decode()
        print(check_result)
        
        # 5. 清理临时文件
        ssh.exec_command('rm /tmp/generate_correct_data_v2.php /tmp/check_all_data_v2.php')
        
        ssh.close()
        print("\n✅ 测试数据生成完成")
        print("\n⚠️ 注意: 这只是第一部分数据，还需要为其他模块生成数据")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()