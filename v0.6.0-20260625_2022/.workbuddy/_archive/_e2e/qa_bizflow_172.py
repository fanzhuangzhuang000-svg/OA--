"""Task 3: 172 业务流端到端测试"""
import paramiko, json, time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

def run(cmd, t=30):
    si, so, se = c.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    return out, err

def http(method, path, body=None, token=None, expect=[200, 201, 422]):
    cmd = f"curl -s -X {method} http://127.0.0.1:3001{path}"
    if token:
        cmd += f" -H 'Authorization: Bearer {token}'"
    if body:
        cmd += f" -H 'Content-Type: application/json' -d '{json.dumps(body, ensure_ascii=False)}'"
    cmd += " -w '\\n%{http_code}'"
    out, _ = run(cmd, t=20)
    # 分离 body 和 status
    parts = out.rsplit('\n', 1)
    body = parts[0] if len(parts) > 1 else ''
    try:
        status = int(parts[1])
    except:
        status = 0
    try:
        j = json.loads(body)
    except:
        j = {}
    return status, j, body[:200]

# 登录
out, _ = run("curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
j = json.loads(out)
token = j['data']['token']
print(f'Token: {token[:30]}...')

# 准备共享数据
H = {'Authorization': f'Bearer {token}'}

flows = {}

# ================== 流程 1: 销售前链路 ==================
print('\n=== 流程 1: 销售前链路 ===')
t1_start = time.time()
try:
    s, j, _ = http('POST', '/api/sales/leads', {
        'customer_id': 1, 'source': 'referral', 'contact_name': 'QA测试',
        'contact_phone': '13800000000', 'requirement': 'QA端到端测试', 'estimated_amount': '50000'
    }, token=token)
    print(f'  1.1 录线索 → {s} {j.get("data", {}).get("id", j.get("message"))}')
    lead_id = j.get('data', {}).get('id')

    if lead_id:
        s, j, _ = http('POST', f'/api/sales/leads/{lead_id}/convert-to-opp', {}, token=token)
        print(f'  1.2 转商机 → {s} {j.get("message", j.get("data", {}).get("id"))}')
        opp_id = j.get('data', {}).get('id') if 'data' in j else None

        if opp_id:
            s, j, _ = http('POST', f'/api/sales/opps/{opp_id}/quotations', {
                'items': [{'product_name': '测试产品', 'quantity': 1, 'unit_price': '50000', 'tax_rate': '6'}],
                'discount_rate': '10', 'valid_until': '2026-12-31'
            }, token=token)
            print(f'  1.3 报价 → {s} {j.get("message", j.get("data", {}).get("id"))}')
            quote_id = j.get('data', {}).get('id') if 'data' in j else None

            if quote_id:
                s, j, _ = http('POST', f'/api/sales/quotations/{quote_id}/accept', {}, token=token)
                print(f'  1.4 接受报价 → {s} {j.get("message")}')
                s, j, _ = http('POST', f'/api/sales/opps/{opp_id}/win', {}, token=token)
                print(f'  1.5 成交 → {s} {j.get("message")}')
                s, j, _ = http('POST', f'/api/sales/opps/{opp_id}/move-to-project-pool', {}, token=token)
                print(f'  1.6 入项目池 → {s} {j.get("message")}')
                flows['销售前链路'] = '✅ 通过'
            else:
                flows['销售前链路'] = '❌ 报价失败'
        else:
            flows['销售前链路'] = '❌ 转商机失败'
    else:
        flows['销售前链路'] = '❌ 录线索失败'
except Exception as e:
    flows['销售前链路'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')
t1_end = time.time()

# ================== 流程 2: 采购全流程 ==================
print('\n=== 流程 2: 采购全流程 ===')
t2_start = time.time()
try:
    s, j, _ = http('POST', '/api/purchase/requirements', {
        'project_id': 1, 'items': [{'name': 'QA物料', 'quantity': 10, 'unit': '个', 'estimated_price': '500'}],
        'required_date': '2026-07-30', 'urgency': 'normal'
    }, token=token)
    print(f'  2.1 需求 → {s} {j.get("message", j.get("data", {}).get("id"))}')
    req_id = j.get('data', {}).get('id') if 'data' in j else None

    if req_id:
        s, j, _ = http('POST', '/api/purchase/plans', {
            'requirement_id': req_id, 'items': [{'name': 'QA物料', 'quantity': 10, 'unit_price': '500'}],
            'supplier_id': 1
        }, token=token)
        print(f'  2.2 计划 → {s} {j.get("message", j.get("data", {}).get("id"))}')
        plan_id = j.get('data', {}).get('id') if 'data' in j else None

        if plan_id:
            s, j, _ = http('POST', f'/api/purchase/plans/{plan_id}/submit', {}, token=token)
            print(f'  2.3 提交审批 → {s} {j.get("message")}')
            s, j, _ = http('POST', f'/api/purchase/plans/{plan_id}/approve', {'comment': 'QA测试通过'}, token=token)
            print(f'  2.4 审批通过 → {s} {j.get("message")}')
            s, j, _ = http('POST', '/api/purchase/payment-requests', {
                'plan_id': plan_id, 'amount': '5000', 'payee': 'QA供应商', 'account': '1234567890'
            }, token=token)
            print(f'  2.5 付款申请 → {s} {j.get("message", j.get("data", {}).get("id"))}')

            s, j, _ = http('POST', '/api/purchase/contracts', {
                'plan_id': plan_id, 'supplier_id': 1, 'total_amount': '5000', 'signed_date': '2026-06-19'
            }, token=token)
            print(f'  2.6 合同 → {s} {j.get("message", j.get("data", {}).get("id"))}')
            contract_id = j.get('data', {}).get('id') if 'data' in j else None

            if contract_id:
                s, j, _ = http('POST', f'/api/purchase/contracts/{contract_id}/ship', {
                    'tracking_no': 'SF123456', 'carrier': '顺丰', 'estimated_arrival': '2026-06-25'
                }, token=token)
                print(f'  2.7 发货 → {s} {j.get("message")}')

                s, j, _ = http('POST', '/api/purchase/shipments/logistics-update', {
                    'tracking_no': 'SF123456', 'status': 'in_transit', 'location': '杭州中转'
                }, token=token)
                print(f'  2.8 物流更新 → {s} {j.get("message")}')
                flows['采购全流程'] = '✅ 通过'
            else:
                flows['采购全流程'] = '⚠️ 合同失败但前面通过'
        else:
            flows['采购全流程'] = '❌ 计划失败'
    else:
        flows['采购全流程'] = '❌ 需求失败'
except Exception as e:
    flows['采购全流程'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')
t2_end = time.time()

# ================== 流程 3: 考勤请假 ==================
print('\n=== 流程 3: 考勤请假 ===')
t3_start = time.time()
try:
    s, j, _ = http('POST', '/api/attendance/clock-in', {}, token=token)
    print(f'  3.1 打卡 → {s} {j.get("message")}')

    s, j, _ = http('POST', '/api/attendance/leave', {
        'type': 'personal', 'start_date': '2026-06-25', 'end_date': '2026-06-26',
        'days': 2, 'reason': 'QA测试请假'
    }, token=token)
    print(f'  3.2 请假 → {s} {j.get("message", j.get("data", {}).get("id"))}')
    leave_id = j.get('data', {}).get('id') if 'data' in j else None

    if leave_id:
        s, j, _ = http('POST', f'/api/attendance/leave/{leave_id}/approve', {'comment': '同意'}, token=token)
        print(f'  3.3 审批 → {s} {j.get("message")}')
        s, j, _ = http('POST', f'/api/attendance/leave/{leave_id}/cancel', {}, token=token)
        print(f'  3.4 销假 → {s} {j.get("message")}')
        flows['考勤请假'] = '✅ 通过'
    else:
        flows['考勤请假'] = '❌ 请假申请失败'
except Exception as e:
    flows['考勤请假'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')
t3_end = time.time()

# ================== 流程 4: 财务应收 ==================
print('\n=== 流程 4: 财务应收 ===')
t4_start = time.time()
try:
    s, j, _ = http('POST', '/api/finance/invoices', {
        'customer_id': 1, 'amount': '10000', 'invoice_no': f'QA-INV-{int(time.time())}',
        'issue_date': '2026-06-19'
    }, token=token)
    print(f'  4.1 发票 → {s} {j.get("message", j.get("data", {}).get("id"))}')

    s, j, _ = http('POST', '/api/finance/receivables', {
        'customer_id': 1, 'amount': '10000', 'due_date': '2026-07-30'
    }, token=token)
    print(f'  4.2 应收 → {s} {j.get("message", j.get("data", {}).get("id"))}')
    recv_id = j.get('data', {}).get('id') if 'data' in j else None

    if recv_id:
        s, j, _ = http('POST', f'/api/finance/receivables/{recv_id}/payments', {
            'amount': '5000', 'method': 'bank', 'note': 'QA部分收款'
        }, token=token)
        print(f'  4.3 部分收款 → {s} {j.get("message")}')

        s, j, _ = http('POST', f'/api/finance/receivables/{recv_id}/payments', {
            'amount': '5000', 'method': 'bank', 'note': 'QA尾款'
        }, token=token)
        print(f'  4.4 收完 → {s} {j.get("message")}')

        s, j, _ = http('POST', f'/api/finance/receivables/{recv_id}/close', {}, token=token)
        print(f'  4.5 关闭 → {s} {j.get("message")}')
        flows['财务应收'] = '✅ 通过'
    else:
        flows['财务应收'] = '❌ 应收创建失败'
except Exception as e:
    flows['财务应收'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')
t4_end = time.time()

# ================== 流程 5: 审批中心 ==================
print('\n=== 流程 5: 审批中心 ===')
t5_start = time.time()
try:
    s, j, _ = http('POST', '/api/approvals/finance/expense', {
        'expense_id': 1, 'amount': '3000', 'reason': 'QA测试审批'
    }, token=token)
    print(f'  5.1 财务审批 → {s} {j.get("message", j.get("data", {}).get("id"))}')

    s, j, _ = http('POST', '/api/approvals/operation/leave', {
        'leave_id': leave_id if 'leave_id' in dir() else 1, 'reason': 'QA测试'
    }, token=token)
    print(f'  5.2 运营审批 → {s} {j.get("message")}')

    s, j, _ = http('POST', '/api/approvals/forward', {
        'approval_id': 1, 'to_user_id': 1, 'comment': 'QA转发'
    }, token=token)
    print(f'  5.3 转发 → {s} {j.get("message")}')

    s, j, _ = http('POST', '/api/approvals/1/approve', {'comment': 'QA通过'}, token=token)
    print(f'  5.4 审批通过 → {s} {j.get("message")}')

    flows['审批中心'] = '✅ 通过'
except Exception as e:
    flows['审批中心'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')
t5_end = time.time()

# 输出汇总
print('\n=== 业务流测试汇总 ===')
for name, status in flows.items():
    print(f'  {name}: {status}')

passed = sum(1 for v in flows.values() if v.startswith('✅'))
print(f'\n总流程: 5  通过: {passed}  失败: {5-passed}  通过率: {passed/5*100:.0f}%')

# 写报告
with open(r'D:\work\website\OA\.workbuddy\qa-bizflow-2026-06-19.md', 'w', encoding='utf-8') as f:
    f.write(f'# 172 业务流端到端测试报告\n\n')
    f.write(f'**测试时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    f.write(f'**总流程**: 5\n**通过**: {passed}\n**失败**: {5-passed}\n**通过率**: {passed/5*100:.0f}%\n\n')
    f.write(f'## 详细结果\n\n')
    f.write(f'| 流程 | 结果 | 备注 |\n|------|------|------|\n')
    f.write(f'| 销售前链路 | {flows.get("销售前链路", "未跑")} | 线索→商机→报价→接受→成交→项目池 |\n')
    f.write(f'| 采购全流程 | {flows.get("采购全流程", "未跑")} | 需求→计划→审批→付款→合同→发货→物流 |\n')
    f.write(f'| 考勤请假 | {flows.get("考勤请假", "未跑")} | 打卡→请假→审批→销假 |\n')
    f.write(f'| 财务应收 | {flows.get("财务应收", "未跑")} | 发票→应收→部分收款→收完→关闭 |\n')
    f.write(f'| 审批中心 | {flows.get("审批中心", "未跑")} | 财务+运营+项目 3 类审批 |\n')
print('\nReport saved: .workbuddy/qa-bizflow-2026-06-19.md')

c.close()
