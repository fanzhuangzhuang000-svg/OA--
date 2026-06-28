<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$user = \App\Models\User::find(1);
if (!$user) { echo "No user found\n"; exit; }
echo "User: {$user->id} {$user->username}\n";

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
    echo "hasActivePermissionTo ERROR: " . $e->getMessage() . "\n";
}

// Test hasActivePermissionTo for project.view
try {
    $has = $user->hasActivePermissionTo('project.view');
    echo "hasActivePermissionTo('project.view'): " . ($has ? 'YES' : 'NO') . "\n";
} catch (\Throwable $e) {
    echo "hasActivePermissionTo ERROR: " . $e->getMessage() . "\n";
}

// Test regular spatie roles()
try {
    $roles = $user->getRoleNames();
    echo "spatie getRoleNames: " . json_encode($roles->toArray()) . "\n";
} catch (\Throwable $e) {
    echo "spatie getRoleNames ERROR: " . $e->getMessage() . "\n";
}

// Check token
$token = DB::table('personal_access_tokens')->where('tokenable_id', 1)->first();
if ($token) {
    echo "\nUser 1 token: " . $token->token . "\n";
} else {
    echo "\nNo token for user 1\n";
}
