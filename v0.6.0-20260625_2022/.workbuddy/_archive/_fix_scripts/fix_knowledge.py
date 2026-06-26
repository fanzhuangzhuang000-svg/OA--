import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

# 用 sftp 下载文件
sftp = ssh.open_sftp()
local = 'D:/work/website/OA/.workbuddy/OtherModels.php'
sftp.get('/var/www/oa-api/app/Models/OtherModels.php', local)
sftp.close()
print('downloaded OtherModels.php')

# 本地读 + 替换
with open(local, 'r', encoding='utf-8') as f:
    content = f.read()

old = "public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class); }"
new = "public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class, 'category_id'); }"

if old in content:
    content = content.replace(old, new)
    with open(local, 'w', encoding='utf-8') as f:
        f.write(content)
    print('replaced OK')
else:
    print('NOT FOUND - check file content')
    # 找下 articles 周围的代码
    import re
    for m in re.finditer(r'function articles.{0,200}', content):
        print('FOUND:', repr(m.group(0)))

ssh.close()
