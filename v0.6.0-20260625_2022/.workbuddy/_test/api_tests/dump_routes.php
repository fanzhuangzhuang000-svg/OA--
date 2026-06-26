<?php
/**
 * dump_routes.php — 在 Laravel 服务器上 dump API 路由为 JSON
 * 用法：php dump_routes.php（在 Laravel 根目录运行）
 */
require_once __DIR__ . '/vendor/autoload.php';

// 加载 Laravel 应用
$app = require_once __DIR__ . '/bootstrap/app.php';

// 引导应用（Laravel 11 风格）
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// 获取路由
$router = $app->make('router');
$routes = [];

foreach ($router->getRoutes() as $route) {
    $uri = $route->uri();
    if (strpos($uri, 'api') === 0 || strpos($uri, 'sanctum') === 0) {
        $routes[] = [
            'method' => implode('|', $route->methods()),
            'uri' => $uri,
            'name' => $route->getName(),
            'action' => $route->getActionName(),
        ];
    }
}

echo json_encode($routes, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
