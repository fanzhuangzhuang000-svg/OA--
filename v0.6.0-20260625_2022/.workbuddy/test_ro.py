import requests
T = requests.post('http://192.168.3.117/api/auth/login', json={'username':'admin1','password':'admin123'}).json()['data']['token']
r = requests.post('http://192.168.3.117/api/repair-orders', headers={'Authorization':f'Bearer {T}'}, json={'contact_name':'张三','contact_phone':'13800139567','equipment_brand':'海康','equipment_model':'DS','fault_description':'块3测试'})
print('status:', r.status_code)
print('body:', r.text[:500])
