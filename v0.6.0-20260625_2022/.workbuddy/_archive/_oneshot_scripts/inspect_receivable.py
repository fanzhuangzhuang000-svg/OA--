import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

cmd = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa << 'EOF'
\\d receivables
SELECT count(*) AS cnt, min(received_date) AS min_d, max(received_date) AS max_d FROM receivables;
SELECT id, project_id, customer_id, amount, received_amount, received_date, status FROM receivables ORDER BY received_date LIMIT 5;
EOF
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
if stderr.read().decode().strip():
    print("STDERR:", stderr.read().decode()[:500])

# service-stats 看是哪个表
cmd2 = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "\\dt" 2>&1 | grep -i -E "service|review|satisfaction" | head -20"""
stdin, stdout, stderr = ssh.exec_command(cmd2)
print("=== service-related tables ===")
print(stdout.read().decode())

ssh.close()
