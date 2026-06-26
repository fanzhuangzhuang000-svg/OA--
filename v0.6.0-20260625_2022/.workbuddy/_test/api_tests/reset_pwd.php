<?php
require 'vendor/autoload.php';
$app = require 'bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// 重新加载 .env
$app->loadEnvironmentFrom('.env');
$app->detectEnvironment(fn () => 'production');

$u = \App\Models\User::find(1);
if ($u) {
    $u->password = bcrypt('admin123');
    $u->save();
    echo "OK user=" . $u->username . "\n";
} else {
    echo "No user id=1\n";
}

$u2 = \App\Models\User::where('username', 'nbcy')->first();
if ($u2) {
    $u2->password = bcrypt('admin123');
    $u2->save();
    echo "OK nbcy\n";
} else {
    echo "No nbcy user\n";
}
