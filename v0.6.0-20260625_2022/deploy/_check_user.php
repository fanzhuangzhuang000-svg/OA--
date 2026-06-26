<?php
// 走 Laravel 11 bootstrap 调 User / Hash
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Models\User;
use Illuminate\Support\Facades\Hash;

echo "Total users: " . User::count() . "\n";

$u = User::find(1);
if (!$u) {
    echo "User id=1 not found!\n";
    $first = User::orderBy('id')->first();
    if ($first) {
        echo "First user: id={$first->id} username={$first->username} email={$first->email}\n";
    }
    exit(0);
}

echo "id={$u->id} username={$u->username} email={$u->email} name={$u->name}\n";
echo "hash prefix: " . substr($u->password, 0, 30) . "\n";
echo "Hash::check('admin123'): " . (Hash::check('admin123', $u->password) ? 'OK' : 'BAD') . "\n";
echo "Hash::check('password'): " . (Hash::check('password', $u->password) ? 'OK' : 'BAD') . "\n";
echo "Hash::check('123456'): " . (Hash::check('123456', $u->password) ? 'OK' : 'BAD') . "\n";
echo "New hash for 'admin123': " . Hash::make('admin123') . "\n";

// 列所有用户 id+username(防 user 表是空 seed 出来的)
echo "\n--- All users ---\n";
foreach (User::orderBy('id')->limit(20)->get() as $row) {
    echo "  id={$row->id} username={$row->username} email={$row->email}\n";
}
