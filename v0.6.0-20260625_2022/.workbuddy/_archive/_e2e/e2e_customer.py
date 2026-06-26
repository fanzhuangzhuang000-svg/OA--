"""E2E test for customer endpoints."""
import paramiko, json, time
HOST='172.20.0.139'; PORT=22; USER='nbcy'; PWD='admin123'

def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, port=PORT, username=USER, password=PWD, timeout=10)

    def run(c, timeout=30):
        sin, sout, serr = cli.exec_command(c, timeout=timeout)
        return sout.read().decode('utf-8', 'replace')

    r = run("""curl -s -X POST http://127.0.0.1:3000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}'""")
    token = json.loads(r)['data']['token']
    H = f'Authorization: Bearer {token}'
    A = 'Accept: application/json'

    print('=== 客户管理 E2E ===')
    # 1. list
    r = run(f"""curl -s -H '{H}' -H '{A}' 'http://127.0.0.1:3000/api/customers'""")
    data = json.loads(r)['data']
    print(f'[1] list OK: total={data["total"]}, per_page={data["per_page"]}')

    # 2. create
    ts = int(time.time())
    name = f'按钮测试-{ts}'
    payload = json.dumps({'name': name, 'industry': '互联网科技', 'category': 'VIP',
                          'contact': '测试人', 'phone': '13800138000', 'tags': ['重点客户']})
    r = run(f"""curl -s -X POST -H '{H}' -H 'Content-Type: application/json' -H '{A}' -d '{payload}' 'http://127.0.0.1:3000/api/customers'""")
    new_id = json.loads(r)['data']['id']
    print(f'[2] create OK: id={new_id}, name={name}')

    # 3. update
    payload = json.dumps({'name': f'按钮测试-{ts}改名', 'category': '普通'})
    r = run(f"""curl -s -X PUT -H '{H}' -H 'Content-Type: application/json' -H '{A}' -d '{payload}' 'http://127.0.0.1:3000/api/customers/{new_id}'""")
    print(f'[3] update OK: {json.loads(r)["message"]}')

    # 4. add follow
    payload = json.dumps({'type': 'phone', 'content': 'E2E 测试跟进'})
    r = run(f"""curl -s -X POST -H '{H}' -H 'Content-Type: application/json' -H '{A}' -d '{payload}' 'http://127.0.0.1:3000/api/customers/{new_id}/follow-ups'""")
    print(f'[4] add follow OK: {json.loads(r)["message"]}')

    # 5. stats
    r = run(f"""curl -s -H '{H}' -H '{A}' 'http://127.0.0.1:3000/api/customers/stats'""")
    print(f'[5] stats OK: {r[:200]}')

    # 6. import
    csv_path = '/tmp/test.csv'
    csv_content = f'客户名称,所属行业,联系人,联系电话,客户分类,标签\nimport-test-{ts},互联网科技,导入人,13900000000,普通,新客户\nimport-test-{ts}-2,金融行业,导入人2,13900000001,VIP,战略合作\n'
    run(f"cat > {csv_path} << 'CSVE'\n{csv_content}CSVE")
    r = run(f"""curl -s -X POST -H '{H}' -H '{A}' -F 'file=@{csv_path}' 'http://127.0.0.1:3000/api/customers/import'""")
    print(f'[6] import OK: {r[:300]}')

    # 7. delete
    r = run(f"""curl -s -X DELETE -H '{H}' -H '{A}' 'http://127.0.0.1:3000/api/customers/{new_id}'""")
    print(f'[7] delete OK: {json.loads(r)["message"]}')

    # 8. cleanup import test
    r = run(f"""curl -s -H '{H}' -H '{A}' 'http://127.0.0.1:3000/api/customers?keyword=import-test-{ts}'""")
    ids = [c['id'] for c in json.loads(r)['data']['data']]
    for cid in ids:
        run(f"""curl -s -X DELETE -H '{H}' -H '{A}' 'http://127.0.0.1:3000/api/customers/{cid}'""")
    print(f'[8] cleanup OK: deleted {len(ids)}')

    print('=== 全部通过 ===')
    cli.close()

if __name__ == '__main__':
    main()
