"""注入 V0.4.1 路由到 172 api.php"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()

# 写路由块到 /tmp
routes_block = '''    // V0.4.1 项目预算（Construction Budget）
    Route::prefix('construction/budgets')->group(function () {
        Route::get('/',                    [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'index']);
        Route::get('/summary/{projectId}', [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'summary'])->where('projectId', '[0-9]+');
        Route::post('/',                   [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'store']);
        Route::get('/{id}',                [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}',                [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'update'])->where('id', '[0-9]+');
        Route::post('/{id}/approve',       [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'approve'])->where('id', '[0-9]+');
        Route::post('/{id}/revise',        [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'revise'])->where('id', '[0-9]+');
        Route::delete('/{id}',             [\\App\\Http\\Controllers\\Api\\Construction\\BudgetController::class, 'destroy'])->where('id', '[0-9]+');
    });

'''

with sftp.file('/tmp/v041_routes.txt', 'w') as f:
    f.write(routes_block)

# 用 awk 在 admin/wipe-data 之前插入
script = r"""awk '/admin\/wipe-data/ && !done {while ((getline line < "/tmp/v041_routes.txt") > 0) print line; close("/tmp/v041_routes.txt"); done=1} {print}' /var/www/oa-api/routes/api.php > /tmp/api_new.php && cp /tmp/api_new.php /var/www/oa-api/routes/api.php && rm /tmp/api_new.php && echo OK"""

si, so, se = ssh.exec_command(script, timeout=30)
out = so.read().decode('utf-8', 'replace').strip()
err = se.read().decode('utf-8', 'replace').strip()
rc = so.channel.recv_exit_status()
print('awk rc:', rc, out, err[:200])

# 验证
si, so, se = ssh.exec_command('grep -n "construction/budgets" /var/www/oa-api/routes/api.php | head -3', timeout=10)
out = so.read().decode('utf-8', 'replace').strip()
print('验证路由:', out)

# 清缓存
si, so, se = ssh.exec_command('php /var/www/oa-api/artisan route:clear && php /var/www/oa-api/artisan config:clear', timeout=30)
print('cache clear:', so.read().decode('utf-8', 'replace')[:200])

# 重启 php-fpm
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=30)
print('restart:', so.read().decode('utf-8', 'replace').strip())

sftp.close()
ssh.close()
