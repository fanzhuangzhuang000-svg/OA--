#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix model foreign key names via sed"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S {cmd}', timeout=30)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Fix DiskFolder.files() foreign key
run('sed -i \'s/hasMany(DiskFile::class)/hasMany(DiskFile::class, "folder_id")/\' /var/www/oa-api/app/Models/OtherModels.php')
print("Fixed DiskFolder.files()")

# Fix KnowledgeCategory.articles() foreign key
run('sed -i \'s/hasMany(KnowledgeArticle::class)/hasMany(KnowledgeArticle::class, "category_id")/\' /var/www/oa-api/app/Models/OtherModels.php')
print("Fixed KnowledgeCategory.articles()")

# Verify changes
result = run('grep -n "hasMany(DiskFile\\|hasMany(KnowledgeArticle" /var/www/oa-api/app/Models/OtherModels.php')
print(f"Verify: {result}")

# Clear caches
run('php /var/www/oa-api/artisan config:clear')
run('php /var/www/oa-api/artisan cache:clear')
run('php /var/www/oa-api/artisan route:clear')
print("Caches cleared")

ssh.close()
print("Done!")
