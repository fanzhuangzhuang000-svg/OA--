# admin E2E 测试污染 — 恢复 checklist

## 触发场景
E2E / 手动测试 修改了 `admin` 用户（密码 / 名字 / 角色 / 状态 / 手机号 / 邮箱），测完没回滚 → 用户登录失败（401 用户名或密码错误）

## 标准操作 (SOP)

### 1. 写一个一次性 PHP 修复脚本
**不要**用 tinker inline 命令（多层引号 escape 太痛苦）。直接写 .php 脚本：

```php
<?php
// /tmp/restore_admin.php — 跑完即删
require __DIR__ . '/vendor/autoload.php';
$app = require __DIR__ . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$u = App\Models\User::where('username', 'admin')->first();
if (!$u) { echo "admin not found\n"; exit(1); }

// 1. 打印现场
echo "BEFORE: id={$u->id} name={$u->name} username={$u->username}\n";
echo "old_hash={$u->password}\n";
foreach (['admin123', 'newpass123', 'password'] as $p) {
    echo "verify $p: " . (\Hash::check($p, $u->password) ? 'OK' : 'FAIL') . "\n";
}

// 2. 恢复
$u->password = \Hash::make('admin123');
$u->name     = '系统管理员';
$u->save();

// 3. 验证
$f = $u->fresh();
echo "AFTER : id={$f->id} name={$f->name} password_hash={$f->password}\n";
echo "verify admin123: " . (\Hash::check('admin123', $f->password) ? 'OK' : 'FAIL') . "\n";
```

### 2. 上传 + 跑 + 删 (一气呵成)
```bash
# 本地
python -c "
import paramiko
cli=paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=10)
sftp=cli.open_sftp()
sftp.put(r'C:\local\restore_admin.php', '/tmp/restore_admin.php')
sftp.chmod('/tmp/restore_admin.php', 0o755)
sftp.close()
cli.close()
"

# 服务器
sudo cp /tmp/restore_admin.php /var/www/oa-api/restore_admin.php
sudo chown www-data:www-data /var/www/oa-api/restore_admin.php
cd /var/www/oa-api
sudo -u www-data php restore_admin.php

# 验证
curl -X POST http://172.20.0.139:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# 期望: {"code":0,"message":"登录成功", ...}

# 清理
rm -f /var/www/oa-api/restore_admin.php /tmp/restore_admin.php
```

### 3. 写一行的 alias 加速
`.workbuddy/ssh.py` 已支持多命令，可以一行跑完：

```bash
python ssh.py "sudo cp /tmp/r.php /var/www/oa-api/ && \
  sudo chown www-data:www-data /var/www/oa-api/r.php && \
  cd /var/www/oa-api && sudo -u www-data php r.php && \
  rm -f r.php /tmp/r.php"
```

## 预防（不要再犯！）

| 错误 | 正确做法 |
|---|---|
| 测前不备份 admin 原值 | sql 导出 / 写快照文件 / 抄在脚本注释 |
| 测完不回滚 admin | 测试结束最后一步是 "RESTORE admin to original" |
| 用真实 admin 测 | 创建 `test_admin / test123` 专用测试账号 |
| 改密后忘记改成什么 | 改之前 `echo "OLD: admin123" >> test.log` |

## 快速定位是不是这个 bug
- 后端响应 **401** + message "用户名或密码错误" → 大概率是密码错（看 `AuthController::login` 第 28 行）
- 后端响应 **500** + log 有 "Route [login] not defined" → 是 v0.3.7.1 修过的 401 bug 复发
- 后端响应 **200** 但前端 401 → 是 axios 拦截器或 token 问题

## 相关 skill
- `laravel-pure-api-401.md` — 401 JSON 处理
- `cross-platform-fileops.md` — Windows + Linux 路径转换
