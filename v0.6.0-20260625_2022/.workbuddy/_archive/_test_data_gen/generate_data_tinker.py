#!/usr/bin/env python3
"""
使用Laravel tinker在152服务器上生成测试数据
这种方法会自动使用正确的表结构
"""

import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def execute_tinker(ssh, php_code):
    """执行Laravel tinker命令"""
    # 转义PHP代码中的特殊字符
    php_code = php_code.replace('"', '\\"')
    php_code = php_code.replace('$', '\\$')
    
    cmd = f"""cd /var/www/oa-api && php artisan tinker --execute="
        {php_code}
    " 2>&1"""
    
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=300)
    
    output = ""
    while True:
        if stdout.channel.exit_status_ready():
            break
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
            output += chunk
            print(chunk, end='')
        time.sleep(0.1)
    
    return output

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 测试Laravel是否可以运行
        print("🧪 测试Laravel tinker...")
        result = execute_tinker(ssh, "echo 'Laravel is working';")
        if 'Laravel is working' in result:
            print("✅ Laravel tinker 可用\n")
        else:
            print("❌ Laravel tinker 不可用\n")
            return False
        
        # ==================== 1. 生成员工档案数据 ====================
        print("1. 生成员工档案数据...")
        php_code = """
            use App\\Models\\User;
            use App\\Models\\EmployeeProfile;
            
            $users = User::limit(30)->get();
            $count = 0;
            foreach ($users as $index => $user) {
                if (EmployeeProfile::where('user_id', $user->id)->exists()) {
                    continue;
                }
                
                EmployeeProfile::create([
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
                ]);
                $count++;
            }
            echo "✅ 生成了 {$count} 条员工档案记录\\n";
        """
        execute_tinker(ssh, php_code)
        
        # ==================== 2. 生成网盘文件夹数据 ====================
        print("\n2. 生成网盘文件夹数据...")
        php_code = """
            use App\\Models\\DiskFolder;
            use App\\Models\\User;
            
            $admin = User::where('role', 'admin')->first();
            $adminId = $admin ? $admin->id : 1;
            
            $folders = [
                ['name' => '公司文档', 'is_system' => true],
                ['name' => '项目资料', 'is_system' => true],
                ['name' => '财务报表', 'is_system' => true],
                ['name' => '人事档案', 'is_system' => true],
                ['name' => '技术文档', 'is_system' => true],
                ['name' => '客户资料', 'is_system' => true],
                ['name' => '市场推广', 'is_system' => false],
                ['name' => '培训材料', 'is_system' => false],
                ['name' => '合同文件', 'is_system' => false],
                ['name' => '研发资料', 'is_system' => false],
            ];
            
            $count = 0;
            foreach ($folders as $folder) {
                if (DiskFolder::where('name', $folder['name'])->exists()) {
                    continue;
                }
                
                DiskFolder::create([
                    'name' => $folder['name'],
                    'created_by' => $adminId,
                    'is_system' => $folder['is_system'],
                ]);
                $count++;
            }
            echo "✅ 生成了 {$count} 个网盘文件夹\\n";
        """
        execute_tinker(ssh, php_code)
        
        # ==================== 3. 生成知识库文章数据 ====================
        print("\n3. 生成知识库文章数据...")
        php_code = """
            use App\\Models\\KnowledgeArticle;
            use App\\Models\\User;
            
            $admin = User::where('role', 'admin')->first();
            $adminId = $admin ? $admin->id : 1;
            
            $articles = [
                ['title' => '系统操作手册', 'category_id' => 1],
                ['title' => '故障排除指南', 'category_id' => 1],
                ['title' => '新员工培训资料', 'category_id' => 2],
                ['title' => '项目管理规范', 'category_id' => 3],
                ['title' => '代码审查流程', 'category_id' => 1],
                ['title' => '测试标准文档', 'category_id' => 1],
                ['title' => '安全管理制度', 'category_id' => 3],
                ['title' => '数据备份策略', 'category_id' => 1],
                ['title' => '客户服务规范', 'category_id' => 2],
                ['title' => '质量控制手册', 'category_id' => 3],
            ];
            
            $count = 0;
            foreach ($articles as $article) {
                if (KnowledgeArticle::where('title', $article['title'])->exists()) {
                    continue;
                }
                
                KnowledgeArticle::create([
                    'title' => $article['title'],
                    'content' => '这是' . $article['title'] . '的详细内容。',
                    'category_id' => $article['category_id'],
                    'author_id' => $adminId,
                    'status' => 'published',
                    'view_count' => fake()->numberBetween(10, 500),
                ]);
                $count++;
            }
            echo "✅ 生成了 {$count} 篇知识库文章\\n";
        """
        execute_tinker(ssh, php_code)
        
        # ==================== 4. 生成考勤数据 ====================
        print("\n4. 生成考勤数据（简化版）...")
        php_code = """
            use App\\Models\\AttendanceRecord;
            use App\\Models\\EmployeeProfile;
            
            $employees = EmployeeProfile::limit(10)->get();
            $count = 0;
            
            foreach ($employees as $employee) {
                // 为每个员工生成30条考勤记录
                for ($i = 0; $i < 30; $i++) {
                    $date = fake()->dateTimeBetween('2025-12-01', '2026-06-22')->format('Y-m-d');
                    
                    if (AttendanceRecord::where('user_id', $employee->user_id)->where('date', $date)->exists()) {
                        continue;
                    }
                    
                    AttendanceRecord::create([
                        'user_id' => $employee->user_id,
                        'date' => $date,
                        'clock_in' => fake()->time('H:i:s'),
                        'clock_out' => fake()->time('H:i:s'),
                        'status' => fake()->randomElement(['normal', 'late', 'early_leave', 'absent']),
                        'work_hours' => fake()->randomFloat(1, 8, 2),
                    ]);
                    $count++;
                }
            }
            echo "✅ 生成了 {$count} 条考勤记录\\n";
        """
        execute_tinker(ssh, php_code)
        
        # ==================== 5. 生成报销数据 ====================
        print("\n5. 生成报销数据...")
        php_code = """
            use App\\Models\\ExpenseClaim;
            use App\\Models\\User;
            
            $users = User::limit(20)->get();
            $count = 0;
            
            foreach ($users as $user) {
                for ($i = 0; $i < 10; $i++) {
                    ExpenseClaim::create([
                        'user_id' => $user->id,
                        'type' => fake()->randomElement(['travel', 'meal', 'transport', 'office']),
                        'amount' => fake()->randomFloat(2, 50, 5000),
                        'description' => fake()->sentence(),
                        'status' => fake()->randomElement(['pending', 'approved', 'rejected']),
                        'expense_date' => fake()->dateTimeBetween('2025-12-01', '2026-06-22'),
                    ]);
                    $count++;
                }
            }
            echo "✅ 生成了 {$count} 条报销记录\\n";
        """
        execute_tinker(ssh, php_code)
        
        # ==================== 6. 最终统计 ====================
        print("\n================ 最终数据统计 ==================\n")
        
        tables = [
            'users', 'employee_profiles', 'attendance_records', 'expense_claims',
            'vehicles', 'inventory_items', 'customers', 'projects',
            'service_orders', 'leads', 'opportunities', 'receivables',
            'payables', 'disk_folders', 'disk_files', 'knowledge_articles',
            'notifications'
        ]
        
        for table in tables:
            php_code = f"""
                echo "{table}: " . DB::table('{table}')->count() . " 条\\n";
            """
            execute_tinker(ssh, php_code)
        
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
