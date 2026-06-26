#!/usr/bin/env python3
"""v3.9.0 阶段2 v2: 分开执行, 避免 transaction 错"""
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
SUDO = 'sudo'

DB_NAME = 'security_oa'
DB_USER = 'oa_user'
DB_PWD = 'oa_pg_pwd_782997781'

def ssh_exec(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PWD, timeout=15)
    print('✅ connected')

    # 1. 建 user
    print(f'\n=== 1. create user {DB_USER} ===')
    out, err = ssh_exec(ssh, f"{SUDO} -u postgres psql -c \"CREATE USER {DB_USER} WITH PASSWORD '{DB_PWD}' CREATEDB;\"")
    print(' ', out.strip() or err.strip())

    # 2. 建库
    print(f'\n=== 2. create database {DB_NAME} ===')
    out, err = ssh_exec(ssh, f"{SUDO} -u postgres psql -c \"CREATE DATABASE {DB_NAME} OWNER {DB_USER} ENCODING 'UTF8' LC_COLLATE 'C' TEMPLATE template0;\"")
    print(' ', out.strip() or err.strip())

    # 3. 测连
    print(f'\n=== 3. test login as oa_user ===')
    out, err = ssh_exec(ssh, f"PGPASSWORD='{DB_PWD}' psql -h 127.0.0.1 -U {DB_USER} -d {DB_NAME} -c 'SELECT current_user, current_database(), version();'", timeout=15)
    print(out.strip()[:300] or err.strip())

    # 4. 看权限
    print(f'\n=== 4. privileges ===')
    out, err = ssh_exec(ssh, f"{SUDO} -u postgres psql -c '\\du {DB_USER}'")
    print(out.strip() or err.strip())
    out, err = ssh_exec(ssh, f"{SUDO} -u postgres psql -c '\\l {DB_NAME}'")
    print(out.strip() or err.strip())

    ssh.close()

if __name__ == '__main__':
    main()
