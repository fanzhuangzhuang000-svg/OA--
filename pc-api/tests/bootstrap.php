<?php
/**
 * V0.4.10 A2 - 极简 Laravel app boot, 不依赖 artisan
 *
 * 给 PHPUnit Feature 测试用, 让 Model scope / GlobalScope 真跑
 * 不用 RefreshDatabase (避免引入完整 migration + 重 DB)
 */
require __DIR__ . '/../vendor/autoload.php';

// 强制用 oa_test 数据库连接（从环境变量读取，不要硬编码密码）
$_ENV['APP_ENV'] = 'testing';
$_ENV['DB_DATABASE'] = getenv('DB_DATABASE') ?: 'security_oa_test';
$_ENV['DB_USERNAME'] = getenv('DB_USERNAME') ?: 'oa_test';
$_ENV['DB_PASSWORD'] = getenv('DB_PASSWORD') ?: '';
$_ENV['CACHE_STORE'] = 'array';
$_ENV['SESSION_DRIVER'] = 'array';

$app = require __DIR__ . '/../bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();
