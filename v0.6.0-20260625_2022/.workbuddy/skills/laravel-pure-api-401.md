---
name: laravel-pure-api-401
description: When a Laravel 11 + Sanctum API project returns 500 with "Route [login] not defined" on protected endpoints, the cause is Laravel's default Authenticate middleware trying to redirect to a web login route. Use this skill to fix it.
when_to_use: Trigger this skill when (1) a Laravel 11+ API project (no web login route) returns 500 on protected endpoints with log showing "Route [login] not defined", or (2) any pure API project where Sanctum / Auth middleware should return 401 JSON but instead throws 500, or (3) E2E tests show 302 redirect from a protected endpoint.
---

# Laravel 11+ 纯 API 项目 401 Route [login] 500 修复

## 症状

- Sanctum 保护的接口，未带 token 调用 → 期望 401 JSON，实际 **500 错误页**
- `laravel.log` 显示 `Symfony\Component\Routing\Exception\RouteNotFoundException: Route [login] not defined.`
- 带 `Accept: application/json` 时正常返回 401 JSON（这是关键判断点）

## 根因

Laravel 11 的 `\Illuminate\Auth\Middleware\Authenticate::redirectTo()` 默认逻辑：

```php
return $request->expectsJson() ? null : route('login');
```

**当客户端没带 `Accept: application/json` header**（curl 默认、Postman 有时不带、某些旧 SDK）时，它会调 `route('login')` 抛 `RouteNotFoundException` — 纯 API 项目**没有** web login 路由，导致 500。

## 修复 (3 步，Laravel 11 风格)

### 步骤 1：创建自定义 Authenticate 中间件

`app/Http/Middleware/Authenticate.php`：

```php
<?php
namespace App\Http\Middleware;

use Illuminate\Auth\Middleware\Authenticate as Middleware;
use Illuminate\Http\Request;

class Authenticate extends Middleware
{
    protected function redirectTo(Request $request): ?string
    {
        return null; // 永远不重定向 — 让 withExceptions 接管返回 401 JSON
    }
}
```

### 步骤 2：在 bootstrap/app.php 中覆盖默认 auth 别名

```php
->withMiddleware(function (Middleware $middleware) {
    $middleware->statefulApi();
    $middleware->alias([
        'auth' => \App\Http\Middleware\Authenticate::class,  // 覆盖默认
    ]);
})
```

**注意**：不能省这一步！否则 Sanctum 仍用 `\Illuminate\Auth\Middleware\Authenticate`，redirectTo 仍会触发 route('login')

### 步骤 3：在 withExceptions 里兜底处理（关键！）

```php
->withExceptions(function (Exceptions $exceptions) {
    // 1) 标准 401 JSON
    $exceptions->render(function (\Illuminate\Auth\AuthenticationException $e, $request) {
        if ($request->is('api/*') || $request->expectsJson()) {
            return response()->json([
                'code' => 401,
                'message' => '未认证,请先登录',
            ], 401);
        }
    });
    
    // 2) 兜底: 即使没 Accept header, 也不让 route('login') 抛 500
    $exceptions->render(function (\Symfony\Component\Routing\Exception\RouteNotFoundException $e, $request) {
        if (str_contains($e->getMessage(), 'Route [login] not defined') && $request->is('api/*')) {
            return response()->json(['code' => 401, 'message' => '未认证,请先登录'], 401);
        }
    });
})
```

## 验证

部署后跑 4 个测试：

```bash
# [1] 422 验证错误 (前端带 Accept)
curl -X POST http://api/api/.../change-password \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"oldPassword":"wrong"}'
# 期望: 422 + JSON {"message":"原密码至少 6 位",...}

# [2] 401 (前端带 Accept)
curl -X PUT http://api/api/auth/profile -H "Accept: application/json" -d '{}'
# 期望: 401 + JSON {"code":401,"message":"未认证,请先登录"}

# [3] 401 (前端无 Accept, 兜底生效)
curl -X PUT http://api/api/auth/profile -d '{}'  # 没有 Accept header
# 期望: 401 + JSON (不再 500)

# [4] 200 正常业务
curl -X POST http://api/api/auth/login -d '{"username":"admin","password":"admin123"}'
# 期望: 200 + token
```

## 关键经验

1. **Laravel 11+ 纯 API 项目必须显式覆盖 auth 别名**，否则 Sanctum 401 触发 route('login') 500
2. **E2E 测试一定要带 `Accept: application/json`**（curl 不带；Axios 默认带）
3. **php-fpm reload 用 `kill -USR2 <master_pid>`**，不是 `kill -HUP`（HUP 是 nginx）
4. **修改中间件/异常处理器后必须 reload php-fpm**，opcache 不会自动刷新
5. **route('login') 抛 500 的兜底**用 `$exceptions->render` 而不是中间件改造，更鲁棒

## 部署流程

```python
import paramiko
cli = paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect('172.20.0.139', username='nbcy', password='admin123')

# 1. chown 让 nbcy 可写
cli.exec_command('echo admin123 | sudo -S chown -R nbcy:nbcy /var/www/oa-api/app/Http/Middleware /var/www/oa-api/bootstrap')

# 2. sftp 上传
sftp = cli.open_sftp()
sftp.put('local/app/Http/Middleware/Authenticate.php', '/var/www/oa-api/app/Http/Middleware/Authenticate.php')
sftp.put('local/bootstrap/app.php', '/var/www/oa-api/bootstrap/app.php')
sftp.close()

# 3. 改回 www-data
cli.exec_command('echo admin123 | sudo -S chown -R www-data:www-data /var/www/oa-api/app/Http/Middleware /var/www/oa-api/bootstrap')

# 4. reload php-fpm (USR2 是 php-fpm 专属信号)
import time
cli.exec_command('echo admin123 | sudo -S kill -USR2 834678')  # master pid
time.sleep(3)  # 等 worker 全部回收
```

## 关联文件

- `pc-api/app/Http/Middleware/Authenticate.php` — 自定义中间件
- `pc-api/bootstrap/app.php` — alias + exception render
- `pc-api/routes/api.php` — 业务路由（不变）
