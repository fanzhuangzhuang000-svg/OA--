import paramiko
import json
cli=paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=10)
def run(c):
    sin,sout,serr=cli.exec_command(c, timeout=30)
    return sout.read().decode('utf-8','replace')

r = run("""curl -s -X POST http://127.0.0.1:3000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' """)
token = json.loads(r)['data']['token']
H = f'Authorization: Bearer {token}'

print('=== Departments ===')
r = run(f"curl -s -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/employees/departments")
depts = json.loads(r)['data']
print(f'  LIST OK ({len(depts)} depts)')

r = run(f"""curl -s -X POST -H '{H}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{"name":"E2E创建部","parent_id":1}}' http://127.0.0.1:3000/api/employees/departments""")
print(f'  CREATE: {r[:200]}')
new_id = json.loads(r)['data']['id']

r = run(f"""curl -s -X PUT -H '{H}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{"name":"E2E更名部","sort_order":88}}' http://127.0.0.1:3000/api/employees/departments/{new_id}""")
print(f'  UPDATE: {r[:200]}')

r = run(f"curl -s -X DELETE -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/employees/departments/{new_id}")
print(f'  DELETE: {r[:200]}')

print()
print('=== Positions ===')
r = run(f"curl -s -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/employees/positions")
print(f'  LIST: {len(json.loads(r)["data"])} positions')

r = run(f"""curl -s -X POST -H '{H}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{"name":"E2E岗位","department_id":1}}' http://127.0.0.1:3000/api/employees/positions""")
print(f'  CREATE: {r[:200]}')

print()
print('=== Skills ===')
r = run(f"curl -s -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/employees/skills")
print(f'  LIST: {len(json.loads(r)["data"])} skills')

r = run(f"""curl -s -X POST -H '{H}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{"name":"E2E技能","color":"#0C447C","category":"other"}}' http://127.0.0.1:3000/api/employees/skills""")
print(f'  CREATE: {r[:200]}')
sid = json.loads(r)['data']['id']

r = run(f"curl -s -X DELETE -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/employees/skills/{sid}")
print(f'  DELETE: {r[:200]}')

print()
print('=== Roles ===')
r = run(f"curl -s -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/roles")
roles = json.loads(r)['data']
print(f'  LIST: {roles["total"]} roles')

r = run(f"""curl -s -X POST -H '{H}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{"name":"e2e_test_role","description":"测试"}}' http://127.0.0.1:3000/api/roles""")
print(f'  CREATE: {r[:200]}')
rid = json.loads(r)['data']['id']

r = run(f"curl -s -X DELETE -H '{H}' -H 'Accept: application/json' http://127.0.0.1:3000/api/roles/{rid}")
print(f'  DELETE: {r[:200]}')
