<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Shift;
use App\Models\ShiftGroup;
use App\Models\ShiftGroupMember;
use App\Models\Schedule;
use App\Models\AttendanceRecord;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class ScheduleController extends Controller
{
    // ========== 班次管理 ==========

    public function listShifts(Request $request): JsonResponse
    {
        $q = Shift::query();
        if ($request->filled('is_active')) $q->where('is_active', $request->boolean('is_active'));
        $shifts = $q->orderBy('sort_order')->orderBy('id')->get();
        return response()->json(['code' => 0, 'data' => $shifts]);
    }

    public function storeShift(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => 'required|string|max:50',
            'code' => 'required|string|max:20|unique:shifts,code',
            'start_time' => 'required|date_format:H:i:s',
            'end_time' => 'required|date_format:H:i:s',
            'late_threshold_minutes' => 'nullable|integer|min:0|max:120',
            'early_leave_threshold_minutes' => 'nullable|integer|min:0|max:120',
            'work_hours' => 'nullable|numeric|min:0|max:24',
            'color' => 'nullable|string|max:20',
            'is_overnight' => 'boolean',
            'is_active' => 'boolean',
            'sort_order' => 'nullable|integer',
            'remark' => 'nullable|string|max:500',
        ]);
        // 自动判断跨夜班
        if (!isset($data['is_overnight'])) {
            $data['is_overnight'] = $data['end_time'] < $data['start_time'];
        }
        $shift = Shift::create($data);
        return response()->json(['code' => 0, 'message' => '班次已创建', 'data' => $shift]);
    }

    public function updateShift(Request $request, Shift $shift): JsonResponse
    {
        $data = $request->validate([
            'name' => 'sometimes|string|max:50',
            'code' => 'sometimes|string|max:20|unique:shifts,code,' . $shift->id,
            'start_time' => 'sometimes|date_format:H:i:s',
            'end_time' => 'sometimes|date_format:H:i:s',
            'late_threshold_minutes' => 'nullable|integer|min:0|max:120',
            'early_leave_threshold_minutes' => 'nullable|integer|min:0|max:120',
            'work_hours' => 'nullable|numeric|min:0|max:24',
            'color' => 'nullable|string|max:20',
            'is_overnight' => 'boolean',
            'is_active' => 'boolean',
            'sort_order' => 'nullable|integer',
            'remark' => 'nullable|string|max:500',
        ]);
        if (isset($data['start_time']) || isset($data['end_time'])) {
            $start = $data['start_time'] ?? $shift->start_time;
            $end   = $data['end_time']   ?? $shift->end_time;
            $data['is_overnight'] = $end < $start;
        }
        $shift->update($data);
        return response()->json(['code' => 0, 'message' => '已更新', 'data' => $shift]);
    }

    public function destroyShift(Shift $shift): JsonResponse
    {
        if ($shift->schedules()->exists()) {
            return response()->json(['code' => 1001, 'message' => '该班次已被排班使用, 不能删除(可停用)'], 422);
        }
        $shift->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }

    // ========== 班组管理 ==========

    public function listGroups(Request $request): JsonResponse
    {
        $groups = ShiftGroup::with(['leader:id,name,username', 'members.user:id,name,username'])
            ->withCount('members')
            ->orderBy('id')
            ->get();
        return response()->json(['code' => 0, 'data' => $groups]);
    }

    public function storeGroup(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => 'required|string|max:50',
            'code' => 'required|string|max:20|unique:shift_groups,code',
            'leader_id' => 'nullable|exists:users,id',
            'color' => 'nullable|string|max:20',
            'description' => 'nullable|string|max:500',
            'is_active' => 'boolean',
        ]);
        $group = ShiftGroup::create($data);
        return response()->json(['code' => 0, 'message' => '班组已创建', 'data' => $group]);
    }

    public function updateGroup(Request $request, ShiftGroup $group): JsonResponse
    {
        $data = $request->validate([
            'name' => 'sometimes|string|max:50',
            'code' => 'sometimes|string|max:20|unique:shift_groups,code,' . $group->id,
            'leader_id' => 'nullable|exists:users,id',
            'color' => 'nullable|string|max:20',
            'description' => 'nullable|string|max:500',
            'is_active' => 'boolean',
        ]);
        $group->update($data);
        return response()->json(['code' => 0, 'message' => '已更新', 'data' => $group]);
    }

    public function destroyGroup(ShiftGroup $group): JsonResponse
    {
        if ($group->members()->exists()) {
            return response()->json(['code' => 1001, 'message' => '班组还有成员, 请先移除'], 422);
        }
        $group->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }

    /**
     * 替换班组所有成员
     * body: { user_ids: [1,2,3] }
     */
    public function syncGroupMembers(Request $request, ShiftGroup $group): JsonResponse
    {
        $data = $request->validate([
            'user_ids' => 'required|array',
            'user_ids.*' => 'exists:users,id',
        ]);
        DB::transaction(function () use ($group, $data) {
            ShiftGroupMember::where('group_id', $group->id)->delete();
            foreach ($data['user_ids'] as $uid) {
                ShiftGroupMember::create([
                    'group_id' => $group->id,
                    'user_id' => $uid,
                    'joined_at' => today(),
                ]);
            }
        });
        return response()->json(['code' => 0, 'message' => '成员已更新 (' . count($data['user_ids']) . ' 人)']);
    }

    public function addGroupMember(Request $request, ShiftGroup $group): JsonResponse
    {
        $data = $request->validate(['user_id' => 'required|exists:users,id']);
        $exists = ShiftGroupMember::where('group_id', $group->id)->where('user_id', $data['user_id'])->exists();
        if ($exists) return response()->json(['code' => 1001, 'message' => '该员工已在班组中'], 422);
        ShiftGroupMember::create(['group_id' => $group->id, 'user_id' => $data['user_id'], 'joined_at' => today()]);
        return response()->json(['code' => 0, 'message' => '已加入班组']);
    }

    public function removeGroupMember(ShiftGroup $group, User $user): JsonResponse
    {
        ShiftGroupMember::where('group_id', $group->id)->where('user_id', $user->id)->delete();
        return response()->json(['code' => 0, 'message' => '已移出班组']);
    }

    // ========== 排班计划 ==========

    /**
     * 排班日历视图: 一段时间范围内所有排班
     * GET /api/schedules?start=2026-06-20&end=2026-06-26
     * 返回: { [date]: [{ user_id, user_name, shift_id, shift_name, color, group_id, group_name, status }] }
     */
    public function index(Request $request): JsonResponse
    {
        $data = $request->validate([
            'start' => 'required|date_format:Y-m-d',
            'end'   => 'required|date_format:Y-m-d|after_or_equal:start',
            'user_id' => 'nullable|exists:users,id',
            'group_id' => 'nullable|exists:shift_groups,id',
            'shift_id' => 'nullable|exists:shifts,id',
        ]);

        $q = Schedule::with(['user:id,name,username', 'shift:id,name,color,start_time,end_time,is_overnight', 'group:id,name,color']);
        $q->whereBetween('date', [$data['start'], $data['end']]);
        if (!empty($data['user_id'])) $q->where('user_id', $data['user_id']);
        if (!empty($data['group_id'])) $q->where('group_id', $data['group_id']);
        if (!empty($data['shift_id'])) $q->where('shift_id', $data['shift_id']);

        $rows = $q->orderBy('date')->orderBy('user_id')->get();

        // 按日期分组
        $byDate = [];
        foreach ($rows as $r) {
            $d = $r->date->format('Y-m-d');
            $byDate[$d][] = [
                'id' => $r->id,
                'user_id' => $r->user_id,
                'user_name' => $r->user->name ?? $r->user->username ?? null,
                'group_id' => $r->group_id,
                'group_name' => $r->group->name ?? null,
                'group_color' => $r->group->color ?? null,
                'shift_id' => $r->shift_id,
                'shift_name' => $r->shift->name ?? null,
                'shift_color' => $r->shift->color ?? null,
                'start_time' => $r->shift->start_time ?? null,
                'end_time' => $r->shift->end_time ?? null,
                'is_overnight' => $r->shift->is_overnight ?? false,
                'status' => $r->status,
                'note' => $r->note,
            ];
        }

        return response()->json([
            'code' => 0,
            'data' => [
                'start' => $data['start'],
                'end'   => $data['end'],
                'by_date' => $byDate,
                'total' => $rows->count(),
            ],
        ]);
    }

    /**
     * 我的排班 (供个人用, 移动端友好)
     * GET /api/schedules/my?month=2026-06
     */
    public function mySchedule(Request $request): JsonResponse
    {
        $data = $request->validate([
            'month' => 'nullable|date_format:Y-m',
        ]);
        $month = $data['month'] ?? today()->format('Y-m');
        $start = $month . '-01';
        $end   = date('Y-m-t', strtotime($start));

        $rows = Schedule::with('shift')
            ->where('user_id', Auth::id())
            ->whereBetween('date', [$start, $end])
            ->orderBy('date')
            ->get();

        $byDate = [];
        foreach ($rows as $r) {
            $byDate[$r->date->format('Y-m-d')] = [
                'shift_id' => $r->shift_id,
                'shift_name' => $r->shift->name ?? null,
                'shift_color' => $r->shift->color ?? null,
                'start_time' => $r->shift->start_time ?? null,
                'end_time' => $r->shift->end_time ?? null,
                'is_overnight' => $r->shift->is_overnight ?? false,
                'status' => $r->status,
            ];
        }
        return response()->json(['code' => 0, 'data' => ['month' => $month, 'by_date' => $byDate]]);
    }

    /**
     * 批量排班 (核心: 周排班表一次保存)
     * POST /api/schedules/batch
     * body: { assignments: [{ user_id, group_id?, date, shift_id, note? }] }
     * 已存在的 (user+date) 会覆盖 shift, 适合排班表点格子后批量提交
     */
    public function batchSave(Request $request): JsonResponse
    {
        $data = $request->validate([
            'assignments' => 'required|array|min:1',
            'assignments.*.user_id'  => 'required|exists:users,id',
            'assignments.*.group_id' => 'nullable|exists:shift_groups,id',
            'assignments.*.date'     => 'required|date_format:Y-m-d',
            'assignments.*.shift_id' => 'required|exists:shifts,id',
            'assignments.*.status'   => 'nullable|in:scheduled,rest,sick,leave,swapped',
            'assignments.*.note'     => 'nullable|string|max:500',
        ]);

        $created = 0; $updated = 0;
        DB::transaction(function () use ($data, &$created, &$updated) {
            foreach ($data['assignments'] as $a) {
                $rec = Schedule::where('user_id', $a['user_id'])->where('date', $a['date'])->first();
                $payload = [
                    'group_id' => $a['group_id'] ?? null,
                    'shift_id' => $a['shift_id'],
                    'status'   => $a['status']   ?? 'scheduled',
                    'note'     => $a['note']     ?? null,
                    'created_by' => Auth::id(),
                ];
                if ($rec) {
                    $rec->update($payload);
                    $updated++;
                } else {
                    $payload['user_id'] = $a['user_id'];
                    $payload['date']    = $a['date'];
                    Schedule::create($payload);
                    $created++;
                }
            }
        });

        return response()->json([
            'code' => 0,
            'message' => "排班保存成功 (新建 {$created}, 更新 {$updated})",
            'data' => ['created' => $created, 'updated' => $updated],
        ]);
    }

    /**
     * 班组批量排班 (整组一起设)
     * POST /api/schedules/batch-by-group
     * body: { group_id, start_date, end_date, shift_id, skip_weekends? }
     * 把班组内所有成员从 start 到 end 每天设为同一班次
     */
    public function batchByGroup(Request $request): JsonResponse
    {
        $data = $request->validate([
            'group_id' => 'required|exists:shift_groups,id',
            'start_date' => 'required|date_format:Y-m-d',
            'end_date'   => 'required|date_format:Y-m-d|after_or_equal:start_date',
            'shift_id'   => 'required|exists:shifts,id',
            'skip_weekends' => 'boolean',
        ]);

        $userIds = ShiftGroupMember::where('group_id', $data['group_id'])->pluck('user_id')->all();
        if (empty($userIds)) {
            return response()->json(['code' => 1001, 'message' => '班组无成员'], 422);
        }

        $cursor = Carbon::parse($data['start_date']);
        $end    = Carbon::parse($data['end_date']);
        $assignments = [];
        while ($cursor->lte($end)) {
            if (!$data['skip_weekends'] || !in_array($cursor->dayOfWeek, [Carbon::SATURDAY, Carbon::SUNDAY], true)) {
                foreach ($userIds as $uid) {
                    $assignments[] = [
                        'user_id'  => $uid,
                        'group_id' => $data['group_id'],
                        'date'     => $cursor->format('Y-m-d'),
                        'shift_id' => $data['shift_id'],
                    ];
                }
            }
            $cursor->addDay();
        }

        $count = count($assignments);
        DB::transaction(function () use ($assignments) {
            foreach ($assignments as $a) {
                Schedule::updateOrCreate(
                    ['user_id' => $a['user_id'], 'date' => $a['date']],
                    ['group_id' => $a['group_id'], 'shift_id' => $a['shift_id'], 'created_by' => Auth::id()],
                );
            }
        });

        return response()->json(['code' => 0, 'message' => "已为 {$count} 个班次分配", 'data' => ['count' => $count]]);
    }

    /**
     * 删除单条排班
     */
    public function destroy(Schedule $schedule): JsonResponse
    {
        $schedule->delete();
        return response()->json(['code' => 0, 'message' => '已删除该排班']);
    }

    /**
     * 智能排班建议: 给定日期范围, 自动从历史考勤中推断常见班次
     * GET /api/schedules/smart-suggest?user_id=1&start_date=2026-06-20&end_date=2026-06-26
     * 从过去 30 天 attendance_records 的 clock_in 时间聚类, 找最常见的 shift
     */
    public function smartSuggest(Request $request): JsonResponse
    {
        $data = $request->validate([
            'user_id'    => 'nullable|exists:users,id',
            'start_date' => 'required|date_format:Y-m-d',
            'end_date'   => 'required|date_format:Y-m-d|after_or_equal:start_date',
        ]);

        $shifts = Shift::where('is_active', true)->orderBy('start_time')->get();
        if ($shifts->isEmpty()) {
            return response()->json(['code' => 1001, 'message' => '请先配置班次'], 422);
        }

        // 1) 拿所有用户的过去 30 天打卡时间分布
        $userIds = !empty($data['user_id']) ? [$data['user_id']] : User::pluck('id')->all();
        $since = Carbon::parse($data['start_date'])->subDays(30)->format('Y-m-d');

        $history = AttendanceRecord::whereIn('user_id', $userIds)
            ->where('date', '>=', $since)
            ->whereNotNull('clock_in')
            ->select('user_id', 'date', 'clock_in')
            ->get()
            ->groupBy('user_id');

        // 2) 给每个用户匹配最接近历史规律的班次
        $suggestions = [];
        foreach ($userIds as $uid) {
            $records = $history[$uid] ?? collect();
            if ($records->isEmpty()) {
                // 无历史 → 推第一个日间班
                $best = $shifts->firstWhere('code', 'day') ?? $shifts->first();
            } else {
                // 算平均 clock_in 时刻
                $totalMin = 0; $n = 0;
                foreach ($records as $r) {
                    $t = Carbon::parse($r->clock_in);
                    $totalMin += $t->hour * 60 + $t->minute;
                    $n++;
                }
                $avgMin = $n > 0 ? $totalMin / $n : 540; // 默认 9:00
                $best = null; $bestDiff = PHP_INT_MAX;
                foreach ($shifts as $s) {
                    [$h, $m] = explode(':', substr($s->start_time, 0, 5));
                    $shiftMin = (int)$h * 60 + (int)$m;
                    $diff = abs($shiftMin - $avgMin);
                    if ($diff < $bestDiff) { $best = $s; $bestDiff = $diff; }
                }
            }
            $suggestions[] = [
                'user_id' => $uid,
                'suggested_shift_id' => $best->id ?? null,
                'suggested_shift_name' => $best->name ?? null,
                'suggested_shift_color' => $best->color ?? null,
            ];
        }
        return response()->json(['code' => 0, 'data' => $suggestions]);
    }

    /**
     * 下一班次提醒: 给当前用户, 返回下一班 + 开始倒计时
     * GET /api/schedules/next-reminder
     */
    public function nextReminder(Request $request): JsonResponse
    {
        $userId = Auth::id();
        $today = today()->format('Y-m-d');
        $tomorrow = today()->addDay()->format('Y-m-d');

        // 找未来 7 天最近一条
        $next = Schedule::with('shift')
            ->where('user_id', $userId)
            ->whereIn('date', [$today, $tomorrow, today()->addDays(2)->format('Y-m-d'), today()->addDays(3)->format('Y-m-d'), today()->addDays(4)->format('Y-m-d'), today()->addDays(5)->format('Y-m-d'), today()->addDays(6)->format('Y-m-d')])
            ->orderBy('date')
            ->orderBy('id')
            ->first();

        if (!$next) {
            return response()->json(['code' => 0, 'data' => null, 'message' => '近 7 天无排班']);
        }
        $shiftStart = $next->date->format('Y-m-d') . ' ' . $next->shift->start_time;
        $minutesUntil = Carbon::now()->diffInMinutes(Carbon::parse($shiftStart), false);

        return response()->json([
            'code' => 0,
            'data' => [
                'date' => $next->date->format('Y-m-d'),
                'shift_name' => $next->shift->name,
                'shift_color' => $next->shift->color,
                'start_time' => $next->shift->start_time,
                'end_time' => $next->shift->end_time,
                'minutes_until_start' => $minutesUntil,
            ],
        ]);
    }

    /**
     * 排班统计: 某月各班次使用次数 / 各员工班次数
     */
    public function stats(Request $request): JsonResponse
    {
        $data = $request->validate(['month' => 'nullable|date_format:Y-m']);
        $month = $data['month'] ?? today()->format('Y-m');
        $start = $month . '-01';
        $end   = date('Y-m-t', strtotime($start));

        $byShift = DB::table('schedules')
            ->join('shifts', 'schedules.shift_id', '=', 'shifts.id')
            ->whereBetween('schedules.date', [$start, $end])
            ->groupBy('shifts.id', 'shifts.name', 'shifts.color')
            ->select('shifts.id', 'shifts.name', 'shifts.color', DB::raw('count(*) as cnt'))
            ->get();

        $byUser = DB::table('schedules')
            ->join('users', 'schedules.user_id', '=', 'users.id')
            ->whereBetween('schedules.date', [$start, $end])
            ->groupBy('users.id', 'users.name', 'users.username')
            ->select('users.id', 'users.name', 'users.username', DB::raw('count(*) as cnt'))
            ->orderByDesc('cnt')
            ->get();

        return response()->json([
            'code' => 0,
            'data' => [
                'month' => $month,
                'by_shift' => $byShift,
                'by_user'  => $byUser,
                'total'    => array_sum($byShift->pluck('cnt')->all()),
            ],
        ]);
    }
}
