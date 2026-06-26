#!/usr/bin/env python3
import os
"""
03_gen_users.py — 阶段 1 第 3 步：扩充用户到 20 个

策略：
- 4 个角色 × 4-5 人 = 20 用户
- 4 部门各分配 (技术/项目/销售/财务/行政)
- 8 职位对应
- 统一密码 admin123
- 走 model_has_roles 关联
"""
import paramiko
import sys

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'admin123'
DB = 'security_oa'
DB_USER = 'oa_user'
DB_PASS = 'oa_pg_pwd_782997781'

# 5 角色 × 4 人 = 20
# 已有 admin (id=1), zhangsan/lisi/wangwu
# 补 16 个
USERS = [
    # username, name, dept_id, pos_id, role_id
    # admin
    ('admin1',     '系统管理员',     15, 10, 1),
    # manager（4 个：技术总监/项目经理/销售经理/财务主管）
    ('tech_mgr',   '陈技术',         11, 3, 2),
    ('proj_mgr',   '林项目',         12, 4, 2),
    ('sales_mgr',  '赵销售',         13, 7, 2),
    ('fin_mgr',    '黄财务',         14, 9, 2),
    # finance（2 个）
    ('fin_zhou',   '周会计',         14, 9, 3),
    ('fin_wu',     '吴出纳',         14, 9, 3),
    # user（8 个工程师/销售/专员）
    ('eng_zhao',   '赵工',           11, 6, 4),
    ('eng_qian',   '钱工',           11, 6, 4),
    ('eng_sun',    '孙工',           11, 5, 4),
    ('eng_li',     '李工',           11, 6, 4),
    ('sales_chen', '陈销售',         13, 8, 4),
    ('sales_yang', '杨销售',         13, 8, 4),
    ('admin_zheng','郑行政',         15, 10, 4),
    ('admin_wang', '王行政',         15, 10, 4),
]

# BCRYPT 哈希（admin123）
BCRYPT = '$2y$10$Ng63UVS6t9mI7tseo.zB4.mgIrCQqWcxeG.gH6GrAEdVb7aDAJMs6'

def ssh_exec(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='replace'), stderr.read().decode('utf-8', errors='replace')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    # 1. 生成 INSERT SQL 到文件
    sql_lines = ["BEGIN;", "SET LOCAL synchronous_commit = OFF;"]

    # 拿到当前最大 id
    out, _ = ssh_exec(ssh, f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT max(id) FROM users;\"")
    next_id = int(out.strip() or '0') + 1
    print(f"users 最大 id={next_id-1}, 从 {next_id} 开始")

    for i, (uname, name, dept_id, pos_id, role_id) in enumerate(USERS):
        uid = next_id + i
        phone = f"139{uid:08d}"  # 保证唯一
        email = f"{uname}@security-oa.com"
        sql_lines.append(
            f"INSERT INTO users (id, name, username, email, phone, password, "
            f"department_id, position_id, gender, status, created_at, updated_at) "
            f"VALUES ({uid}, '{name}', '{uname}', '{email}', '{phone}', "
            f"'{BCRYPT}', {dept_id}, {pos_id}, 'male', 'active', NOW(), NOW()) "
            f"ON CONFLICT (username) DO NOTHING;"
        )

    sql_lines.append("COMMIT;")

    # 2. 关联 model_has_roles
    sql_lines.append("BEGIN;")
    for i, (uname, name, dept_id, pos_id, role_id) in enumerate(USERS):
        uid = next_id + i
        sql_lines.append(
            f"INSERT INTO model_has_roles (role_id, model_type, model_id) "
            f"VALUES ({role_id}, 'App\\\\Models\\\\User', {uid}) ON CONFLICT DO NOTHING;"
        )
    sql_lines.append("COMMIT;")

    # 3. 写到本地
    sql_path = os.path.abspath('03_gen_users.sql')
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    print(f"SQL 写入 {sql_path}, {len(sql_lines)} 行")

    # 4. sftp 上传 + psql 执行
    sftp = ssh.open_sftp()
    sftp.put(sql_path, '/tmp/03_gen_users.sql')
    sftp.close()
    print("sftp 上传 OK")

    cmd = f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -f /tmp/03_gen_users.sql 2>&1"
    out, err = ssh_exec(ssh, cmd)
    print(out)
    if err:
        print("STDERR:", err)

    # 5. 验证
    out, _ = ssh_exec(ssh, f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -c \"SELECT count(*) FROM users;\"")
    print("users 总数:", out.strip())
    out, _ = ssh_exec(ssh, f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -c \"SELECT r.name, count(*) FROM model_has_roles mhr JOIN roles r ON r.id=mhr.role_id GROUP BY r.name;\"")
    print("角色分布:", out.strip())

    ssh.close()

if __name__ == '__main__':
    main()
