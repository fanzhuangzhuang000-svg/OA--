<?php
$env_path = "/var/www/oa-api/.env";
$content = file_get_contents($env_path);

// 删除所有 CACHE_DRIVER 和 SESSION_DRIVER 行
$lines = explode("\n", $content);
$new_lines = [];
foreach ($lines as $line) {
    if (strpos(trim($line), 'CACHE_DRIVER=') === 0) continue;
    if (strpos(trim($line), 'SESSION_DRIVER=') === 0) continue;
    $new_lines[] = $line;
}
$new_lines[] = "CACHE_DRIVER=file";
$new_lines[] = "SESSION_DRIVER=file";
$content = implode("\n", $new_lines);
file_put_contents($env_path, $content);
echo "OK: CACHE_DRIVER=file, SESSION_DRIVER=file";
?>
