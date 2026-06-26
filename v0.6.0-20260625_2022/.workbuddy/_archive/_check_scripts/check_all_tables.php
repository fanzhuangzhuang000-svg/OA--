<?php
/**
 * 检查所有表的数据量
 * 使用方法：php check_all_tables.php
 */

// 数据库连接配置
$host = '127.0.0.1';
$port = '5432';
$dbname = 'security_oa';
$username = 'postgres';  // 使用postgres用户，不需要密码

// 连接数据库
$dbh = pg_connect("host=$host port=$port dbname=$dbname user=$username");
if (!$dbh) {
    die("数据库连接失败\n");
}

// 获取所有表
$result = pg_query($dbh, "
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    ORDER BY tablename
");
$tables = [];
while ($row = pg_fetch_assoc($result)) {
    $tables[] = $row['tablename'];
}

echo "找到 " . count($tables) . " 张表\n\n";

$emptyTables = [];
$lowDataTables = [];
$tableStats = [];

foreach ($tables as $table) {
    $result = pg_query($dbh, "SELECT COUNT(*) as cnt FROM \"$table\"");
    if ($result) {
        $row = pg_fetch_assoc($result);
        $count = (int)$row['cnt'];
        $tableStats[] = [$table, $count];
        
        if ($count == 0) {
            $emptyTables[] = $table;
        } elseif ($count < 10) {
            $lowDataTables[] = [$table, $count];
        }
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

pg_close($dbh);
?>
