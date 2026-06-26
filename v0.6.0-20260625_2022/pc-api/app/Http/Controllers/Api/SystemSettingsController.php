<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\SystemSetting;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * 系统设置 — 集中管理：
 *  - 系统名称 / 简称 / 版权 / 备案号 / 公告 / 联系邮箱
 *  - 审批流程模板 (data_management: 替换原前端 hardcoded)
 *  - admin 一键清理业务数据
 */
class SystemSettingsController extends Controller
{
    /** GET /api/settings — 读全部设置 */
    public function index(): JsonResponse
    {
        $rows = SystemSetting::all();
        $data = [];
        foreach ($rows as $r) {
            $data[$r->key] = $this->normalize($r->value);
        }
        return response()->json([
            'code' => 0,
            'data' => $data,
        ]);
    }

    /**
     * PG JSONB 经 PDO 返回来可能是：
     *   - 已经是 array (数值/对象)
     *   - 字符串 '"foo"' (带引号)
     *   - 字符串 'foo' (无引号 — bug 驱动)
     * 统一去掉首尾的 JSON 字符串引号
     */
    private function normalize($v)
    {
        if ($v === null) return null;
        if (is_array($v) || is_bool($v) || is_int($v) || is_float($v)) return $v;
        $s = (string) $v;
        $decoded = json_decode($s, true);
        if (json_last_error() === JSON_ERROR_NONE) {
            // 解出来是字符串就直接给；是 array/数字/布尔已递归处理
            return $decoded;
        }
        return $s;
    }

    /**
     * PUT /api/settings — 批量更新
     * body: { system_name: 'xxx', copyright: '...', ... }
     */
    public function update(Request $request): JsonResponse
    {
        $allowed = [
            'system_name'         => 'nullable|string|max:64',
            'system_short_name'   => 'nullable|string|max:32',
            'copyright'           => 'nullable|string|max:255',
            'copyright_url'       => 'nullable|string|max:255',
            'announcement'        => 'nullable|string|max:2000',
            'icp'                 => 'nullable|string|max:64',
            'contact_email'       => 'nullable|email|max:128',
            // 闲置超时配置
            'idle_enabled'        => 'nullable|boolean',
            'idle_timeout_minutes'=> 'nullable|integer|min:1|max:1440',  // 最多 24 小时
            'idle_warning_seconds'=> 'nullable|integer|min:0|max:600',   // 最多 10 分钟
        ];
        $data = $request->validate($allowed);

        // 闲置配置业务校验:警告秒数不能 >= 超时秒数
        $toMin = isset($data['idle_timeout_minutes']) ? (int) $data['idle_timeout_minutes'] : null;
        $toSec = isset($data['idle_warning_seconds']) ? (int) $data['idle_warning_seconds'] : null;
        if ($toMin !== null && $toSec !== null && $toSec >= $toMin * 60) {
            return response()->json([
                'code'    => 1001,
                'message' => '提前提示秒数不能大于等于总超时时间',
            ], 422);
        }

        $userId = $request->user()?->id;
        $updated = 0;
        foreach ($data as $key => $val) {
            // null 表示不更新；空串表示清空
            $jsonVal = json_encode($val, JSON_UNESCAPED_UNICODE);
            DB::table('system_settings')->updateOrInsert(
                ['key' => $key],
                [
                    'value'       => $jsonVal,
                    'updated_at'  => now(),
                    'updated_by'  => $userId,
                ]
            );
            $updated++;
        }

        // 重新读一次返回最新值
        $latest = [];
        foreach (SystemSetting::all() as $r) {
            $latest[$r->key] = $this->normalize($r->value);
        }
        return response()->json([
            'code'    => 0,
            'message' => "已更新 {$updated} 项设置",
            'data'    => $latest,
        ]);
    }

    /**
     * GET /api/settings/idle-config — 读取闲置超时配置
     * 前端 useIdleTimer 启动时调用
     * 返回: { enabled, timeout_minutes, warning_seconds, timeout_ms, warning_ms }
     */
    public function getIdleConfig(): JsonResponse
    {
        $enabled = SystemSetting::get('idle_enabled', true);
        $toMin   = SystemSetting::get('idle_timeout_minutes', 30);
        $toSec   = SystemSetting::get('idle_warning_seconds', 60);

        // 强转 int(从 DB 读出可能是 int 或 string)
        $enabled = (bool) $enabled;
        $toMin   = max(1, min(1440, (int) $toMin));
        $toSec   = max(0, min(600, (int) $toSec));
        // 警告秒数不能 >= 总秒数,自动夹一下
        if ($toSec >= $toMin * 60) {
            $toSec = max(0, $toMin * 60 - 1);
        }

        return response()->json([
            'code'    => 0,
            'data'    => [
                'enabled'         => $enabled,
                'timeout_minutes' => $toMin,
                'warning_seconds' => $toSec,
                'timeout_ms'      => $toMin * 60 * 1000,
                'warning_ms'      => $toSec * 1000,
            ],
        ]);
    }

    /**
     * GET /api/settings/port — 读端口配置
     * 返回: { port: number, default: number }
     */
    public function getPortConfig(): JsonResponse
    {
        $port = SystemSetting::get('custom_web_port', 80);
        // 兜底：DB 里的值可能是字符串/数组，统一强转 int
        if (!is_int($port) && !is_float($port)) {
            $port = (int) $port;
        }
        return response()->json([
            'code'    => 0,
            'data'    => [
                'port'    => $port,
                'default' => 80,
            ],
        ]);
    }

    /**
     * PUT /api/settings/port — 改端口配置
     * body: { port: 9000 }  — 1-65535 整数
     * ⚠ 改完需重启 web 服务（PHP-FPM + nginx/apache）才能生效
     */
    public function updatePortConfig(Request $request): JsonResponse
    {
        $data = $request->validate([
            'port' => 'required|integer|min:1|max:65535',
        ]);

        $userId = $request->user()?->id;
        DB::table('system_settings')->updateOrInsert(
            ['key' => 'custom_web_port'],
            [
                'value'      => json_encode((int) $data['port'], JSON_UNESCAPED_UNICODE),
                'updated_at' => now(),
                'updated_by' => $userId,
            ]
        );

        return response()->json([
            'code'    => 0,
            'message' => '端口配置已保存，需重启 web 服务后生效',
            'data'    => [
                'port'    => (int) $data['port'],
                'default' => 80,
            ],
        ]);
    }

    /**
     * POST /api/admin/wipe-data — admin 一键清空业务数据
     * body: { password: 'admin123' }  — 二次确认密码
     * 保留: users (含 admin), roles, permissions, system_settings, departments, positions, skill_tags
     * 清理: 业务表（项目/客户/工单/车辆/库存/财务/审批/报销/考勤/网盘/知识库/消息...）
     */
    public function wipeData(Request $request): JsonResponse
    {
        $data = $request->validate([
            'password'      => 'required|string',
            'confirm_phrase'=> 'required|string|in:确认清空', // 防误操作
        ]);

        $user = $request->user();
        // 仅 admin (id=1) 允许
        if (!$user || $user->id !== 1) {
            return response()->json(['code' => 1003, 'message' => '仅超级管理员可执行此操作'], 403);
        }
        // 二次密码校验
        if (!\Hash::check($data['password'], $user->password)) {
            return response()->json(['code' => 1001, 'message' => '管理员密码不正确'], 422);
        }

        // 剩余独立表（不会被 CASCADE 覆盖的），按 FK 依赖倒序排列
        $standalone = [
            // 库存子表先于父表
            'stock_records', 'device_serial_numbers', 'inventory_items',
            'inventory_categories', 'warehouses',
            // 知识库
            'knowledge_articles', 'knowledge_categories',
            // 消息/日志
            'notifications', 'system_logs',
            // 入职/离职/技能/证书
            'employee_onboardings', 'employee_resignations',
            'employee_profiles', 'certificates',
            // 排班
            'shift_group_members', 'shift_groups',
            'schedules', 'schedule_shift_assignments',
            // 销售
            'sales_products', 'sales_quotes',
            // 审批
            'approval_records', 'approval_records_v2',
            'approval_templates',
            // 维保/网盘
            'maintenance_contracts',
            'disk_files', 'disk_folders',
        ];

        $deleted = [];

        // Phase 1: TRUNCATE CASCADE 清空核心业务表及其 FK 子表
        try {
            DB::statement('TRUNCATE TABLE projects, customers, service_orders, vehicles, expense_claims, fuel_cards RESTART IDENTITY CASCADE');
            $deleted['_cascade'] = 'projects+customers+service_orders+vehicles+expense_claims+fuel_cards (cascaded all FK children)';
        } catch (\Throwable $e) {
            return response()->json([
                'code'    => 1002,
                'message' => 'TRUNCATE 清空失败: ' . $e->getMessage(),
            ], 500);
        }

        // Phase 2: 逐表清理剩余独立表（每个表独立 try，不中断整体）
        foreach ($standalone as $t) {
            try {
                // 用独立事务避免前一个表的问题影响后续表
                DB::statement("DELETE FROM \"{$t}\"");
                $deleted[$t] = 1;
            } catch (\Illuminate\Database\QueryException $qe) {
                if (str_contains($qe->getMessage(), 'does not exist') || str_contains($qe->getMessage(), '42P01')) {
                    $deleted[$t] = 0;
                } else {
                    $deleted[$t] = 'ERR: ' . $qe->getMessage();
                }
            } catch (\Throwable $e) {
                $deleted[$t] = 'ERR: ' . $e->getMessage();
            }
        }

        return response()->json([
            'code'    => 0,
            'message' => '业务数据已清空，admin / 部门 / 角色 / 权限 / 设置 已保留',
            'data'    => $deleted,
        ]);
    }
}
