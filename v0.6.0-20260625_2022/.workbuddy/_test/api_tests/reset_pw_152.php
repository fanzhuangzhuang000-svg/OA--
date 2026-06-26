<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$u = App\Models\User::find(1);
if ($u) {
    $u->password = Illuminate\Support\Facades\Hash::make('admin123');
    $u->save();
    echo "Password reset for: " . $u->username . "\n";
} else {
    echo "User #1 not found\n";
}
