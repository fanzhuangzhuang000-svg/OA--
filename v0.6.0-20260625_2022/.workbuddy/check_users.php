<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
foreach ([74 => 'admin1', 80 => 'fin_wu', 86 => 'sales_yang', 82 => 'eng_qian', 1 => 'admin'] as $id => $username) {
    $u = App\Models\User::find($id);
    if (!$u) continue;
    $un = App\Support\AuthScope::isUnrestricted($u) ? 'YES' : 'NO';
    $role = App\Support\AuthScope::classify($u);
    echo "id={$id} username={$username} role={$role} unrestricted={$un}" . PHP_EOL;
}
