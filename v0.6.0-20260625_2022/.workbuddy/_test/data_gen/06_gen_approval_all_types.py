#!/usr/bin/env python3
import os
"""
06_gen_approval_all_types.py — 阶段 1 第 6 步：15+ 类审批全进审批中心

策略：
- 现存只有 4 类：Project/LeaveRequest/ExpenseClaim/PurchaseOrder
- 补 11+ 类：VehicleUsage/Refund/Customer/PurchaseContract/PurchasePayment/
           MaintenanceContract/Reimbursement/Attendance/...
- 100+ 条记录，3 种状态都覆盖
"""
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'admin123'
DB_PASS = 'oa_pg_pwd_782997781'
DB_USER = 'oa_user'
DB = 'security_oa'

# 15+ 审批类型
APPROVAL_TYPES = [
    ('Project', 'projects', 72, 122),                # 项目审批
    ('ProjectContract', 'project_contracts', 70, 85), # 项目合同
    ('ProjectSettlement', 'project_settlements', 1, 25),  # 项目结算
    ('PurchaseRequirement', 'purchase_requirements', 1, 30),  # 采购需求
    ('PurchaseOrder', 'purchase_orders', 1, 30),     # 采购订单
    ('PurchaseContract', 'purchase_contracts', 1, 15),  # 采购合同
    ('PurchasePayment', 'purchase_payment_requests', 25, 55),  # 采购付款
    ('ExpenseClaim', 'expense_claims', 14, 63),      # 报销
    ('LeaveRequest', 'leave_requests', 21, 20),      # 请假
    ('OvertimeRequest', 'overtime_requests', 12, 11),  # 加班
    ('VehicleUsage', 'vehicle_usage_requests', 51, 50),  # 用车
    ('MaintenanceContract', 'maintenance_contracts', 16, 15),  # 维保合同
    ('Refund', 'receivables', 15, 54),                # 退款
    ('FuelRecharge', 'fuel_card_recharges', 21, 50),  # 油卡充值
    ('Training', 'training_records', 1, 1),           # 培训（可能不存在）
]

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    def max_id(t):
        out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT max(id) FROM {t};\"" )[1].read().decode().strip()
        return int(out or '0')

    def table_exists(t):
        out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT count(*) FROM information_schema.tables WHERE table_name='{t}';\"" )[1].read().decode().strip()
        return int(out or '0') > 0

    aid_start = max_id('approval_records') + 1
    sql = ['BEGIN;']
    sql.append('SET LOCAL synchronous_commit = OFF;')

    current_aid = aid_start
    for approvable_type, table, start_id, max_id_val in APPROVAL_TYPES:
        if not table_exists(table):
            print(f"  [skip] {approvable_type}: table {table} 不存在")
            continue
        # 取实际最大 id
        actual_max = max_id(table)
        if actual_max == 0:
            print(f"  [skip] {approvable_type}: table {table} 空")
            continue
        # 给每类业务 5-10 条审批
        count = min(8, actual_max)
        step = max(1, actual_max // count)
        for k in range(count):
            target_id = (k + 1) * step
            if target_id > actual_max:
                target_id = actual_max - (count - k - 1)
            status = ['pending', 'approved', 'rejected'][k % 3]
            # 审批人
            user_id = 76 + (k % 4)  # 75-78
            sql.append(f"""INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES ({current_aid}, '{approvable_type}', {target_id}, {user_id}, '{status}', '{status}', '{approvable_type} 审批 #{k+1}', NOW() - INTERVAL '{k*2} days', NOW());""")
            current_aid += 1
        print(f"  {approvable_type}: 8 条")

    sql.append('COMMIT;')
    sql_text = '\n'.join(sql)
    with open(os.path.abspath('06_gen_approvals.sql'), 'w', encoding='utf-8') as f:
        f.write(sql_text)
    print(f"\nSQL 写入: {len(sql)} 行, 审批 {current_aid - aid_start} 条")

    sftp = ssh.open_sftp()
    sftp.put(os.path.abspath('06_gen_approvals.sql'), '/tmp/06_gen_approvals.sql')
    sftp.close()
    out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -f /tmp/06_gen_approvals.sql 2>&1 | tail -10")[1].read().decode()
    print("执行结果:")
    print(out)

    # 验证
    out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -c \"SELECT approvable_type, count(*) FROM approval_records GROUP BY approvable_type ORDER BY count(*) DESC;\"" )[1].read().decode()
    print("审批类型分布:")
    print(out)

    ssh.close()

if __name__ == '__main__':
    main()
