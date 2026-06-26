#!/usr/bin/env python3
import os
"""
07_gen_attendance_extend.py — 阶段 1 第 7 步：考勤/请假/加班/报销 扩展

策略：
- attendance: 1000 条 (20 用户 × 50 天)
- leave_requests: 30 条新
- overtime_requests: 30 条新
- expense_claims: 已有 50 条，新增
- vehicle_usage_requests: 50 条新
- notifications: 100 条新
"""
import paramiko
from datetime import date, timedelta

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'admin123'
DB_PASS = 'oa_pg_pwd_782997781'
DB_USER = 'oa_user'
DB = 'security_oa'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    def max_id(t):
        out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT max(id) FROM {t};\"" )[1].read().decode().strip()
        return int(out or '0')

    sql = ['BEGIN;']
    sql.append('SET LOCAL synchronous_commit = OFF;')

    # ===== 1. 考勤 1000 条 =====
    aid_start = max_id('attendance_records') + 1
    user_ids = list(range(74, 89))  # 74-88, 15 用户
    statuses = ['normal', 'late', 'absent', 'leave', 'field']
    print("生成考勤 1000 条...")
    for i in range(1000):
        aid = aid_start + i
        user_id = user_ids[i % len(user_ids)]
        # 50 天前的某天
        day_offset = i // 20  # 20 用户同一天
        work_date = date(2026, 5, 1) + timedelta(days=day_offset % 50)
        status = statuses[i % 5]
        clock_in = "TIME '09:00:00'" if status != 'absent' else 'NULL'
        clock_out = "TIME '18:00:00'" if status != 'absent' else 'NULL'
        work_hours = 8.0 if status == 'normal' else (4.0 if status == 'late' else 0.0)
        overtime = 2.0 if (i % 10 == 0) else 0.0
        project_id = 72 + (i % 50) if status == 'field' else 'NULL'
        sql.append(f"""INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES ({aid}, {user_id}, DATE '{work_date}', {clock_in}, {clock_out}, '{status}', {work_hours}, {overtime}, {project_id}, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;""")

    # ===== 2. 请假 30 条 =====
    lid_start = max_id('leave_requests') + 1
    print("生成请假 30 条...")
    leave_types = ['personal', 'sick', 'annual', 'marriage', 'maternity']
    for i in range(30):
        lid = lid_start + i
        user_id = user_ids[i % len(user_ids)]
        ltype = leave_types[i % 5]
        start = date(2026, 5, 1) + timedelta(days=i)
        end = start + timedelta(days=1 + i % 3)
        days = (end - start).days + 1
        status = ['pending', 'approved', 'rejected'][i % 3]
        approver = 76 if i % 2 == 0 else 78
        sql.append(f"""INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES ({lid}, {user_id}, '{ltype}', DATE '{start}', DATE '{end}', {days}, '{ltype}类请假 #{i+1}', '{status}', {approver}, NOW() - INTERVAL '{i} days', NOW() - INTERVAL '{i+5} days', NOW());""")

    # ===== 3. 加班 30 条 =====
    oid_start = max_id('overtime_requests') + 1
    print("生成加班 30 条...")
    for i in range(30):
        oid = oid_start + i
        user_id = user_ids[i % len(user_ids)]
        odate = date(2026, 5, 1) + timedelta(days=i)
        hours = 2.0 + (i % 5)
        status = ['pending', 'approved', 'rejected'][i % 3]
        comp = ['leave', 'money'][i % 2]
        sql.append(f"""INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES ({oid}, {user_id}, DATE '{odate}', TIME '18:00:00', TIME '{19 + i % 4}:00:00', {hours}, '加班 #{i+1}', '{comp}', '{status}', 76, NOW() - INTERVAL '{i} days', NOW() - INTERVAL '{i+5} days', NOW());""")

    # ===== 4. 用车 50 条 =====
    vuid_start = max_id('vehicle_usage_requests') + 1
    print("生成用车 50 条...")
    for i in range(50):
        vuid = vuid_start + i
        user_id = user_ids[i % len(user_ids)]
        vehicle_id = 1 + (i % 5)
        sdate = date(2026, 5, 1) + timedelta(days=i)
        status = ['pending', 'approved', 'rejected', 'completed'][i % 4]
        sql.append(f"""INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES ({vuid}, {vehicle_id}, {user_id}, DATE '{sdate}', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #{i+1}', {1 + i % 4}, true, '{status}', 76, NOW() - INTERVAL '{i} days', NOW());""")

    # ===== 5. 通知 100 条 =====
    nid_start = max_id('notifications') + 1
    print("生成通知 100 条...")
    notif_types = ['approval_pending', 'project_update', 'payment_due', 'leave_result', 'attendance_reminder']
    for i in range(100):
        nid = nid_start + i
        user_id = user_ids[i % len(user_ids)]
        ntype = notif_types[i % 5]
        title = f'{ntype} 通知 #{i+1}'
        sql.append(f"""INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES ({nid}, '{ntype}', '{title}', '通知内容 #{i+1}', {user_id}, 'App\\Models\\User', 1, 'info', NOW() - INTERVAL '{i % 30} days', NOW());""")

    sql.append('COMMIT;')
    sql_text = '\n'.join(sql)
    with open(os.path.abspath('07_gen_attendance.sql'), 'w', encoding='utf-8') as f:
        f.write(sql_text)
    print(f"\nSQL 写入: {len(sql)} 行")

    sftp = ssh.open_sftp()
    sftp.put(os.path.abspath('07_gen_attendance.sql'), '/tmp/07_gen_attendance.sql')
    sftp.close()

    out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -f /tmp/07_gen_attendance.sql 2>&1 | tail -5")[1].read().decode()
    print(out)

    # 验证
    for t in ['attendance_records', 'leave_requests', 'overtime_requests', 'vehicle_usage_requests', 'notifications']:
        out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT count(*) FROM {t};\"" )[1].read().decode().strip()
        print(f"  {t}: {out}")

    ssh.close()

if __name__ == '__main__':
    main()
