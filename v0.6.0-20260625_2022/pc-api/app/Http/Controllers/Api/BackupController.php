<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;

class BackupController extends Controller
{
    protected string $backupDir = '';

    public function __construct()
    {
        $this->backupDir = storage_path('app/backups');
    }

    /** 备份列表 */
    public function index(): JsonResponse
    {
        if (!is_dir($this->backupDir)) {
            return response()->json(['code' => 0, 'data' => []]);
        }
        $files = [];
        foreach (scandir($this->backupDir, SCANDIR_SORT_DESCENDING) as $f) {
            if ($f === '.' || $f === '..') continue;
            $path = $this->backupDir . '/' . $f;
            if (is_file($path)) {
                $files[] = [
                    'id' => $f,
                    'filename' => $f,
                    'size' => round(filesize($path) / 1024 / 1024, 2) . ' MB',
                    'time' => date('Y-m-d H:i:s', filemtime($path)),
                    'status' => '完成',
                ];
            }
        }
        return response()->json(['code' => 0, 'data' => $files]);
    }

    /** 手动触发备份 */
    public function store(Request $request): JsonResponse
    {
        if (!is_dir($this->backupDir)) {
            mkdir($this->backupDir, 0755, true);
        }
        $label = $request->input('label', 'manual');
        $ts = now()->format('Ymd_His');
        $filename = "oa_backup_{$label}_{$ts}.sql";
        $filepath = $this->backupDir . '/' . $filename;

        // T2-7 修复: 用 pg_dump 替代 mysqldump（项目实际用 PostgreSQL）
        $db = config('database.connections.pgsql');
        $cmd = sprintf(
            'PGPASSWORD=%s pg_dump -h %s -p %s -U %s -d %s -F p --no-owner --no-acl %s > %s 2>/dev/null',
            escapeshellarg($db['password']),
            escapeshellarg($db['host']),
            escapeshellarg((string)$db['port']),
            escapeshellarg($db['username']),
            escapeshellarg($db['database']),
            '',  // 不带额外参数
            escapeshellarg($filepath)
        );
        exec($cmd, $output, $ret);
        if ($ret !== 0 || !file_exists($filepath) || filesize($filepath) === 0) {
            return response()->json(['code' => 1001, 'message' => '备份失败: pg_dump 退出码 ' . $ret . ', 文件大小 ' . (file_exists($filepath) ? filesize($filepath) : 0)]);
        }
        // 压缩
        $gzpath = $filepath . '.gz';
        exec("gzip -f " . escapeshellarg($filepath));
        $filename .= '.gz';

        return response()->json(['code' => 0, 'data' => ['filename' => $filename]]);
    }

    /** 下载备份 */
    public function download(Request $request, string $filename)
    {
        $path = $this->backupDir . '/' . basename($filename);
        if (!file_exists($path)) {
            return response()->json(['code' => 404, 'message' => '文件不存在']);
        }
        return response()->download($path, $filename);
    }

    /** 删除备份 */
    public function destroy(Request $request, string $filename): JsonResponse
    {
        $path = $this->backupDir . '/' . basename($filename);
        if (file_exists($path)) {
            unlink($path);
        }
        return response()->json(['code' => 0, 'message' => '已删除']);
    }
}
