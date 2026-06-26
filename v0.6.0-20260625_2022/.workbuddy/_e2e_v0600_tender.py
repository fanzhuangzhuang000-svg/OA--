"""
V0.6.0 招标中心 E2E 验证

流程:
1. 内部: 创建招标项目 (含清单 + 邀请 3 家供应商)
2. 内部: 发布 (生成 public_token)
3. 外部 (Portal): 通过 token 拉公开信息
4. 外部 (Portal): 3 家供应商提交投标
5. 内部: 查看投标列表
6. 内部: 评标打分 (3 家)
7. 内部: 中标 (自动生成 PO + 应付)
8. 验证: 中标供应商状态=awarded, 其他=rejected, PO 和 payable 已落库
"""
import sys
import requests

API = 'http://192.168.3.117:8081'

PASS = 0
FAIL = 0
ERRORS = []


def check(name, ok, msg=''):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f'  ✓ {name}')
    else:
        FAIL += 1
        print(f'  ✗ {name} — {msg}')


def main():
    r = requests.post(f'{API}/api/auth/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
    tok = r.json()['data']['token']
    H = {'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'}

    print('[1] 内部: 创建招标项目 (草稿)')
    # 拿 3 个 supplier
    rs = requests.get(f'{API}/api/suppliers', headers=H, params={'per_page': 5}, timeout=10)
    sups = (rs.json().get('data') or {}).get('items') or []
    sup_ids = [s['id'] for s in sups[:3]]
    print(f'   邀请供应商 ids: {sup_ids}')

    r1 = requests.post(f'{API}/api/tenders', headers=H, json={
        'name': 'V0.6.0-E2E 招标测试项目',
        'type': 'tender',
        'project_id': None,
        'description': 'E2E 验证招标中心全流程',
        'required_items': [
            {'name': '高清摄像头', 'spec': '200万像素', 'unit': '台', 'qty': 10},
            {'name': 'NVR 录像机', 'spec': '8路', 'unit': '台', 'qty': 1},
        ],
        'invited_supplier_ids': sup_ids,
        'deadline': '2026-12-31 23:59:59',
        'open_at': '2027-01-01 10:00:00',
        'score_config': {'technical': 40, 'price': 40, 'business': 20},
    }, timeout=10)
    check('create tender', r1.status_code == 201, r1.text[:200])
    t = r1.json()['data']
    tender_id = t['id']
    token = t['public_token']
    print(f'   id={tender_id} code={t["code"]} token={token[:8]}...')

    print('[2] 内部: 发布')
    r2 = requests.post(f'{API}/api/tenders/{tender_id}/publish', headers=H, timeout=10)
    check('publish', r2.status_code == 200 and r2.json()['data']['status'] == 'bidding', r2.text[:200])

    print('[3] 外部 Portal: 通过 token 拉公开信息')
    r3 = requests.get(f'{API}/api/portal/t/{token}', timeout=10)
    check('tender by token', r3.status_code == 200, r3.text[:200])
    pt = r3.json()['data']
    check('公开信息有 name', pt.get('name') == 'V0.6.0-E2E 招标测试项目')
    check('公开信息有 deadline', pt.get('deadline') is not None)
    check('公开信息有 required_items (2 条)', len(pt.get('required_items') or []) == 2)
    check('不返回 invited_supplier_ids (内部字段)', 'invited_supplier_ids' not in pt)
    check('不返回 score_config (内部字段)', 'score_config' not in pt)

    print('[4] 外部 Portal: 3 家供应商提交投标')
    bid_data = [
        {'sup_id': sup_ids[0], 'amount': 18000, 'days': 7, 'tech': 80},
        {'sup_id': sup_ids[1], 'amount': 16000, 'days': 5, 'tech': 90},  # 最低价
        {'sup_id': sup_ids[2], 'amount': 20000, 'days': 6, 'tech': 85},
    ]
    bid_ids = []
    for bd in bid_data:
        rb = requests.post(f'{API}/api/portal/t/{token}/bids', json={
            'supplier_id': bd['sup_id'],
            'total_amount': bd['amount'],
            'lead_time_days': bd['days'],
            'technical_proposal': f'E2E-{bd["sup_id"]} 投标方案: ...',
            'remark': '价格已含税',
            'items': [
                {'name': '高清摄像头', 'spec': '200万像素', 'unit': '台', 'quantity': 10, 'unit_price': bd['amount'] * 0.95 / 10},
                {'name': 'NVR 录像机', 'spec': '8路', 'unit': '台', 'quantity': 1, 'unit_price': bd['amount'] * 0.05},
            ],
        }, timeout=10)
        check(f'bid by sup {bd["sup_id"]}', rb.status_code == 200, rb.text[:200])
        bid_ids.append(rb.json()['data']['id'])

    # 重复投标应该被拒
    rdup = requests.post(f'{API}/api/portal/t/{token}/bids', json={
        'supplier_id': sup_ids[0], 'total_amount': 99999,
    }, timeout=10)
    # 注: 重复的会更新而非拒绝 — 这版逻辑是 upsert
    print(f'   重复投标: st={rdup.status_code} (upsert)')

    print('[5] 内部: 投标列表')
    r5 = requests.get(f'{API}/api/tenders/{tender_id}/bids', headers=H, timeout=10)
    check('list bids', r5.status_code == 200, r5.text[:200])
    bids_list = r5.json()['data']
    check('3 家投标', len(bids_list) == 3, f'实际 {len(bids_list)}')
    for b in bids_list:
        print(f'     - bid {b["id"]} sup={b["supplier"]["name"]} 金额={b["total_amount"]} status={b["status"]}')

    print('[6] 内部: 评标打分')
    # 最低价得分最高: sup_ids[1] 16000, 90 tech → 90
    # 其他按价格相对评分
    r6 = requests.post(f'{API}/api/tenders/{tender_id}/evaluate', headers=H, json={
        'evaluations': [
            {'bid_id': bid_ids[0], 'technical': 80, 'price': 70, 'business': 85},  # 18000
            {'bid_id': bid_ids[1], 'technical': 90, 'price': 100, 'business': 90},  # 16000 (winner)
            {'bid_id': bid_ids[2], 'technical': 85, 'price': 60, 'business': 80},  # 20000
        ],
    }, timeout=10)
    check('evaluate', r6.status_code == 200, r6.text[:200])

    # 看分数
    r5b = requests.get(f'{API}/api/tenders/{tender_id}/bids', headers=H, timeout=10)
    for b in r5b.json()['data']:
        print(f'     - bid {b["id"]} sup={b["supplier"]["name"]} score={b.get("total_score")} status={b["status"]}')

    print('[7] 内部: 中标 (选 sup_ids[1] / 16000)')
    r7 = requests.post(f'{API}/api/tenders/{tender_id}/award', headers=H, json={
        'bid_id': bid_ids[1],
    }, timeout=10)
    check('award', r7.status_code == 200, r7.text[:300])
    award_data = r7.json()['data']
    check('中标 bid 状态=awarded', award_data['bid']['status'] == 'awarded')
    check('中标 tender 状态=awarded', award_data['tender']['status'] == 'awarded')
    auto = award_data.get('auto', {})
    po = auto.get('po')
    payable = auto.get('payable')
    print(f'   自动 PO: {po}')
    print(f'   自动 Payable: {payable}')
    check('PO 已生成', po is not None and po.get('code'))
    check('Payable 已生成', payable is not None and payable.get('ref_no'))

    print('[8] 验证: 其他供应商状态=rejected')
    # award 之后再拉一次最新状态
    r5c = requests.get(f'{API}/api/tenders/{tender_id}/bids', headers=H, timeout=10)
    for b in r5c.json()['data']:
        if b['id'] != bid_ids[1]:
            check(f'  bid {b["id"]} status=rejected', b['status'] == 'rejected')

    print('[9] 验证: 中标后不能再投标')
    r9 = requests.post(f'{API}/api/portal/t/{token}/bids', json={
        'supplier_id': sup_ids[2], 'total_amount': 15000,
    }, timeout=10)
    check('中标后新投标被拒', r9.status_code == 422, r9.text[:200])

    print('[10] 验证: 取消状态不可再操作')
    r10 = requests.post(f'{API}/api/tenders/{tender_id}/publish', headers=H, timeout=10)
    check('已 awarded 再 publish 被拒', r10.status_code == 422, r10.text[:200])

    print()
    print('======================================')
    print(f'✅ 通过 {PASS}  失败 {FAIL}')
    print('======================================')
    if FAIL > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
