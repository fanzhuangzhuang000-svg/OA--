<?php
// 资金和项目流转测试脚本 - Session B 阶段 3
// 测试目标：验证应收/收款/关闭流程，项目创建/阶段/施工/跟踪流程

require __DIR__ . '/vendor/autoload.php';

use Illuminate\Support\Facades\Http;

class FinanceProjectFlowTest
{
    private string $baseUrl = 'http://172.20.0.139/api';
    private string $token = '';
    private array $testData = [];
    
    public function run(): void
    {
        echo "🚀 Session B 阶段 3：资金和项目流转测试\n";
        echo "==========================================\n\n";
        
        // 1. 登录获取 token
        if (! $this->login()) {
            echo "❌ 登录失败，测试终止\n";
            return;
        }
        
        // 2. 测试资金流转
        $this->testFinanceFlow();
        
        // 3. 测试项目流转
        $this->testProjectFlow();
        
        echo "\n✅ 所有测试完成\n";
    }
    
    private function login(): bool
    {
        echo "🔑 登录获取 token...\n";
        
        $response = Http::post($this->baseUrl . '/auth/login', [
            'username' => 'admin',
            'password' => 'admin123',
        ]);
        
        if ($response->successful() && $response->json('code') === 0) {
            $this->token = $response->json('data.token');
            echo "  ✅ 登录成功\n";
            return true;
        }
        
        echo "  ❌ 登录失败: " . json_encode($response->json()) . "\n";
        return false;
    }
    
    private function testFinanceFlow(): void
    {
        echo "\n💰 测试资金流转...\n";
        echo "------------------------\n";
        
        $http = Http::withToken($this->token);
        
        // 2.1 创建应收款
        echo "  1️⃣ 创建应收款...\n";
        $receivable = [
            'customer_id' => 1, // 假设客户 ID=1 存在
            'project_id' => null,
            'amount' => 100000,
            'received_amount' => 0,
            'status' => 'pending',
            'received_date' => null,
            'note' => '测试应收款',
        ];
        
        $response = $http->post($this->baseUrl . '/finance/receivables', $receivable);
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            $receivableId = $data['data']['id'] ?? null;
            $this->testData['receivable_id'] = $receivableId;
            echo "    ✅ 应收款创建成功 (ID: {$receivableId})\n";
        } else {
            echo "    ❌ 创建失败: " . json_encode($data) . "\n";
            return;
        }
        
        // 2.2 创建收款记录
        echo "  2️⃣ 创建收款记录...\n";
        $payment = [
            'amount' => 50000,
            'payment_date' => now()->toDateString(),
            'payment_method' => 'bank_transfer',
            'note' => '测试收款',
        ];
        
        $response = $http->post(
            $this->baseUrl . "/finance/receivables/{$receivableId}/payments",
            $payment
        );
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 收款记录创建成功\n";
        } else {
            echo "    ❌ 创建失败: " . json_encode($data) . "\n";
        }
        
        // 2.3 再收一笔，凑满 100000
        echo "  3️⃣ 再创建一笔收款记录（凑满）...\n";
        $payment['amount'] = 50000;
        $response = $http->post(
            $this->baseUrl . "/finance/receivables/{$receivableId}/payments",
            $payment
        );
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 第二笔收款记录创建成功\n";
        } else {
            echo "    ❌ 创建失败: " . json_encode($data) . "\n";
        }
        
        // 2.4 关闭应收款
        echo "  4️⃣ 关闭应收款...\n";
        $response = $http->post(
            $this->baseUrl . "/finance/receivables/{$receivableId}/close"
        );
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 应收款关闭成功\n";
        } else {
            echo "    ❌ 关闭失败: " . json_encode($data) . "\n";
        }
        
        // 2.5 验证应收款状态
        echo "  5️⃣ 验证应收款状态...\n";
        $response = $http->get($this->baseUrl . "/finance/receivables/{$receivableId}");
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            $status = $data['data']['status'] ?? '';
            $receivedAmount = $data['data']['received_amount'] ?? 0;
            echo "    ✅ 状态: {$status}, 已收金额: {$receivedAmount}\n";
        } else {
            echo "    ❌ 查询失败: " . json_encode($data) . "\n";
        }
        
        echo "  ✅ 资金流转测试完成\n";
    }
    
    private function testProjectFlow(): void
    {
        echo "\n🏗️ 测试项目流转...\n";
        echo "------------------------\n";
        
        $http = Http::withToken($this->token);
        
        // 3.1 创建项目
        echo "  1️⃣ 创建项目...\n";
        $project = [
            'name' => '测试项目 ' . now()->format('Y-m-d H:i:s'),
            'customer_id' => 1,
            'type' => 'implementation',
            'status' => 'pending',
            'stage' => 'initiation',
            'progress' => 0,
            'member_ids' => [1], // 假设用户 ID=1 存在
        ];
        
        $response = $http->post($this->baseUrl . '/projects', $project);
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            $projectId = $data['data']['id'] ?? null;
            $this->testData['project_id'] = $projectId;
            echo "    ✅ 项目创建成功 (ID: {$projectId})\n";
        } else {
            echo "    ❌ 创建失败: " . json_encode($data) . "\n";
            return;
        }
        
        // 3.2 更新项目阶段（发起 → 询价）
        echo "  2️⃣ 更新项目阶段 (initiation → inquiry)...\n";
        $response = $http->put(
            $this->baseUrl . "/projects/{$projectId}/stage",
            ['stage' => 'inquiry']
        );
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 阶段更新成功\n";
        } else {
            echo "    ❌ 更新失败: " . json_encode($data) . "\n";
        }
        
        // 3.3 继续更新阶段（询价 → 合同）
        echo "  3️⃣ 继续更新阶段 (inquiry → contract)...\n";
        $response = $http->put(
            $this->baseUrl . "/projects/{$projectId}/stage",
            ['stage' => 'contract']
        );
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 阶段更新成功\n";
        } else {
            echo "    ❌ 更新失败: " . json_encode($data) . "\n";
        }
        
        // 3.4 创建施工日志
        echo "  4️⃣ 创建施工日志...\n";
        $log = [
            'content' => '测试施工日志',
            'log_date' => now()->toDateString(),
            'progress' => 30,
        ];
        
        $response = $http->post(
            $this->baseUrl . "/projects/{$projectId}/construction-logs",
            $log
        );
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 施工日志创建成功\n";
        } else {
            echo "    ❌ 创建失败: " . json_encode($data) . "\n";
        }
        
        // 3.5 查看项目跟踪
        echo "  5️⃣ 查看项目跟踪...\n";
        $response = $http->get($this->baseUrl . "/projects/{$projectId}/tracking");
        $data = $response->json();
        
        if ($response->successful() && ($data['code'] ?? -1) === 0) {
            echo "    ✅ 项目跟踪数据获取成功\n";
            echo "    当前阶段: " . ($data['data']['current_stage'] ?? 'unknown') . "\n";
        } else {
            echo "    ❌ 获取失败: " . json_encode($data) . "\n";
        }
        
        echo "  ✅ 项目流转测试完成\n";
    }
}

$test = new FinanceProjectFlowTest();
$test->run();
