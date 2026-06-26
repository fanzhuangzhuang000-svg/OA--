#!/usr/bin/env python3
"""
测试152服务器工作台API端点
"""
import paramiko
import requests
import json
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 先测试登录获取token
        print("\n🔐 测试登录获取token...")
        login_cmd = """sudo -u www-data php -r '
require_once "/var/www/oa-api/vendor/autoload.php";
$app = require_once "/var/www/oa-api/bootstrap/app.php";
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

use Illuminate\\Support\\Facades\\Auth;
use App\\Models\\User;

// 查找admin用户
$user = User::where("username", "admin")->first();
if ($user) {
    echo "USER_ID:" . $user->id . "\\n";
    echo "USERNAME:" . $user->username . "\\n";
} else {
    echo "ERROR: admin user not found\\n";
}
'
"""
        
        stdin, stdout, stderr = ssh.exec_command(login_cmd, timeout=30)
        result = stdout.read().decode('utf-8', errors='ignore')
        print(f"   查询结果: {result}")
        
        # 测试API端点
        api_endpoints = [
            '/api/dashboard/stats',
            '/api/dashboard/todo',
            '/api/dashboard/project-progress',
            '/api/dashboard/service-stats',
            '/api/dashboard/revenue-trend'
        ]
        
        print("\n🔍 测试工作台API端点...")
        print("=" * 60)
        
        for endpoint in api_endpoints:
            cmd = f"""sudo -u www-data php -r '
require_once "/var/www/oa-api/vendor/autoload.php";
$app = require_once "/var/www/oa-api/bootstrap/app.php";
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

// 模拟API请求
$_SERVER["REQUEST_URI"] = "{endpoint}";
$_SERVER["REQUEST_METHOD"] = "GET";

try {{
    $request = Illuminate\\Http\\Request::create("{endpoint}", "GET");
    $response = app()->handle($request);
    $status = $response->getStatusCode();
    $content = $response->getContent();
    $data = json_decode($content, true);
    
    echo "ENDPOINT:{endpoint}\\n";
    echo "STATUS:{$status}\\n";
    if ($data) {{
        echo "CODE:" . ($data["code"] ?? "N/A") . "\\n";
        if (isset($data["data"])) {{
            if (is_array($data["data"])) {{
                echo "DATA_COUNT:" . count($data["data"]) . "\\n";
            }} else {{
                echo "DATA:" . json_encode($data["data"], JSON_UNESCAPED_UNICODE) . "\\n";
            }}
        }}
    }} else {{
        echo "RAW_RESPONSE:" . substr($content, 0, 200) . "\\n";
    }}
}} catch (Exception $e) {{
    echo "ERROR:" . $e->getMessage() . "\\n";
}}
'
"""
            
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            print(f"\n📍 端点: {endpoint}")
            if output:
                for line in output.strip().split('\n'):
                    if line.startswith('ENDPOINT:') or line.startswith('STATUS:') or line.startswith('CODE:') or line.startswith('DATA_COUNT:') or line.startswith('ERROR:'):
                        print(f"   {line}")
            if error:
                print(f"   ⚠️ 错误: {error[:100]}")
        
        print("\n" + "=" * 60)
        print("✅ API端点测试完成")
        
        # 检查routes/api.php中是否有这些路由
        print("\n📋 检查routes/api.php中的dashboard路由...")
        cmd = "grep -n 'dashboard' /var/www/oa-api/routes/api.php 2>/dev/null || echo 'NO_DASHBOARD_ROUTES'"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
        result = stdout.read().decode('utf-8', errors='ignore')
        print(f"   {result}")
        
        ssh.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败")
