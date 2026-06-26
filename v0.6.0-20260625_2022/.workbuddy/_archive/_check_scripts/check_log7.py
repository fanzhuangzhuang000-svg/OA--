import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 整文件 220 行 + 找 :id 错误附近
stdin, stdout, stderr = ssh.exec_command('wc -l /var/www/oa-api/storage/logs/laravel.log')
print('lines:', stdout.read().decode())
# 用 awk 取每次 :id 错误前 10 行
cmd = """awk '/invalid input syntax for type bigint: ":id"/{print "---FOUND---"; for(i=NR-10;i<NR+3;i++) print arr[i]%1==0?arr[i]:arr[i]; print arr[NR]} {arr[NR]=$0}' /var/www/oa-api/storage/logs/laravel.log | tail -80"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print('=== :id context ===')
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
