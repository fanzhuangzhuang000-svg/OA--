#!/usr/bin/env python3
"""阶段 1 第 2 步：关键缺口分析"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

queries = [
    ("审批类型覆盖", "SELECT approvable_type, count(*) FROM approval_records GROUP BY approvable_type;"),
    ("用户角色", """SELECT u.id, u.name, u.username, r.name as role
        FROM users u
        LEFT JOIN model_has_roles mhr ON mhr.model_id = u.id AND mhr.model_type='App\\Models\\User'
        LEFT JOIN roles r ON r.id = mhr.role_id
        ORDER BY u.id;"""),
    ("项目完成度", "SELECT stage, count(*), count(actual_end_date) as finished FROM projects GROUP BY stage ORDER BY stage;"),
    ("客户商机阶段", "SELECT pipeline_stage, count(*) FROM customers GROUP BY pipeline_stage;"),
    ("采购订单状态", "SELECT status, count(*) FROM purchase_orders GROUP BY status;"),
    ("工单状态", "SELECT status, count(*) FROM service_orders GROUP BY status;"),
    ("报销状态", "SELECT status, count(*) FROM expense_claims GROUP BY status;"),
    ("车辆使用状态", "SELECT status, count(*) FROM vehicle_usage_requests GROUP BY status;"),
    ("应收应付", "SELECT status, count(*) FROM receivables GROUP BY status;"),
    ("应付", "SELECT status, count(*) FROM payables GROUP BY status;"),
    ("项目结算", "SELECT count(*), sum(settlement_amount) FROM project_settlements;"),
    ("付款申请", "SELECT status, count(*) FROM purchase_payment_requests GROUP BY status;"),
    ("付款记录", "SELECT status, count(*) FROM purchase_payments GROUP BY status;"),
    ("维保合同", "SELECT status, count(*) FROM maintenance_contracts GROUP BY status;"),
    ("油卡余额", "SELECT count(*), sum(balance) FROM fuel_cards;"),
    ("知识库文章", "SELECT count(*) FROM knowledge_articles;"),
    ("文件数", "SELECT count(*) FROM disk_files;"),
    ("角色", "SELECT id, name FROM roles;"),
    ("权限", "SELECT count(*) FROM permissions;"),
]

for title, q in queries:
    print(f"\n=== {title} ===")
    safe = q.replace("'", "'\\''")
    cmd = f"PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -c \"{q}\""
    print(ssh.exec_command(cmd)[1].read().decode('utf-8', errors='replace'))

ssh.close()
