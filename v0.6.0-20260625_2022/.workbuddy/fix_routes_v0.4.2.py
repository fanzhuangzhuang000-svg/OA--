"""修路由对齐 LedgerController 实际方法 + SupplierController 关系"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)

# 删旧 V0.4.2 路由块（行 832-880 范围），重写
sftp = ssh.open_sftp()
# 拉回 api.php 本地改
import io
with sftp.open('/var/www/oa-api/routes/api.php', 'r') as f:
    content = f.read().decode('utf-8')

# 找 V0.4.2 块并替换
import re
# 匹配从 "// V0.4.2 供应商管理" 到 "// V0.4.2 往来资金" 之前
pattern = r'    // V0.4.2 供应商管理.*?(?=    // V0.4.2 往来资金|    // ========== admin)'
new_block = r'''    // V0.4.2 供应商管理（基础 CRUD）
    Route::get('suppliers',               [\App\Http\Controllers\Api\SupplierController::class, 'index']);
    Route::post('suppliers',              [\App\Http\Controllers\Api\SupplierController::class, 'store']);
    Route::get('suppliers/{id}',          [\App\Http\Controllers\Api\SupplierController::class, 'show'])->where('id', '[0-9]+');
    Route::put('suppliers/{id}',          [\App\Http\Controllers\Api\SupplierController::class, 'update'])->where('id', '[0-9]+');
    Route::delete('suppliers/{id}',       [\App\Http\Controllers\Api\SupplierController::class, 'destroy'])->where('id', '[0-9]+');
    Route::get('suppliers/{id}/contacts',      [\App\Http\Controllers\Api\SupplierController::class, 'contacts'])->where('id', '[0-9]+');
    Route::post('suppliers/{id}/contacts',     [\App\Http\Controllers\Api\SupplierController::class, 'addContact'])->where('id', '[0-9]+');
    Route::get('suppliers/{id}/evaluations',   [\App\Http\Controllers\Api\SupplierController::class, 'evaluations'])->where('id', '[0-9]+');
    Route::post('suppliers/{id}/evaluations',  [\App\Http\Controllers\Api\SupplierController::class, 'addEvaluation'])->where('id', '[0-9]+');
    Route::get('suppliers/{id}/attachments',   [\App\Http\Controllers\Api\SupplierController::class, 'attachments'])->where('id', '[0-9]+');

    // V0.4.2 外部报价（管理端）
    Route::get('external/quote-requests',                  [\App\Http\Controllers\Api\ExternalQuoteController::class, 'index']);
    Route::post('external/quote-requests',                 [\App\Http\Controllers\Api\ExternalQuoteController::class, 'store']);
    Route::get('external/quote-requests/{id}',             [\App\Http\Controllers\Api\ExternalQuoteController::class, 'show'])->where('id', '[0-9]+');
    Route::post('external/quote-requests/{id}/invite',     [\App\Http\Controllers\Api\ExternalQuoteController::class, 'invite'])->where('id', '[0-9]+');
    Route::post('external/quote-requests/{id}/close',      [\App\Http\Controllers\Api\ExternalQuoteController::class, 'close'])->where('id', '[0-9]+');
    Route::get('external/quote-requests/{id}/quotes',      [\App\Http\Controllers\Api\ExternalQuoteController::class, 'listQuotes'])->where('id', '[0-9]+');
    Route::post('external/quote-requests/{id}/award',      [\App\Http\Controllers\Api\ExternalQuoteController::class, 'award'])->where('id', '[0-9]+');
    Route::post('external/quotes', [\App\Http\Controllers\Api\ExternalQuoteController::class, 'submitQuote'])
        ->middleware(\App\Http\Middleware\SupplierOnly::class);

    // V0.4.2 供应商门户（SupplierOnly）
    Route::prefix('supplier-portal')->middleware(\App\Http\Middleware\SupplierOnly::class)->group(function () {
        Route::get('invitations',   [\App\Http\Controllers\Api\SupplierPortalController::class, 'invitations']);
        Route::get('my-quotes',     [\App\Http\Controllers\Api\SupplierPortalController::class, 'myQuotes']);
        Route::get('my-contracts',  [\App\Http\Controllers\Api\SupplierPortalController::class, 'myContracts']);
        Route::get('profile',       [\App\Http\Controllers\Api\SupplierPortalController::class, 'profile']);
    });

    // V0.4.2 往来资金（对齐 LedgerController 实际方法）
    Route::get('finance/supplier-payables',        [\App\Http\Controllers\Api\LedgerController::class, 'suppliers']);
    Route::get('finance/supplier-payables/{id}',   [\App\Http\Controllers\Api\LedgerController::class, 'supplierLedger'])->where('id', '[0-9]+');
    Route::get('finance/supplier-payments',        [\App\Http\Controllers\Api\LedgerController::class, 'supplierPayables']);
    Route::post('finance/supplier-payments',       [\App\Http\Controllers\Api\LedgerController::class, 'createSupplierPayment']);
    Route::get('finance/customer-receivables',     [\App\Http\Controllers\Api\LedgerController::class, 'customers']);
    Route::get('finance/customer-receivables/{id}',[\App\Http\Controllers\Api\LedgerController::class, 'customerLedger'])->where('id', '[0-9]+');
    Route::get('finance/customer-receipts',        [\App\Http\Controllers\Api\LedgerController::class, 'customerReceivables']);
    Route::post('finance/customer-receipts',       [\App\Http\Controllers\Api\LedgerController::class, 'createCustomerReceipt']);
    Route::get('finance/summary',                  [\App\Http\Controllers\Api\LedgerController::class, 'summary']);
    Route::get('finance/aging',                    [\App\Http\Controllers\Api\LedgerController::class, 'aging']);
    Route::get('finance/overdue-alerts',           [\App\Http\Controllers\Api\LedgerController::class, 'overdueAlerts']);
    Route::get('finance/warranty-receivables',     [\App\Http\Controllers\Api\LedgerController::class, 'warrantyReceivables']);

'''
new_content = content.replace(content[content.find('    // V0.4.2'):content.find('    // ========== admin')], new_block)

# 写回
with sftp.open('/var/www/oa-api/routes/api.php', 'w') as f:
    f.write(new_content)

print('routes updated')

# 清缓存 + 重启
for c in ['config:clear', 'route:clear', 'cache:clear']:
    si, so, se = ssh.exec_command(f'php /var/www/oa-api/artisan {c}', timeout=30)
    so.read()

si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm', timeout=30)
so.read()

# 验证
si, so, se = ssh.exec_command('php /var/www/oa-api/artisan route:list --path=suppliers 2>&1 | head -15', timeout=30)
print('routes:')
print(so.read().decode('utf-8', 'replace')[:1500])
sftp.close()
ssh.close()
