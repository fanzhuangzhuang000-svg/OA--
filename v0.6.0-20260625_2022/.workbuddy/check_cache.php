<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
try {
    \Illuminate\Support\Facades\Cache::put('test_key_xyz', 'hello_redis', 60);
    $val = \Illuminate\Support\Facades\Cache::get('test_key_xyz');
    echo "write/read OK: $val" . PHP_EOL;
    echo "default store: " . \Illuminate\Support\Facades\Cache::getDefaultDriver() . PHP_EOL;
} catch (\Throwable $e) {
    echo "ERROR: " . $e->getMessage() . PHP_EOL;
}
