<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "=== PERMISSIONS (system.role, project.view) ===\n";
$perms = DB::select('SELECT id, name, guard_name FROM permissions WHERE name IN (?, ?)', ['system.role', 'project.view']);
if (empty($perms)) echo "(NONE FOUND!)\n";
foreach ($perms as $p) echo "ID:{$p->id} name:{$p->name} guard:{$p->guard_name}\n";

echo "\n=== ALL ROLES ===\n";
$roles = DB::select('SELECT id, name, guard_name FROM roles');
foreach ($roles as $r) echo "ID:{$r->id} name:{$r->name} guard:{$r->guard_name}\n";

echo "\n=== ROLE_HAS_PERMISSIONS (system.role, project.view) ===\n";
$rp = DB::select('SELECT r.name as role_name, p.name as perm_name FROM role_has_permissions rp JOIN roles r ON rp.role_id=r.id JOIN permissions p ON rp.permission_id=p.id WHERE p.name IN (?,?)', ['system.role','project.view']);
if (empty($rp)) echo "(NONE!)\n";
foreach ($rp as $row) echo "role:{$row->role_name} -> perm:{$row->perm_name}\n";

echo "\n=== MODEL_HAS_ROLES ===\n";
$mr = DB::select('SELECT mr.model_id, mr.model_type, r.name as role_name, mr.expires_at FROM model_has_roles mr JOIN roles r ON mr.role_id=r.id ORDER BY mr.model_id LIMIT 20');
foreach ($mr as $row) echo "user:{$row->model_id} type:{$row->model_type} role:{$row->role_name} expires:" . ($row->expires_at ?: 'NULL') . "\n";

echo "\n=== USERS ===\n";
$users = DB::select('SELECT id, name, username FROM users LIMIT 10');
foreach ($users as $u) echo "ID:{$u->id} name:{$u->name} username:{$u->username}\n";

echo "\n=== TOKENS=***\n";
$tokens = DB::select('SELECT id, tokenable_type, tokenable_id, name, token FROM personal_access_tokens LIMIT 10');
foreach ($tokens as $t) echo "ID:{$t->id} uid:{$t->tokenable_id} name:{$t->name} token:{$t->token}\n";

echo "\n=== PERMISSION GUARD_NAME ===\n";
$pg = DB::select('SELECT DISTINCT guard_name, COUNT(*) as cnt FROM permissions GROUP BY guard_name');
foreach ($pg as $g) echo "guard:{$g->guard_name} count:{$g->cnt}\n";

echo "\n=== ROLE GUARD_NAME ===\n";
$rg = DB::select('SELECT DISTINCT guard_name, COUNT(*) as cnt FROM roles GROUP BY guard_name');
foreach ($rg as $g) echo "guard:{$g->guard_name} count:{$g->cnt}\n";

echo "\n=== MODEL_TYPE in model_has_roles ===\n";
$mt = DB::select('SELECT DISTINCT model_type, COUNT(*) as cnt FROM model_has_roles GROUP BY model_type');
foreach ($mt as $m) echo "type:{$m->model_type} count:{$m->cnt}\n";
