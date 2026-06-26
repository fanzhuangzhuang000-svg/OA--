<?php
require 'vendor/autoload.php';
$app = require 'bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// 测试密码
$tests = [
    'admin' => 'admin123',
    'admin' => 'password',
];
foreach ($tests as $u => $p) {
    $user = \App\Models\User::where('username', $u)->first();
    if (!$user) { echo "No user $u\n"; continue; }
    echo "user={$user->username} id={$user->id} email={$user->email} hash_prefix=" . substr($user->password ?? 'null', 0, 10) . "\n";
    if (\Hash::check($p, $user->password)) echo "  -> $p ✅\n";
    else echo "  -> $p ❌\n";
}
