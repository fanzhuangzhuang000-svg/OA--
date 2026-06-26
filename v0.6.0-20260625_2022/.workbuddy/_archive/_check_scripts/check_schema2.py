import paramiko, re
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 读 .env 拿 DB 密码
stdin, stdout, stderr = ssh.exec_command('sudo grep -E "^DB_" /var/www/oa-api/.env 2>&1')
print("=== .env DB ===")
print(stdout.read().decode('utf-8', errors='ignore'))
# 看后端 KnowledgeCategory / KnowledgeArticle model
stdin, stdout, stderr = ssh.exec_command('sudo grep -rn "knowledge_category_id\\|category_id" /var/www/oa-api/app/Models/ 2>/dev/null')
print("\n=== category_id refs ===")
print(stdout.read().decode('utf-8', errors='ignore'))
# 看 model 完整定义
stdin, stdout, stderr = ssh.exec_command('sudo find /var/www/oa-api/app/Models -name "Knowledge*" -exec cat {} \\;')
print("\n=== Knowledge models ===")
print(stdout.read().decode('utf-8', errors='ignore')[:5000])
ssh.close()
