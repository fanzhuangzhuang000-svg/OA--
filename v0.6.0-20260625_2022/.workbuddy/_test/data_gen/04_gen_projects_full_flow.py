#!/usr/bin/env python3
import os
"""
04_gen_projects_full_flow.py — 阶段 1 第 4 步：项目跑完 7 阶段

策略：
- 在现有 71 项目基础上，再补 50 个
- 每项目走完 7 阶段（inquiry → initiation → contract → purchase → construction → settlement → warranty）
- actual_end_date 全部填上（关键：大哥要求"确认环节"）
- 同时补：合同 + 付款节点 + 施工日志 + 项目结算 + 项目成员

数据规模：
- 50 新项目（id 72-121）
- 50 合同
- 150 付款节点（每合同 3 个）
- 500 施工日志（每项目 10 条）
- 30 项目结算（已完成项目才有）
- 100 项目成员
"""
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'admin123'
DB_PASS = 'oa_pg_pwd_782997781'
DB_USER = 'oa_user'
DB = 'security_oa'

PROJECT_TYPES = ['camera', 'alarm', 'access', 'patrol', 'integrated']
STAGES = ['inquiry', 'initiation', 'contract', 'purchase', 'construction', 'settlement', 'warranty']
STAGE_NAMES_CN = ['询价', '立项', '合同', '采购', '施工', '结算', '维保']
CITIES = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '重庆']
PRIORITIES = ['high', 'medium', 'low']

# 50 项目
def gen_projects():
    projects = []
    for i in range(1, 51):
        proj_id = 71 + i
        # customer id 实际存在 1-27, 29-31
        cust_id = ((i - 1) % 30)
        # 跳过 28
        if cust_id >= 27:
            cust_id += 1
        cust_id += 1  # 回到 1-indexed
        mgr_id = [75, 76, 77, 78, 79][i % 5]  # 4 manager + finance
        # 阶段分布：50 项目按 7 阶段滚动
        stage_idx = i % 7
        stage = STAGES[stage_idx]
        # 完成度跟阶段走
        progress = [10, 25, 40, 55, 70, 90, 100][stage_idx]
        # 已完成阶段的项目：actual_end_date 有值
        actual_end = 'NULL'
        if stage_idx >= 1:  # 至少过 inquiry 才能算开工
            actual_end = f"DATE '2026-0{min(progress // 15 + 3, 6)}-15'"
        # 预算
        budget_device = 100000 + (i * 10000) % 500000
        projects.append({
            'id': proj_id,
            'project_no': f'PRJ-2026-{proj_id:04d}',
            'name': f'{CITIES[i % 10]}市{STAGE_NAMES_CN[stage_idx]}类项目#{i}',
            'customer_id': cust_id,
            'type': PROJECT_TYPES[i % 5],
            'stage': stage,
            'status': 'in_progress' if stage_idx < 6 else 'completed',
            'budget_device': budget_device,
            'budget_material': budget_device // 4,
            'budget_labor': budget_device // 5,
            'budget_outsource': budget_device // 10,
            'budget_other': budget_device // 20,
            'progress': progress,
            'manager_id': mgr_id,
            'start_date': f"DATE '2026-{(i % 6) + 1:02d}-01'",
            'end_date': f"DATE '2026-{(i % 6) + 4:02d}-30'",
            'actual_end_date': actual_end,
            'priority': PRIORITIES[i % 3],
        })
    return projects

def gen_contracts(projects):
    """每项目 1 合同（id 71-120）"""
    contracts = []
    for p in projects:
        if p['stage'] in ['inquiry', 'initiation']:
            continue  # 还没到合同阶段
        contract_id = 70 + (p['id'] - 70)
        amount = float(p['budget_device'] + p['budget_material'] + p['budget_labor'] + p['budget_outsource'] + p['budget_other'])
        if p['stage'] == 'contract':
            status = 'active'
        else:
            status = 'completed'
        # 直接用 date 字面量
        contracts.append({
            'id': contract_id,
            'project_id': p['id'],
            'contract_no': f'CT-2026-{contract_id:04d}',
            'contract_amount': amount,
            'payment_method': 'installment' if (p['id'] % 2) == 0 else 'lump_sum',
            'contract_start': p['start_date'],  # 已经是 DATE '2026-xx-xx'
            'contract_end': p['end_date'],
            'status': status,
            'signed_at': f"TIMESTAMP '2026-{(p['id'] % 6) + 1:02d}-01 09:00:00'",
        })
    return contracts

def gen_payment_nodes(contracts):
    """每合同 3 付款节点（首付款/进度款/尾款）"""
    nodes = []
    nid = 90
    node_names = ['首付款(30%)', '进度款(50%)', '尾款(20%)']
    node_pcts = [30, 50, 20]
    for c in contracts:
        for i, (name, pct) in enumerate(zip(node_names, node_pcts)):
            nid += 1
            amount = round(float(c['contract_amount']) * pct / 100, 2)
            # 状态根据 stage
            if c['status'] == 'active':
                if i == 0:
                    status, actual_date, paid = 'paid', c['contract_start'], amount
                else:
                    status, actual_date, paid = 'pending', 'NULL', 0
            else:
                actual_date = f"DATE '2026-{((nid % 6) + 1):02d}-{(nid % 28) + 1:02d}'"
                if i == 0:
                    status, paid = 'paid', amount
                elif i == 1:
                    status, paid = 'paid', amount
                else:
                    status, paid = 'paid', amount
            nodes.append({
                'id': nid,
                'contract_id': c['id'],
                'name': name,
                'percentage': pct,
                'amount': amount,
                'planned_date': f"DATE '2026-{(nid % 6) + 1:02d}-{(i + 1) * 10:02d}'",
                'actual_date': actual_date,
                'status': status,
                'paid_amount': paid,
            })
    return nodes

def gen_construction_logs(projects):
    """每项目 10 条施工日志"""
    logs = []
    lid = 150
    weather_options = ['晴', '阴', '雨', '多云', '雪']
    contents = ['设备安装', '线路铺设', '设备调试', '现场勘测', '系统联调', '电源接入', '网络配置', '客户培训', '验收测试', '文档归档']
    for p in projects:
        if p['stage'] in ['inquiry', 'initiation', 'contract']:
            continue
        for j in range(10):
            lid += 1
            logs.append({
                'id': lid,
                'project_id': p['id'],
                'user_id': 81 + (j % 8),  # 工程师 id 81-88
                'work_date': f"DATE '2026-{(lid % 6) + 1:02d}-{(j + 1) * 3:02d}'",
                'weather': weather_options[j % 5],
                'content': f'{contents[j % 10]} - {p["name"]}',
                'work_hours': 6.0 + (j % 4),
                'status': 'submitted',
            })
    return logs

def gen_settlements(projects):
    """已完成项目（warranty）才有结算"""
    settlements = []
    sid = 0
    for p in projects:
        if p['stage'] != 'warranty':
            continue
        sid += 1
        total_income = float(p['budget_device'] + p['budget_material'])
        total_cost = total_income * 0.7
        cost_labor = total_cost * 0.3
        cost_material = total_cost * 0.4
        cost_outsource = total_cost * 0.2
        cost_other = total_cost * 0.1
        profit = total_income - total_cost
        profit_rate = round(profit / total_income * 100, 2) if total_income > 0 else 0
        settlements.append({
            'id': sid,
            'project_id': p['id'],
            'total_income': total_income,
            'total_cost': total_cost,
            'cost_labor': cost_labor,
            'cost_material': cost_material,
            'cost_outsource': cost_outsource,
            'cost_other': cost_other,
            'profit': profit,
            'profit_rate': profit_rate,
            'settlement_date': f"DATE '2026-06-15'",
            'status': 'approved',
        })
    return settlements

def gen_project_members(projects):
    """每项目 2-3 个成员（id 12-150）"""
    members = []
    mid = 12
    for p in projects:
        used_users = set()
        for k in range(2 + (p['id'] % 2)):  # 2 或 3 个
            mid += 1
            uid = 81 + (k + p['id']) % 8  # 工程师组 81-88
            # 避免同一项目同一用户重复（unique 约束）
            if uid in used_users:
                uid = 81 + (uid - 81 + 1) % 8
            used_users.add(uid)
            members.append({
                'id': mid,
                'project_id': p['id'],
                'user_id': uid,
                'role': ['worker', 'lead', 'observer'][k % 3],
                'join_date': p['start_date'],  # join_date
            })
    return members

def main():
    projects = gen_projects()
    contracts = gen_contracts(projects)
    pay_nodes = gen_payment_nodes(contracts)
    logs = gen_construction_logs(projects)
    settlements = gen_settlements(projects)
    members = gen_project_members(projects)

    sql = ['BEGIN;']
    sql.append('SET LOCAL synchronous_commit = OFF;')

    # 1. projects
    for p in projects:
        sql.append(f"""INSERT INTO projects (id, project_no, name, customer_id, type, stage, status,
            budget_device, budget_material, budget_labor, budget_outsource, budget_other,
            progress, manager_id, start_date, end_date, actual_end_date, priority, created_at, updated_at)
            VALUES ({p['id']}, '{p['project_no']}', '{p['name']}', {p['customer_id']}, '{p['type']}',
            '{p['stage']}', '{p['status']}', {p['budget_device']}, {p['budget_material']},
            {p['budget_labor']}, {p['budget_outsource']}, {p['budget_other']}, {p['progress']},
            {p['manager_id']}, {p['start_date']}, {p['end_date']}, {p['actual_end_date']},
            '{p['priority']}', NOW(), NOW()) ON CONFLICT (id) DO NOTHING;""")

    # 2. project_contracts
    for c in contracts:
        sql.append(f"""INSERT INTO project_contracts (id, project_id, contract_no, contract_amount,
            payment_method, contract_start, contract_end, status, signed_at, created_at, updated_at)
            VALUES ({c['id']}, {c['project_id']}, '{c['contract_no']}', {c['contract_amount']},
            '{c['payment_method']}', {c['contract_start']}, {c['contract_end']}, '{c['status']}',
            {c['signed_at']}, NOW(), NOW()) ON CONFLICT (id) DO NOTHING;""")

    # 3. contract_payment_nodes
    for n in pay_nodes:
        sql.append(f"""INSERT INTO contract_payment_nodes (id, contract_id, name, percentage, amount,
            planned_date, actual_date, status, paid_amount, created_at, updated_at)
            VALUES ({n['id']}, {n['contract_id']}, '{n['name']}', {n['percentage']}, {n['amount']},
            {n['planned_date']}, {n['actual_date']}, '{n['status']}', {n['paid_amount']}, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING;""")

    # 4. construction_logs
    for l in logs:
        sql.append(f"""INSERT INTO construction_logs (id, project_id, user_id, work_date, weather,
            content, work_hours, status, created_at, updated_at)
            VALUES ({l['id']}, {l['project_id']}, {l['user_id']}, {l['work_date']}, '{l['weather']}',
            '{l['content']}', {l['work_hours']}, '{l['status']}', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING;""")

    # 5. project_settlements
    for s in settlements:
        sql.append(f"""INSERT INTO project_settlements (id, project_id, total_income, total_cost,
            cost_labor, cost_material, cost_outsource, cost_other, profit, profit_rate,
            settlement_date, status, created_at, updated_at)
            VALUES ({s['id']}, {s['project_id']}, {s['total_income']}, {s['total_cost']},
            {s['cost_labor']}, {s['cost_material']}, {s['cost_outsource']}, {s['cost_other']},
            {s['profit']}, {s['profit_rate']}, {s['settlement_date']}, '{s['status']}',
            NOW(), NOW()) ON CONFLICT (id) DO NOTHING;""")

    # 6. project_members
    for m in members:
        sql.append(f"""INSERT INTO project_members (id, project_id, user_id, role, join_date, status, created_at, updated_at)
            VALUES ({m['id']}, {m['project_id']}, {m['user_id']}, '{m['role']}',
            {m['join_date']}, 'active', NOW(), NOW()) ON CONFLICT (id) DO NOTHING;""")

    sql.append('COMMIT;')

    # 0. customers 40 个 (供 projects 外键, 适配 customers 实际 schema)
    customers_sql = []
    city_names = ['北京','上海','广州','深圳','杭州','成都','西安','武汉','南京','苏州','天津','青岛','大连','厦门','济南','福州','宁波','温州','佛山','东莞']
    for cid in range(1, 41):
        cname = f"{city_names[(cid-1) % 20]}安防公司#{cid}"
        city = city_names[(cid-1) % 20]
        customers_sql.append(
            f"INSERT INTO customers (id, name, credit_code, industry, category, province, city, district, address, source, status, created_at, updated_at) "
            f"VALUES ({cid}, '{cname}', '9133{(1000+cid):04d}MA{(10000+cid):05d}', '安防工程', 'normal', '{city}市', '{city}市', '中心区', '{city}市某街某号', 'referral', 'active', NOW(), NOW()) ON CONFLICT (id) DO NOTHING;"
        )
    sql = customers_sql + sql

    sql_text = '\n'.join(sql)
    with open(os.path.abspath('04_gen_projects.sql'), 'w', encoding='utf-8') as f:
        f.write(sql_text)
    print(f"SQL 写入: {len(sql)} 行")
    print(f"  customers: 40")
    print(f"  projects: {len(projects)}")
    print(f"  contracts: {len(contracts)}")
    print(f"  payment_nodes: {len(pay_nodes)}")
    print(f"  construction_logs: {len(logs)}")
    print(f"  settlements: {len(settlements)}")
    print(f"  members: {len(members)}")

    # 上传并执行
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    sftp = ssh.open_sftp()
    sftp.put(os.path.abspath('04_gen_projects.sql'), '/tmp/04_gen_projects.sql')
    sftp.close()

    out = ssh.exec_command(f"PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB} -f /tmp/04_gen_projects.sql 2>&1 | tail -20")[1].read().decode()
    print("执行结果：")
    print(out)
    ssh.close()

if __name__ == '__main__':
    main()
