#!/usr/bin/env python3
import os
"""
05_gen_finance_full_flow.py — 阶段 1 第 5 步：资金流转闭环

闭环：
- expense_claims（员工报销）
  - 各种状态：draft / submitted / approved / paid / rejected
- receivables（应收：客户付款节点 → 台账）
  - pending / partial / fully_paid
- payables（应付：供应商付款 → 台账）
- finance_payments（实际打款流水）
- purchase_payment_requests（采购付款申请）
- purchase_payments（采购付款记录）
- fuel_cards（油卡）
- fuel_card_recharges（油卡充值）
"""
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'admin123'
DB_PASS = 'oa_pg_pwd_782997781'
DB_USER = 'oa_user'
DB = 'security_oa'

def main():
    # 获取当前最大 id
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    def max_id(t):
        out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT max(id) FROM {t};\"" )[1].read().decode().strip()
        return int(out or '0')

    sql = ['BEGIN;']
    sql.append('SET LOCAL synchronous_commit = OFF;')

    # ===== 1. 报销：50 单 =====
    eid_start = max_id('expense_claims') + 1
    e_items_start = 100  # 假设 expense_items 从 100 开始
    categories = ['travel', 'meal', 'office', 'training', 'other']
    statuses = ['draft', 'submitted', 'approved', 'paid', 'rejected']
    sql.append('-- expense_claims')
    for i in range(50):
        eid = eid_start + i
        cat = categories[i % 5]
        amount = 500 + (i * 137) % 4500
        status = statuses[i % 5]
        user_id = 81 + (i % 8)  # 工程师组
        desc = f'{cat}类报销单 #{i+1}'
        paid = 'NULL'
        if status == 'paid':
            paid = f"{amount}"
        approver = 76 if i % 3 == 0 else 78
        sql.append(f"""INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES ({eid}, 'EXP-2026-{eid:05d}', {user_id}, '{cat}', {amount}, '{desc}', '{status}', {approver}, {paid if paid != 'NULL' else 'NULL'}, NOW() - INTERVAL '{i % 30} days', NOW()) ON CONFLICT DO NOTHING;""")

    # ===== 2. 应收：40 单 =====
    rid_start = max_id('receivables') + 1
    sql.append('-- receivables')
    for i in range(40):
        rid = rid_start + i
        cust_id = (i % 30)
        if cust_id >= 27: cust_id += 1
        cust_id += 1
        contract_id = 70 + ((i % 15) + 1)
        amount = 50000 + (i * 15000) % 200000
        # 状态：pending / partial / fully_paid 各 1/3
        status = ['pending', 'partial', 'fully_paid'][i % 3]
        if status == 'fully_paid':
            received = amount
            remain = 0
            recv_date = f"DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}'"
        elif status == 'partial':
            received = amount * 0.6
            remain = amount - received
            recv_date = f"DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}'"
        else:
            received = 0
            remain = amount
            recv_date = 'NULL'
        overdue = 0 if status == 'fully_paid' else (i * 5) % 60
        sql.append(f"""INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES ({rid}, {cust_id}, {72 + (i % 30)}, {contract_id}, {amount}, {received}, {remain}, DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}', {recv_date}, {overdue}, '{status}', NOW() - INTERVAL '{i % 30} days', NOW()) ON CONFLICT DO NOTHING;""")

    # ===== 3. 应付：40 单 =====
    pid_start = max_id('payables') + 1
    sql.append('-- payables')
    for i in range(40):
        pid = pid_start + i
        # suppliers 实际 id 6-10
        supplier_id = 6 + (i % 5)
        amount = 20000 + (i * 8000) % 100000
        status = ['pending', 'partial', 'fully_paid'][i % 3]
        if status == 'fully_paid':
            paid = amount
            remain = 0
            paid_date = f"DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}'"
        elif status == 'partial':
            paid = amount * 0.5
            remain = amount - paid
            paid_date = f"DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}'"
        else:
            paid = 0
            remain = amount
            paid_date = 'NULL'
        sql.append(f"""INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES ({pid}, {supplier_id}, {72 + (i % 30)}, {amount}, {paid}, {remain}, DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}', {paid_date}, 'monthly', '{status}', NOW() - INTERVAL '{i % 30} days', NOW()) ON CONFLICT DO NOTHING;""")

    # ===== 4. finance_payments：60 笔实际打款 =====
    fp_start = max_id('finance_payments') + 1
    sql.append('-- finance_payments')
    for i in range(60):
        fid = fp_start + i
        # 30 笔收款 + 30 笔付款
        if i < 30:
            receivable_id = rid_start + (i % 40)
            payable_id = 'NULL'
            account_id = (i % 4) + 1
        else:
            receivable_id = 'NULL'
            payable_id = pid_start + ((i - 30) % 40)
            account_id = (i % 4) + 1
        amount = 5000 + (i * 700) % 50000
        method = ['transfer', 'cash', 'check'][i % 3]
        voucher = f'V-2026-{fid:05d}'
        sql.append(f"""INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES ({fid}, {receivable_id}, {payable_id}, {account_id}, {amount}, DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}', '{method}', '{voucher}', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;""")

    # ===== 5. 采购付款申请：30 =====
    ppr_start = max_id('purchase_payment_requests') + 1
    sql.append('-- purchase_payment_requests')
    for i in range(30):
        rid = ppr_start + i
        # suppliers 实际 id 6-10
        supplier_id = 6 + (i % 5)
        # purchase_contracts 实际 id 1-15
        contract_id = 1 + (i % 15)
        amount = 10000 + (i * 4000) % 80000
        status = ['pending', 'approved', 'paid', 'rejected'][i % 4]
        approver = 76 if i % 2 == 0 else 78
        applicant_id = 75 + (i % 10)
        sql.append(f"""INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES ({rid}, 'PPR-2026-{rid:05d}', {contract_id}, {supplier_id}, {amount}, 'installment', DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}', '{status}', '申请人{i}', {applicant_id}, {approver}, NOW() - INTERVAL '{i % 20} days', '采购付款申请 #{i+1}', NOW() - INTERVAL '{i % 30} days', NOW()) ON CONFLICT DO NOTHING;""")

    # ===== 6. 采购付款记录：30 =====
    pp_start = max_id('purchase_payments') + 1
    sql.append('-- purchase_payments')
    for i in range(30):
        pid = pp_start + i
        request_id = ppr_start + i
        # purchase_contracts 实际 id 1-15
        contract_id = 1 + (i % 15)
        # suppliers 实际 id 6-10
        supplier_id = 6 + (i % 5)
        amount = 10000 + (i * 4000) % 80000
        operator_id = 79  # fin_zhou
        voucher = f'PV-2026-{pid:05d}'
        sql.append(f"""INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES ({pid}, 'PP-2026-{pid:05d}', {request_id}, {contract_id}, {supplier_id}, {amount}, 'transfer', DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}', '{voucher}', '周会计', {operator_id}, 'success', '采购付款记录 #{i+1}', NOW() - INTERVAL '{i % 30} days', NOW()) ON CONFLICT DO NOTHING;""")

    # ===== 7. 油卡充值：30 =====
    fcr_start = max_id('fuel_card_recharges') + 1
    sql.append('-- fuel_card_recharges')
    for i in range(30):
        fid = fcr_start + i
        card_id = (i % 8) + 1
        amount = 500 + (i * 200) % 3000
        method = ['transfer', 'cash'][i % 2]
        sql.append(f"""INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES ({fid}, {card_id}, {amount}, DATE '2026-{(i%6)+1:02d}-{(i%28)+1:02d}', '{method}', '财务操作员', 'FR-2026-{fid:05d}', NOW() - INTERVAL '{i % 30} days', NOW()) ON CONFLICT DO NOTHING;""")

    sql.append('COMMIT;')

    sql_text = '\n'.join(sql)
    with open(os.path.abspath('05_gen_finance.sql'), 'w', encoding='utf-8') as f:
        f.write(sql_text)
    print(f"SQL 写入: {len(sql)} 行")

    sftp = ssh.open_sftp()
    sftp.put(os.path.abspath('05_gen_finance.sql'), '/tmp/05_gen_finance.sql')
    sftp.close()

    out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -f /tmp/05_gen_finance.sql 2>&1 | tail -10")[1].read().decode()
    print("执行结果:")
    print(out)

    # 验证
    for t in ['expense_claims', 'receivables', 'payables', 'finance_payments', 'purchase_payment_requests', 'purchase_payments', 'fuel_card_recharges']:
        out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -t -A -c \"SELECT count(*) FROM {t};\"" )[1].read().decode().strip()
        print(f"  {t}: {out}")

    ssh.close()

if __name__ == '__main__':
    main()
