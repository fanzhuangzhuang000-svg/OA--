<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\EmployeeResignation;
use App\Models\EmployeeOnboarding;
use App\Models\ShiftGroupMember;
use App\Models\AttendanceRecord;
use App\Models\EmployeeProfile;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class EmployeeResignationController extends Controller
{
    /**
     * GET /api/employee-resignations
     */
    public function index(Request $request): JsonResponse
    {
        $data = $request->validate([
            'user_id' => 'nullable|exists:users,id',
            'status'  => 'nullable|in:draft,pending,approved,completed,cancelled',
            'resign_type' => 'nullable|in:voluntary,involuntary,contract_end,retirement,other',
            'page' => 'nullable|integer|min:1',
            'per_page' => 'nullable|integer|min:1|max:200',
        ]);

        $q = EmployeeResignation::with([
            'user:id,name,username,phone',
            'handoverTo:id,name',
            'approver:id,name',
            'creator:id,name',
            'certificateFile:id,name,original_name,size',
        ]);

        if (!empty($data['user_id'])) $q->where('user_id', $data['user_id']);
        if (!empty($data['status'])) $q->where('status', $data['status']);
        if (!empty($data['resign_type'])) $q->where('resign_type', $data['resign_type']);

        $q->orderBy('created_at', 'desc');
        $rows = $q->paginate($data['per_page'] ?? 20);
        return response()->json(['code' => 0, 'data' => $rows]);
    }

    /**
     * GET /api/employee-resignations/{id}
     */
    public function show(EmployeeResignation $resignation): JsonResponse
    {
        $resignation->load(['user', 'handoverTo', 'approver', 'creator', 'certificateFile']);
        return response()->json(['code' => 0, 'data' => $resignation]);
    }

    /**
     * POST /api/employee-resignations
     * 创建离职申请 (draft 或 pending)
     */
    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'user_id'        => 'required|exists:users,id',
            'resign_date'    => 'required|date_format:Y-m-d',
            'notice_date'    => 'nullable|date_format:Y-m-d',
            'last_work_day'  => 'required|date_format:Y-m-d',
            'resign_type'    => 'required|in:voluntary,involuntary,contract_end,retirement,other',
            'reason'         => 'required|string|max:2000',
            'handover_to_user_id' => 'nullable|exists:users,id|different:user_id',
            'handover_note'  => 'nullable|string|max:2000',
            'assets_checklist'   => 'nullable|array',
            'final_salary_amount'  => 'nullable|numeric|min:0',
            'leave_balance_payout' => 'nullable|numeric|min:0',
            'severance_pay'        => 'nullable|numeric|min:0',
            'social_security_cutoff' => 'nullable|date_format:Y-m-d',
            'remark'          => 'nullable|string|max:2000',
            'submit'          => 'nullable|boolean',  // true=直接提交审批, false=存草稿
        ]);

        $user = User::findOrFail($data['user_id']);
        if (!$user->is_active) {
            return response()->json(['code' => 1001, 'message' => '该用户已是离职状态'], 422);
        }
        // 同一人不能有未完成的离职
        $existing = EmployeeResignation::where('user_id', $data['user_id'])
            ->whereIn('status', ['draft', 'pending', 'approved'])
            ->exists();
        if ($existing) {
            return response()->json(['code' => 1002, 'message' => '该员工已有未结的离职申请'], 422);
        }

        $resignation = EmployeeResignation::create([
            'user_id'      => $data['user_id'],
            'resign_date'  => $data['resign_date'],
            'notice_date'  => $data['notice_date'] ?? Carbon::now()->format('Y-m-d'),
            'last_work_day' => $data['last_work_day'],
            'resign_type'  => $data['resign_type'],
            'reason'       => $data['reason'],
            'handover_to_user_id' => $data['handover_to_user_id'] ?? null,
            'handover_note' => $data['handover_note'] ?? null,
            'assets_checklist' => $data['assets_checklist'] ?? null,
            'final_salary_amount' => $data['final_salary_amount'] ?? null,
            'leave_balance_payout' => $data['leave_balance_payout'] ?? null,
            'severance_pay' => $data['severance_pay'] ?? null,
            'social_security_cutoff' => $data['social_security_cutoff'] ?? null,
            'remark'       => $data['remark'] ?? null,
            'status'       => !empty($data['submit']) ? 'pending' : 'draft',
            'created_by'   => Auth::id(),
        ]);

        return response()->json(['code' => 0, 'message' => '离职申请已创建', 'data' => $resignation], 201);
    }

    /**
     * PUT /api/employee-resignations/{id}
     * 更新 (仅 draft / pending 可改)
     */
    public function update(Request $request, EmployeeResignation $resignation): JsonResponse
    {
        if (!in_array($resignation->status, ['draft', 'pending'], true)) {
            return response()->json(['code' => 1001, 'message' => '已审批的离职单不能修改'], 422);
        }
        $data = $request->validate([
            'resign_date'   => 'sometimes|date_format:Y-m-d',
            'notice_date'   => 'nullable|date_format:Y-m-d',
            'last_work_day' => 'sometimes|date_format:Y-m-d',
            'resign_type'   => 'sometimes|in:voluntary,involuntary,contract_end,retirement,other',
            'reason'        => 'sometimes|string|max:2000',
            'handover_to_user_id' => 'nullable|exists:users,id|different:user_id',
            'handover_note' => 'nullable|string|max:2000',
            'assets_checklist' => 'nullable|array',
            'final_salary_amount'  => 'nullable|numeric|min:0',
            'leave_balance_payout' => 'nullable|numeric|min:0',
            'severance_pay'        => 'nullable|numeric|min:0',
            'social_security_cutoff' => 'nullable|date_format:Y-m-d',
            'remark' => 'nullable|string|max:2000',
        ]);

        $resignation->update($data);
        return response()->json(['code' => 0, 'message' => '已更新', 'data' => $resignation]);
    }

    /**
     * POST /api/employee-resignations/{id}/submit
     * 草稿 -> 提交审批
     */
    public function submit(EmployeeResignation $resignation): JsonResponse
    {
        if ($resignation->status !== 'draft') {
            return response()->json(['code' => 1001, 'message' => '仅草稿状态可提交'], 422);
        }
        $resignation->update(['status' => 'pending']);
        return response()->json(['code' => 0, 'message' => '已提交审批', 'data' => $resignation]);
    }

    /**
     * POST /api/employee-resignations/{id}/approve
     * 审批通过 (pending -> approved)
     */
    public function approve(EmployeeResignation $resignation): JsonResponse
    {
        if ($resignation->status !== 'pending') {
            return response()->json(['code' => 1001, 'message' => '仅待审批状态可审批'], 422);
        }
        $resignation->update([
            'status' => 'approved',
            'approved_by' => Auth::id(),
            'approved_at' => now(),
        ]);
        return response()->json(['code' => 0, 'message' => '已审批', 'data' => $resignation]);
    }

    /**
     * POST /api/employee-resignations/{id}/cancel
     * 撤回 (draft/pending/approved -> cancelled)
     */
    public function cancel(EmployeeResignation $resignation): JsonResponse
    {
        if (in_array($resignation->status, ['completed', 'cancelled'], true)) {
            return response()->json(['code' => 1001, 'message' => '已完成或已取消的单不能再撤回'], 422);
        }
        $resignation->update(['status' => 'cancelled']);
        return response()->json(['code' => 0, 'message' => '已撤回']);
    }

    /**
     * POST /api/employee-resignations/{id}/complete
     * 办结 (approved -> completed): 事务内
     *   1) 标记 User.is_active = false, status = 'inactive'
     *   2) 解除所有班组
     *   3) 更新 EmployeeProfile.leave_date
     *   4) 归档 Onboarding
     *   5) 标记资产归还
     *   6) 计算总工资 = 各项之和
     */
    public function complete(Request $request, EmployeeResignation $resignation): JsonResponse
    {
        if ($resignation->status !== 'approved') {
            return response()->json(['code' => 1001, 'message' => '仅已审批的单可办结'], 422);
        }
        $data = $request->validate([
            'all_assets_returned' => 'required|boolean',
            'paid_date'           => 'nullable|date_format:Y-m-d',
            'paid_method'         => 'nullable|string|max:32',
            'resign_certificate_file_id' => 'nullable|exists:disk_files,id',
        ]);

        try {
            $result = DB::transaction(function () use ($resignation, $data) {
                $user = $resignation->user;

                // 1) 冻结账号
                $user->update(['is_active' => false, 'status' => 'inactive']);

                // 2) 解除所有班组
                ShiftGroupMember::where('user_id', $user->id)->delete();

                // 3) 更新 EmployeeProfile.leave_date
                EmployeeProfile::where('user_id', $user->id)
                    ->update(['leave_date' => $resignation->last_work_day]);

                // 4) 归档 Onboarding
                EmployeeOnboarding::where('user_id', $user->id)
                    ->update(['status' => 'archived']);

                // 5) 计算总工资
                $total = ($resignation->final_salary_amount ?? 0)
                       + ($resignation->leave_balance_payout ?? 0)
                       + ($resignation->severance_pay ?? 0);

                $resignation->update([
                    'status' => 'completed',
                    'all_assets_returned' => $data['all_assets_returned'],
                    'paid_date' => $data['paid_date'] ?? Carbon::now()->format('Y-m-d'),
                    'paid_method' => $data['paid_method'] ?? '银行转账',
                    'resign_certificate_file_id' => $data['resign_certificate_file_id'] ?? null,
                    'total_settlement' => $total,
                ]);

                return $resignation;
            });

            return response()->json([
                'code' => 0,
                'message' => '离职办结完成, 账号已冻结',
                'data' => $result->fresh(['user', 'handoverTo', 'certificateFile']),
            ]);
        } catch (\Throwable $e) {
            return response()->json(['code' => 1002, 'message' => '办结失败: ' . $e->getMessage()], 422);
        }
    }

    /**
     * GET /api/employee-resignations/settlement-preview
     * 离职工资预览 (按用户 + 离职日 自动算)
     * query: user_id, resign_date
     */
    public function settlementPreview(Request $request): JsonResponse
    {
        $data = $request->validate([
            'user_id' => 'required|exists:users,id',
            'resign_date' => 'required|date_format:Y-m-d',
        ]);

        $user = User::findOrFail($data['user_id']);
        $profile = EmployeeProfile::where('user_id', $user->id)->first();

        // 1) 当月已工作天数 (含首日)
        $resign = Carbon::parse($data['resign_date']);
        $monthStart = $resign->copy()->startOfMonth();
        $workedDays = $monthStart->diffInDays($resign) + 1;

        // 2) 应出勤天数 (排除周末)
        $workDays = 0;
        $cursor = $monthStart->copy();
        while ($cursor->lte($resign)) {
            if (!in_array($cursor->dayOfWeek, [Carbon::SATURDAY, Carbon::SUNDAY], true)) {
                $workDays++;
            }
            $cursor->addDay();
        }

        // 3) 当月实际打卡天数
        $actualDays = AttendanceRecord::where('user_id', $user->id)
            ->whereBetween('date', [$monthStart->format('Y-m-d'), $resign->format('Y-m-d')])
            ->whereNotNull('clock_in')
            ->count();

        $baseSalary = $profile?->base_salary ?? 0;
        $dailyRate  = $baseSalary > 0 ? round($baseSalary / 21.75, 2) : 0; // 21.75 月计薪日
        $finalSalary = $dailyRate * $actualDays;

        // 4) 未休年假 (从入职日算)
        $unpaidLeave = 0; // 简化: 暂不计算, HR 后台录入

        // 5) 经济补偿金 (N, 1年1个月工资, 不满半年0.5, 满半年1)
        $severance = 0;
        if ($profile && $profile->hire_date) {
            $years = Carbon::parse($profile->hire_date)->diffInYears($resign);
            $months = Carbon::parse($profile->hire_date)->diffInMonths($resign) % 12;
            $n = $years + ($months >= 6 ? 1 : ($months > 0 ? 0.5 : 0));
            $severance = $n * $baseSalary;
        }

        return response()->json([
            'code' => 0,
            'data' => [
                'user_id' => $user->id,
                'user_name' => $user->name,
                'resign_date' => $data['resign_date'],
                'hire_date' => $profile?->hire_date?->format('Y-m-d'),
                'work_years' => $profile?->hire_date ? round(Carbon::parse($profile->hire_date)->diffInDays($resign) / 365, 1) : 0,
                'base_salary' => $baseSalary,
                'daily_rate' => $dailyRate,
                'month_work_days' => $workDays,
                'month_actual_days' => $actualDays,
                'final_salary_amount' => round($finalSalary, 2),
                'leave_balance_payout' => $unpaidLeave,
                'severance_pay' => round($severance, 2),
                'total_settlement' => round($finalSalary + $unpaidLeave + $severance, 2),
                'social_security_cutoff' => $resign->format('Y-m'),
            ],
        ]);
    }
}
