"""修复 KnowledgeCategory::articles 外键（152 服务器）"""
import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

sftp = c.open_sftp()

# 1. 读原文件
with sftp.open('/var/www/oa-api/app/Models/OtherModels.php', 'r') as f:
    content = f.read().decode('utf-8')

# 2. 替换
old = "public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class); }"
new = "public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class, 'category_id'); }"
new_content = content.replace(old, new)
print('CHANGED:', content != new_content, 'OLD found:', content.count(old))

# 3. 通过 sudo tee 写回（sftp 写 www-data owner 没权限）
import tempfile
with tempfile.NamedTemporaryFile('w', suffix='.php', delete=False, encoding='utf-8') as tf:
    tf.write(new_content)
    local = tf.name

# 上传到 /tmp
sftp.put(local, '/tmp/OtherModels.php')

# sudo cp 覆盖
si, so, se = c.exec_command('sudo cp /tmp/OtherModels.php /var/www/oa-api/app/Models/OtherModels.php && sudo chown www-data:www-data /var/www/oa-api/app/Models/OtherModels.php && rm /tmp/OtherModels.php && echo OK', timeout=30)
print('cp:', so.read().decode('utf-8', errors='ignore'))
sftp.close()

# 4. 验证
si, so, se = c.exec_command('grep -A 1 "function articles" /var/www/oa-api/app/Models/OtherModels.php | head -4', timeout=30)
print('verify:', so.read().decode('utf-8', errors='ignore'))

# 5. 重启 fpm + 清 log
si, so, se = c.exec_command('sudo systemctl restart php8.3-fpm && sudo -u www-data sh -c "> /var/www/oa-api/storage/logs/laravel.log" && echo DONE', timeout=30)
print('restart:', so.read().decode('utf-8', errors='ignore'))

c.close()
