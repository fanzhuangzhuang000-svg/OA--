<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Department;
use App\Models\Position;
use App\Models\SkillTag;
use App\Models\Certificate;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;

class EmployeeController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = User::with([
            'department:id,name',
            'position:id,name,department_id',
            'profile',
            'profile.skills:id,name,color',
            'roles:id,name'
        ]);
        // 默认只显示未禁用的，除非传了 status
        if ($request->filled('status') && in_array($request->status, ['active', 'inactive'], true)) {
            $query->where('status', $request->status);
        } else {
            $query->where('status', 'active');
        }
        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $query->where(function ($q) use ($kw) {
                $q->where('name', 'like', "%{$kw}%")
                  ->orWhere('username', 'like', "%{$kw}%")
                  ->orWhere('phone', 'like', "%{$kw}%")
                  ->orWhere('email', 'like', "%{$kw}%")
                  ->orWhereHas('profile', function ($pq) use ($kw) {
                      $pq->where('employee_no', 'like', "%{$kw}%");
                  });
            });
        }
        if ($request->filled('department_id')) $query->where('department_id', $request->department_id);
        if ($request->filled('position_id'))   $query->where('position_id', $request->position_id);
        $list = $query->orderBy('created_at', 'desc')->paginate($request->per_page ?? 15);
        // 加 is_active 字段（前端习惯用）+ 把 profile.skills 平铺到顶层 skills
        $list->getCollection()->transform(function ($u) {
            $statusValue = $u->status instanceof \BackedEnum ? $u->status->value : $u->status;
            $u->is_active = $statusValue === 'active';
            // 把 profile.skills 平铺为顶层 skills 数组（前端表格要用）
            $u->skills = $u->profile && $u->profile->skills ? $u->profile->skills->map(fn($s) => [
                'id'          => $s->id,
                'name'        => $s->name,
                'color'       => $s->color,
                'pivot'       => $s->pivot ? ['proficiency' => $s->pivot->proficiency] : null,
            ]) : [];
            return $u;
        });
        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'          => 'required|string|max:50',
            'username'      => 'required|string|max:64|unique:users',
            'phone'         => 'nullable|string|max:20|unique:users',
            'email'         => 'nullable|email|max:100|unique:users',
            'password'      => 'required|string|min:6',
            'department_id' => 'nullable|exists:departments,id',
            'position_id'   => 'nullable|exists:positions,id',
            'gender'        => 'nullable|string|max:8',
            'role_id'       => 'nullable|exists:roles,id',
            'hire_date'     => 'nullable|date',
        ]);
        // 不要手动 bcrypt — User 模型 casts 已配 'password' => 'hashed' 自动加密
        $data['status'] = 'active';
        // phone NOT NULL UNIQUE — 不填时生成唯一占位 (限20字符), 避免空串 UNIQUE 冲突
        if (empty($data['phone'])) {
            $data['phone'] = mb_substr('TEL-' . ($data['username'] ?? 'user') . '-' . bin2hex(random_bytes(2)), 0, 20);
        }
        // email nullable UNIQUE — 空串会冲突, 不填时从 data 移除让 DB 用 null 默认值
        if (empty($data['email'] ?? null)) {
            unset($data['email']);
        }
        $roleId = $data['role_id'] ?? null;
        unset($data['role_id']);
        $hireDate = $data['hire_date'] ?? null;
        unset($data['hire_date']);

        $user = User::create($data);
        if ($roleId) {
            $user->roles()->sync([$roleId]);
        }
        // employee_profiles.hire_date / base_salary / salary_allowance / contract_type 都是 NOT NULL
        $user->profile()->create([
            'hire_date'        => $hireDate ?? date('Y-m-d'),
            'employee_no'      => 'EMP' . str_pad((string) $user->id, 5, '0', STR_PAD_LEFT),
            'contract_type'    => 'open',
            'base_salary'      => 0,
            'salary_allowance' => 0,
        ]);
        $user->load(['department', 'position', 'profile', 'roles']);
        return response()->json(['code' => 0, 'message' => '员工已创建', 'data' => $user]);
    }

    public function show(User $user): JsonResponse
    {
        $user->load(['department', 'position', 'profile', 'profile.certificates', 'profile.skills:id,name,color', 'roles:id,name']);
        $statusValue = $user->status instanceof \BackedEnum ? $user->status->value : $user->status;
        $user->is_active = $statusValue === 'active';
        $user->skills = $user->profile && $user->profile->skills ? $user->profile->skills->map(fn($s) => [
            'id'    => $s->id,
            'name'  => $s->name,
            'color' => $s->color,
        ]) : [];
        return response()->json(['code' => 0, 'data' => $user]);
    }

    public function update(Request $request, User $user): JsonResponse
    {
        $data = $request->validate([
            'name'          => 'sometimes|required|string|max:50',
            'phone'         => 'sometimes|nullable|string|max:20|unique:users,phone,' . $user->id,
            'email'         => 'sometimes|nullable|email|max:100|unique:users,email,' . $user->id,
            'department_id' => 'sometimes|nullable|exists:departments,id',
            'position_id'   => 'sometimes|nullable|exists:positions,id',
            'gender'        => 'sometimes|nullable|string|max:8',
            'status'        => 'sometimes|nullable|string|in:active,inactive',
            'is_active'     => 'sometimes|boolean',
            'hire_date'     => 'sometimes|nullable|date',
            'role_id'       => 'sometimes|nullable|exists:roles,id',
        ]);
        $roleId = null;
        if (array_key_exists('role_id', $data)) {
            $roleId = $data['role_id'];
            unset($data['role_id']);
        }
        $hireDate = null;
        if (array_key_exists('hire_date', $data)) {
            $hireDate = $data['hire_date'];
            unset($data['hire_date']);
        }
        if (array_key_exists('is_active', $data)) {
            $data['status'] = $data['is_active'] ? 'active' : 'inactive';
            unset($data['is_active']);
        }
        $user->fill($data)->save();
        if ($roleId !== null) $user->roles()->sync([$roleId]);
        if ($hireDate !== null) {
            $profile = $user->profile ?: $user->profile()->create(['employee_no' => 'EMP' . str_pad((string) $user->id, 5, '0', STR_PAD_LEFT)]);
            $profile->hire_date = $hireDate;
            $profile->save();
        }
        $user->load(['department', 'position', 'profile', 'roles']);
        return response()->json(['code' => 0, 'message' => '员工已更新', 'data' => $user]);
    }

    public function destroy(User $user): JsonResponse
    {
        if ($user->id === 1) {
            return response()->json(['code' => 1001, 'message' => '超级管理员不能删除'], 422);
        }
        $user->update(['status' => 'inactive']);
        // 撤销所有 token 强制下线
        $user->tokens()->delete();
        return response()->json(['code' => 0, 'message' => '员工已离职']);
    }

    /**
     * 重置员工密码 — POST /api/users/{user}/reset-password
     * 默认重置为 123456，调用方可传 password 自定义
     */
    public function resetPassword(Request $request, User $user): JsonResponse
    {
        $data = $request->validate([
            'password' => 'nullable|string|min:6|max:64',
        ]);
        $newPwd = $data['password'] ?? '123456';
        $user->update(['password' => $newPwd]); // casts:password => hashed 自动加密
        // 撤销 token 强制重新登录
        $user->tokens()->delete();
        return response()->json([
            'code'    => 0,
            'message' => '密码已重置',
            'data'    => ['id' => $user->id, 'username' => $user->username, 'password' => $newPwd],
        ]);
    }

    // =================== 部门管理 ===================

    /**
     * 部门列表（整棵树 — 平铺给前端）
     * GET /api/employees/departments
     */
    public function departments(Request $request): JsonResponse
    {
        $depts = Cache::remember('departments:all', 300, function () {
            return Department::with(['children', 'manager:id,name,username', 'users:id,department_id'])
                ->orderBy('sort_order')
                ->get()
                ->map(function (Department $d) {
                    $count = $d->users->count();
                    foreach ($d->children as $c) {
                        $count += $c->users->count();
                    }
                    return [
                        'id'          => $d->id,
                        'name'        => $d->name,
                        'parent_id'   => $d->parent_id,
                        'manager_id'  => $d->manager_id,
                        'manager'     => $d->manager?->name,
                        'sort_order'  => $d->sort_order,
                        'status'      => $d->status,
                        'description' => $d->description ?? '',
                        'count'       => $count,
                    ];
                })->values();
        });
        return response()->json(['code' => 0, 'data' => $depts]);
    }

    public function storeDepartment(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'        => 'required|string|max:64',
            'parent_id'   => 'nullable|exists:departments,id',
            'manager_id'  => 'nullable|exists:users,id',
            'sort_order'  => 'nullable|integer|min:0|max:9999',
            'description' => 'nullable|string|max:255',
        ]);
        $data['status'] = 'active';
        Cache::forget('departments:all');
        $dept = Department::create($data);
        return response()->json(['code' => 0, 'message' => '部门已创建', 'data' => $dept]);
    }

    public function updateDepartment(Request $request, Department $department): JsonResponse
    {
        $data = $request->validate([
            'name'        => 'sometimes|required|string|max:64',
            'parent_id'   => 'sometimes|nullable|exists:departments,id',
            'manager_id'  => 'sometimes|nullable|exists:users,id',
            'sort_order'  => 'sometimes|nullable|integer|min:0|max:9999',
            'description' => 'sometimes|nullable|string|max:255',
        ]);
        // 防呆：不能把 parent 设为自己的子孙
        if (! empty($data['parent_id'])) {
            $cur = Department::find($data['parent_id']);
            while ($cur) {
                if ($cur->id === $department->id) {
                    return response()->json(['code' => 1001, 'message' => '不能将部门的上级设为自己或其子孙'], 422);
                }
                $cur = $cur->parent;
            }
        }
        Cache::forget('departments:all');
        $department->fill($data)->save();
        return response()->json(['code' => 0, 'message' => '部门已更新', 'data' => $department]);
    }

    public function destroyDepartment(Department $department): JsonResponse
    {
        if ($department->id === 1) {
            return response()->json(['code' => 1001, 'message' => '根部门不能删除'], 422);
        }
        $childCnt = Department::where('parent_id', $department->id)->count();
        if ($childCnt > 0) {
            return response()->json(['code' => 1002, 'message' => "部门「{$department->name}」下还有 {$childCnt} 个子部门，请先处理"], 422);
        }
        $userCnt = User::where('department_id', $department->id)->count();
        if ($userCnt > 0) {
            return response()->json(['code' => 1003, 'message' => "部门「{$department->name}」下还有 {$userCnt} 名员工，请先调整"], 422);
        }
        Cache::forget('departments:all');
        $department->positions()->delete();
        $department->delete();
        return response()->json(['code' => 0, 'message' => '部门已删除']);
    }

    // =================== 岗位管理 ===================

    public function positions(Request $request): JsonResponse
    {
        $positions = Cache::remember('positions:all', 300, function () {
            return Position::with('department:id,name')->withCount('users')->orderBy('sort_order')->get()
                ->map(function (Position $p) {
                    return [
                        'id'            => $p->id,
                        'name'          => $p->name,
                        'department_id' => $p->department_id,
                        'department'    => $p->department?->name,
                        'level'         => $p->level,
                        'count'         => $p->users_count,
                        'description'   => $p->description,
                        'sort_order'    => $p->sort_order,
                        'status'        => $p->status,
                    ];
                });
        });
        return response()->json(['code' => 0, 'data' => $positions]);
    }

    public function storePosition(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'          => 'required|string|max:64',
            'department_id' => 'required|exists:departments,id',
            'level'         => 'nullable|string|max:50',
            'description'   => 'nullable|string|max:255',
            'sort_order'    => 'nullable|integer|min:0|max:9999',
        ]);
        $data['status'] = 'active';
        if (empty($data['level'])) {
            $data['level'] = 'P5';
        }
        Cache::forget('positions:all');
        $pos = Position::create($data);
        return response()->json(['code' => 0, 'message' => '岗位已创建', 'data' => $pos]);
    }

    public function updatePosition(Request $request, Position $position): JsonResponse
    {
        $data = $request->validate([
            'name'          => 'sometimes|required|string|max:64',
            'department_id' => 'sometimes|required|exists:departments,id',
            'level'         => 'sometimes|nullable|string|max:50',
            'description'   => 'sometimes|nullable|string|max:255',
            'sort_order'    => 'sometimes|nullable|integer|min:0|max:9999',
        ]);
        Cache::forget('positions:all');
        $position->fill($data)->save();
        return response()->json(['code' => 0, 'message' => '岗位已更新', 'data' => $position]);
    }

    public function destroyPosition(Position $position): JsonResponse
    {
        $userCnt = User::where('position_id', $position->id)->count();
        if ($userCnt > 0) {
            return response()->json(['code' => 1001, 'message' => "岗位「{$position->name}」下还有 {$userCnt} 名员工，请先调整"], 422);
        }
        Cache::forget('positions:all');
        $position->delete();
        return response()->json(['code' => 0, 'message' => '岗位已删除']);
    }

    // =================== 技能标签 ===================

    public function skills(Request $request): JsonResponse
    {
        $tags = SkillTag::withCount('employees')->orderBy('sort_order')->get();
        return response()->json(['code' => 0, 'data' => $tags]);
    }

    public function storeSkill(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'        => 'required|string|max:32|unique:skill_tags',
            'category'    => 'nullable|string|in:install,debug,network,cloud,maintain,other',
            'color'       => 'nullable|string|max:7',
            'description' => 'nullable|string|max:255',
        ]);
        $data['category'] = $data['category'] ?? 'other';
        $data['color']    = $data['color']    ?? '#409EFF';
        $tag = SkillTag::create($data);
        return response()->json(['code' => 0, 'message' => '技能已创建', 'data' => $tag]);
    }

    public function updateSkill(Request $request, SkillTag $skillTag): JsonResponse
    {
        $data = $request->validate([
            'name'        => 'sometimes|required|string|max:32|unique:skill_tags,name,' . $skillTag->id,
            'category'    => 'sometimes|nullable|string|in:install,debug,network,cloud,maintain,other',
            'color'       => 'sometimes|nullable|string|max:7',
            'description' => 'sometimes|nullable|string|max:255',
        ]);
        $skillTag->fill($data)->save();
        return response()->json(['code' => 0, 'message' => '技能已更新', 'data' => $skillTag]);
    }

    public function destroySkill(SkillTag $skillTag): JsonResponse
    {
        $empCnt = $skillTag->employees()->count();
        if ($empCnt > 0) {
            $skillTag->employees()->detach();
        }
        $skillTag->delete();
        return response()->json([
            'code'    => 0,
            'message' => '技能已删除' . ($empCnt > 0 ? "，已解绑 {$empCnt} 名员工" : ''),
        ]);
    }

    // 给员工绑定技能
    public function attachSkill(Request $request, SkillTag $skillTag): JsonResponse
    {
        $data = $request->validate([
            'user_id'     => 'required|exists:users,id',
            'proficiency' => 'nullable|in:beginner,intermediate,advanced,expert',
        ]);
        $user = User::findOrFail($data['user_id']);
        $proficiency = $data['proficiency'] ?? 'intermediate';
        // 拿到或创建 profile
        $profile = $user->profile ?: $user->profile()->create([
            'employee_no'      => 'EMP' . str_pad((string) $user->id, 5, '0', STR_PAD_LEFT),
            'hire_date'        => date('Y-m-d'),
            'contract_type'    => 'open',
            'base_salary'      => 0,
            'salary_allowance' => 0,
        ]);
        $profile->skills()->syncWithoutDetaching([
            $skillTag->id => ['proficiency' => $proficiency],
        ]);
        return response()->json(['code' => 0, 'message' => '技能已绑定']);
    }

    // 给员工解绑技能
    public function detachSkill(Request $request, SkillTag $skillTag): JsonResponse
    {
        $data = $request->validate([
            'user_id' => 'required|exists:users,id',
        ]);
        $user = User::findOrFail($data['user_id']);
        $profile = $user->profile;
        if ($profile) {
            $profile->skills()->detach($skillTag->id);
        }
        return response()->json(['code' => 0, 'message' => '技能已解绑']);
    }

    // 列出某员工的技能
    public function userSkills(Request $request, User $user): JsonResponse
    {
        $profile = $user->profile()->with('skills')->first();
        $skills = $profile ? $profile->skills : collect();
        return response()->json(['code' => 0, 'data' => $skills]);
    }

    public function import(Request $request): JsonResponse
    {
        $request->validate(['file' => 'required|file|mimes:csv,xlsx,xls|max:10240']);
        $file = $request->file('file');
        $success = 0; $failed = 0; $errors = [];
        if (strtolower($file->getClientOriginalExtension()) !== 'csv') {
            return response()->json(['code' => 1001, 'message' => '请使用 CSV 格式导入'], 422);
        }
        $rows = [];
        if (($h = fopen($file->getRealPath(), 'r')) !== false) {
            $bom = fread($h, 3);
            if ($bom !== "\xEF\xBB\xBF") rewind($h);
            while (($r = fgetcsv($h)) !== false) $rows[] = $r;
            fclose($h);
        }
        foreach (array_slice($rows, 1) as $idx => $r) {
            if (empty($r[0]) || empty($r[1])) { $failed++; continue; }
            try {
                $user = User::create([
                    'name'          => trim($r[0]),
                    'username'      => trim($r[1]),
                    'password'      => trim($r[2] ?? '123456'),  // User casts 自动 hash
                    'phone'         => !empty(trim($r[5] ?? '')) ? trim($r[5]) : ('TEL-IMPORT-' . bin2hex(random_bytes(3))),
                    'email'         => $r[6] ?? null,
                    'department_id' => is_numeric($r[3] ?? null) ? (int) $r[3] : null,
                    'position_id'   => is_numeric($r[4] ?? null) ? (int) $r[4] : null,
                    'status'        => 'active',
                ]);
                $user->profile()->create([
                    'hire_date'        => !empty($r[7]) ? $r[7] : date('Y-m-d'),
                    'employee_no'      => 'EMP' . str_pad((string) $user->id, 5, '0', STR_PAD_LEFT),
                    'contract_type'    => 'open',
                    'base_salary'      => 0,
                    'salary_allowance' => 0,
                ]);
                $success++;
            } catch (\Throwable $e) {
                $failed++;
                $errors[] = "第 " . ($idx + 2) . " 行: " . $e->getMessage();
            }
        }
        return response()->json(['code' => 0, 'data' => compact('success', 'failed', 'errors')]);
    }

    // =================== 证书 ===================

    public function certificates(Request $request): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => Certificate::with('profile.user')->orderBy('expire_date')->get()]);
    }
}
