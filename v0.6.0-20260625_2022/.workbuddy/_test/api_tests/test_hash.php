<?php
require __DIR__.'/vendor/autoload.php';
$app = require __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
echo "HASH=" . Illuminate\Support\Facades\Hash::make('admin123') . "\n";
$user = App\Models\User::find(1);
echo "USER_PASSWORD=" . ($user ? $user->password : 'NULL') . "\n";
echo "CHECK=" . (\Illuminate\Support\Facades\Hash::check('admin123', $user->password) ? 'YES' : 'NO') . "\n";
