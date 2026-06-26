#!/usr/bin/env python3
"""
智能生成152服务器测试数据
先检查表结构，再生成正确的数据
"""

import paramiko
import time
import json

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def get_table_columns(ssh, table_name):
    """获取表的字段信息"""
    cmd = f"""cd /var/www/oa-api && php -r "
        \\$columns = \Illuminate\Support\Facades\DB::connection()->getSchemaBuilder()->getColumnListing('{table_name}');
        echo json_encode(\\$columns);
    " 2>&1"""
    
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    time.sleep(1)
    
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    
    if error:
        print(f"   ⓪ 获取{table_name}表结构失败: {error}")
        return []
    
    try:
        columns = json.loads(output)
        return columns
    except:
        print(f"   ⓪ 解析{table_name}表结构失败: {output}")
        return []

def execute_php(ssh, php_code):
    """执行PHP代码"""
    # 转义PHP代码
    php_code = php_code.replace('"', '\\"')
    php_code = php_code.replace('$', '\\$')
    
    cmd = f"""cd /var/www/oa-api && php -r "{php_code}" 2>&1"""
    
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    time.sleep(1)
    
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    
    if error and 'Notice:' not in error and 'Warning:' not in error:
        print(f"   ⚠️ PHP错误: {error}")
    
    return output

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        print("================ 开始智能生成测试数据 =================\n")
        
        # ==================== 1. 员工档案数据 ====================
        print("1. 检查并生成员工档案数据...")
        columns = get_table_columns(ssh, 'employee_profiles')
        if columns:
            print(f"   表字段: {', '.join(columns)}")
            
            # 生成员工档案
            php_code = """
                use Illuminate\Support\Facades\DB;
                
                $users = DB::table('users')->limit(30)->get();
                $count = 0;
                
                foreach ($users as $index => $user) {
                    $exists = DB::table('employee_profiles')->where('user_id', $user->id)->exists();
                    if ($exists) continue;
                    
                    DB::table('employee_profiles')->insert([
                        'user_id' => $user->id,
                        'employee_no' => 'EMP' . str_pad($index + 1, 4, '0', STR_PAD_LEFT),
                        'hire_date' => fake()->dateTimeBetween('2023-01-01', '2025-11-30')->format('Y-m-d'),
                        'contract_type' => fake()->randomElement(['permanent', 'temporary', 'probation']),
                        'base_salary' => fake()->numberBetween(5000, 25000),
                        'salary_allowance' => fake()->numberBetween(500, 3000),
                        'emergency_contact' => fake()->name(),
                        'emergency_phone' => fake()->phoneNumber(),
                        'bank_name' => fake()->randomElement(['工商银行', '建设银行', '农业银行']),
                        'bank_account' => fake()->bankAccountNumber(),
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                    $count++;
                }
                
                echo "✅ 生成了 {$count} 条员工档案记录";
            """
            result = execute_php(ssh, php_code)
            print(f"   {result}\n")
        else:
            print("   ⚠️ 无法获取employee_profiles表结构\n")
        
        # ==================== 2. 网盘文件夹数据 ====================
        print("2. 检查并生成网盘文件夹数据...")
        columns = get_table_columns(ssh, 'disk_folders')
        if columns:
            print(f"   表字段: {', '.join(columns)}")
            
            # 生成网盘文件夹
            php_code = """
                use Illuminate\Support\Facades\DB;
                
                $adminId = 1;
                $folders = [
                    ['name' => '公司文档', 'is_system' => true, 'path' => '/1/'],
                    ['name' => '项目资料', 'is_system' => true, 'path' => '/2/'],
                    ['name' => '财务报表', 'is_system' => true, 'path' => '/3/'],
                    ['name' => '人事档案', 'is_system' => true, 'path' => '/4/'],
                    ['name' => '技术文档', 'is_system' => true, 'path' => '/5/'],
                    ['name' => '客户资料', 'is_system' => true, 'path' => '/6/'],
                ];
                
                $count = 0;
                foreach ($folders as $folder) {
                    $exists = DB::table('disk_folders')->where('name', $folder['name'])->exists();
                    if ($exists) continue;
                    
                    DB::table('disk_folders')->insert([
                        'name' => $folder['name'],
                        'path' => $folder['path'],
                        'created_by' => $adminId,
                        'is_system' => $folder['is_system'],
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                    $count++;
                }
                
                echo "✅ 生成了 {$count} 个网盘文件夹";
            """
            result = execute_php(ssh, php_code)
            print(f"   {result}\n")
        else:
            print("   ⚠️ 无法获取disk_folders表结构\n")
        
        # ==================== 3. 知识库文章数据 ====================
        print("3. 检查并生成知识库文章数据...")
        columns = get_table_columns(ssh, 'knowledge_articles')
        if columns:
            print(f"   表字段: {', '.join(columns)}")
            
            # 先检查knowledge_categories表是否有数据
            php_code = """
                use Illuminate\Support\Facades\DB;
                
                $categoryCount = DB::table('knowledge_categories')->count();
                echo $categoryCount;
            """
            result = execute_php(ssh, php_code)
            print(f"   知识库分类数量: {result}")
            
            if int(result) > 0:
                # 生成知识库文章
                php_code = """
                    use Illuminate\Support\Facades\DB;
                    
                    $adminId = 1;
                    $categoryId = DB::table('knowledge_categories')->first()->id;
                    
                    $articles = [
                        ['title' => '系统操作手册'],
                        ['title' => '故障排除指南'],
                        ['title' => '新员工培训资料'],
                        ['title' => '项目管理规范'],
                        ['title' => '代码审查流程'],
                    ];
                    
                    $count = 0;
                    foreach ($articles as $article) {
                        $exists = DB::table('knowledge_articles')->where('title', $article['title'])->exists();
                        if ($exists) continue;
                        
                        DB::table('knowledge_articles')->insert([
                            'title' => $article['title'],
                            'content' => '这是' . $article['title'] . '的详细内容。',
                            'category_id' => $categoryId,
                            'author_id' => $adminId,
                            'status' => 'published',
                            'view_count' => fake()->numberBetween(10, 500),
                            'created_at' => now(),
                            'updated_at' => now(),
                        ]);
                        $count++;
                    }
                    
                    echo "✅ 生成了 {$count} 篇知识库文章";
                """
                result = execute_php(ssh, php_code)
                print(f"   {result}\n")
            else:
                print("   ⚠️ knowledge_categories表没有数据，跳过\n")
        else:
            print("   ⚠️ 无法获取knowledge_articles表结构\n")
        
        # ==================== 4. 考勤数据 ====================
        print("4. 生成考勤数据...")
        columns = get_table_columns(ssh, 'attendance_records')
        if columns:
            print(f"   表字段: {', '.join(columns)}")
            
            # 生成考勤数据
            php_code = """
                use Illuminate\Support\Facades\DB;
                
                $userIds = DB::table('users')->limit(10)->pluck('id')->toArray();
                $count = 0;
                
                foreach ($userIds as $userId) {
                    // 为每个用户生成30条考勤记录
                    for ($i = 0; $i < 30; $i++) {
                        $date = fake()->dateTimeBetween('2025-12-01', '2026-06-22')->format('Y-m-d');
                        
                        $exists = DB::table('attendance_records')
                            ->where('user_id', $userId)
                            ->where('date', $date)
                            ->exists();
                        if ($exists) continue;
                        
                        DB::table('attendance_records')->insert([
                            'user_id' => $userId,
                            'date' => $date,
                            'clock_in' => fake()->time('H:i:s'),
                            'clock_out' => fake()->time('H:i:s'),
                            'status' => fake()->randomElement(['normal', 'late', 'early_leave', 'absent']),
                            'work_hours' => fake()->randomFloat(1, 8, 2),
                            'created_at' => now(),
                            'updated_at' => now(),
                        ]);
                        $count++;
                    }
                }
                
                echo "✅ 生成了 {$count} 条考勤记录";
            """
            result = execute_php(ssh, php_code)
            print(f"   {result}\n")
        else:
            print("   ⚠️ 无法获取attendance_records表结构\n")
        
        # ==================== 5. 报销数据 ====================
        print("5. 检查并生成报销数据...")
        columns = get_table_columns(ssh, 'expense_claims')
        if columns:
            print(f"   表字段: {', '.join(columns)}")
            
            # 生成报销数据（使用正确的字段名）
            php_code = """
                use Illuminate\Support\Facades\DB;
                
                $userIds = DB::table('users')->limit(20)->pluck('id')->toArray();
                $count = 0;
                
                foreach ($userIds as $userId) {
                    for ($i = 0; $i < 10; $i++) {
                        $data = [
                            'user_id' => $userId,
                            'amount' => fake()->randomFloat(2, 50, 5000),
                            'description' => fake()->sentence(),
                            'status' => fake()->randomElement(['pending', 'approved', 'rejected']),
                            'created_at' => now(),
                            'updated_at' => now(),
                        ];
                        
                        // 可选字段
                        if (Schema::hasColumn('expense_claims', 'project_id')) {
                            $data['project_id'] = DB::table('projects')->inRandomOrder()->first()->id ?? null;
                        }
                        if (Schema::hasColumn('expense_claims', 'expense_date')) {
                            $data['expense_date'] = fake()->dateTimeBetween('2025-12-01', '2026-06-22')->format('Y-m-d');
                        }
                        
                        DB::table('expense_claims')->insert($data);
                        $count++;
                    }
                }
                
                echo "✅ 生成了 {$count} 条报销记录";
            """
            result = execute_php(ssh, php_code)
            print(f"   {result}\n")
        else:
            print("   ⚠️ 无法获取expense_claims表结构\n")
        
        # ==================== 6. 最终统计 ====================
        print("================ 最终数据统计 ==================\n")
        
        tables = [
            'users', 'employee_profiles', 'attendance_records', 'expense_claims',
            'vehicles', 'inventory_items', 'customers', 'projects',
            'service_orders', 'leads', 'opportunities', 'receivables',
            'payables', 'disk_folders', 'knowledge_articles', 'notifications'
        ]
        
        for table in tables:
            php_code = f"""
                use Illuminate\Support\Facades\DB;
                echo DB::table('{table}')->count();
            """
            result = execute_php(ssh, php_code)
            if result.isdigit():
                print(f"  {table:30s}: {result:>6s} 条")
        
        print("\n✅ 测试数据生成完成！")
        print("⏰ 数据时间跨度: 2025-12-01 至 2026-06-22 (至少6个月)")
        
        # 关闭SSH连接
        ssh.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 所有操作完成！152服务器现在有了更多的测试数据")
    else:
        print("\n❌ 操作失败，请检查错误信息")
