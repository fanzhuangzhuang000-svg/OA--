<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// 模拟 sales_yang 登录 (id=86)
$user = App\Models\User::find(86);
echo 'user: ' . $user->username . ' role=' . App\Support\AuthScope::classify($user) . PHP_EOL;

// 模拟 auth 上下文
Illuminate\Support\Facades\Auth::setUser($user);

// 跑 query 看 SQL
$query = App\Models\Project::query();
echo 'SQL: ' . $query->toSql() . PHP_EOL;
echo 'Bindings: ' . json_encode($query->getBindings()) . PHP_EOL;
echo 'Count: ' . $query->count() . PHP_EOL;

// 也试 warranty
$query2 = App\Models\Warranty::query();
echo 'Warranty SQL: ' . $query2->toSql() . PHP_EOL;
echo 'Warranty Count: ' . $query2->count() . PHP_EOL;
