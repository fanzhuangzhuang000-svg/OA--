#!/usr/bin/env python3
"""
阶段 1 第 1 步：扫描 172 端所有表当前数据量
输出: data_gen/01_scan_report.txt
"""
import paramiko
import sys

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'admin123'
DB = 'security_oa'
DB_USER = 'oa_user'
DB_PASS = 'oa_pg_pwd_782997781'

def ssh_exec(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    # 1. 列出所有业务表（排除框架表）
    sql_list_tables = """
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
      AND tablename NOT IN ('migrations', 'failed_jobs', 'jobs', 'cache', 'cache_locks', 'sessions', 'password_reset_tokens')
      AND tablename NOT LIKE 'spatie_%'
      AND tablename NOT LIKE '%_pivot'
    ORDER BY tablename;
    """
    cmd_list = f"PGPASSWORD={DB_PASS} psql -U {DB_USER} -d {DB} -t -A -c \"{sql_list_tables}\""
    tables = [t.strip() for t in ssh_exec(ssh, cmd_list).splitlines() if t.strip()]
    print(f"找到 {len(tables)} 个业务表", file=sys.stderr)

    # 2. 每张表 count
    lines = []
    lines.append("=" * 80)
    lines.append("172 服务器数据现状扫描")
    lines.append("=" * 80)
    lines.append(f"{'表名':<45} {'行数':>10}")
    lines.append("-" * 80)

    total = 0
    for t in tables:
        cmd = f"PGPASSWORD={DB_PASS} psql -U {DB_USER} -d {DB} -t -A -c \"SELECT count(*) FROM {t};\""
        try:
            cnt = int(ssh_exec(ssh, cmd).strip() or '0')
        except Exception as e:
            cnt = -1
            print(f"  [ERR] {t}: {e}", file=sys.stderr)
        lines.append(f"{t:<45} {cnt:>10}")
        total += max(cnt, 0)

    lines.append("-" * 80)
    lines.append(f"{'TOTAL':<45} {total:>10}")
    lines.append("=" * 80)

    out = '\n'.join(lines)
    print(out)

    out_path = '_test/data_gen/01_scan_report.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out + '\n')
    print(f"\n报告写入 {out_path}", file=sys.stderr)

    ssh.close()

if __name__ == '__main__':
    main()
