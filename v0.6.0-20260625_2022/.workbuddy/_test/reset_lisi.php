<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$u = App\Models\User::find(72);
$u->password = Illuminate\Support\Facades\Hash::make('admin123');
$u->save();
echo 'OK: ' . substr($u->password, 0, 30) . PHP_EOL;
