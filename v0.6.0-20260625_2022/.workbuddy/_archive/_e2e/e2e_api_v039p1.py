#!/usr/bin/env python3
"""
v0.3.9 P1 后端 E2E 验证 (v2 - 用已知可用字段)
针对 172 测试平台: 172.20.0.139:3001
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_API = "http://172.20.0.139:3001/api"
RESULTS = []
RESOURCES = {}


def http(method, path, body=None, token=None, multipart=None, expect=None):
    url = BASE_API + path
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if multipart:
        headers.update(multipart.get("headers", {}))
        data = multipart["data"]
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8", errors="ignore")
            status = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        status = e.code
    except Exception as e:
        return 0, None, f"EXC: {e}"
    try:
        j = json.loads(raw) if raw else None
    except Exception:
        j = None
    if expect is not None:
        if isinstance(expect, list):
            ok = status in expect
        else:
            ok = status == expect
        RESULTS.append({"endpoint": f"{method} {path}", "expect": str(expect), "actual": status, "ok": ok, "resp": raw[:200] if not ok else ""})
    return status, j, raw


def login(username="admin", password="admin123"):
    s, j, _ = http("POST", "/auth/login", {"username": username, "password": password})
    if s == 200 and j:
        return j.get("data", {}).get("token") or j.get("token")
    raise RuntimeError(f"login failed status={s}")


def get_id(j, key="id"):
    if not j or not isinstance(j, dict):
        return None
    d = j.get("data")
    if isinstance(d, dict):
        return d.get(key)
    return None


def find_user(token):
    s, j, _ = http("GET", "/users?per_page=10", token=token)
    if s == 200 and j:
        d = j.get("data", {})
        users = d.get("data", []) if isinstance(d, dict) else d
        if users:
            return users[0]["id"]
    return 1


def find_customer(token):
    s, j, _ = http("GET", "/customers?per_page=10", token=token)
    if s == 200 and j:
        d = j.get("data", {})
        items = d.get("data", []) if isinstance(d, dict) else d
        if items:
            return items[0]["id"]
    return 1


def section(t):
    print(f"\n{'=' * 70}\n  {t}\n{'=' * 70}")


def main():
    print(f"v0.3.9 P1 API E2E v2 - {datetime.now().isoformat()}")
    token = login()
    user_id = find_user(token)
    customer_id = find_customer(token)
    print(f"user_id={user_id}  customer_id={customer_id}")

    # ===== 1. Leads (5 端点) =====
    section("1. Leads (5 端点)")

    # 1.1 POST 新建
    s, j, _ = http("POST", "/sales/leads", {
        "customer_id": customer_id,
        "customer_name": "E2E 测试客户",
        "contact_name": "张三",
        "contact_phone": "13800000001",
        "source": "phone",
        "grade": "B",
        "estimated_amount": 50000,
        "owner_id": user_id,
        "requirement": "需要监控设备",
        "notes": "E2E 测试创建",
    }, token=token, expect=200)
    lead_id = get_id(j) if j else None
    RESOURCES["lead_id"] = lead_id
    print(f"  POST /sales/leads -> {s}, lead_id={lead_id}")

    # 1.2 PUT 编辑
    if lead_id:
        s, j, _ = http("PUT", f"/sales/leads/{lead_id}", {
            "requirement": "更新需求",
            "rating": "A",
        }, token=token, expect=200)
        print(f"  PUT /sales/leads/{lead_id} -> {s}")

    # 1.3 PATCH status
    if lead_id:
        s, j, _ = http("PATCH", f"/sales/leads/{lead_id}/status", {
            "status": "contacting",
        }, token=token, expect=200)
        s, j, _ = http("PATCH", f"/sales/leads/{lead_id}/status", {
            "status": "qualified",
        }, token=token, expect=200)
        print(f"  PATCH /sales/leads/{lead_id}/status -> {s}")

    # 1.5 转商机
    opp_id = None
    if lead_id:
        s, j, _ = http("POST", f"/sales/leads/{lead_id}/convert-to-opp", {
            "name": "E2E 商机-从线索",
            "estimated_amount": 50000,
            "sales_id": user_id,
            "presale_id": user_id,
            "expected_sign_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "stage": "requirement",
        }, token=token, expect=200)
        opp_id = get_id(j)
        RESOURCES["opp_id"] = opp_id
        print(f"  POST /sales/leads/{lead_id}/convert-to-opp -> {s}, opp_id={opp_id}")

    # 1.4 DELETE
    s, j, _ = http("POST", "/sales/leads", {
        "customer_id": customer_id, "customer_name": "E2E 临时",
        "contact_name": "李四", "contact_phone": "13800000002",
        "source": "phone", "grade": "C", "owner_id": user_id,
    }, token=token, expect=200)
    del_lead_id = get_id(j) if j else None
    if del_lead_id:
        s, j, _ = http("DELETE", f"/sales/leads/{del_lead_id}", token=token, expect=200)
        print(f"  DELETE /sales/leads/{del_lead_id} -> {s}")

    # 1.6 状态机非法流转
    s, j, _ = http("PATCH", f"/sales/leads/{lead_id}/status" if lead_id else "/sales/leads/9999/status",
        {"status": "discarded"}, token=token, expect=409)  # qualified→discarded 合法，但 disposed→new 非法
    # qualified→new 不合法 - 用 converted→contacting 也不合法
    s, j, _ = http("PATCH", f"/sales/leads/{lead_id}/status" if lead_id else "/sales/leads/9999/status",
        {"status": "new"}, token=token, expect=409)
    print(f"  状态机非法流转 (qualified→new) -> {s} (期望 409)")

    # ===== 2. Opps (6 端点) =====
    section("2. Opps (6 端点)")

    # 2.1 POST
    s, j, _ = http("POST", "/sales/opps", {
        "customer_id": customer_id, "name": "E2E 商机",
        "estimated_amount": 100000, "sales_id": user_id, "presale_id": user_id,
        "expected_sign_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "stage": "requirement", "type": "comprehensive",
    }, token=token, expect=200)
    new_opp_id = get_id(j) if j else None
    RESOURCES["new_opp_id"] = new_opp_id
    print(f"  POST /sales/opps -> {s}, new_opp_id={new_opp_id}")

    # 2.2 PUT
    if new_opp_id:
        s, j, _ = http("PUT", f"/sales/opps/{new_opp_id}", {
            "name": "E2E 商机-更新",
            "estimated_amount": 150000,
        }, token=token, expect=200)
        print(f"  PUT /sales/opps/{new_opp_id} -> {s}")

    # 2.3 PATCH stage
    if new_opp_id:
        s, j, _ = http("PATCH", f"/sales/opps/{new_opp_id}/stage", {
            "stage": "solution",
        }, token=token, expect=200)
        print(f"  PATCH stage (requirement→solution) -> {s}")

    # 2.5 DELETE
    s, j, _ = http("POST", "/sales/opps", {
        "customer_id": customer_id, "name": "E2E 临时",
        "estimated_amount": 1000, "sales_id": user_id, "presale_id": user_id,
    }, token=token, expect=200)
    del_opp_id = get_id(j) if j else None
    if del_opp_id:
        s, j, _ = http("DELETE", f"/sales/opps/{del_opp_id}", token=token, expect=200)
        print(f"  DELETE /sales/opps/{del_opp_id} -> {s}")

    # 2.4 mark-lost (用现有 opp 31)
    s, j, _ = http("POST", "/sales/opps/31/mark-lost", {
        "lost_reason": "price_high",
        "notes": "E2E 战败测试",
    }, token=token, expect=200)
    print(f"  POST /sales/opps/31/mark-lost -> {s}")

    # 2.5 mark-won (新建一个)
    s, j, _ = http("POST", "/sales/opps", {
        "customer_id": customer_id, "name": "E2E 成交测试",
        "estimated_amount": 200000, "sales_id": user_id, "presale_id": user_id,
    }, token=token, expect=200)
    won_opp_id = get_id(j) if j else None
    if won_opp_id:
        for st in ["solution", "negotiation", "contracting"]:
            http("PATCH", f"/sales/opps/{won_opp_id}/stage", {"stage": st}, token=token)
        s, j, _ = http("POST", f"/sales/opps/{won_opp_id}/mark-won", {
            "contract_amount": 200000,
            "signed_at": "2026-06-19",
        }, token=token, expect=200)
        pool_id = None
        if j and isinstance(j, dict):
            d = j.get("data") or {}
            pool_id = d.get("id") or d.get("pool_id")
        RESOURCES["won_opp_id"] = won_opp_id
        RESOURCES["pool_id"] = pool_id
        print(f"  mark-won -> {s}, pool_id={pool_id}")

    # ===== 3. Quotes (7 端点) =====
    section("3. Quotes (7 端点)")

    quote_id = None
    if won_opp_id:
        s, j, _ = http("POST", "/sales/quotes", {
            "opportunity_id": won_opp_id,
            "version": 1,
            "discount_rate": 10,
            "tax_rate": 13,
            "valid_until": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "items": [
                {"name": "海康摄像头", "specification": "4K", "unit": "台", "quantity": 10, "unit_price": 2000, "total_price": 20000},
                {"name": "线材", "specification": "Cat5e", "unit": "箱", "quantity": 5, "unit_price": 1000, "total_price": 5000},
            ],
        }, token=token, expect=200)
        quote_id = get_id(j) if j else None
        RESOURCES["quote_id"] = quote_id
        print(f"  POST /sales/quotes -> {s}, quote_id={quote_id}")

    if quote_id:
        s, j, _ = http("PUT", f"/sales/quotes/{quote_id}", {
            "notes": "E2E 编辑",
        }, token=token, expect=200)
        print(f"  PUT /sales/quotes/{quote_id} -> {s}")

        s, j, _ = http("POST", f"/sales/quotes/{quote_id}/items", {
            "items": [{"name": "硬盘", "specification": "4TB", "unit": "块", "quantity": 2, "unit_price": 800, "total_price": 1600}],
        }, token=token, expect=200)
        print(f"  POST items -> {s}")

        s, j, _ = http("PUT", f"/sales/quotes/{quote_id}/status", {"status": "submitted"}, token=token, expect=200)
        s, j, _ = http("PUT", f"/sales/quotes/{quote_id}/status", {"status": "accepted"}, token=token, expect=200)
        print(f"  status: submitted→accepted -> {s}")

        s, j, _ = http("POST", f"/sales/quotes/{quote_id}/new-version", token=token, expect=200)
        v2_id = get_id(j) if j else None
        RESOURCES["quote_v2_id"] = v2_id
        print(f"  new-version -> {s}, v2_id={v2_id}")

    # DELETE 草稿报价单
    if won_opp_id:
        s, j, _ = http("POST", "/sales/quotes", {
            "opportunity_id": won_opp_id, "version": 1,
            "discount_rate": 0, "tax_rate": 13,
            "items": [{"name": "测试", "unit": "个", "quantity": 1, "unit_price": 100, "total_price": 100}],
        }, token=token, expect=200)
        del_quote_id = get_id(j) if j else None
        if del_quote_id:
            s, j, _ = http("DELETE", f"/sales/quotes/{del_quote_id}", token=token, expect=200)
            print(f"  DELETE quote -> {s}")

    # ===== 4. Referrers (3 端点) =====
    section("4. Referrers (3 端点)")

    s, j, _ = http("POST", "/sales/referrers", {
        "name": "E2E 推荐人",
        "phone": "13800000003",
        "bank_name": "招商银行",
        "bank_account": "6225880000000001",
        "commission_rate": 5,
    }, token=token, expect=200)
    referrer_id = get_id(j) if j else None
    RESOURCES["referrer_id"] = referrer_id
    print(f"  POST referrers -> {s}, referrer_id={referrer_id}")

    if referrer_id:
        s, j, _ = http("PUT", f"/sales/referrers/{referrer_id}", {
            "name": "E2E 推荐人-更新",
            "commission_rate": 8,
        }, token=token, expect=200)
        print(f"  PUT referrers -> {s}")

    # ===== 5. Pool (2 端点) =====
    section("5. Pool (2 端点)")

    pool_id = RESOURCES.get("pool_id")
    if pool_id:
        s, j, _ = http("PUT", f"/sales/pool/{pool_id}", {
            "notes": "E2E 更新",
        }, token=token, expect=200)
        print(f"  PUT pool -> {s}")

    # 转施工（用 RESOURCES.pool_id）
    new_project_id = None
    if pool_id:
        s, j, _ = http("POST", f"/sales/pool/{pool_id}/convert-to-project", {
            "name": "E2E 施工项目",
            "manager_id": user_id,
            "start_date": "2026-06-19",
            "end_date": "2026-09-19",
            "budget": 200000,
            "team_member_ids": [user_id],
        }, token=token, expect=200)
        if j and isinstance(j, dict):
            d = j.get("data") or {}
            new_project_id = d.get("id") or d.get("project_id")
        RESOURCES["new_project_id"] = new_project_id
        print(f"  convert-to-project -> {s}, project_id={new_project_id}")

    # ===== 6. Follow-ups + 附件 (5 端点) =====
    section("6. Follow-ups + 附件 (5 端点)")

    follow_id = None
    target_id = RESOURCES.get("won_opp_id") or RESOURCES.get("new_opp_id") or 1
    s, j, _ = http("POST", "/sales/follow-ups", {
        "target_type": "lead",
        "target_id": lead_id or 1,
        "content": "E2E 测试跟进",
        "next_action": "客户回访",
        "next_action_at": (datetime.now() + timedelta(days=3)).isoformat(),
    }, token=token, expect=200)
    follow_id = get_id(j) if j else None
    RESOURCES["follow_id"] = follow_id
    print(f"  POST /sales/follow-ups -> {s}, follow_id={follow_id}")

    if follow_id:
        s, j, _ = http("PUT", f"/sales/follow-ups/{follow_id}", {
            "content": "E2E 跟进-更新",
        }, token=token, expect=200)
        print(f"  PUT follow-up -> {s}")

        # 上传附件
        png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        boundary = "----E2Eboundary" + str(int(time.time()))
        body = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"e2e.png\"\r\n"
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + png + f"\r\n--{boundary}--\r\n".encode()
        s, j, _ = http("POST", f"/sales/follow-ups/{follow_id}/attachments", token=token,
            multipart={
                "headers": {"Content-Type": f"multipart/form-data; boundary={boundary}"},
                "data": body,
            }, expect=200)
        attachment_id = None
        if j and isinstance(j, dict):
            d = j.get("data") or {}
            if isinstance(d, dict):
                attachment_id = d.get("id")
            elif isinstance(d, list) and d:
                attachment_id = d[0].get("id")
        RESOURCES["attachment_id"] = attachment_id
        print(f"  upload attachment -> {s}, att_id={attachment_id}")

        if attachment_id:
            s, j, _ = http("GET", f"/sales/follow-ups/attachments/{attachment_id}/download",
                token=token, expect=200)
            print(f"  download -> {s}")
            s, j, _ = http("DELETE", f"/sales/follow-ups/attachments/{attachment_id}", token=token, expect=200)
            print(f"  delete attachment -> {s}")

        s, j, _ = http("DELETE", f"/sales/follow-ups/{follow_id}", token=token, expect=200)
        print(f"  DELETE follow-up -> {s}")

    # 7. 业务边界用例
    section("7. 业务边界用例")

    # 7.1 折扣 > 30% → 422
    if won_opp_id:
        s, j, _ = http("POST", "/sales/quotes", {
            "opportunity_id": won_opp_id, "version": 1,
            "discount_rate": 35,  # 违规
            "tax_rate": 13,
            "items": [{"name": "测试", "unit": "个", "quantity": 1, "unit_price": 100, "total_price": 100}],
        }, token=token, expect=422)
        print(f"  折扣 35% -> {s} (期望 422)")

    # 7.2 跨用户编辑 → 403
    try:
        user_token = login("zhangsan", "password")
        if RESOURCES.get("new_opp_id"):
            s, j, _ = http("PUT", f"/sales/opps/{RESOURCES['new_opp_id']}", {
                "name": "越权编辑",
            }, token=user_token, expect=403)
            print(f"  越权编辑 opp -> {s} (期望 403)")
        if RESOURCES.get("lead_id"):
            s, j, _ = http("PUT", f"/sales/leads/{RESOURCES['lead_id']}", {
                "requirement": "越权",
            }, token=user_token, expect=403)
            print(f"  越权编辑 lead -> {s} (期望 403)")
    except Exception as e:
        print(f"  越权测试异常: {e}")

    # 7.3 删除已转商机的线索 → 409/422
    if RESOURCES.get("lead_id") and RESOURCES.get("opp_id"):
        s, j, _ = http("DELETE", f"/sales/leads/{RESOURCES['lead_id']}", token=token, expect=[409, 422])
        print(f"  删已转商机线索 -> {s} (期望 409/422)")

    # 7.4 同商机重复建结算单 → 409
    if RESOURCES.get("won_opp_id"):
        s, j, _ = http("POST", "/sales/referral-settlements", {
            "opportunity_id": RESOURCES["won_opp_id"],
            "contract_amount": 200000, "commission_rate": 5,
        }, token=token, expect=[200, 201, 404])
        print(f"  首建结算单 -> {s}")
        if s in (200, 201):
            s2, _, _ = http("POST", "/sales/referral-settlements", {
                "opportunity_id": RESOURCES["won_opp_id"],
                "contract_amount": 200000, "commission_rate": 5,
            }, token=token, expect=409)
            print(f"  重复建结算单 -> {s2} (期望 409)")

    # 7.5 标记 lost 后无法再 mark-won
    s, j, _ = http("POST", "/sales/opps/31/mark-won", {
        "contract_amount": 100, "signed_at": "2026-06-19",
    }, token=token, expect=[409, 422])
    print(f"  lost→won 非法流转 -> {s} (期望 409/422)")

    # ===== 汇总 =====
    section("测试结果汇总")
    total = len(RESULTS)
    ok = sum(1 for r in RESULTS if r["ok"])
    fail = total - ok
    print(f"\n  总计: {total}  ✅ {ok}  ❌ {fail}  通过率: {ok/total*100:.1f}%")
    if fail > 0:
        print(f"\n  失败清单:")
        for r in RESULTS:
            if not r["ok"]:
                print(f"    ❌ {r['endpoint']:50s} 期望 {r['expect']} 实际 {r['actual']}")
                if r.get("resp"):
                    print(f"       响应: {r['resp'][:120]}")

    report_path = "D:/work/website/OA/.workbuddy/shots/v039p1/api_results.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base": BASE_API,
            "total": total, "ok": ok, "fail": fail,
            "pass_rate": f"{ok/total*100:.1f}",
            "results": RESULTS,
            "resources": RESOURCES,
        }, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  详细结果: {report_path}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
