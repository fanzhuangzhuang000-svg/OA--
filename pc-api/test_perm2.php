<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$user = \App\Models\User::find(3);
if (!$user) { echo "No user 3 found\n"; exit; }
echo "User: id={$user->id} username={$user->username}\n";

// Test activeRoles
try {
    $roles = $user->activeRoles()->pluck('roles.name')->all();
    echo "activeRoles: " . json_encode($roles) . "\n";
} catch (\Throwable $e) {
    echo "activeRoles ERROR: " . $e->getMessage() . "\n";
}

// Test hasActivePermissionTo
try {
    $has = $user->hasActivePermissionTo('system.role');
    echo "hasActivePermissionTo('system.role'): " . ($has ? 'YES' : 'NO') . "\n";
} catch (\Throwable $e) {
    echo "hasActivePermissionTo('system.role') ERROR: " . $e->getMessage() . "\n";
}

// Test spatie roles
try {
    $roles = $user->getRoleNames();
    echo "spatie getRoleNames: " . json_encode($roles->toArray()) . "\n";
} catch (\Throwable $e) {
    echo "spatie getRoleNames ERROR: " . $e->getMessage() . "\n";
}

// Check if the column exists
try {
    $result = \DB::select("SELECT column_name FROM information_schema.columns WHERE table_name='model_has_roles' AND column_name='expires_at'");
    echo "expires_at column exists: " . (count($result) > 0 ? 'YES' : 'NO') . "\n";
} catch (\Throwable $e) {
    echo "Column check ERROR: " . $e->getMessage() . "\n";
}

// Get token for user 3
$token = DB::table('personal_access_tokens')->where('tokenable_id', 3)->first();
if ($token) {
    echo "\nUser 3 token: " . $token->token . "\n";
}
