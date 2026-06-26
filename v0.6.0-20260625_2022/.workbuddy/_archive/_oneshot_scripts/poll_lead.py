#!/usr/bin/env python3
"""轮询 lead POST 直到非 500"""
import json, time, urllib.request, urllib.error


def login():
    req = urllib.request.Request("http://172.20.0.139:3001/api/auth/login",
        data=json.dumps({"username":"admin","password":"admin123"}).encode(),
        headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["data"]["token"]


def probe_lead():
    token = login()
    body = {"customer_name":"测试","contact_name":"张三","contact_phone":"13800000000","source":"phone","grade":"B","owner_id":1}
    req = urllib.request.Request("http://172.20.0.139:3001/api/sales/leads",
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","Accept":"application/json","Authorization":f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200]


for i in range(20):
    code, resp = probe_lead()
    print(f"{time.strftime('%H:%M:%S')} lead: {code} {resp[:120]}")
    if code == 200:
        print("  → lead 修复！")
        break
    time.sleep(30)
