<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// 启用 SQL 日志
\DB::enableQueryLog();

$u = App\Models\User::find(1);
echo "User: " . $u->name . PHP_EOL;
echo "model_type in table: " . $u->getMorphClass() . PHP_EOL;

// 直接查中间表
$count = \DB::table('model_has_roles')->where('model_id', 1)->where('model_type', 'App\\Models\\User')->count();
echo "Direct DB query count: $count" . PHP_EOL;

// 用 Eloquent
$roles = $u->roles()->get();
echo "Eloquent roles() count: " . $roles->count() . PHP_EOL;

print_r(\DB::getQueryLog());
