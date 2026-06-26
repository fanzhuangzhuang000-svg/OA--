<?php
$api = 'http://127.0.0.1/api';

echo "=== Step 1: Login ===\n";
$ch = curl_init($api . '/auth/login');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'username' => 'admin',
    'password' => 'admin123'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
$loginRes = curl_exec($ch);
$loginCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo "Status: $loginCode\n";
echo "Body: " . substr($loginRes, 0, 300) . "\n\n";

$loginData = json_decode($loginRes, true);
$token = $loginData['token'] ?? $loginData['data']['token'] ?? '';
if (!$token) {
    echo "Login FAILED\n";
    exit(1);
}
echo "Token: " . substr($token, 0, 20) . "...\n\n";

echo "=== Step 2: Wipe Data ===\n";
$ch = curl_init($api . '/admin/wipe-data');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'password' => 'admin123',
    'confirm_phrase' => '确认清空'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Authorization: Bearer ' . $token
]);
$wipeRes = curl_exec($ch);
$wipeCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo "Status: $wipeCode\n";
echo "Body: $wipeRes\n";
