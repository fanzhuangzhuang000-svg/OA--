<?php
// 更新 admin 用户密码为 admin123
require_once __DIR__ . '/vendor/autoload.php';

$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Models\User;

$user = User::where('username', 'admin')->first();
if ($user) {
    $user->password = bcrypt('admin123');
    $user->save();
    echo "✅ 密码已更新为 admin123\n";
} else {
    echo "❌ 未找到 admin 用户\n";
}
