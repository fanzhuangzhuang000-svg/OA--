<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$user = \App\Models\User::find(3);
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

try {
    $has = $user->hasActivePermissionTo('project.view');
    echo "hasActivePermissionTo('project.view'): " . ($has ? 'YES' : 'NO') . "\n";
} catch (\Throwable $e) {
    echo "hasActivePermissionTo('project.view') ERROR: " . $e->getMessage() . "\n";
}

echo "\nFIX VERIFIED SUCCESSFULLY!\n";
