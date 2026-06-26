<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;
use Spatie\Permission\Traits\HasRoles;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable, HasRoles, SoftDeletes;

    /**
     * V0.5.2 修: Sanctum HasApiTokens trait 把 getDefaultGuardName 默认成 sanctum,
     * 但我们的 role/permission 都注册在 web guard, 所以强制覆盖回 web
     * 否则 syncRoles/hasRole 会抛 "no role named X for guard sanctum"
     */
    public function getDefaultGuardName(): string
    {
        return 'web';
    }

    protected $fillable = [
        'name', 'username', 'email', 'phone', 'password', 'avatar',
        'department_id', 'position_id', 'gender', 'id_card', 'status',
        'last_login_at', 'last_login_ip',
    ];

    protected $hidden = ['password', 'remember_token', 'deleted_at'];
    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
        'last_login_at' => 'datetime',
        'status' => \App\Enums\UserStatus::class,
        'gender' => \App\Enums\Gender::class,
    ];

    // ========== 关联关系 ==========

    public function department()
    {
        return $this->belongsTo(Department::class);
    }

    public function position()
    {
        return $this->belongsTo(Position::class);
    }

    public function profile()
    {
        return $this->hasOne(EmployeeProfile::class);
    }

    public function skills()
    {
        // 通过 EmployeeProfile 中转，关联到 SkillTag
        return $this->hasOne(EmployeeProfile::class)->with('skills');
    }

    public function getSkillsAttribute()
    {
        return $this->profile ? $this->profile->skills : collect();
    }

    public function certificates()
    {
        return $this->hasManyThrough(Certificate::class, EmployeeProfile::class);
    }

    public function attendanceRecords()
    {
        return $this->hasMany(AttendanceRecord::class);
    }

    public function managedProjects()
    {
        return $this->hasMany(Project::class, 'manager_id');
    }

    public function projectMemberships()
    {
        return $this->hasMany(ProjectMember::class);
    }

    public function expenseClaims()
    {
        return $this->hasMany(ExpenseClaim::class);
    }

    public function serviceOrdersAssigned()
    {
        return $this->hasMany(ServiceOrder::class, 'assigned_to');
    }

    public function vehicleUsageRequests()
    {
        return $this->hasMany(VehicleUsageRequest::class, 'applicant_id');
    }

    public function notifications()
    {
        return $this->morphMany(Notification::class, 'notifiable')
            ->whereNull('read_at')
            ->orderBy('created_at', 'desc');
    }

    public function allNotifications()
    {
        return $this->morphMany(Notification::class, 'notifiable')
            ->orderBy('created_at', 'desc');
    }

    // ========== 辅助方法 ==========

    public function hasSkill(string $skillName): bool
    {
        return $this->skills()->where('name', $skillName)->exists();
    }

    public function isActive(): bool
    {
        return $this->status === \App\Enums\UserStatus::ACTIVE;
    }

    public function getInitialsAttribute(): string
    {
        return mb_substr($this->name, 0, 1);
    }

    // ========== V0.5.3 临时权限（基于 spatie + expires_at）==========

    /**
     * 用户的「有效角色」关系 — 过滤掉过期的
     * V0.5.3 注意: spatie 的 roles() 关系返回所有（包括过期的），
     * 调用方应改用 activeRoles() / hasActiveRole() / hasActivePermissionTo()，
     * 不要再直接 ->roles 做权限判断。
     */
    public function modelHasRoles()
    {
        return $this->morphMany(\Spatie\Permission\Models\Role::class, 'model', 'model_type', 'model_id')
            ->join('model_has_roles', 'roles.id', '=', 'model_has_roles.role_id')
            ->select('roles.*', 'model_has_roles.expires_at', 'model_has_roles.granted_by', 'model_has_roles.reason');
    }

    /**
     * 当前所有「有效」角色（不过期的）
     * 用于: AuthScope / CheckPermission / v-permission / "我的权限"
     */
    public function activeRoles()
    {
        return \Spatie\Permission\Models\Role::query()
            ->join('model_has_roles', 'roles.id', '=', 'model_has_roles.role_id')
            ->where('model_has_roles.model_type', self::class)
            ->where('model_has_roles.model_id', $this->id)
            ->where(function ($q) {
                $q->whereNull('model_has_roles.expires_at')
                  ->orWhere('model_has_roles.expires_at', '>', now());
            })
            ->select('roles.*', 'model_has_roles.expires_at', 'model_has_roles.granted_by', 'model_has_roles.reason');
    }

    /**
     * 当前所有角色记录（含过期状态）— 管理员查看用
     */
    public function allRoleAssignments()
    {
        return \Spatie\Permission\Models\Role::query()
            ->join('model_has_roles', 'roles.id', '=', 'model_has_roles.role_id')
            ->where('model_has_roles.model_type', self::class)
            ->where('model_has_roles.model_id', $this->id)
            ->select(
                'roles.id', 'roles.name', 'roles.description', 'roles.color',
                'model_has_roles.expires_at',
                'model_has_roles.granted_by',
                'model_has_roles.reason'
            )
            ->orderBy('model_has_roles.expires_at'); // 永久（null）排后面
    }

    public function hasActiveRole(string $roleName): bool
    {
        return $this->activeRoles()->where('roles.name', $roleName)->exists();
    }

    /**
     * 检查权限 — 仅基于有效角色
     * V0.5.3 覆盖 spatie 默认 hasPermissionTo（默认不过滤过期）
     * 用 spatie 自身的 Permission::findByName + roleHasPermission 走 5.0 老路径，
     * 避免 HasPermissions::getPermissionsViaRoles 内置 cache 截胡
     */
    public function hasActivePermissionTo(string $permissionName): bool
    {
        $perm = \Spatie\Permission\Models\Permission::findByName($permissionName, 'web');
        if (!$perm) {
            return false;
        }
        // 取我所有有效角色的 id
        $roleIds = $this->activeRoles()->pluck('roles.id')->all();
        if (empty($roleIds)) {
            return false;
        }
        // 看这些角色里有没有这个权限
        return \Illuminate\Support\Facades\DB::table('role_has_permissions')
            ->where('permission_id', $perm->id)
            ->whereIn('role_id', $roleIds)
            ->exists();
    }

    /**
     * 当前所有有效权限名（去重）
     */
    public function activePermissionNames(): array
    {
        $roleIds = $this->activeRoles()->pluck('roles.id')->all();
        if (empty($roleIds)) {
            return [];
        }
        return \Illuminate\Support\Facades\DB::table('role_has_permissions')
            ->join('permissions', 'permissions.id', '=', 'role_has_permissions.permission_id')
            ->whereIn('role_has_permissions.role_id', $roleIds)
            ->pluck('permissions.name')
            ->unique()
            ->values()
            ->all();
    }
}
