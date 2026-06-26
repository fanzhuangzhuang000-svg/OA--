✅ 前端已部署到 172.20.0.139

=== 当前状态 ===
1. ✅ 前端登录页面已更新：
   - 演示密码改为 admin123
   - 增加了密码提示（登录按钮下方）
   - 加强了阻止浏览器自动填充（autocomplete="off"）

2. ✅ 前端文件已上传到 /var/www/oa-web

3. ❌ admin 用户密码未更新（自动更新失败）

=== 请手动更新密码 ===

方法1：SSH 到服务器手动运行
--------------------------------
ssh nbcy@172.20.0.139
# 输入密码: admin123

# 创建密码更新脚本
cat > /tmp/update_pwd.php << 'EOF'
<?php
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
use App\Models\User;
$user = User::where('username', 'admin')->first();
if ($user) {
    $user->password = bcrypt('admin123');
    $user->save();
    echo "✅ 密码已更新为 admin123\n";
} else {
    echo "❌ 未找到 admin 用户\n";
}
EOF

# 复制到 Laravel 目录
sudo cp /tmp/update_pwd.php /var/www/oa-api/
sudo chown www-data:www-data /var/www/oa-api/update_pwd.php

# 运行脚本
cd /var/www/oa-api
sudo -u www-data php update_pwd.php

# 删除临时脚本
rm /tmp/update_pwd.php
rm /var/www/oa-api/update_pwd.php
--------------------------------


方法2：如果可以登录系统，在 UI 中修改
--------------------------------
1. 使用旧密码登录（Admin@2026）
2. 进入"系统设置" → "用户管理"
3. 编辑 admin 用户，修改密码为 admin123


=== 请测试 ===
1. 清除浏览器缓存 (Ctrl+F5)
2. 访问 http://172.20.0.139
3. 尝试登录：
   - 如果旧密码 Admin@2026 可以登录 → 用方法2修改密码
   - 如果旧密码不行 → 用方法1手动更新密码
4. 检查密码提示是否显示
5. 检查是否还有自动填充
