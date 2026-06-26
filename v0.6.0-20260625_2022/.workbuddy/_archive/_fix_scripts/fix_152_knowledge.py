"""修复 KnowledgeCategory::articles 外键（152 服务器）"""
import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

# 1. 直接传文件
old_str = "public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class); }"
new_str = "public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class, 'category_id'); }"

# 用 perl 替换（比 sed 更安全）
script = f"""
cd /var/www/oa-api
perl -i -pe 's|hasMany\\(KnowledgeArticle::class\\)|hasMany(KnowledgeArticle::class, \\x27category_id\\x27)|g' app/Models/OtherModels.php
grep -A 1 'public function articles' app/Models/OtherModels.php | head -5
"""
si, so, se = c.exec_command(script, timeout=30)
print(so.read().decode('utf-8', errors='ignore'))

# 2. 重启 fpm + 清 log
script2 = """
sudo systemctl restart php8.3-fpm
> /var/www/oa-api/storage/logs/laravel.log
echo OK
"""
si, so, se = c.exec_command(script2, timeout=30)
print('restart:', so.read().decode('utf-8', errors='ignore'))

c.close()
