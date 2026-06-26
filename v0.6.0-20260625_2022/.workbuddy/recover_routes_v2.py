"""V0.4.2 路由 v2 — 完全对齐实际方法名"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()

v042_block = r'''    // V0.4.2 供应商管理（对齐 SupplierController 实际方法）
    Route::get('suppliers',                  [\App\Http\Controllers\Api\SupplierController::class, 'index']);
    Route::post('suppliers',                 [\App\Http\Controllers\Api\SupplierController::class, 'store']);
    Route::get('suppliers/{id}',             [\App\Http\Controllers\Api\SupplierController::class, 'show'])->where('id', '[0-9]+');
    Route::put('suppliers/{id}',             [\App\Http\Controllers\Api\SupplierController::class, 'update'])->where('id', '[0-9]+');
    Route::delete('suppliers/{id}',          [\App\Http\Controllers\Api\SupplierController::class, 'destroy'])->where('id', '[0-9]+');
    Route::post('suppliers/{id}/change-status',[\App\Http\Controllers\Api\SupplierController::class, 'changeStatus'])->where('id', '[0-9]+');
    Route::post('suppliers/{id}/sync-contacts',[\App\Http\Controllers\Api\SupplierController::class, 'syncContacts'])->where('id', '[0-9]+');
    Route::get('suppliers/{id}/evaluations', [\App\Http\Controllers\Api\SupplierController::class, 'evaluations'])->where('id', '[0-9]+');
    Route::post('suppliers/{id}/evaluations',[\App\Http\Controllers\Api\SupplierController::class, 'addEvaluation'])->where('id', '[0-9]+');

    // V0.4.2 外部报价（对齐 ExternalQuoteController 实际方法）
    Route::get('external/quote-requests',                  [\App\Http\Controllers\Api\ExternalQuoteController::class, 'indexRequests']);
    Route::post('external/quote-requests',                 [\App\Http\Controllers\Api\ExternalQuoteController::class, 'storeRequest']);
    Route::get('external/quote-requests/{id}',             [\App\Http\Controllers\Api\ExternalQuoteController::class, 'showRequest'])->where('id', '[0-9]+');
    Route::post('external/quote-requests/{id}/close',      [\App\Http\Controllers\Api\ExternalQuoteController::class, 'closeRequest'])->where('id', '[0-9]+');
    Route::post('external/quote-requests/{id}/cancel',     [\App\Http\Controllers\Api\ExternalQuoteController::class, 'cancelRequest'])->where('id', '[0-9]+');
    Route::get('external/quote-requests/{id}/quotes',      [\App\Http\Controllers\Api\ExternalQuoteController::class, 'listQuotes'])->where('id', '[0-9]+');
    Route::post('external/quotes/{id}/shortlist',          [\App\Http\Controllers\Api\ExternalQuoteController::class, 'shortlistQuote'])->where('id', '[0-9]+');
    Route::post('external/quotes/{id}/reject',             [\App\Http\Controllers\Api\ExternalQuoteController::class, 'rejectQuote'])->where('id', '[0-9]+');
    Route::post('external/quotes/{id}/award',             [\App\Http\Controllers\Api\ExternalQuoteController::class, 'awardQuote'])->where('id', '[0-9]+');

    // V0.4.2 往来资金（对齐 LedgerController 实际方法）
    Route::get('finance/supplier-payables',         [\App\Http\Controllers\Api\LedgerController::class, 'suppliers']);
    Route::get('finance/supplier-payables/{id}',    [\App\Http\Controllers\Api\LedgerController::class, 'supplierLedger'])->where('id', '[0-9]+');
    Route::get('finance/supplier-payments',         [\App\Http\Controllers\Api\LedgerController::class, 'supplierPayables']);
    Route::post('finance/supplier-payments',        [\App\Http\Controllers\Api\LedgerController::class, 'createSupplierPayment']);
    Route::get('finance/supplier-payments/{id}',    [\App\Http\Controllers\Api\LedgerController::class, 'showSupplierPayment'])->where('id', '[0-9]+');
    Route::get('finance/customer-receivables',      [\App\Http\Controllers\Api\LedgerController::class, 'customers']);
    Route::get('finance/customer-receivables/{id}', [\App\Http\Controllers\Api\LedgerController::class, 'customerLedger'])->where('id', '[0-9]+');
    Route::get('finance/customer-receipts',         [\App\Http\Controllers\Api\LedgerController::class, 'customerReceivables']);
    Route::post('finance/customer-receipts',        [\App\Http\Controllers\Api\LedgerController::class, 'createCustomerReceipt']);
    Route::get('finance/customer-receipts/{id}',    [\App\Http\Controllers\Api\LedgerController::class, 'showCustomerReceipt'])->where('id', '[0-9]+');
    Route::get('finance/summary',                   [\App\Http\Controllers\Api\LedgerController::class, 'summary']);
    Route::get('finance/aging',                     [\App\Http\Controllers\Api\LedgerController::class, 'aging']);

'''
with sftp.file('/tmp/v042_block.txt', 'w') as f:
    f.write(v042_block)

# 移除现有 V0.4.2 块
# 用 sed 找到 V0.4.2 块开始到 admin/wipe-data 之前（删掉）
# 但 250 万行结构下不靠谱
# 简化：直接覆盖 api.php（用本地干净版 + 新块注入）

import os
local_api = r'D:\work\website\OA\pc-api\routes\api.php'
sftp.put(local_api, '/tmp/api_clean.txt')

script = r'''awk '/admin\/wipe-data/ && !done {while ((getline line < "/tmp/v042_block.txt") > 0) print line; close("/tmp/v042_block.txt"); done=1} {print}' /tmp/api_clean.txt > /tmp/api_final.php && cp /tmp/api_final.php /var/www/oa-api/routes/api.php && wc -l /var/www/oa-api/routes/api.php && echo OK'''
si, so, se = ssh.exec_command(script, timeout=60)
print(so.read().decode('utf-8', 'replace').strip())

# 清缓存 + 重启
for c in ['config:clear', 'route:clear', 'cache:clear']:
    si, so, se = ssh.exec_command(f'php /var/www/oa-api/artisan {c}', timeout=30)
    so.read()
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm', timeout=30)
so.read()
print('php-fpm restarted')

# 验证文件
si, so, se = ssh.exec_command('ls -la /var/www/oa-api/routes/api.php', timeout=10)
print(so.read().decode('utf-8', 'replace').strip())

# 验证路由
si, so, se = ssh.exec_command('php -d memory_limit=512M /var/www/oa-api/artisan route:list --path=suppliers 2>&1 | head -20', timeout=60)
print('=== routes suppliers ===')
print(so.read().decode('utf-8', 'replace')[:1500])

sftp.close()
ssh.close()
