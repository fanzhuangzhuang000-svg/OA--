"""注入 V0.4.2 路由到 172 api.php + Middleware 注册"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()

# 1. 路由块
routes_block = '''    // V0.4.2 供应商管理
    Route::prefix('suppliers')->group(function () {
        Route::get('/',                    [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'index']);
        Route::post('/',                   [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'store']);
        Route::get('/{id}',                [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}',                [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'update'])->where('id', '[0-9]+');
        Route::delete('/{id}',             [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'destroy'])->where('id', '[0-9]+');
        Route::get('/{id}/contacts',       [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'contacts'])->where('id', '[0-9]+');
        Route::post('/{id}/contacts',      [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'addContact'])->where('id', '[0-9]+');
        Route::get('/{id}/evaluations',    [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'evaluations'])->where('id', '[0-9]+');
        Route::post('/{id}/evaluations',   [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'addEvaluation'])->where('id', '[0-9]+');
        Route::get('/{id}/attachments',    [\\App\\Http\\Controllers\\Api\\SupplierController::class, 'attachments'])->where('id', '[0-9]+');
    });

    // V0.4.2 外部报价（需供应商登录才能 POST，前端走 supplier-portal）
    Route::prefix('external')->group(function () {
        Route::get('/quote-requests',                       [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'index']);
        Route::post('/quote-requests',                      [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'store']);
        Route::get('/quote-requests/{id}',                  [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'show'])->where('id', '[0-9]+');
        Route::post('/quote-requests/{id}/invite',          [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'invite'])->where('id', '[0-9]+');
        Route::post('/quote-requests/{id}/close',           [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'close'])->where('id', '[0-9]+');
        Route::get('/quote-requests/{id}/quotes',           [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'listQuotes'])->where('id', '[0-9]+');
        Route::post('/quote-requests/{id}/award',           [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'award'])->where('id', '[0-9]+');
    });

    // V0.4.2 供应商门户（用 SupplierOnly 中间件）
    Route::prefix('supplier-portal')->middleware(\\App\\Http\\Middleware\\SupplierOnly::class)->group(function () {
        Route::get('/invitations',      [\\App\\Http\\Controllers\\Api\\SupplierPortalController::class, 'invitations']);
        Route::get('/my-quotes',        [\\App\\Http\\Controllers\\Api\\SupplierPortalController::class, 'myQuotes']);
        Route::get('/my-contracts',     [\\App\\Http\\Controllers\\Api\\SupplierPortalController::class, 'myContracts']);
        Route::get('/profile',          [\\App\\Http\\Controllers\\Api\\SupplierPortalController::class, 'profile']);
    });

    // V0.4.2 供应商提交报价（supplier-only）
    Route::post('/external/quotes', [\\App\\Http\\Controllers\\Api\\ExternalQuoteController::class, 'submitQuote'])
        ->middleware(\\App\\Http\\Middleware\\SupplierOnly::class);

    // V0.4.2 往来资金（供应商总账 / 客户总账 / 应收应付 / 收付款）
    Route::prefix('finance')->group(function () {
        Route::get('/supplier-ledger',          [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'supplierLedger']);
        Route::get('/customer-ledger',          [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'customerLedger']);
        Route::get('/supplier-payables',        [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'supplierPayables']);
        Route::get('/customer-receivables',     [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'customerReceivables']);
        Route::get('/warranty-receivables',     [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'warrantyReceivables']);
        Route::get('/overdue-alerts',           [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'overdueAlerts']);
        Route::get('/supplier-payments/{payableId}', [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'supplierPayments'])->where('payableId', '[0-9]+');
        Route::get('/customer-receipts/{receivableId}', [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'customerReceipts'])->where('receivableId', '[0-9]+');
        Route::post('/supplier-payments',       [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'createSupplierPayment']);
        Route::post('/customer-receipts',       [\\App\\Http\\Controllers\\Api\\LedgerController::class, 'createCustomerReceipt']);
    });

'''

with sftp.file('/tmp/v042_routes.txt', 'w') as f:
    f.write(routes_block)

# 用 awk 在 admin/wipe-data 之前插入
script = r"""awk '/admin\/wipe-data/ && !done {while ((getline line < "/tmp/v042_routes.txt") > 0) print line; close("/tmp/v042_routes.txt"); done=1} {print}' /var/www/oa-api/routes/api.php > /tmp/api_new.php && cp /tmp/api_new.php /var/www/oa-api/routes/api.php && rm /tmp/api_new.php && echo ROUTES_INJECTED"""

si, so, se = ssh.exec_command(script, timeout=30)
print('routes inject:', so.read().decode('utf-8', 'replace').strip())
si, so, se = ssh.exec_command('grep -c "V0.4.2" /var/www/oa-api/routes/api.php', timeout=10)
print('V0.4.2 count in api.php:', so.read().decode('utf-8', 'replace').strip())

# 2. 清缓存 + 重启
for c in ['config:clear', 'route:clear', 'cache:clear']:
    si, so, se = ssh.exec_command(f'php /var/www/oa-api/artisan {c}', timeout=30)
    print(f'{c}:', so.read().decode('utf-8', 'replace').strip()[:50])

si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=30)
print('php-fpm:', so.read().decode('utf-8', 'replace').strip())

# 3. 验证路由表
si, so, se = ssh.exec_command('php /var/www/oa-api/artisan route:list --path=suppliers 2>&1 | head -15', timeout=30)
print('\n=== 路由验证 ===')
print(so.read().decode('utf-8', 'replace')[:800])

sftp.close()
ssh.close()
