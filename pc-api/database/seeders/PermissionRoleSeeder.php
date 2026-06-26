<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

/**
 * V0.5.0 — 授权中心 Seeder
 *
 * 数据结构:
 *  - 4 个核心角色 (admin/finance/manager/user)  ← AuthScope 直接读
 *  - 51 个细粒度权限 (按 module.action 命名)
 *  - 4 角色默认权限矩阵
 *  - 19 个 demo 用户的 role 绑定
 */
class PermissionRoleSeeder extends Seeder
{
    /**
     * V0.5.0 — 业务权限字典 (module.action 英文, 与已有 51 个 permission 对齐)
     * 前端 role/Index.vue 树用中文 label, 但 DB name 是英文点号
     */
    private array $modules = [
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

    public function run(): void
    {
        // 1) 清空 + 重建 permissions（保留 roles / model_has_* 关系）
        Permission::query()->delete();

        // 2) 写权限 (英文 name + 中文 label + display_name)
        $allPerms = [];
        foreach ($this->modules as $mod => $perms) {
            foreach ($perms as $p) {
                $perm = Permission::create([
                    'name'         => $p['name'],
                    'guard_name'   => 'web',
                    'module'       => $mod,
                    'description'  => $p['label'],
                    'display_name' => $p['label'],
                ]);
                $allPerms[] = $perm->name;
            }
        }

        // 3) 4 核心角色 + 默认权限矩阵
        $presets = [
            'admin' => [
                'description' => '系统最高权限，所有模块',
                'color' => '#A32D2D',
                'perms' => $allPerms, // 全部
            ],
            'finance' => [
                'description' => '财务模块 + 全局查看',
                'color' => '#534AB7',
                'perms' => array_values(array_filter($allPerms, fn($n) =>
                    str_starts_with($n, 'finance.') || str_starts_with($n, 'approval.')
                )),
            ],
            'user' => [
                'description' => '普通员工：考勤+个人',
                'color' => '#909399',
                // user 是基础角色 - 给自己独有的 attendance.* + approval.mine
                // manager/finance/admin 通过继承链自动获得 user 权限
                'perms' => array_values(array_filter($allPerms, fn($n) =>
                    str_starts_with($n, 'attendance.') ||
                    str_starts_with($n, 'approval.mine')
                )),
            ],
            'manager' => [
                'description' => '项目经理/部门经理（继承 user）',
                'color' => '#0C447C',
                // manager 自己独有的: project.* / employee.* / approval.template
                // attendance.* / approval.mine 通过继承 user 自动获得
                'perms' => array_values(array_filter($allPerms, fn($n) =>
                    str_starts_with($n, 'project.') ||
                    str_starts_with($n, 'employee.') ||
                    $n === 'approval.template'
                )),
            ],
            'finance' => [
                'description' => '财务（继承 user）',
                'color' => '#534AB7',
                // finance 自己独有的: finance.*
                'perms' => array_values(array_filter($allPerms, fn($n) =>
                    str_starts_with($n, 'finance.')
                )),
            ],
            'admin' => [
                'description' => '系统最高权限（继承 manager+finance）',
                'color' => '#A32D2D',
                // admin 自己独有的: system.* / approval.config
                'perms' => array_values(array_filter($allPerms, fn($n) =>
                    str_starts_with($n, 'system.') ||
                    $n === 'approval.config'
                )),
            ],
        ];

        // V0.5.1 继承链 (spatie Role 继承模型):
        //   admin    > manager, finance  (admin 自动有 manager+finance 的所有权限)
        //   manager  > user
        //   finance  > user
        //   user     > (无)
        // 这样:
        //   - 给 user 加新权限, manager/finance/admin 自动有
        //   - 给 admin 加权限不会污染低层 (admin 自身已有)
        $inheritMap = [
            'manager' => 'user',
            'finance' => 'user',
            'admin'   => 'manager',  // 间接继承 user, finance 通过 manager -> user
        ];
        // admin 也直接继承 finance
        $adminInheritsExtra = ['finance'];

        foreach ($presets as $name => $cfg) {
            $role = Role::updateOrCreate(
                ['name' => $name, 'guard_name' => 'web'],
                ['description' => $cfg['description'], 'color' => $cfg['color']]
            );
            $role->syncPermissions($cfg['perms']);
        }

        // 配置继承关系 (用 spatie 内部表 role_has_permissions 反向; 这里用 model 层方法)
        $managerRole = Role::where('name', 'manager')->where('guard_name', 'web')->first();
        $financeRole = Role::where('name', 'finance')->where('guard_name', 'web')->first();
        $adminRole   = Role::where('name', 'admin')->where('guard_name', 'web')->first();
        $userRole    = Role::where('name', 'user')->where('guard_name', 'web')->first();

        if ($managerRole && $userRole) {
            // 把 manager 没有的 user 权限也写到 role_has_permissions
            $userPerms = $userRole->permissions()->pluck('name')->all();
            $managerPerms = $managerRole->permissions()->pluck('name')->all();
            $missing = array_diff($userPerms, $managerPerms);
            if ($missing) {
                $managerRole->givePermissionTo($missing);
            }
        }
        if ($financeRole && $userRole) {
            $userPerms = $userRole->permissions()->pluck('name')->all();
            $financePerms = $financeRole->permissions()->pluck('name')->all();
            $missing = array_diff($userPerms, $financePerms);
            if ($missing) {
                $financeRole->givePermissionTo($missing);
            }
        }
        if ($adminRole && $managerRole && $financeRole) {
            // admin 继承 manager + finance 的所有权限
            $mgrPerms = $managerRole->permissions()->pluck('name')->all();
            $finPerms = $financeRole->permissions()->pluck('name')->all();
            $adminPerms = $adminRole->permissions()->pluck('name')->all();
            $missing = array_diff(array_unique(array_merge($mgrPerms, $finPerms)), $adminPerms);
            if ($missing) {
                $adminRole->givePermissionTo($missing);
            }
        }

        // 4) 演示用户绑定 (覆盖清理已有绑定, 一对一)
        $bindings = [
            'admin1'    => 'admin',
            'admin'     => 'admin',
            'fin_wu'    => 'finance',
            'fin_zhou'  => 'finance',
            'fin_mgr'   => 'finance',
            'sales_yang'=> 'manager',
            'sales_chen'=> 'manager',
            'sales_mgr' => 'manager',
            'tech_mgr'  => 'manager',
            'proj_mgr'  => 'manager',
            'eng_qian'  => 'user',
            'eng_zhao'  => 'user',
            'eng_sun'   => 'user',
            'zhangsan'  => 'user',
            'lisi'      => 'user',
            'wangwu'    => 'user',
        ];

        foreach ($bindings as $username => $roleName) {
            $user = \App\Models\User::where('username', $username)->first();
            if ($user) {
                // syncRoles 会清掉所有旧绑定, 然后只挂这一个
                $user->syncRoles([$roleName]);
            }
        }

        // 5) 清理: admin1/admin 双绑定 (上面 syncRoles 已清, 此处防万一)
        \Spatie\Permission\Models\Role::where('name', 'UI测试-角色名称')->delete();
    }
}
