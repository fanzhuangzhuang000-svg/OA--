<?php
// 重置 117 上 4 个测试用户密码
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

$usernames = ['proj_mgr', 'fin_zhou', 'eng_zhao', 'sales_chen', 'tech_mgr'];
foreach ($usernames as $u) {
    $user = App\Models\User::where('username', $u)->first();
    if ($user) {
        $user->password = Illuminate\Support\Facades\Hash::make('123456');
        $user->save();
        echo "{$u}:OK id={$user->id}" . PHP_EOL;
    } else {
        echo "{$u}:NOTFOUND" . PHP_EOL;
    }
}
echo "DONE" . PHP_EOL;
