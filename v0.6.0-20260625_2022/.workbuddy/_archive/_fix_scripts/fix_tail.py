import paramiko, sys, io
host='172.20.0.139'; user='nbcy'; pwd='admin123'; port=22
cli=paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(host, port=port, username=user, password=pwd, timeout=10, banner_timeout=10, auth_timeout=10)

def run(c, timeout=30, stdin=None):
    sin, sout, serr = cli.exec_command(c, timeout=timeout)
    if stdin is not None:
        sin.write(stdin)
        sin.channel.shutdown_write()
    out = sout.read().decode('utf-8','replace')
    err = serr.read().decode('utf-8','replace')
    if out: print(out)
    if err: print('[STDERR]', err)
    return out, err

# 1) Build new content locally
new_routes = """    // 项目管理
    Route::prefix('projects')->group(function () {
        Route::get('/', [ProjectController::class, 'index']);
        Route::post('/', [ProjectController::class, 'store']);
        // 注意: 静态路径必须放在 {project} 之前, 否则会被路由参数吞掉
        Route::get('suppliers', [ProjectController::class, 'suppliers']);
        Route::post('suppliers', [ProjectController::class, 'storeSupplier']);
        Route::get('{project}', [ProjectController::class, 'show']);
        Route::put('{project}', [ProjectController::class, 'update']);
        Route::put('{project}/stage', [ProjectController::class, 'updateStage']);
        Route::get('{project}/construction-logs', [ProjectController::class, 'constructionLogs']);
        Route::post('{project}/construction-logs', [ProjectController::class, 'storeConstructionLog']);
        // 补充: 项目维度下的供应商/合同
        Route::get('{project}/suppliers', [ProjectController::class, 'projectSuppliers']);
        Route::get('{project}/contracts', [ProjectController::class, 'projectContracts']);
    });"""

# 2) Replace block on the server using sed in-place via sudo tee
run("sudo cp /var/www/oa-api/routes/api.php /var/www/oa-api/routes/api.php.bak.$(date +%s)")

# Use Python heredoc replacement via sudo python3 to avoid escaping nightmares
script = r"""
import re, sys
p = '/var/www/oa-api/routes/api.php'
old = '''    // 项目管理
    Route::prefix('projects')->group(function () {
        Route::get('/', [ProjectController::class, 'index']);
        Route::post('/', [ProjectController::class, 'store']);
        Route::get('suppliers', [ProjectController::class, 'suppliers']);
        Route::post('suppliers', [ProjectController::class, 'storeSupplier']);
        Route::get('{project}', [ProjectController::class, 'show']);
        Route::put('{project}', [ProjectController::class, 'update']);
        Route::put('{project}/stage', [ProjectController::class, 'updateStage']);
        Route::get('{project}/construction-logs', [ProjectController::class, 'constructionLogs']);
        Route::post('{project}/construction-logs', [ProjectController::class, 'storeConstructionLog']);
    });'''
new = '''    // 项目管理
    Route::prefix('projects')->group(function () {
        Route::get('/', [ProjectController::class, 'index']);
        Route::post('/', [ProjectController::class, 'store']);
        // 注意: 静态路径必须放在 {project} 之前, 否则会被路由参数吞掉
        Route::get('suppliers', [ProjectController::class, 'suppliers']);
        Route::post('suppliers', [ProjectController::class, 'storeSupplier']);
        Route::get('{project}', [ProjectController::class, 'show']);
        Route::put('{project}', [ProjectController::class, 'update']);
        Route::put('{project}/stage', [ProjectController::class, 'updateStage']);
        Route::get('{project}/construction-logs', [ProjectController::class, 'constructionLogs']);
        Route::post('{project}/construction-logs', [ProjectController::class, 'storeConstructionLog']);
        // 补充: 项目维度下的供应商/合同
        Route::get('{project}/suppliers', [ProjectController::class, 'projectSuppliers']);
        Route::get('{project}/contracts', [ProjectController::class, 'projectContracts']);
    });'''
s = open(p).read()
if old in s:
    open(p,'w').write(s.replace(old, new, 1))
    print('routes.php: replaced OK')
else:
    print('routes.php: old block NOT FOUND'); sys.exit(2)
"""
# Write script to /tmp on server via sftp (use nbcy's home for staging)
sftp = cli.open_sftp()
with sftp.open('/tmp/_patch.py', 'w') as f:
    f.write(script)
sftp.close()
run("sudo cp /tmp/_patch.py /var/www/oa-api/storage/_patch.py && sudo chown www-data:www-data /var/www/oa-api/storage/_patch.py && sudo -u www-data python3 /var/www/oa-api/storage/_patch.py")
run("sudo rm -f /var/www/oa-api/storage/_patch.py /tmp/_patch.py")

# 3) Patch ProjectModels.php - fix paymentNodes FK
script2 = r"""
p = '/var/www/oa-api/app/Models/ProjectModels.php'
s = open(p).read()
old3 = "    public function paymentNodes(): HasMany { return $this->hasMany(ContractPaymentNode::class); }"
new3 = "    public function paymentNodes(): HasMany { return $this->hasMany(ContractPaymentNode::class, 'contract_id'); }"
if old3 in s:
    open(p,'w').write(s.replace(old3, new3, 1))
    print('ProjectModels.php: replaced OK')
else:
    print('ProjectModels.php: not found'); raise SystemExit(3)
"""
sftp = cli.open_sftp()
with sftp.open('/tmp/_patch2.py', 'w') as f:
    f.write(script2)
sftp.close()
run("sudo cp /tmp/_patch2.py /var/www/oa-api/storage/_patch2.py && sudo chown www-data:www-data /var/www/oa-api/storage/_patch2.py && sudo -u www-data python3 /var/www/oa-api/storage/_patch2.py")
run("sudo rm -f /var/www/oa-api/storage/_patch2.py /tmp/_patch2.py")

# 4) Append projectSuppliers / projectContracts to ProjectController
script3 = r"""
p = '/var/www/oa-api/app/Http/Controllers/Api/ProjectController.php'
s = open(p).read()
if 'projectSuppliers' in s:
    print('ProjectController.php: already has methods, skipping')
else:
    addition = '''
    public function projectSuppliers(Project $project): JsonResponse
    {
        $supplierIds = PurchaseOrder::where('project_id', $project->id)->pluck('supplier_id')->unique();
        return response()->json(['code' => 0, 'data' => Supplier::whereIn('id', $supplierIds)->get()]);
    }

    public function projectContracts(Project $project): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => $project->contract()->with('paymentNodes')->get()]);
    }
}
'''
    s2 = s.rstrip()
    if s2.endswith('}'):
        s2 = s2[:-1] + addition
    else:
        s2 = s + addition
    open(p,'w').write(s2)
    print('ProjectController.php: appended')
"""
sftp = cli.open_sftp()
with sftp.open('/tmp/_patch3.py', 'w') as f:
    f.write(script3)
sftp.close()
run("sudo cp /tmp/_patch3.py /var/www/oa-api/storage/_patch3.py && sudo chown www-data:www-data /var/www/oa-api/storage/_patch3.py && sudo -u www-data python3 /var/www/oa-api/storage/_patch3.py")
run("sudo rm -f /var/www/oa-api/storage/_patch3.py /tmp/_patch3.py")

# 5) Clear caches + reload php-fpm
run("cd /var/www/oa-api && sudo -u www-data php artisan route:clear 2>&1 | tail -3")
run("cd /var/www/oa-api && sudo -u www-data php artisan config:clear 2>&1 | tail -3")
run("cd /var/www/oa-api && sudo -u www-data php artisan cache:clear 2>&1 | tail -3")
run("sudo systemctl reload php8.3-fpm 2>&1 | tail -2")

cli.close()
print("\nALL DONE.")
