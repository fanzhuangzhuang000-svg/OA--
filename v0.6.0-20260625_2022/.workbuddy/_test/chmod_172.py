import paramiko, sys
sys.path.insert(0, r'D:\work\website\OA\.workbuddy')
import importlib.util
spec = importlib.util.spec_from_file_location('deploy', r'D:\work\website\OA\.workbuddy\deploy_to_172.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ssh = m.ssh_connect()

# 用脚本文件避免转义
script = r'''cat > /tmp/chmod_all.sh <<'BASH_EOF'
#!/bin/bash
# 让 nbcy 用户能读
sudo chmod -R a+rX /var/www/oa-api/app /var/www/oa-api/bootstrap /var/www/oa-api/config /var/www/oa-api/database /var/www/oa-api/database/seeders /var/www/oa-api/database/factories /var/www/oa-api/database/migrations /var/www/oa-api/public /var/www/oa-api/resources /var/www/oa-api/routes /var/www/oa-api/composer.json /var/www/oa-api/artisan 2>/dev/null
sudo chmod -R a+rX /var/www/oa-web 2>/dev/null
echo DONE
BASH_EOF
chmod +x /tmp/chmod_all.sh
bash /tmp/chmod_all.sh
'''
si, so, se = ssh.exec_command(script, timeout=60)
print(so.read().decode())
print('ERR:', se.read().decode()[:300])
ssh.close()
