<?php
$json_path = "/var/www/oa-api/composer.json";
$content = file_get_contents($json_path);
$data = json_decode($content, true);

if (!isset($data['autoload']['files'])) {
    $data['autoload']['files'] = array(
        "app/Http/Controllers/Api/ModuleControllers.php",
        "app/Models/CoreModels.php",
        "app/Models/ProjectModels.php",
        "app/Models/ServiceModels.php",
        "app/Models/OtherModels.php"
    );
    file_put_contents($json_path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n");
    echo "OK: files autoload added";
} else {
    echo "OK: files autoload already exists";
}
?>
