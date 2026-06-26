"""
Create the missing Laravel framework tables that are needed:
- personal_access_tokens (Sanctum)
- password_reset_tokens (built-in)
- sessions (built-in)
- cache (built-in)
- cache_locks (built-in)
- jobs (queue)
- failed_jobs (queue)

These normally come from:
- php artisan install:api (publishes Sanctum migration)
- php artisan queue:table
- php artisan session:table

For PG, we create them directly to avoid running publish commands.
"""
import time
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=20)
print(f"[OK] Connected to {HOST}")

# SQL to create all missing tables
sql_script = r"""
-- Laravel 11 framework tables (Sanctum, sessions, cache, queue)
-- All use the same connection: pgsql

-- Sanctum tokens
CREATE TABLE IF NOT EXISTS personal_access_tokens (
    id BIGSERIAL PRIMARY KEY,
    tokenable_type VARCHAR(255) NOT NULL,
    tokenable_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    token VARCHAR(64) NOT NULL UNIQUE,
    abilities TEXT NULL,
    last_used_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
);
CREATE INDEX IF NOT EXISTS pat_tokenable_index ON personal_access_tokens (tokenable_type, tokenable_id);
CREATE INDEX IF NOT EXISTS pat_expires_at_index ON personal_access_tokens (expires_at);

-- Password reset tokens
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    email VARCHAR(255) PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL
);

-- Sessions (for database driver)
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id BIGINT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    payload TEXT NOT NULL,
    last_activity INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_user_id_index ON sessions (user_id);
CREATE INDEX IF NOT EXISTS sessions_last_activity_index ON sessions (last_activity);

-- Cache (for database driver)
CREATE TABLE IF NOT EXISTS cache (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    expiration INTEGER NOT NULL
);

-- Cache locks
CREATE TABLE IF NOT EXISTS cache_locks (
    key VARCHAR(255) PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    expiration INTEGER NOT NULL
);

-- Jobs (queue)
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    queue VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    attempts SMALLINT NOT NULL,
    reserved_at INTEGER NULL,
    available_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS jobs_queue_index ON jobs (queue);

-- Failed jobs
CREATE TABLE IF NOT EXISTS failed_jobs (
    id BIGSERIAL PRIMARY KEY,
    uuid VARCHAR(255) NOT NULL UNIQUE,
    connection TEXT NOT NULL,
    queue TEXT NOT NULL,
    payload TEXT NOT NULL,
    exception TEXT NOT NULL,
    failed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# Write SQL to a temp file, then execute via psql
cmd = f"cat > /tmp/missing_tables.sql << 'SQLEOF'\n{sql_script}\nSQLEOF\necho 'SQL written'\nls -la /tmp/missing_tables.sql"
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"OUT: {stdout.read().decode('utf-8', errors='replace')}")
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"ERR: {err[:300]}")

# Run psql
print("\n[2/3] Running psql to create missing tables...")
cmd = "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -f /tmp/missing_tables.sql 2>&1 | tail -30"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"OUT: {out}")
if err: print(f"ERR: {err[:1000]}")

# Verify tables exist
print("\n[3/3] Verifying tables...")
cmd = "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c '\\dt' 2>&1 | tail -50"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Test login again
print("\n[+] Testing login...")
test_cmd = '''curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"username":"admin","password":"admin123"}' http://127.0.0.1/api/auth/login 2>&1 | head -c 2000'''
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=20)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"Login response:\n{out}")

client.close()
print("\n[DONE]")
