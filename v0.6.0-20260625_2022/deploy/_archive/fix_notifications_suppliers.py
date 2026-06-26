#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix: create Notification model + fix suppliers route order"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S {cmd}', timeout=30)
    return stdout.read().decode('utf-8', errors='replace').strip()

def put_file(path, content):
    sftp = ssh.open_sftp()
    f = sftp.open(path, 'w')
    f.write(content)
    f.close()
    sftp.close()

# 1. Create Notification model
run('chown nbcy:nbcy /var/www/oa-api/app/Models')
put_file('/var/www/oa-api/app/Models/Notification.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class Notification extends Model
{
    protected $table = 'notifications';

    protected $fillable = [
        'type', 'notifiable_type', 'notifiable_id',
        'data', 'read_at',
    ];

    protected $casts = [
        'data' => 'array',
        'read_at' => 'datetime',
    ];

    public function notifiable()
    {
        return $this->morphTo();
    }
}
''')
run('chown www-data:www-data /var/www/oa-api/app/Models/Notification.php')
print("Created Notification model")

# 2. Fix suppliers route order - move suppliers before {project}
run('chown nbcy:nbcy /var/www/oa-api/routes/api.php')
sftp = ssh.open_sftp()
content = sftp.open('/var/www/oa-api/routes/api.php').read().decode('utf-8')
sftp.close()

# Find and reorder: suppliers route should come before {project} route
# Current order: show/{project} -> update/{project} -> stage/{project} -> construction-logs/{project} -> suppliers -> storeSupplier
# Need to move suppliers lines before show

old_projects = """    // 项目管理
    Route::prefix('projects')->group(function () {
        Route::get('/', [ProjectController::class, 'index']);
        Route::post('/', [ProjectController::class, 'store']);
        Route::get('{project}', [ProjectController::class, 'show']);
        Route::put('{project}', [ProjectController::class, 'update']);
        Route::put('{project}/stage', [ProjectController::class, 'updateStage']);
        Route::get('{project}/construction-logs', [ProjectController::class, 'constructionLogs']);
        Route::post('{project}/construction-logs', [ProjectController::class, 'storeConstructionLog']);
        Route::get('suppliers', [ProjectController::class, 'suppliers']);
        Route::post('suppliers', [ProjectController::class, 'storeSupplier']);
    });"""

new_projects = """    // 项目管理
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
    });"""

content = content.replace(old_projects, new_projects)
put_file('/var/www/oa-api/routes/api.php', content)
run('chown www-data:www-data /var/www/oa-api/routes/api.php')
print("Fixed suppliers route order")

# Clear caches
run('php /var/www/oa-api/artisan config:clear')
run('php /var/www/oa-api/artisan cache:clear')
run('php /var/www/oa-api/artisan route:clear')
print("Caches cleared")

ssh.close()
print("Done!")
