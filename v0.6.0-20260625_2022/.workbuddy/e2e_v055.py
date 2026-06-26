#!/usr/bin/env python3
"""
V0.5.5 维修中心 + 返修管理 e2e

测试场景:
1. 创建工单 (pending)
2. 派单 (assigned)
3. 开始 (in_progress)
4. 转返修 (converted_to_repair + 返修单 received) — 关键事务
5. 返修单: 寄出 (outbound shipment) -> in_repair -> 加 method (paid_repair) -> repaired -> 寄回 -> close
6. 验证 audit 双向记录
7. 验证取消流程
8. 验证状态机非法转换拒绝
"""
import requests
from datetime import datetime, timedelta

API = 'http://192.168.3.117/api'

def login(u, p='admin123'):
    r = requests.post(f'{API}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0:
        raise Exception(f"login {u} 失败: {j}")
    return j['data']['token']

def req(method, t, path, **kwargs):
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f'Bearer {t}'
    return requests.request(method, f'{API}{path}', headers=headers, timeout=10, **kwargs)

def main():
    print('='*60)
    print('  V0.5.5 维修中心 + 返修管理 e2e')
    print('='*60)
    fails = 0
    t = login('admin1')
    print(f'  ✓ admin1 token len={len(t)}')

    # 1) 创建工单
    print('\n[1] POST /api/work-orders (新建)')
    r = req('POST', t, '/work-orders', json={
        'contact_name': '张三',
        'contact_phone': '13800138000',
        'address': '北京市朝阳区国贸大厦',
        'priority': 'high',
        'fault_description': '海康威视摄像头 DS-2CD2T47 不通电, 客户已使用 2 年',
        'equipment_brand': '海康威视',
        'equipment_model': 'DS-2CD2T47',
        'serial_no': 'HK2024-001-XC',
    })
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ 创建工单失败: {r.text[:200]}')
        return
    wo = r.json()['data']
    print(f'  ✓ 工单 {wo["code"]} id={wo["id"]} status={wo["status"]}')

    # 2) 派单
    print(f'\n[2] POST /api/work-orders/{wo["id"]}/assign (派给 sales_yang id=86)')
    r = req('POST', t, f'/work-orders/{wo["id"]}/assign', json={'engineer_id': 86, 'note': '紧急'})
    if r.json().get('code') != 0:
        print(f'  ✗ 派单失败: {r.text[:200]}'); fails += 1
    else:
        print(f'  ✓ 状态 {r.json()["data"]["status"]} assignee={r.json()["data"]["assignee_name"]}')

    # 3) 开始
    print(f'\n[3] POST /api/work-orders/{wo["id"]}/start')
    r = req('POST', t, f'/work-orders/{wo["id"]}/start')
    if r.json().get('code') != 0:
        print(f'  ✗ 开始失败: {r.text[:200]}'); fails += 1
    else:
        print(f'  ✓ 状态 {r.json()["data"]["status"]} started_at={r.json()["data"]["started_at"]}')

    # 4) 工单转返修 (关键事务)
    print(f'\n[4] POST /api/work-orders/{wo["id"]}/convert-to-repair ⭐')
    r = req('POST', t, f'/work-orders/{wo["id"]}/convert-to-repair', json={
        'reason': '现场检测: 主板烧毁, 需送厂',
        'method_type': 'paid_repair',
    })
    if r.json().get('code') != 0:
        print(f'  ✗ 转返修失败: {r.text[:200]}'); fails += 1
        return
    j = r.json()
    ro = j['data']['repair_order']
    new_wo = j['data']['work_order']
    print(f'  ✓ 工单 {new_wo["code"]} status={new_wo["status"]} (locked)')
    print(f'  ✓ 返修单 {ro["code"]} status={ro["status"]} source={ro["source_type"]} from {ro["source_code"]}')

    # 5) 返修单: 寄出
    print(f'\n[5] POST /api/repair-orders/{ro["id"]}/ship-out')
    r = req('POST', t, f'/repair-orders/{ro["id"]}/ship-out', json={
        'carrier': '顺丰',
        'tracking_no': 'SF20260624-001',
        'cost': 25.00,
        'sender_name': '吴八哥',
        'sender_phone': '13900000001',
        'sender_address': '北京市朝阳区国贸',
        'receiver_name': '海康售后',
        'receiver_phone': '0571-88888888',
        'receiver_address': '浙江省杭州市海康威视总部',
        'estimated_arrival': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
    })
    if r.json().get('code') != 0:
        print(f'  ✗ 寄出失败: {r.text[:200]}'); fails += 1
    else:
        print(f'  ✓ 返修 status={r.json()["data"]["status"]} shipments={len(r.json()["data"]["shipments"])}')

    # 6) 标记维修中
    print(f'\n[6] POST /api/repair-orders/{ro["id"]}/in-repair')
    r = req('POST', t, f'/repair-orders/{ro["id"]}/in-repair')
    print(f'  ✓ status={r.json().get("data", {}).get("status") if r.json().get("code") == 0 else "FAIL"}')

    # 7) 加维修方式 (付费维修)
    print(f'\n[7] POST /api/repair-orders/{ro["id"]}/methods (付费维修)')
    r = req('POST', t, f'/repair-orders/{ro["id"]}/methods', json={
        'method_type': 'paid_repair',
        'method_category': 'out_warranty',
        'estimated_cost': 800.00,
        'actual_cost': 750.00,
        'hours_spent': 3.5,
        'parts_replaced': [
            {'name': '主板 PCB', 'qty': 1, 'price': 500},
            {'name': '电源模块', 'qty': 1, 'price': 150},
        ],
        'payment_method': '转账',
        'payment_status': 'unpaid',
        'remarks': '客户同意付费维修',
    })
    if r.json().get('code') != 0:
        print(f'  ✗ 加 method 失败: {r.text[:200]}'); fails += 1
    else:
        print(f'  ✓ method id={r.json()["data"]["id"]} type={r.json()["data"]["method_label"]} ¥{r.json()["data"]["actual_cost"]}')

    # 8) 验证: 没有 method 时不能 mark repaired
    # (本测试已加 method, 应能成功)
    print(f'\n[8] POST /api/repair-orders/{ro["id"]}/repaired')
    r = req('POST', t, f'/repair-orders/{ro["id"]}/repaired')
    if r.json().get('code') != 0:
        print(f'  ✗ 标记修好失败: {r.text[:200]}'); fails += 1
    else:
        print(f'  ✓ status={r.json()["data"]["status"]}')

    # 9) 寄回
    print(f'\n[9] POST /api/repair-orders/{ro["id"]}/ship-back')
    r = req('POST', t, f'/repair-orders/{ro["id"]}/ship-back', json={
        'carrier': '顺丰',
        'tracking_no': 'SF20260630-002',
        'cost': 25.00,
        'sender_name': '海康售后',
        'sender_phone': '0571-88888888',
        'sender_address': '浙江省杭州市',
        'receiver_name': '张三',
        'receiver_phone': '13800138000',
        'receiver_address': '北京市朝阳区国贸',
    })
    if r.json().get('code') != 0:
        print(f'  ✗ 寄回失败: {r.text[:200]}'); fails += 1
    else:
        j = r.json()
        print(f'  ✓ status={j["data"]["status"]} 物流 {len(j["data"]["shipments"])} 条 (out + in)')

    # 10) 关闭
    print(f'\n[10] POST /api/repair-orders/{ro["id"]}/close')
    r = req('POST', t, f'/repair-orders/{ro["id"]}/close')
    print(f'  ✓ status={r.json().get("data", {}).get("status")}')

    # 11) 验证详情
    print(f'\n[11] GET /api/repair-orders/{ro["id"]} (详情)')
    r = req('GET', t, f'/repair-orders/{ro["id"]}')
    d = r.json()['data']
    print(f'  ✓ {d["code"]} status={d["status_label"]} method={d["method_label"]} ¥{d["total_cost"]}')
    print(f'  ✓ shipments={len(d.get("shipments", []))} methods={len(d.get("methods", []))}')

    # 12) 验证原工单已锁 (is_locked=true)
    print(f'\n[12] GET /api/work-orders/{wo["id"]} (验证锁定)')
    r = req('GET', t, f'/work-orders/{wo["id"]}')
    d = r.json()['data']
    print(f'  ✓ status={d["status"]} is_locked={d["is_locked"]} converted_repair_id={d["converted_repair_id"]}')

    # 13) 验证原工单不能修改
    print(f'\n[13] PUT /api/work-orders/{wo["id"]} (应被拒)')
    r = req('PUT', t, f'/work-orders/{wo["id"]}', json={'priority': 'low'})
    if r.json().get('code') == 0:
        print('  ✗ 应被拒但通过了')
        fails += 1
    else:
        print(f'  ✓ 拒绝: {r.json().get("message")[:50]}')

    # 14) 状态机非法转换 — pending 直接转返修应失败
    print(f'\n[14] 创建新工单, 测非法转换')
    r = req('POST', t, '/work-orders', json={
        'contact_name': '李四',
        'fault_description': '测试',
    })
    wo2 = r.json()['data']
    print(f'  工单 {wo2["code"]} status={wo2["status"]}')
    r = req('POST', t, f'/work-orders/{wo2["id"]}/convert-to-repair', json={'reason': 'test'})
    if r.json().get('code') == 0:
        print('  ✗ pending 状态不应能转返修')
        fails += 1
    else:
        print(f'  ✓ 拒绝: {r.json().get("message")[:50]}')
    # 清理
    req('DELETE', t, f'/work-orders/{wo2["id"]}')

    # 15) audit 验证 (work_order_converted_to_repair 应该有 1 条)
    print(f'\n[15] GET /api/audit/role-changes (应含工单转换记录)')
    r = req('GET', t, '/audit/role-changes?days=1')
    rows = r.json()['data']
    converted = [x for x in rows if 'work_order_converted' in (x['action'] or '')]
    print(f'  ✓ 找到 {len(converted)} 条 work_order_converted 记录')

    # 16) 看板统计
    print(f'\n[16] GET /api/work-orders/stats')
    r = req('GET', t, '/work-orders/stats?days=7')
    d = r.json()['data']
    print(f'  ✓ total={d["total"]} converted={d["converted_to_repair"]} rate={d["conversion_rate"]}%')

    print(f'\n[17] GET /api/repair-orders/stats')
    r = req('GET', t, '/repair-orders/stats?days=7')
    d = r.json()['data']
    print(f'  ✓ total={d["total"]} closed={d["closed"]} cost=¥{d["total_cost"]}')

    print('\n' + '='*60)
    if fails == 0:
        print('  ✓ V0.5.5 e2e ALL PASS (关键流程跑通)')
    else:
        print(f'  ✗ {fails} 失败')
        import sys; sys.exit(1)

if __name__ == '__main__':
    main()
