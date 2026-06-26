#!/bin/bash
BASE='http://127.0.0.1/api'
# 登录
LOGIN=$(curl -sS -X POST "$BASE/auth/login" -H 'Content-Type: application/json' -d '{"username":"nbcy","password":"admin123"}')
echo "登录响应: $LOGIN" | head -c 200
echo ""
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('token',''))")
echo "TOKEN: ${TOKEN:0:20}..."

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  exit 1
fi

# 拿一个 status=new 的线索
LEADS=$(curl -sS "$BASE/sales/leads?per_page=50&status=new" -H "Authorization: Bearer $TOKEN")
echo "线索列表: $LEADS" | head -c 200
echo ""
LEAD_ID=$(echo "$LEADS" | python3 -c "import sys,json; d=json.load(sys.stdin).get('data',{}).get('data',[]); print(d[0]['id'] if d else '')")
echo "测试线索 ID: $LEAD_ID"

if [ -z "$LEAD_ID" ]; then
  echo "❌ 无可用线索"
  exit 1
fi

# 模拟前端看板拖动测试
echo ""
echo "=== 状态机测试 ==="
test_status() {
  local src=$1
  local dst=$2
  # 先重置为 src
  if [ "$src" != "now" ]; then
    curl -sS -X PUT "$BASE/sales/leads/$LEAD_ID/status" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "{\"status\":\"$src\"}" > /dev/null
  fi
  # 实际测试 dst
  RESP=$(curl -sS -X PUT "$BASE/sales/leads/$LEAD_ID/status" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "{\"status\":\"$dst\"}")
  CODE=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code','?'))")
  MSG=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','')[:60] if d.get('code')!=0 else f\"OK -> db={d.get('data',{}).get('status','?')}\")")
  if [ "$CODE" = "0" ]; then
    echo "✅ $src → $dst  $MSG"
  else
    echo "❌ $src → $dst  $MSG"
  fi
}

# 关键测试：前端看板值 (contacted/qualified/proposal/negotiating/won/lost)
test_status "new" "contacted"      # 跟进中
test_status "new" "proposal"       # 方案报价
test_status "new" "negotiating"    # 谈判中
test_status "new" "won"            # 成交
test_status "new" "lost"           # 战败
test_status "new" "qualified"      # 合格
