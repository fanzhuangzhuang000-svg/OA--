<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$u = App\Models\User::where('username', 'eng_qian')->first();
if ($u) {
    echo 'FOUND id=' . $u->id . ' status=' . ($u->status instanceof BackedEnum ? $u->status->value : (string) $u->status) . PHP_EOL;
    echo Hash::check('admin123', $u->password) ? 'PWD_OK' : 'PWD_BAD';
} else {
    echo 'NOT_FOUND';
}
