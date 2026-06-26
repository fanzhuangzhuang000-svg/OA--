<?php
$path = "/var/www/oa-api/composer.json";
$c = json_decode(file_get_contents($path), true);

// 加 files 段 (rsync 时丢了)
if (!isset($c["autoload"]["files"])) {
    $c["autoload"]["files"] = [];
}
$files = [
    "app/Http/Controllers/Api/ModuleControllers.php",
    "app/Models/CoreModels.php",
    "app/Models/ProjectModels.php",
    "app/Models/ServiceModels.php",
    "app/Models/OtherModels.php"
];
foreach ($files as $f) {
    if (!in_array($f, $c["autoload"]["files"])) {
        $c["autoload"]["files"][] = $f;
    }
}

file_put_contents($path, json_encode($c, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
echo "Patched: " . count($c["autoload"]["files"]) . " files in autoload\n";
print_r($c["autoload"]["files"]);
