# API 烟囱测试报告

**总端点**: 635 | **通过**: 635 | **耗时**: 114.0s

## 状态码分布
- HTTP 200: 345
- HTTP 404: 123
- HTTP 422: 112
- HTTP 429: 38
- HTTP 409: 17

## 失败端点（HTTP >= 500）
共 0 个


## 401/404/422 端点（业务层，路由可达）

### HTTP 404 (123 个)
- `PUT /api/vehicles/maintenances/1` → 404 (184.9ms)
  body: `{"code":404,"message":"\u63a5\u53e3\u4e0d\u5b58\u5728"}`
- `PUT /api/sales/leads/1` → 404 (174.7ms)
  body: `{"code":404,"message":"\u63a5\u53e3\u4e0d\u5b58\u5728"}`
- `POST /api/sales/leads/1/convert-to-opp` → 404 (174.4ms)
  body: `{"code":404,"message":"\u63a5\u53e3\u4e0d\u5b58\u5728"}`
- `POST /api/expenses/1/pay` → 404 (170.6ms)
  body: `{"code":404,"message":"\u63a5\u53e3\u4e0d\u5b58\u5728"}`
- `DELETE /api/sales/products/1` → 404 (168.7ms)
  body: `{"code":404,"message":"\u63a5\u53e3\u4e0d\u5b58\u5728"}`
- ...还有 118 个

### HTTP 422 (112 个)
- `POST /api/disk/folders` → 422 (191.7ms)
  body: `{"code":422,"message":"\u6570\u636e\u6821\u9a8c\u5931\u8d25","errors":{"name":["validation.required"`
- `POST /api/vehicles/apply` → 422 (185.8ms)
  body: `{"code":422,"message":"\u6570\u636e\u6821\u9a8c\u5931\u8d25","errors":{"usage_date":["validation.req`
- `POST /api/sales/leads` → 422 (183.9ms)
  body: `{"code":422,"message":"\u6570\u636e\u6821\u9a8c\u5931\u8d25","errors":{"customer_name":["validation.`
- `POST /api/inventory/batch-delete` → 422 (183.7ms)
  body: `{"code":422,"message":"\u6570\u636e\u6821\u9a8c\u5931\u8d25","errors":{"ids":["validation.required"]`
- `DELETE /api/finance/receivables/1` → 422 (181.9ms)
  body: `{"code":1001,"message":"\u8be5\u5e94\u6536\u5355\u5df2\u6709\u6536\u6b3e\u8bb0\u5f55\uff0c\u4e0d\u51`
- ...还有 107 个

### HTTP 429 (38 个)
- `HEAD /api/settings` → 429 (164.1ms)
- `POST /api/users` → 429 (158.5ms)
  body: `{"code":429,"message":"Too Many Attempts."}`
- `HEAD /api/service/orders/stats` → 429 (156.8ms)
- `GET /api/users/1` → 429 (151.8ms)
  body: `{"code":429,"message":"Too Many Attempts."}`
- `HEAD /api/users/1` → 429 (149.7ms)
- ...还有 33 个

## 最慢的 20 个
- `POST /api/backups` → 200 (316.9ms)
- `HEAD /api/vehicles/applies` → 200 (198.9ms)
- `POST /api/inventory/batch-export` → 200 (193.8ms)
- `GET /api/projects/payment-calendar` → 200 (192.7ms)
- `GET /api/vehicles/maintenances` → 200 (192.4ms)
- `POST /api/disk/folders` → 422 (191.7ms)
- `HEAD /api/finance/summary/aging` → 200 (188.5ms)
- `GET /api/customers/health` → 200 (187.3ms)
- `HEAD /api/customers/health` → 200 (187.0ms)
- `GET /api/customers` → 200 (186.2ms)
- `POST /api/vehicles/apply` → 422 (185.8ms)
- `HEAD /api/customers` → 200 (185.3ms)
- `PUT /api/vehicles/maintenances/1` → 404 (184.9ms)
- `DELETE /api/sales/quotes/1` → 409 (184.4ms)
- `POST /api/sales/leads` → 422 (183.9ms)
- `GET /api/finance/summary/cashflow` → 200 (183.7ms)
- `POST /api/inventory/batch-delete` → 422 (183.7ms)
- `POST /api/attendance/clock-out` → 200 (183.3ms)
- `DELETE /api/finance/receivables/1` → 422 (181.9ms)
- `POST /api/sales/pool/1/convert-to-project` → 422 (181.7ms)