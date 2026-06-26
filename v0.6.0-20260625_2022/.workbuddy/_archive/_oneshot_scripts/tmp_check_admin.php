<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

$user = App\Models\User::where("username", "admin")->first();
if ($user) {
    echo "admin id=" . $user->id . "\n";
    echo "pass len=" . strlen($user->password) . "\n";
    echo "pass start=" . substr($user->password, 0, 10) . "\n";
} else {
    echo "no admin user found\n";
}
