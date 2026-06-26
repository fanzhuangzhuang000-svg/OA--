import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 拿所有表 + 行数
cmd = r"""
export PGPASSWORD='oa_pg_pwd_782997781'
psql -U oa_user -d security_oa -t -A -F'|' -c "
SELECT
  c.relname AS table_name,
  c.reltuples::bigint AS estimated_rows
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = 'public'
ORDER BY c.reltuples DESC, c.relname;
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
print("ALL TABLES (table | estimated_rows):")
print(out)

# 2. 实际 count（reltuples 不准）
print("\n=== ACTUAL COUNTS (sorted ascending) ===")
tables = [line.split('|')[0] for line in out.strip().split('\n') if line.strip()]
results = []
for t in tables:
    cmd = f"export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -t -A -c \"SELECT count(*) FROM {t};\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    cnt = stdout.read().decode().strip()
    results.append((t, int(cnt) if cnt.isdigit() else 0))

results.sort(key=lambda x: x[1])
print(f"{'TABLE':<45} {'ROWS':>8}")
print('-' * 55)
for t, c in results:
    flag = ' <-- EMPTY' if c == 0 else (' <-- SPARSE' if c < 10 else '')
    print(f"{t:<45} {c:>8}{flag}")

ssh.close()
