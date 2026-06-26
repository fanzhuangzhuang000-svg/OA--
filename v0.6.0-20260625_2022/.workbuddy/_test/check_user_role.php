<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$u = App\Models\User::find(1);
echo "admin user found: " . ($u ? $u->name : 'NO') . PHP_EOL;
echo "roles count: " . $u->roles()->count() . PHP_EOL;
foreach ($u->roles as $r) echo "- role: " . $r->name . PHP_EOL;
echo "hasRole(admin): " . ($u->hasRole('admin') ? 'true' : 'false') . PHP_EOL;
echo "hasRole(sales_manager): " . ($u->hasRole('sales_manager') ? 'true' : 'false') . PHP_EOL;
echo "hasRole(manager): " . ($u->hasRole('manager') ? 'true' : 'false') . PHP_EOL;
