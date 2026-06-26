#!/usr/bin/env python3
"""Server-side 41-endpoint regression after split."""
import paramiko, json, urllib.request

HOST = "172.20.0.139"
USER = "nbcy"
PASSWORD = "admin123"
PORT = 22
BASE = "http://172.20.0.139:3001"

ENDPOINTS = [
    "dashboard/stats", "dashboard/recent-projects", "dashboard/recent-service-orders",
    "employees", "employees/departments", "employees/positions", "employees/skills",
    "customers", "customers/1", "customers/1/devices", "customers/1/follow-ups",
    "projects", "projects/1", "projects/1/construction-logs", "projects/1/contracts",
    "projects/1/suppliers", "projects/suppliers",
    "service/orders", "service/orders/1", "service/stats", "service/maintenance-contracts",
    "expenses", "expenses/my",
    "vehicles", "vehicles/usage",
    "inventory", "inventory/stock-records", "inventory/warehouses",
    "finance/overview", "finance/receivables", "finance/payables",
    "disk/folders", "disk/files",
    "knowledge/categories", "knowledge/articles",
    "attendance/overview", "attendance/records", "attendance/report",
    "notifications", "notifications/unread-count",
    "system-logs",
]

def login():
    req = urllib.request.Request(
        f"{BASE}/api/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)["data"]["token"]

def call(token, ep):
    req = urllib.request.Request(
        f"{BASE}/api/{ep}?month=2026-06&per_page=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR:{e}"[:8]

def main():
    token = login()
    print(f"token OK, len={len(token)}\n")
    ok = 0; bad = 0
    for ep in ENDPOINTS:
        code = call(token, ep)
        sym = "OK " if code == 200 else "BAD"
        if code == 200: ok += 1
        else: bad += 1
        print(f"  [{sym}] {ep:42s} {code}")
    print(f"\n=== Total: {ok} OK / {bad} FAIL / {len(ENDPOINTS)} ep ===")
    if bad > 0:
        # 拉日志
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, PORT, USER, PASSWORD, timeout=10)
        si, so, se = ssh.exec_command("tail -30 /var/www/oa-api/storage/logs/laravel.log")
        print("\n=== laravel.log tail ===")
        print(so.read().decode()[:2000])
        ssh.close()

if __name__ == "__main__":
    main()
