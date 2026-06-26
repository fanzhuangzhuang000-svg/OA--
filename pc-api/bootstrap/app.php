<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withProviders([
        // Laravel 11 核心 provider (bootstrap/cache/services.php 不存在时必须)
        // 只包含有对应 config 文件的 provider, 避免缺少配置报错
        Illuminate\Auth\AuthServiceProvider::class,
        Illuminate\Cache\CacheServiceProvider::class,
        Illuminate\Cookie\CookieServiceProvider::class,
        Illuminate\Database\DatabaseServiceProvider::class,
        Illuminate\Encryption\EncryptionServiceProvider::class,
        Illuminate\Filesystem\FilesystemServiceProvider::class,
        Illuminate\Foundation\Providers\FoundationServiceProvider::class,
        Illuminate\Hashing\HashServiceProvider::class,
        Illuminate\Mail\MailServiceProvider::class,
        Illuminate\Notifications\NotificationServiceProvider::class,
        Illuminate\Pagination\PaginationServiceProvider::class,
        Illuminate\Pipeline\PipelineServiceProvider::class,
        Illuminate\Queue\QueueServiceProvider::class,
        Illuminate\Redis\RedisServiceProvider::class,
        Illuminate\Auth\Passwords\PasswordResetServiceProvider::class,
        Illuminate\Session\SessionServiceProvider::class,
        Illuminate\Translation\TranslationServiceProvider::class,
        Illuminate\Validation\ValidationServiceProvider::class,
        Illuminate\View\ViewServiceProvider::class,
        App\Providers\AppServiceProvider::class,
        App\Providers\AuthServiceProvider::class,
        App\Providers\EventServiceProvider::class,
        App\Providers\RouteServiceProvider::class,
    ])
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php', // v0.3.11 块四: 加载 console 命令
        apiPrefix: 'api',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        // v0.3.9 修复 SPA login 419 CSRF — 纯 token API 项目不需要 stateful 中间件
        // $middleware->statefulApi();

        // 1) 强制 API 全部返回 JSON（即使客户端没带 Accept）
        // 2) HandleCors (CORS 配置见 config/cors.php)
        // 3) throttle:api — 默认 60 req/min（App\Providers\RouteServiceProvider 默认）
        // 4) 业务 API 前缀下挂审计日志中间件（监听 POST/PUT/PATCH/DELETE）
        $middleware->api(prepend: [
            \App\Http\Middleware\ForceJsonResponse::class,
            \Illuminate\Http\Middleware\HandleCors::class,
            'throttle:api',
            \App\Http\Middleware\AuditLogger::class,
        ]);

        // 覆盖默认 auth 别名 — 纯 API 项目 redirectTo() 永远返回 null
        // (Sanctum 仍解析 token，只是不再走 web login 路由)
        $middleware->alias([
            'auth' => \App\Http\Middleware\Authenticate::class,
            // v0.3.11 P0: 跨用户 403 鉴权 — 路由: ->middleware('owns:lead')
            'owns' => \App\Http\Middleware\CheckResourceOwnership::class,
            // v0.3.14 D1: 数据范围中间件 — 路由: ->middleware('data_scope:own')
            'data_scope' => \App\Http\Middleware\DataScope::class,
            // V0.5.0 L3: 接口授权 — 路由: ->middleware('permission:project.view')
            'permission' => \App\Http\Middleware\CheckPermission::class,
            // V0.5.1 L4: 字段脱敏 — 路由: ->middleware('field_mask')
            'field_mask' => \App\Http\Middleware\ApplyFieldMask::class,
            // V0.5.3: 临时权限过期校验 — 路由: ->middleware('role_active')
            'role_active' => \App\Http\Middleware\CheckRoleActive::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        // ===== T5 错误监控 — 所有未处理的异常都进 ErrorReporter =====
        // 不阻断原有渲染流程 — 只是额外写一份结构化 JSON 错误日志
        $exceptions->report(function (\Throwable $e) {
            if (! $e instanceof \Illuminate\Auth\AuthenticationException) {
                \App\Services\ErrorReporter::report($e, [
                    'url' => request()?->fullUrl(),
                    'ip'  => request()?->ip(),
                ]);
            }
        });

        // 纯 API 项目: 未认证 / 认证失败 一律返回 401 JSON
        // 避免 Laravel 默认的 route('login') 重定向 (无 web login 路由)
        $exceptions->render(function (\Illuminate\Auth\AuthenticationException $e, $request) {
            if ($request->is('api/*') || $request->expectsJson()) {
                return response()->json([
                    'code' => 401,
                    'message' => '未认证,请先登录',
                ], 401);
            }
        });

        // 兜底: 即使未带 Accept: application/json，也确保无 login 路由时不抛 500
        $exceptions->render(function (\Symfony\Component\Routing\Exception\RouteNotFoundException $e, $request) {
            if (str_contains($e->getMessage(), 'Route [login] not defined') && $request->is('api/*')) {
                return response()->json([
                    'code' => 401,
                    'message' => '未认证,请先登录',
                ], 401);
            }
        });

        // ========== 纯 API 项目: 所有 API 异常一律返回 JSON ==========
        // 即使 APP_DEBUG=false，前端也能拿到结构化错误而不是 HTML 错误页
        $exceptions->render(function (\Throwable $e, $request) {
            if (!($request->is('api/*') || $request->expectsJson())) {
                return null; // 非 API 请求走默认（web 错误页）
            }

            // 1) ValidationException
            if ($e instanceof \Illuminate\Validation\ValidationException) {
                return response()->json([
                    'code'    => 422,
                    'message' => '数据校验失败',
                    'errors'  => $e->errors(),
                ], 422);
            }

            // 2) ModelNotFoundException
            if ($e instanceof \Illuminate\Database\Eloquent\ModelNotFoundException) {
                $model = class_basename($e->getModel());
                return response()->json([
                    'code'    => 404,
                    'message' => "{$model} 不存在",
                ], 404);
            }

            // 3) NotFoundHttpException（路由不存在）
            if ($e instanceof \Symfony\Component\HttpKernel\Exception\NotFoundHttpException) {
                return response()->json([
                    'code'    => 404,
                    'message' => '接口不存在',
                ], 404);
            }

            // 4) MethodNotAllowedHttpException
            if ($e instanceof \Symfony\Component\HttpKernel\Exception\MethodNotAllowedHttpException) {
                return response()->json([
                    'code'    => 405,
                    'message' => '请求方法不允许',
                ], 405);
            }

            // 5) HttpException（其他状态码）
            if ($e instanceof \Symfony\Component\HttpKernel\Exception\HttpExceptionInterface) {
                return response()->json([
                    'code'    => $e->getStatusCode(),
                    'message' => $e->getMessage() ?: '请求异常',
                ], $e->getStatusCode());
            }

            // 5.5) QueryException: SQL 错误（比如把 "NaN" 塞进 bigint 字段）
            //      隐式 route binding 之前没有强转，直接 PG 报 22P02
            if ($e instanceof \Illuminate\Database\QueryException) {
                $sqlState = $e->errorInfo[0] ?? '';
                if ($sqlState === '22P02') {
                    return response()->json([
                        'code'    => 404,
                        'message' => '资源不存在或参数错误',
                    ], 404);
                }
            }

            // 6) 所有其他异常 — 500
            $payload = [
                'code'    => 500,
                'message' => config('app.debug') ? $e->getMessage() : '服务器内部错误',
            ];
            if (config('app.debug')) {
                $payload['exception'] = get_class($e);
                $payload['file']      = $e->getFile() . ':' . $e->getLine();
            }
            return response()->json($payload, 500);
        });
    })
    // v0.3.11 块四: 注册 Schedule (Laravel 11+ 必须在 bootstrap 注册)
    ->withSchedule(function (\Illuminate\Console\Scheduling\Schedule $schedule) {
        // 每日 01:00 把过期的报价单自动改 expired (实际命令在 routes/console.php)
    })
    // v0.3.11 块四: 显式加载 routes/console.php (Laravel 11+ 改 withCommands 或 withRouting)
    ->create();
