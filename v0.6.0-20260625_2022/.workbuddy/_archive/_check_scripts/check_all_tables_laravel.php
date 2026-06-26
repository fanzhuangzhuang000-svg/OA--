<?php
/**
 * 检查所有表的数据量（使用Laravel数据库配置）
 * 使用方法：php check_all_tables_laravel.php
 */

// 引导Laravel应用
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

// 获取所有表
$tables = [];
$allTables = DB::select("
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    ORDER BY tablename
");
foreach ($allTables as $row) {
    $tables[] = $row->tablename;
}

echo "找到 " . count($tables) . " 张表\n\n";

$emptyTables = [];
$lowDataTables = [];
$tableStats = [];

foreach ($tables as $table) {
    try {
        $count = DB::table($table)->count();
        $tableStats[] = [$table, $count];
        
        if ($count == 0) {
            $emptyTables[] = $table;
        } elseif ($count < 10) {
            $lowDataTables[] = [$table, $count];
        }
    } catch (Exception $e) {
        // 忽略错误
    }
}

// 按数据量排序
usort($tableStats, function($a, $b) {
    return $a[1] - $b[1];
});

// 输出统计
echo "📊 数据量统计：\n";
echo "   总表数: " . count($tables) . "\n";
echo "   空白表 (0条): " . count($emptyTables) . "\n";
echo "   低数据表 (<10条): " . count($lowDataTables) . "\n";
echo "   有数据表 (≥10条): " . (count($tables) - count($emptyTables) - count($lowDataTables)) . "\n\n";

// 输出空白表
if ($emptyTables) {
    echo "❌ 空白表 (0条数据，需要生成):\n";
    foreach ($emptyTables as $i => $table) {
        echo "   " . ($i + 1) . ". $table\n";
    }
    echo "\n";
}

// 输出低数据表
if ($lowDataTables) {
    echo "⚠️ 低数据表 (<10条，建议增加):\n";
    foreach ($lowDataTables as $i => $item) {
        echo "   " . ($i + 1) . ". {$item[0]}: {$item[1]}条\n";
    }
    echo "\n";
}

// 输出有数据的表
echo "✅ 有数据的表 (≥10条):\n";
$hasData = array_filter($tableStats, function($item) {
    return $item[1] >= 10;
});
$hasData = array_values($hasData);
foreach ($hasData as $i => $item) {
    if ($i < 30) {
        echo "   " . ($i + 1) . ". {$item[0]}: {$item[1]}条\n";
    }
}
if (count($hasData) > 30) {
    echo "   ... 还有 " . (count($hasData) - 30) . " 张表\n";
}
?>
