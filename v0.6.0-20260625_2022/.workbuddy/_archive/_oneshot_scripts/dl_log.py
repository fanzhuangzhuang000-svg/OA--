import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
sftp = ssh.open_sftp()
sftp.get('/var/www/oa-api/storage/logs/laravel.log', 'D:/work/website/OA/.workbuddy/laravel.log')
sftp.close()
print('downloaded')
ssh.close()
