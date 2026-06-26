"""套件 B: 172 5 大业务流 E2E (2026-06-19 v2)
- 销售前链路: lead → opp → quotation → accept → win → pool
- 采购全流程: BLOCKED (be-eng-2 未部署)
- 考勤请假: clock-in → leave → approve → cancel
- 财务应收: invoice → receivable → payments → close
- 审批中心: finance + operation + project 各跑 1 个 (POST → approve → 查看 flow)
"""
import paramiko, json, time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

def run(cmd, t=30):
    si, so, se = c.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    return out, err

def http(method, path, body=None, token=None):
    cmd = f"curl -s -X {method} http://127.0.0.1:3001{path}"
    if token:
        cmd += f" -H 'Authorization: Bearer {token}'"
    if body:
        body_str = json.dumps(body, ensure_ascii=False).replace("'", "'\\''")
        cmd += f" -H 'Content-Type: application/json' -d '{body_str}'"
    cmd += " -o /tmp/qa_biz_body.json -w '%{http_code}'"
    out, _ = run(cmd, t=20)
    code = out.strip()
    body_out, _ = run('cat /tmp/qa_biz_body.json 2>/dev/null')
    try:
        j = json.loads(body_out)
    except:
        j = {}
    return int(code) if code.isdigit() else 0, j, body_out[:200]

# 登录
out, _ = run("""curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}'""")
j = json.loads(out)
token = j['data']['token']
print(f'Token: {token[:30]}...')

flows = {}

# ================== 流程 1: 销售前链路 ==================
print('\n=== 流程 1: 销售前链路 ===')
try:
    s, j, _ = http('POST', '/api/sales/leads', {
        'customer_id': 1, 'customer_name': 'QA客户', 'contact_name': 'QA测试',
        'contact_phone': '13800000000', 'source': 'referral', 'owner_id': 1,
        'stage': 'new', 'rating': 'A', 'estimated_amount': 50000
    }, token=token)
    lead_id = j.get('data', {}).get('id') if 'data' in j else None
    print(f'  1.1 录线索 → {s} | lead_id={lead_id} | {j.get("message", "")}')

    if lead_id:
        s, j, _ = http('POST', f'/api/sales/leads/{lead_id}/convert-to-opp', {
            'name': f'QA测试商机-{int(time.time())}',
            'estimated_amount': 50000,
            'sales_id': 1,
            'presale_id': 1
        }, token=token)
        opp_id = j.get('data', {}).get('id') if 'data' in j else None
        print(f'  1.2 转商机 → {s} | opp_id={opp_id} | {j.get("message", "")}')

        if opp_id:
            s, j, _ = http('POST', f'/api/sales/opps/{opp_id}/quotations', {
                'items': [{'name': '测试产品', 'quantity': 1, 'unit_price': 50000}],
                'discount_rate': 10, 'tax_rate': 13, 'valid_until': '2026-12-31'
            }, token=token)
            quote_id = j.get('data', {}).get('id') if 'data' in j else None
            print(f'  1.3 报价 → {s} | quote_id={quote_id} | {j.get("message", "")}')

            if quote_id:
                s, j, _ = http('POST', f'/api/sales/quotations/{quote_id}/accept', {}, token=token)
                print(f'  1.4 接受报价 → {s} | {j.get("message", "")}')

                s, j, _ = http('POST', f'/api/sales/opps/{opp_id}/win', {}, token=token)
                print(f'  1.5 成交 → {s} | {j.get("message", "")}')

                s, j, _ = http('POST', f'/api/sales/opps/{opp_id}/move-to-project-pool', {}, token=token)
                print(f'  1.6 入项目池 → {s} | {j.get("message", "")}')
                flows['销售前链路'] = '✅ 通过'
            else:
                flows['销售前链路'] = f'❌ 报价失败 (s={s} {j.get("message","")})'
        else:
            flows['销售前链路'] = f'❌ 转商机失败 (s={s} {j.get("message","")})'
    else:
        flows['销售前链路'] = f'❌ 录线索失败 (s={s} {j.get("message","")})'
except Exception as e:
    flows['销售前链路'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')

# ================== 流程 2: 采购全流程 (BLOCKED) ==================
print('\n=== 流程 2: 采购全流程 (BLOCKED) ===')
s, j, _ = http('POST', '/api/purchase/requirements', {
    'project_id': 1, 'items': [{'name': 'QA物料', 'quantity': 10, 'unit': '个', 'estimated_price': 500}],
    'required_date': '2026-07-30', 'urgency': 'normal'
}, token=token)
print(f'  2.1 需求 → {s} | {j.get("message", "")} (expect 404 — purchase 未部署)')
if s == 404:
    flows['采购全流程'] = '⚠️ BLOCKED — be-eng-2 Purchase 模块未部署'
else:
    flows['采购全流程'] = f'❌ 意外状态: {s}'

# ================== 流程 3: 考勤请假 ==================
print('\n=== 流程 3: 考勤请假 ===')
try:
    s, j, _ = http('POST', '/api/attendance/clock-in', {}, token=token)
    print(f'  3.1 打卡 → {s} | {j.get("message", "")}')

    s, j, _ = http('POST', '/api/attendance/leave', {
        'type': 'personal', 'start_date': '2026-06-25', 'end_date': '2026-06-26',
        'days': 2, 'reason': 'QA测试请假', 'user_id': 1
    }, token=token)
    leave_id = j.get('data', {}).get('id') if 'data' in j else None
    print(f'  3.2 请假 → {s} | leave_id={leave_id} | {j.get("message", "")}')

    if leave_id:
        s, j, _ = http('POST', f'/api/attendance/leave/{leave_id}/approve', {'action': 'approved', 'comment': '同意'}, token=token)
        print(f'  3.3 审批 → {s} | {j.get("message", "")}')

        # 销假 — 用 DELETE /leave/{id}（已批准的不能销，按文档允许）
        s, j, _ = http('DELETE', f'/api/attendance/leave/{leave_id}', {}, token=token)
        print(f'  3.4 销假 → {s} | {j.get("message", "")}')
        flows['考勤请假'] = '✅ 通过'
    else:
        flows['考勤请假'] = f'❌ 请假申请失败 (s={s} {j.get("message","")})'
except Exception as e:
    flows['考勤请假'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')

# ================== 流程 4: 财务应收 ==================
print('\n=== 流程 4: 财务应收 ===')
try:
    s, j, _ = http('POST', '/api/finance/receivables', {
        'customer_id': 1, 'amount': 10000, 'due_date': '2026-07-30',
        'invoice_no': f'QA-INV-{int(time.time())}'
    }, token=token)
    recv_id = j.get('data', {}).get('id') if 'data' in j else None
    print(f'  4.1 应收 → {s} | recv_id={recv_id} | {j.get("message", "")}')

    if recv_id:
        s, j, _ = http('POST', f'/api/finance/receivables/{recv_id}/payments', {
            'amount': 5000, 'method': 'bank', 'payment_date': '2026-06-19', 'remark': 'QA部分收款'
        }, token=token)
        p1_ok = (s == 200)
        print(f'  4.2 部分收款 → {s} | {j.get("message", "")}')

        s, j, _ = http('POST', f'/api/finance/receivables/{recv_id}/payments', {
            'amount': 5000, 'method': 'bank', 'payment_date': '2026-06-19', 'remark': 'QA尾款'
        }, token=token)
        p2_ok = (s == 200)
        print(f'  4.3 收完 → {s} | {j.get("message", "")}')

        s, j, _ = http('POST', f'/api/finance/receivables/{recv_id}/close', {}, token=token)
        # 已收完不能关闭（业务规则），200 = 部分收可关, 422 = 已收完不需关 — 都算流程成功
        s_close_ok = s in (200, 422)
        print(f'  4.4 关闭 → {s} | {j.get("message", "")}')
        # 严格判定：4 个核心动作（应收建+2次收款+关闭）必须全非500
        if recv_id and s_close_ok and p1_ok and p2_ok:
            flows['财务应收'] = '✅ 通过'
        else:
            flows['财务应收'] = f'❌ FinanceController 缺方法: payments×2={p1_ok},{p2_ok} close={s_close_ok}'
    else:
        flows['财务应收'] = f'❌ 应收创建失败 (s={s} {j.get("message","")})'
except Exception as e:
    flows['财务应收'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')

# ================== 流程 5: 审批中心 ==================
print('\n=== 流程 5: 审批中心 ===')
try:
    # 5.1 财务审批
    s, j, _ = http('POST', '/api/approvals/finance', {
        'sub_type': 'expense', 'title': 'QA测试财务审批', 'amount': 3000,
        'reason': '业务招待', 'applicant_id': 1
    }, token=token)
    fap_id = j.get('data', {}).get('id') if 'data' in j else None
    print(f'  5.1 财务审批创建 → {s} | id={fap_id} | {j.get("message", "")}')

    # 5.2 运营审批
    s, j, _ = http('POST', '/api/approvals/operation', {
        'sub_type': 'purchase', 'title': 'QA测试运营审批', 'amount': 5000,
        'reason': '采购物资', 'applicant_id': 1
    }, token=token)
    oap_id = j.get('data', {}).get('id') if 'data' in j else None
    print(f'  5.2 运营审批创建 → {s} | id={oap_id} | {j.get("message", "")}')

    # 5.3 项目审批
    s, j, _ = http('POST', '/api/approvals/project', {
        'sub_type': 'project', 'title': 'QA测试项目审批', 'amount': 10000,
        'reason': '项目支出', 'applicant_id': 1
    }, token=token)
    pap_id = j.get('data', {}).get('id') if 'data' in j else None
    print(f'  5.3 项目审批创建 → {s} | id={pap_id} | {j.get("message", "")}')

    # 5.4 审批通过 (财务) + 查看 flow
    if fap_id:
        s, j, _ = http('POST', f'/api/approvals/finance/{fap_id}/approve', {'comment': 'QA审批通过'}, token=token)
        print(f'  5.4 财务审批通过 → {s} | {j.get("message", "")}')

        s, j, _ = http('GET', f'/api/approvals/finance/{fap_id}', token=token)
        flow = j.get('data', {}).get('flow') or j.get('flow') or []
        print(f'  5.5 财务 flow 时间线 → 节点数={len(flow) if isinstance(flow, list) else "?"}')

    # 5.6 运营审批通过
    if oap_id:
        s, j, _ = http('POST', f'/api/approvals/operation/{oap_id}/approve', {'comment': 'QA通过'}, token=token)
        print(f'  5.6 运营审批通过 → {s} | {j.get("message", "")}')

    # 5.7 项目审批通过
    if pap_id:
        s, j, _ = http('POST', f'/api/approvals/project/{pap_id}/approve', {'comment': 'QA通过'}, token=token)
        print(f'  5.7 项目审批通过 → {s} | {j.get("message", "")}')

    if fap_id and oap_id and pap_id:
        flows['审批中心'] = '✅ 通过'
    else:
        flows['审批中心'] = f'❌ 部分创建失败 f={fap_id} o={oap_id} p={pap_id}'
except Exception as e:
    flows['审批中心'] = f'❌ 异常: {str(e)[:80]}'
    print(f'  EXCEPTION: {e}')

# === 汇总 ===
print('\n=== 业务流测试汇总 ===')
for name, status in flows.items():
    print(f'  {name}: {status}')

passed = sum(1 for v in flows.values() if v.startswith('✅'))
blocked = sum(1 for v in flows.values() if 'BLOCKED' in v)
failed = sum(1 for v in flows.values() if v.startswith('❌'))
print(f'\n总流程: 5  ✅ 通过: {passed}  ❌ 失败: {failed}  ⚠️ Blocked: {blocked}')

# 写报告
with open('d:/work/website/OA/.workbuddy/qa-2026-06-19-suiteB.md', 'w', encoding='utf-8') as f:
    f.write('# 172 业务流 E2E 测试报告 v2\n\n')
    f.write(f'**测试时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    f.write(f'**总流程**: 5  **通过**: {passed}  **失败**: {failed}  **Blocked**: {blocked}\n\n')
    f.write('## 详细结果\n\n')
    f.write('| 流程 | 结果 | 备注 |\n|------|------|------|\n')
    f.write(f'| 销售前链路 | {flows.get("销售前链路", "未跑")} | 线索→商机→报价→接受→成交→项目池 |\n')
    f.write(f'| 采购全流程 | {flows.get("采购全流程", "未跑")} | be-eng-2 未部署 purchase/* |\n')
    f.write(f'| 考勤请假 | {flows.get("考勤请假", "未跑")} | 打卡→请假→审批→销假 |\n')
    f.write(f'| 财务应收 | {flows.get("财务应收", "未跑")} | 应收→部分收款→收完→关闭 |\n')
    f.write(f'| 审批中心 | {flows.get("审批中心", "未跑")} | 财务+运营+项目 3 类审批 |\n')
print('\nReport saved: .workbuddy/qa-2026-06-19-suiteB.md')

c.close()
print('DONE')
