import paramiko, sys, io

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 先 list tables (用 -A 拿纯文本，无边框)
cmd = r"""export PGPASSWORD='oa_pg_pwd_782997781'
psql -U oa_user -d security_oa -t -A -c "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname='public' ORDER BY c.relname;" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(cmd)
tables_raw = stdout.read().decode('utf-8', errors='replace')
tables = [t.strip() for t in tables_raw.split('\n') if t.strip()]

print(f"Found {len(tables)} tables")
print("Sample:", tables[:5])

# 强制 UTF-8 输出 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

results = []
for t in tables:
    cmd = f"export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -t -A -c \"SELECT count(*) FROM {t};\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    cnt = stdout.read().decode('utf-8', errors='replace').strip()
    try:
        n = int(cnt)
    except:
        n = -1
    results.append((t, n))

results.sort(key=lambda x: x[1])
print(f"\n{'TABLE':<45} {'ROWS':>8}")
print('-' * 55)
for t, c in results:
    flag = ''
    if c == 0: flag = '  <== EMPTY'
    elif c < 10: flag = '  <== SPARSE'
    print(f"{t:<45} {c:>8}{flag}")

empty = [t for t,c in results if c == 0]
sparse = [t for t,c in results if 0 < c < 10]
print(f"\nSummary: {len(empty)} empty, {len(sparse)} sparse, {len(tables)-len(empty)-len(sparse)} ok")

ssh.close()
