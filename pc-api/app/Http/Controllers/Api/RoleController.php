<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

class RoleController extends Controller
{
    /**
     * 角色列表（分页 + 搜索）
     */
    public function index(Request $request): JsonResponse
    {
        $query = Role::query()->with('permissions:id,name');

        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $query->where(function ($q) use ($kw) {
                $q->where('name', 'like', "%{$kw}%")
                  ->orWhere('description', 'like', "%{$kw}%");
            });
        }

        $perPage = (int) ($request->per_page ?? 20);
        $page = $query->orderBy('id')->paginate($perPage);

        // 注入 memberCount / permCount / createTime / color 给前端表格
        $userCounts = DB::table('model_has_roles')
            ->select('role_id', DB::raw('COUNT(*) as cnt'))
            ->where('model_type', 'App\\Models\\User')
            ->groupBy('role_id')
            ->pluck('cnt', 'role_id');

        $data = collect($page->items())->map(function (Role $role) use ($userCounts) {
            return [
                'id'           => $role->id,
                'name'         => $role->name,
                'description'  => $role->description ?? '',
                'color'        => $role->color ?? '#0C447C',
                'memberCount'  => (int) ($userCounts[$role->id] ?? 0),
                'permCount'    => $role->permissions->count(),
                'createTime'   => $role->created_at?->format('Y-m-d H:i:s'),
                'permissionNames' => $role->permissions->pluck('name'),
            ];
        });

        return response()->json([
            'code' => 0,
            'data' => [
                'data' => $data,
                'total' => $page->total(),
                'per_page' => $page->perPage(),
                'current_page' => $page->currentPage(),
                'last_page' => $page->lastPage(),
            ],
        ]);
    }

    /**
     * 角色详情
     */
    public function show(Role $role): JsonResponse
    {
        $role->load('permissions:id,name');
        return response()->json([
            'code' => 0,
            'data' => [
                'id'          => $role->id,
                'name'        => $role->name,
                'description' => $role->description,
                'color'       => $role->color ?? '#0C447C',
                'permissions' => $role->permissions->pluck('name'),
                'createTime'  => $role->created_at?->format('Y-m-d H:i:s'),
            ],
        ]);
    }

    /**
     * 创建角色
     */
    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'         => ['required', 'string', 'max:64', Rule::unique('roles', 'name')->where('guard_name', 'web')],
            'description'  => ['nullable', 'string', 'max:255'],
            'color'        => ['nullable', 'string', 'max:16'],
            'permissions'  => ['array'],
            'permissions.*' => ['string', 'exists:permissions,name'],
        ]);

        $role = Role::create([
            'name'        => $data['name'],
            'guard_name'  => 'web',
            'description' => $data['description'] ?? null,
            'color'       => $data['color'] ?? '#0C447C',
        ]);

        if (!empty($data['permissions'])) {
            $role->syncPermissions($data['permissions']);
        }

        return response()->json(['code' => 0, 'message' => '角色已创建', 'data' => ['id' => $role->id]]);
    }

    /**
     * 更新角色
     */
    public function update(Request $request, Role $role): JsonResponse
    {
        $data = $request->validate([
            'name'         => ['sometimes', 'required', 'string', 'max:64', Rule::unique('roles', 'name')->where('guard_name', 'web')->ignore($role->id)],
            'description'  => ['nullable', 'string', 'max:255'],
            'color'        => ['nullable', 'string', 'max:16'],
            'permissions'  => ['array'],
            'permissions.*' => ['string', 'exists:permissions,name'],
        ]);

        $role->fill([
            'name'        => $data['name']        ?? $role->name,
            'description' => array_key_exists('description', $data) ? $data['description'] : $role->description,
            'color'       => $data['color']       ?? $role->color,
        ])->save();

        if (array_key_exists('permissions', $data)) {
            $role->syncPermissions($data['permissions']);
        }

        return response()->json(['code' => 0, 'message' => '角色已更新']);
    }

    /**
     * 删除角色（已分配用户的角色不能删）
     */
    public function destroy(Role $role): JsonResponse
    {
        // 引用计数
        $cnt = DB::table('model_has_roles')
            ->where('role_id', $role->id)
            ->where('model_type', 'App\\Models\\User')
            ->count();
        if ($cnt > 0) {
            return response()->json(['code' => 1001, 'message' => "角色「{$role->name}」已分配给 {$cnt} 个用户，请先解除绑定"], 422);
        }
        $role->delete();
        return response()->json(['code' => 0, 'message' => '角色已删除']);
    }

    /**
     * 同步角色的权限 (含继承链自动同步)
     * POST /api/roles/{role}/permissions
     * body: { permissions: ["perm.name1", "perm.name2"] }
     */
    public function assignPermissions(Request $request, Role $role): JsonResponse
    {
        $data = $request->validate([
            'permissions'   => ['array'],
            'permissions.*' => ['string', 'exists:permissions,name'],
        ]);
        $perms = $data['permissions'] ?? [];

        // V0.5.2 业务侧赋权限时, 自动同步继承链
        //   1) 当前角色 syncPermissions(perms)
        //   2) 找到继承自本角色的"子角色" (通过 InheritanceMap 静态配置), 把 perms 也加给子角色
        $role->syncPermissions($perms);
        \App\Support\PermissionInheritance::propagateToChildren($role->name, $perms);

        return response()->json([
            'code' => 0,
            'message' => '权限配置已保存',
            'data' => ['count' => count($perms)],
        ]);
    }

    /**
     * 业务权限树（来自业务模块字典，与前端 hardcoded 树一一对应）
     * GET /api/permissions/tree
     */
    public function permissionTree(): JsonResponse
    {
        $tree = $this->buildPermissionTree();
        return response()->json(['code' => 0, 'data' => $tree]);
    }

    /**
     * V0.5.2 角色权限矩阵
     * GET /api/roles/matrix
     * 返回: { roles:[name,...], permissions:[{module,name,label},...], matrix:{role_name:[perm_name,...]}, inheritance:Graph }
     */
    public function matrix(): JsonResponse
    {
        $roles = Role::where('guard_name', 'web')->orderBy('id')->get(['id', 'name', 'description', 'color']);

        // 全部权限按 module 分组
        $perms = Permission::orderBy('module')->orderBy('id')
            ->get(['id', 'name', 'module', 'description', 'display_name']);

        // 角色 -> 权限集合
        $roleMatrix = [];
        foreach ($roles as $r) {
            $p = DB::table('role_has_permissions')
                ->join('permissions', 'permissions.id', '=', 'role_has_permissions.permission_id')
                ->where('role_has_permissions.role_id', $r->id)
                ->pluck('permissions.name')
                ->all();
            sort($p);
            $roleMatrix[$r->name] = $p;
        }

        return response()->json([
            'code' => 0,
            'data' => [
                'roles' => $roles->map(fn($r) => [
                    'id'          => $r->id,
                    'name'        => $r->name,
                    'description' => $r->description,
                    'color'       => $r->color ?? '#0C447C',
                ])->all(),
                'permissions' => $perms->map(fn($p) => [
                    'id'           => $p->id,
                    'name'         => $p->name,
                    'module'       => $p->module,
                    'label'        => $p->description ?? $p->name,
                    'display_name' => $p->display_name,
                ])->all(),
                'matrix'      => $roleMatrix,
                'inheritance' => \App\Support\PermissionInheritance::getGraph(),
            ],
        ]);
    }

    /**
     * V0.5.2 角色继承图
     * GET /api/permissions/inheritance
     */
    public function inheritanceGraph(): JsonResponse
    {
        return response()->json([
            'code' => 0,
            'data' => \App\Support\PermissionInheritance::getGraph(),
        ]);
    }

    /**
     * V0.5.0 L1 前端用 — 当前登录用户的所有权限 name 列表
     * GET /api/permissions/my
     */
    public function myPermissions(): JsonResponse
    {
        $user = auth()->user();
        if (!$user) {
            return response()->json(['code' => 401, 'message' => '未认证'], 401);
        }
        // admin 直接返所有权限 (前端不显示 hidden menu)
        $userRoles = [];
        try {
            $userRoles = $user->roles->pluck('name')->all();
        } catch (\Throwable $e) {
            // ignore
        }
        if (in_array('admin', $userRoles, true)) {
            $list = Permission::orderBy('module')->orderBy('id')->get(['name', 'module', 'display_name', 'description'])
                ->map(fn($p) => [
                    'name' => $p->name,
                    'module' => $p->module,
                    'label' => $p->display_name ?? $p->description ?? $p->name,
                ]);
            return response()->json(['code' => 0, 'data' => $list, 'roles' => $userRoles]);
        }

        $list = $user->getAllPermissions()->map(fn($p) => [
            'name' => $p->name,
            'module' => $p->module ?? '',
            'label' => $p->display_name ?? $p->description ?? $p->name,
        ])->values();

        return response()->json(['code' => 0, 'data' => $list, 'roles' => $userRoles]);
    }

    /**
     * 所有权限（平铺列表）
     */
    public function permissionIndex(): JsonResponse
    {
        $list = Permission::orderBy('id')->get(['id', 'name', 'module', 'description'])->map(function ($p) {
            return [
                'id'          => $p->id,
                'name'        => $p->name,
                'label'       => $p->description ?? $p->name,
                'module'      => $p->module,
            ];
        });
        return response()->json(['code' => 0, 'data' => $list]);
    }

    /**
     * 业务权限字典（与数据库 permissions.name 一一对应）
     * name 必须 = permissions.name（英文点号），label 给前端展示用
     */
    private function buildPermissionTree(): array
    {
        $modules = [
            '系统管理' => [
                ['name' => 'system.config',   'label' => '系统参数配置'],
                ['name' => 'system.log',      'label' => '系统日志查看'],
                ['name' => 'system.backup',   'label' => '数据备份管理'],
                ['name' => 'system.role',     'label' => '角色权限管理'],
            ],
            '员工管理' => [
                ['name' => 'employee.view',   'label' => '员工列表查看'],
                ['name' => 'employee.create', 'label' => '员工信息编辑'],
                ['name' => 'employee.org',    'label' => '组织架构管理'],
                ['name' => 'employee.skill',  'label' => '技能标签管理'],
            ],
            '考勤管理' => [
                ['name' => 'attendance.view',    'label' => '考勤总览'],
                ['name' => 'attendance.record',  'label' => '打卡记录查看'],
                ['name' => 'attendance.leave',   'label' => '请假审批'],
                ['name' => 'attendance.overtime','label' => '加班审批'],
                ['name' => 'attendance.report',  'label' => '考勤报表'],
            ],
            '项目管理' => [
                ['name' => 'project.view',   'label' => '项目列表查看'],
                ['name' => 'project.create', 'label' => '项目创建编辑'],
                ['name' => 'project.assign', 'label' => '任务分配管理'],
                ['name' => 'project.report', 'label' => '项目报表'],
            ],
            '客户管理' => [
                ['name' => 'customer.view',  'label' => '客户列表查看'],
                ['name' => 'customer.edit',  'label' => '客户信息编辑'],
                ['name' => 'customer.map',   'label' => '客户分布地图'],
            ],
            '财务管理' => [
                ['name' => 'finance.view',     'label' => '财务概览'],
                ['name' => 'finance.receive',  'label' => '应收账款'],
                ['name' => 'finance.pay',      'label' => '应付账款'],
                ['name' => 'finance.approve',  'label' => '报销审批'],
            ],
            '库存管理' => [
                ['name' => 'inventory.view',     'label' => '库存总览'],
                ['name' => 'inventory.transfer', 'label' => '出入库记录'],
                ['name' => 'inventory.alert',    'label' => '库存预警设置'],
            ],
            '审批流程' => [
                ['name' => 'approval.template', 'label' => '流程模板管理'],
                ['name' => 'approval.mine',     'label' => '我的审批'],
                ['name' => 'approval.config',   'label' => '审批配置'],
            ],
        ];
        $tree = [];
        foreach ($modules as $mod => $perms) {
            $children = [];
            foreach ($perms as $p) {
                $children[] = [
                    'id'    => $p['name'],
                    'name'  => $p['name'],
                    'label' => $p['label'],
                ];
            }
            $tree[] = [
                'id'       => $mod,
                'name'     => $mod,
                'label'    => $mod,
                'children' => $children,
            ];
        }
        return $tree;
    }

    // =============================================================
    // V0.5.1 用户-角色管理 (admin 限定)
    // =============================================================

    /**
     * 改用户角色
     * PUT /api/users/{user}/roles
     * body: { roles: ["admin","finance"] }  — 替换用户所有角色
     */
    public function usersSyncRoles(Request $request, \App\Models\User $user): JsonResponse
    {
        $roleNames = (array) $request->input('roles', []);
        // 校验所有 role name 都存在
        $valid = \Spatie\Permission\Models\Role::whereIn('name', $roleNames)->pluck('name')->all();
        if (count($valid) !== count($roleNames)) {
            $invalid = array_diff($roleNames, $valid);
            return response()->json([
                'code' => 422,
                'message' => '无效角色: ' . implode(',', $invalid),
            ], 422);
        }
        // 记录原角色 (audit 用)
        $oldRoles = $user->roles->pluck('name')->sort()->values()->all();
        $newRoles = collect($valid)->sort()->values()->all();
        // V0.5.2 修: User::getDefaultGuardName 已返回 'web', 直接 syncRoles 即可
        $user->syncRoles($valid);
        $freshRoles = $user->fresh()->roles->pluck('name')->all();

        // V0.5.2: 写 audit log (action=role_changed)
        if ($oldRoles !== $newRoles) {
            \App\Support\Audit::write('role_changed', sprintf(
                '用户「%s」(%d) 角色变更: %s → %s',
                $user->username, $user->id,
                implode(',', $oldRoles) ?: '(无)',
                implode(',', $newRoles) ?: '(无)'
            ), [
                'target_user_id' => $user->id,
                'target_username' => $user->username,
                'old_roles' => $oldRoles,
                'new_roles' => $newRoles,
            ]);
        }

        return response()->json([
            'code' => 0,
            'data' => [
                'id'    => $user->id,
                'roles' => $freshRoles,
            ],
            'message' => '已更新',
        ]);
    }

    /**
     * 一键赋角色 — 给多个用户批量赋同一个角色
     * POST /api/users/bulk-assign-role
     * body: { user_ids: [1,2,3], role: "manager" }
     */
    public function usersBulkAssignRole(Request $request): JsonResponse
    {
        $userIds = (array) $request->input('user_ids', []);
        $roleName = (string) $request->input('role', '');
        if (!$roleName || !Role::where('name', $roleName)->exists()) {
            return response()->json(['code' => 422, 'message' => '角色不存在'], 422);
        }
        $count = 0;
        foreach ($userIds as $uid) {
            $u = \App\Models\User::find($uid);
            if ($u) {
                $u->assignRole($roleName);
                $count++;
            }
        }
        return response()->json([
            'code' => 0,
            'data' => ['affected' => $count],
            'message' => "已为 {$count} 个用户分配角色「{$roleName}」",
        ]);
    }

    // =============================================================
    // V0.5.3 临时角色授权
    // =============================================================

    /**
     * 查一个用户的所有角色记录（含过期/永久/grant 信息）
     * GET /api/users/{user}/roles
     */
    public function usersListRoles(Request $request, \App\Models\User $user): JsonResponse
    {
        $rows = $user->allRoleAssignments()
            ->get()
            ->map(function ($r) {
                $expires = $r->expires_at ? \Carbon\Carbon::parse($r->expires_at) : null;
                $isExpired = $expires && $expires->isPast();
                $isPermanent = $expires === null;
                return [
                    'name'        => $r->name,
                    'description' => $r->description,
                    'color'       => $r->color ?? '#0C447C',
                    'expires_at'  => $r->expires_at ? \Carbon\Carbon::parse($r->expires_at)->toDateTimeString() : null,
                    'granted_by'  => $r->granted_by,
                    'reason'      => $r->reason,
                    'status'      => $isExpired ? 'expired' : ($isPermanent ? 'permanent' : 'temporary'),
                    'days_left'   => $expires && !$isExpired ? (int) now()->diffInDays($expires, false) : null,
                ];
            });

        // 注入角色名（前端可能用 role id 转 name）
        return response()->json([
            'code' => 0,
            'data' => [
                'user_id'      => $user->id,
                'username'     => $user->username,
                'assignments'  => $rows->values()->all(),
                'active_count' => $rows->whereIn('status', ['permanent', 'temporary'])->count(),
            ],
        ]);
    }

    /**
     * 给一个用户授临时角色（可批量）
     * POST /api/users/{user}/roles/temporary
     * body:
     *   { assignments: [
     *       { "role": "finance", "expires_at": "2026-07-01 18:00", "reason": "项目借调" },
     *       { "role": "manager", "expires_at": "2026-12-31", "reason": "代理" }
     *     ] }
     * 语义: **替换**所有当前临时角色（永久角色保留）
     */
    public function usersGrantTemporary(Request $request, \App\Models\User $user): JsonResponse
    {
        $data = $request->validate([
            'assignments'                  => 'required|array|min:1',
            'assignments.*.role'            => 'required|string|max:100',
            'assignments.*.expires_at'      => 'required|date|after:now',
            'assignments.*.reason'          => 'nullable|string|max:500',
        ]);

        $grantedBy = $request->user()?->id;
        $oldAssignments = $user->allRoleAssignments()
            ->whereNotNull('model_has_roles.expires_at')
            ->get(['roles.name as name', 'model_has_roles.expires_at', 'model_has_roles.reason'])
            ->map(fn ($r) => (array) $r)
            ->all();

        $entries = [];
        foreach ($data['assignments'] as $a) {
            // 校验 role 存在
            $exists = Role::where('name', $a['role'])->where('guard_name', 'web')->exists();
            if (!$exists) {
                return response()->json([
                    'code' => 422,
                    'message' => "角色不存在: {$a['role']}",
                ], 422);
            }
            $entries[] = [
                'name'       => $a['role'],
                'expires_at' => \Carbon\Carbon::parse($a['expires_at']),
                'reason'     => $a['reason'] ?? null,
            ];
        }

        $added = \App\Support\TemporaryRole::syncTemporary($user, $entries, $grantedBy);

        // audit
        \App\Support\Audit::write('temporary_role_granted', sprintf(
            '用户「%s」(%d) 临时角色变更: %s → %s',
            $user->username, $user->id,
            $oldAssignments ? implode(',', array_column($oldAssignments, 'name')) : '(无)',
            implode(',', array_column($entries, 'name'))
        ), [
            'target_user_id' => $user->id,
            'target_username' => $user->username,
            'old_assignments' => $oldAssignments,
            'new_assignments' => array_map(fn ($e) => [
                'role' => $e['name'],
                'expires_at' => $e['expires_at']->toDateTimeString(),
                'reason' => $e['reason'],
            ], $entries),
            'granted_by' => $grantedBy,
        ]);

        return response()->json([
            'code'    => 0,
            'data'    => [
                'user_id'    => $user->id,
                'added'      => $added,
                'assignments' => $user->fresh()->allRoleAssignments()
                    ->get()
                    ->map(fn ($r) => [
                        'name'       => $r->name,
                        'expires_at' => $r->expires_at,
                        'reason'     => $r->reason,
                    ])
                    ->values()
                    ->all(),
            ],
            'message' => '已分配临时角色',
        ]);
    }

    /**
     * 撤销一个用户的一个角色（永久/临时都删）
     * DELETE /api/users/{user}/roles/{role}
     * 注: {role} 是 role name 字符串（前端按 name 识别），不是数字 id
     */
    public function usersRevokeRole(Request $request, \App\Models\User $user, string $role): JsonResponse
    {
        $exists = Role::where('name', $role)->where('guard_name', 'web')->exists();
        if (!$exists) {
            return response()->json(['code' => 404, 'message' => "角色不存在: {$role}"], 404);
        }

        $revokedBy = $request->user()?->id;
        $reason = (string) $request->input('reason', '');
        $ok = \App\Support\TemporaryRole::revoke($user, $role, $reason ?: null, $revokedBy);
        if (!$ok) {
            return response()->json(['code' => 404, 'message' => "用户未持有角色「{$role}」"], 404);
        }

        \App\Support\Audit::write('role_revoked', sprintf(
            '撤销用户「%s」(%d) 的角色「%s」%s',
            $user->username, $user->id, $role,
            $reason ? "（理由: {$reason}）" : ''
        ), [
            'target_user_id' => $user->id,
            'target_username' => $user->username,
            'role' => $role,
            'reason' => $reason,
            'revoked_by' => $revokedBy,
        ]);

        return response()->json([
            'code'    => 0,
            'message' => "已撤销角色「{$role}」",
        ]);
    }

    /**
     * 查用户当前有效角色 + 有效权限
     * GET /api/users/{user}/roles/active
     */
    public function usersActiveRoles(Request $request, \App\Models\User $user): JsonResponse
    {
        $roles = $user->activeRoles()
            ->get(['roles.id', 'roles.name', 'roles.description', 'roles.color', 'model_has_roles.expires_at', 'model_has_roles.reason'])
            ->map(fn ($r) => [
                'id'          => $r->id,
                'name'        => $r->name,
                'description' => $r->description,
                'color'       => $r->color ?? '#0C447C',
                'expires_at'  => $r->expires_at ? \Carbon\Carbon::parse($r->expires_at)->toDateTimeString() : null,
                'reason'      => $r->reason,
            ]);

        $permissions = $user->activePermissionNames();

        return response()->json([
            'code' => 0,
            'data' => [
                'user_id'     => $user->id,
                'username'    => $user->username,
                'roles'       => $roles,
                'permissions' => $permissions,
            ],
        ]);
    }

    /**
     * 管理员看 7 天内即将过期的角色
     * GET /api/roles/expiring?within_days=7
     */
    public function expiringSoon(Request $request): JsonResponse
    {
        $days = (int) $request->input('within_days', 7);
        $rows = \App\Support\TemporaryRole::expiringSoon($days);
        return response()->json([
            'code' => 0,
            'data' => [
                'within_days' => $days,
                'count'       => count($rows),
                'rows'        => $rows,
            ],
        ]);
    }
}
