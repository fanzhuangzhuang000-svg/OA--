import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 远程读 DashboardController 关键方法
cmds = [
    "wc -l /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php",
    "echo '=== projectProgress method ==='",
    "sed -n '/function projectProgress/,/^    }/p' /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php | head -60",
    "echo '=== todo method ==='",
    "sed -n '/function todo/,/^    }/p' /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php | head -60",
    "echo '=== serviceStats method ==='",
    "sed -n '/function serviceStats/,/^    }/p' /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php | head -60",
    "echo '=== revenueTrend method ==='",
    "sed -n '/function revenueTrend/,/^    }/p' /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php | head -60",
    "echo '=== stats method ==='",
    "sed -n '/function stats/,/^    }/p' /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php | head -100",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out)
    if err.strip():
        print("ERR:", err[:300])

ssh.close()
