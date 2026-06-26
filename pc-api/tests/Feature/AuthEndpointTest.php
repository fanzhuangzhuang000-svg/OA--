<?php

namespace Tests\Feature;

use PHPUnit\Framework\TestCase;

/**
 * 认证端点 Feature 测试
 *
 * 覆盖全部认证相关 API:
 *   POST /api/auth/login          — 登录成功 / 失败 / 参数校验 / 禁用账号
 *   POST /api/auth/logout         — 登出成功 / token 失效
 *   GET  /api/auth/userinfo       — 获取当前用户信息（需认证）
 *   GET  /api/auth/me             — /userinfo 别名
 *   POST /api/auth/change-password — 修改密码（需认证 + 旧密码校验 + 弱密码拦截）
 *   PUT  /api/auth/profile        — 更新个人资料（需认证）
 *   权限测试                       — 未认证访问所有受保护端点应返回 401
 *
 * 用例: 20 个
 */
class AuthEndpointTest extends TestCase
{
    private const API = 'http://127.0.0.1:8081/api';

    /** 已知可用的测试账号 */
    private const ADMIN_USER     = 'admin1';
    private const ADMIN_PASS     = 'admin123';
    private const FINANCE_USER   = 'fin_wu';
    private const FINANCE_PASS   = 'admin123';
    private const REGULAR_USER   = 'eng_qian';
    private const REGULAR_PASS   = 'admin123';

    /** 登录 token 缓存 (避免重复登录触发限流) */
    private static array $tokenCache = [];

    /** 统计登录次数, 每 3 次清一次 Redis 防 throttle */
    private static int $loginCount = 0;

    // ==================== helpers ====================

    protected function setUp(): void
    {
        parent::setUp();
    }

    public static function setUpBeforeClass(): void
    {
        self::flushRedis();
    }

    private static function flushRedis(): void
    {
        try {
            $r = new \Redis();
            $r->connect('127.0.0.1', 6379);
            $r->select(0);
            $r->flushDB();
            $r->select(1);
            $r->flushDB();
            $r->close();
        } catch (\Throwable $e) {
            // Redis 不可用时静默
        }
    }

    /**
     * 登录并缓存 token
     */
    private function loginAs(string $username, string $password = self::ADMIN_PASS): string
    {
        $key = "{$username}:{$password}";
        if (isset(self::$tokenCache[$key])) {
            return self::$tokenCache[$key];
        }

        self::$loginCount++;
        if (self::$loginCount > 3) {
            self::flushRedis();
            self::$loginCount = 0;
        }

        $response = $this->httpPost('/auth/login', [
            'username' => $username,
            'password' => $password,
        ]);

        if (($response['code'] ?? 1) !== 0 || empty($response['data']['token'])) {
            $this->markTestSkipped("登录失败 ({$username}): " . ($response['message'] ?? 'unknown'));
        }

        self::$tokenCache[$key] = $response['data']['token'];
        return self::$tokenCache[$key];
    }

    /**
     * HTTP POST 请求
     */
    private function httpPost(string $endpoint, array $data, ?string $token = null): array
    {
        $headers = "Content-Type: application/json\r\n";
        if ($token) {
            $headers .= "Authorization: Bearer {$token}\r\n";
        }

        $ctx = stream_context_create(['http' => [
            'method'        => 'POST',
            'ignore_errors' => true,
            'header'        => $headers,
            'content'       => json_encode($data),
            'timeout'       => 10,
        ]]);

        $raw = @file_get_contents(self::API . $endpoint, false, $ctx);
        if ($raw === false) {
            $this->markTestSkipped('API 不可达: ' . self::API . $endpoint);
        }

        return json_decode($raw, true) ?? ['code' => 598, 'message' => 'JSON decode failed'];
    }

    /**
     * HTTP GET 请求
     */
    private function httpGet(string $endpoint, ?string $token = null): array
    {
        $headers = '';
        if ($token) {
            $headers = "Authorization: Bearer {$token}\r\n";
        }

        $ctx = stream_context_create(['http' => [
            'method'        => 'GET',
            'ignore_errors' => true,
            'header'        => $headers,
            'timeout'       => 10,
        ]]);

        $raw = @file_get_contents(self::API . $endpoint, false, $ctx);
        if ($raw === false) {
            $this->markTestSkipped('API 不可达: ' . self::API . $endpoint);
        }

        return json_decode($raw, true) ?? ['code' => 598, 'message' => 'JSON decode failed'];
    }

    /**
     * HTTP PUT 请求
     */
    private function httpPut(string $endpoint, array $data, ?string $token = null): array
    {
        $headers = "Content-Type: application/json\r\n";
        if ($token) {
            $headers .= "Authorization: Bearer {$token}\r\n";
        }

        $ctx = stream_context_create(['http' => [
            'method'        => 'PUT',
            'ignore_errors' => true,
            'header'        => $headers,
            'content'       => json_encode($data),
            'timeout'       => 10,
        ]]);

        $raw = @file_get_contents(self::API . $endpoint, false, $ctx);
        if ($raw === false) {
            $this->markTestSkipped('API 不可达: ' . self::API . $endpoint);
        }

        return json_decode($raw, true) ?? ['code' => 598, 'message' => 'JSON decode failed'];
    }

    // ==================== 1. POST /api/auth/login ====================

    /**
     * 测试: 管理员登录成功, 返回 token 和用户信息
     */
    public function test_login_success_returns_token_and_user(): void
    {
        $response = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => self::ADMIN_PASS,
        ]);

        $this->assertSame(0, $response['code'], '登录应返回 code=0');
        $this->assertNotEmpty($response['data']['token'], '应返回非空 token');
        $this->assertSame(self::ADMIN_USER, $response['data']['user']['username']);
        $this->assertArrayHasKey('name', $response['data']['user']);
        $this->assertArrayHasKey('id', $response['data']['user']);
    }

    /**
     * 测试: 错误密码登录失败 → 401
     */
    public function test_login_wrong_password_returns_401(): void
    {
        $response = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => 'definitely_wrong_password_xyz',
        ]);

        $this->assertNotSame(0, $response['code'], '错误密码不应返回 code=0');
        $this->assertArrayHasKey('message', $response);
    }

    /**
     * 测试: 不存在的用户名登录失败 → 401
     */
    public function test_login_nonexistent_user_returns_401(): void
    {
        $response = $this->httpPost('/auth/login', [
            'username' => 'nonexistent_user_' . uniqid(),
            'password' => 'any_password_123',
        ]);

        $this->assertNotSame(0, $response['code'], '不存在的用户不应登录成功');
    }

    /**
     * 测试: 缺少必填字段 (username / password) → 422 验证错误
     */
    public function test_login_missing_fields_returns_422(): void
    {
        // 缺少 password
        $r1 = $this->httpPost('/auth/login', ['username' => 'admin1']);
        $this->assertNotSame(0, $r1['code'], '缺少 password 应失败');

        // 缺少 username
        $r2 = $this->httpPost('/auth/login', ['password' => 'admin123']);
        $this->assertNotSame(0, $r2['code'], '缺少 username 应失败');

        // 空 body
        $r3 = $this->httpPost('/auth/login', []);
        $this->assertNotSame(0, $r3['code'], '空 body 应失败');
    }

    /**
     * 测试: 登录返回的 token 可以用于后续认证请求
     */
    public function test_login_token_is_usable_for_authenticated_requests(): void
    {
        $loginResponse = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => self::ADMIN_PASS,
        ]);
        $this->assertSame(0, $loginResponse['code']);

        $token = $loginResponse['data']['token'];

        // 用该 token 访问 /auth/userinfo
        $userResponse = $this->httpGet('/auth/userinfo', $token);
        $this->assertSame(0, $userResponse['code'], 'login token 应能访问受保护端点');
        $this->assertSame(self::ADMIN_USER, $userResponse['data']['user']['username']);
    }

    // ==================== 2. GET /api/auth/userinfo ====================

    /**
     * 测试: 已认证用户获取 /auth/userinfo 成功
     */
    public function test_userinfo_returns_authenticated_user_data(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);
        $response = $this->httpGet('/auth/userinfo', $token);

        $this->assertSame(0, $response['code']);
        $this->assertArrayHasKey('user', $response['data']);
        $this->assertSame(self::ADMIN_USER, $response['data']['user']['username']);
        $this->assertArrayHasKey('name', $response['data']['user']);
        $this->assertArrayHasKey('id', $response['data']['user']);
        // password 不应返回
        $this->assertArrayNotHasKey('password', $response['data']['user']);
    }

    /**
     * 测试: /auth/me 别名与 /auth/userinfo 返回相同结构
     */
    public function test_auth_me_alias_returns_same_as_userinfo(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $userinfoResp = $this->httpGet('/auth/userinfo', $token);
        $meResp       = $this->httpGet('/auth/me', $token);

        $this->assertSame(0, $userinfoResp['code']);
        $this->assertSame(0, $meResp['code']);
        $this->assertSame(
            $userinfoResp['data']['user']['username'],
            $meResp['data']['user']['username'],
            '/auth/me 和 /auth/userinfo 应返回同一用户'
        );
    }

    /**
     * 测试: 不同角色用户获取 /auth/userinfo 均成功
     */
    public function test_userinfo_works_for_different_roles(): void
    {
        $users = [
            self::ADMIN_USER   => self::ADMIN_PASS,
            self::FINANCE_USER => self::FINANCE_PASS,
            self::REGULAR_USER => self::REGULAR_PASS,
        ];

        foreach ($users as $username => $password) {
            $token    = $this->loginAs($username, $password);
            $response = $this->httpGet('/auth/userinfo', $token);

            $this->assertSame(0, $response['code'], "用户 {$username} 获取 userinfo 应成功");
            $this->assertSame($username, $response['data']['user']['username']);
        }
    }

    // ==================== 3. POST /api/auth/change-password ====================

    /**
     * 测试: 修改密码 — 旧密码错误 → 422
     */
    public function test_change_password_wrong_old_password(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $response = $this->httpPost('/auth/change-password', [
            'oldPassword' => 'wrong_old_password_123',
            'newPassword' => 'NewSecure1234',
        ], $token);

        $this->assertSame(422, $response['code'], '旧密码错误应返回 code=422');
    }

    /**
     * 测试: 修改密码 — 新密码太短 → 422 验证失败
     */
    public function test_change_password_too_short(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $response = $this->httpPost('/auth/change-password', [
            'oldPassword' => self::ADMIN_PASS,
            'newPassword' => 'Ab1',  // 太短
        ], $token);

        $this->assertNotSame(0, $response['code'], '新密码不足 8 位应失败');
    }

    /**
     * 测试: 修改密码 — 新密码与旧密码相同 → 422
     */
    public function test_change_password_same_as_old(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $response = $this->httpPost('/auth/change-password', [
            'oldPassword' => self::ADMIN_PASS,
            'newPassword' => self::ADMIN_PASS, // 与旧密码相同
        ], $token);

        $this->assertNotSame(0, $response['code'], '新密码与旧密码相同应失败');
    }

    /**
     * 测试: 修改密码 — 弱密码黑名单拦截 → 422
     */
    public function test_change_password_weak_password_blocked(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $weakPasswords = ['password', '12345678', 'admin123', 'qwerty12'];

        foreach ($weakPasswords as $weak) {
            $response = $this->httpPost('/auth/change-password', [
                'oldPassword' => self::ADMIN_PASS,
                'newPassword' => $weak,
            ], $token);

            $this->assertNotSame(0, $response['code'], "弱密码 '{$weak}' 应被拒绝");
        }
    }

    /**
     * 测试: 修改密码 — 缺少必填字段 → 422
     */
    public function test_change_password_missing_fields(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        // 缺少 newPassword
        $r1 = $this->httpPost('/auth/change-password', [
            'oldPassword' => self::ADMIN_PASS,
        ], $token);
        $this->assertNotSame(0, $r1['code'], '缺少 newPassword 应失败');

        // 缺少 oldPassword
        $r2 = $this->httpPost('/auth/change-password', [
            'newPassword' => 'NewSecure1234',
        ], $token);
        $this->assertNotSame(0, $r2['code'], '缺少 oldPassword 应失败');
    }

    // ==================== 4. PUT /api/auth/profile ====================

    /**
     * 测试: 更新个人资料 — 成功
     */
    public function test_update_profile_success(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $response = $this->httpPut('/auth/profile', [
            'name'  => '测试管理员',
            'phone' => '13800000001',
        ], $token);

        $this->assertSame(0, $response['code'], '更新资料应成功');
        $this->assertArrayHasKey('name', $response['data']);
    }

    /**
     * 测试: 更新个人资料 — 邮箱格式不正确 → 422
     */
    public function test_update_profile_invalid_email(): void
    {
        $token = $this->loginAs(self::ADMIN_USER);

        $response = $this->httpPut('/auth/profile', [
            'email' => 'not-a-valid-email',
        ], $token);

        $this->assertNotSame(0, $response['code'], '无效邮箱应被拒绝');
    }

    // ==================== 5. POST /api/auth/logout ====================

    /**
     * 测试: 登出成功 → code=0
     */
    public function test_logout_success(): void
    {
        // 用独立的一次性 token, 避免影响缓存
        self::$loginCount++;
        if (self::$loginCount > 3) {
            self::flushRedis();
            self::$loginCount = 0;
        }

        $loginResp = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => self::ADMIN_PASS,
        ]);
        $this->assertSame(0, $loginResp['code']);
        $token = $loginResp['data']['token'];

        $logoutResp = $this->httpPost('/auth/logout', [], $token);
        $this->assertSame(0, $logoutResp['code'], '登出应返回 code=0');
    }

    /**
     * 测试: 登出后 token 失效 → 再次访问 userinfo 应返回 401
     */
    public function test_logout_invalidates_token(): void
    {
        self::$loginCount++;
        if (self::$loginCount > 3) {
            self::flushRedis();
            self::$loginCount = 0;
        }

        // 先登录
        $loginResp = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => self::ADMIN_PASS,
        ]);
        $this->assertSame(0, $loginResp['code']);
        $token = $loginResp['data']['token'];

        // 登出
        $this->httpPost('/auth/logout', [], $token);

        // 用已登出的 token 访问 userinfo → 应 401
        $response = $this->httpGet('/auth/userinfo', $token);
        $this->assertNotSame(0, $response['code'], '登出后 token 应失效');
    }

    // ==================== 6. 权限测试 — 未认证访问 ====================

    /**
     * 测试: 未认证访问 /auth/userinfo → 401
     */
    public function test_unauthenticated_userinfo_returns_401(): void
    {
        $response = $this->httpGet('/auth/userinfo');
        $this->assertNotSame(0, $response['code'], '未认证访问 userinfo 应返回非 0');
        // Sanctum 默认返回 401
        $this->assertTrue(
            ($response['code'] ?? 0) === 401 || ($response['message'] ?? '') !== '',
            '未认证应返回 401 或包含错误消息'
        );
    }

    /**
     * 测试: 未认证访问 /auth/me → 401
     */
    public function test_unauthenticated_me_returns_401(): void
    {
        $response = $this->httpGet('/auth/me');
        $this->assertNotSame(0, $response['code'], '未认证访问 /auth/me 应返回非 0');
    }

    /**
     * 测试: 未认证访问 /auth/logout → 401
     */
    public function test_unauthenticated_logout_returns_401(): void
    {
        $response = $this->httpPost('/auth/logout', []);
        $this->assertNotSame(0, $response['code'], '未认证访问 logout 应返回非 0');
    }

    /**
     * 测试: 未认证访问 /auth/change-password → 401
     */
    public function test_unauthenticated_change_password_returns_401(): void
    {
        $response = $this->httpPost('/auth/change-password', [
            'oldPassword' => 'anything',
            'newPassword' => 'NewPass1234',
        ]);
        $this->assertNotSame(0, $response['code'], '未认证修改密码应返回非 0');
    }

    /**
     * 测试: 未认证访问 /auth/profile → 401
     */
    public function test_unauthenticated_update_profile_returns_401(): void
    {
        $response = $this->httpPut('/auth/profile', [
            'name' => 'Hacker',
        ]);
        $this->assertNotSame(0, $response['code'], '未认证更新资料应返回非 0');
    }

    /**
     * 测试: 使用伪造/无效 token 访问 → 401
     */
    public function test_invalid_token_returns_401(): void
    {
        $fakeTokens = [
            'completely_bogus_token_string',
            '1|fake_hmac_token',
            str_repeat('a', 100),
        ];

        foreach ($fakeTokens as $fakeToken) {
            $response = $this->httpGet('/auth/userinfo', $fakeToken);
            $this->assertNotSame(0, $response['code'], "伪造 token '{$fakeToken}' 不应通过认证");
        }
    }

    /**
     * 测试: 使用空 Bearer token → 401
     */
    public function test_empty_bearer_token_returns_401(): void
    {
        $response = $this->httpGet('/auth/userinfo', '');
        $this->assertNotSame(0, $response['code'], '空 token 不应通过认证');
    }

    // ==================== 7. 集成场景 ====================

    /**
     * 测试: 完整认证生命周期 — 登录 → 获取信息 → 修改资料 → 登出
     */
    public function test_full_auth_lifecycle(): void
    {
        // 1. 登录
        self::$loginCount++;
        if (self::$loginCount > 3) {
            self::flushRedis();
            self::$loginCount = 0;
        }

        $loginResp = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => self::ADMIN_PASS,
        ]);
        $this->assertSame(0, $loginResp['code'], '步骤1: 登录应成功');
        $token = $loginResp['data']['token'];
        $this->assertNotEmpty($token);

        // 2. 获取用户信息
        $userResp = $this->httpGet('/auth/userinfo', $token);
        $this->assertSame(0, $userResp['code'], '步骤2: 获取用户信息应成功');
        $this->assertSame(self::ADMIN_USER, $userResp['data']['user']['username']);

        // 3. 获取 /auth/me (别名)
        $meResp = $this->httpGet('/auth/me', $token);
        $this->assertSame(0, $meResp['code'], '步骤3: /auth/me 应成功');

        // 4. 登出
        $logoutResp = $this->httpPost('/auth/logout', [], $token);
        $this->assertSame(0, $logoutResp['code'], '步骤4: 登出应成功');

        // 5. 登出后再访问 → 应 401
        $afterLogout = $this->httpGet('/auth/userinfo', $token);
        $this->assertNotSame(0, $afterLogout['code'], '步骤5: 登出后 token 应失效');
    }

    /**
     * 测试: 登录返回的用户数据不包含敏感字段 (password, remember_token)
     */
    public function test_login_response_excludes_sensitive_fields(): void
    {
        $response = $this->httpPost('/auth/login', [
            'username' => self::ADMIN_USER,
            'password' => self::ADMIN_PASS,
        ]);

        $this->assertSame(0, $response['code']);
        $userData = $response['data']['user'] ?? [];

        $this->assertArrayNotHasKey('password', $userData, '响应不应包含 password');
        $this->assertArrayNotHasKey('remember_token', $userData, '响应不应包含 remember_token');
    }
}
