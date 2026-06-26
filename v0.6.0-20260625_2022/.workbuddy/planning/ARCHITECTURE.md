# v0.3.9 P1 业务逻辑 — 技术架构方案

> 编写：architect · 日期：2026-06-19
> 范围：销售前链路 P1（线索/商机/报价/项目池/跟进/推荐人 5 个模块的真实业务逻辑）

---

## 一、架构总览

```
┌──────────────────────────────────────────────────────────┐
│  浏览器 (Vue3 + Element Plus)                            │
│  ├─ /sales/leads/*     /sales/opps/*    /sales/pool/*    │
│  ├─ /project/pool      /project/list                     │
│  └─ /sales/referrers                                       │
└─────────────────────┬────────────────────────────────────┘
                      │  axios (拦截器自动解包 res.data)
                      ▼
┌──────────────────────────────────────────────────────────┐
│  Nginx (172.20.0.139 / 152.136.115.121)                  │
│  ├─ 3000  /pc-web  (SPA fallback → dist/index.html)      │
│  └─ 3001  /pc-api  (php-fpm 8.3)                          │
└─────────────────────┬────────────────────────────────────┘
                      │  Sanctum Token 认证 (auth:sanctum)
                      ▼
┌──────────────────────────────────────────────────────────┐
│  Laravel 13 (PHP 8.3) — /var/www/oa-api                  │
│  ├─ SalesController      (5 模块 30+ 端点)                │
│  ├─ ProjectController    (转施工项目 / 状态同步)          │
│  ├─ FollowUpObserver     (附件清理 / 状态推送)            │
│  └─ ProjectObserver      (签约 → 居间费自动生成)          │
│                                                            │
│  ├─ Storage (public disk)                                 │
│  │   └─ /var/www/oa-api/storage/app/public/follow-ups/   │
│  └─ 业务事务: DB::transaction (转化 / 结算 / 签约)        │
└─────────────────────┬────────────────────────────────────┘
                      │  Eloquent ORM
                      ▼
┌──────────────────────────────────────────────────────────┐
│  PostgreSQL 15 (security_oa / oa_user)                    │
│  leads / opportunities / quotations / quotation_items     │
│  project_pool / sales_follow_ups / sales_follow_up_attach│
│  + 已有: projects / contracts / referrers / inventory     │
└──────────────────────────────────────────────────────────┘
```

**核心原则**（贯穿全文）
1. **单文件装所有类** — 销售前链路 8 个 Model 全部塞到 `ProjectModels.php`（项目 / 销售 / 客户跟进同源）
2. **路由顺序** — 任何 prefix group 中 `{通配}` 必须放最后
3. **PSR-4 兜底** — 新 Controller 类只需 use + 路由引用；composer.json 的 files autoload 兜底多类单文件
4. **分页解包** — 后端返回 `{code, data: {current_page, data, total}}` → 拦截器解包后前端 `d.data` + `d.total`
5. **PG check 约束** — 部署后必须手动 `DROP CONSTRAINT`，避免 mock 数据违反枚举

---

## 二、5 个功能模块的详细技术设计

### 2.1 API 真实 CRUD 替换

#### 2.1.1 当前 mock 数据清单

| Vue 文件 | mock 入口 | 期望替换为 |
|---------|----------|-----------|
| `views/sales/Leads.vue` | `handleConvert` `handleDiscard` `新建线索` | `POST /api/sales/leads` `POST /api/sales/leads/{id}/convert` `PUT /api/sales/leads/{id}/discard` |
| `views/sales/LeadsBoard.vue` | 拖拽改 stage | `PUT /api/sales/leads/{id}/stage` |
| `views/sales/Opps.vue` | `handleWin` `新建商机` | `POST /api/sales/opps/{id}/win` `POST /api/sales/opps` |
| `views/sales/OppsBoard.vue` | 拖拽 + 战败弹窗 | `PUT /api/sales/opps/{id}/stage` `PUT /api/sales/opps/{id}/lose` |
| `views/sales/Quotes.vue` | `handleNewVersion` `handleSubmit` `handleAccept` | `POST /api/sales/quotes` `PUT /api/sales/quotes/{id}/status` `POST /api/sales/quotes/{id}/items` |
| `views/sales/Referrers.vue` | 新建/编辑推荐人 | `POST /api/sales/referrers` `PUT /api/sales/referrers/{id}` |
| `views/project/Pool.vue` | `handleConvert` | `POST /api/sales/pool/{id}/convert-to-project`（已存在，需补真正实现） |

#### 2.1.2 路由注册位置

**`pc-api/routes/api.php`** 在 `Route::prefix('sales')->group(...)` 内 `follow-ups` 前插入（保持通配前置）：

```php
// 销售前链路 — 必须先注册固定路由（{lead} 通配会吞子路径）
Route::prefix('sales')->group(function () {
    // 线索
    Route::prefix('leads')->group(function () {
        Route::get('/',                       [SalesController::class, 'leadsIndex']);
        Route::get('source-options',          [SalesController::class, 'leadsSourceOptions']);
        Route::post('/',                      [SalesController::class, 'leadsStore']);       // 新
        Route::get('{lead}',                  [SalesController::class, 'leadsShow']);
        Route::put('{lead}',                  [SalesController::class, 'leadsUpdate']);      // 新
        Route::delete('{lead}',               [SalesController::class, 'leadsDestroy']);     // 新
        Route::put('{lead}/stage',            [SalesController::class, 'leadsUpdateStage']); // 新
        Route::put('{lead}/discard',          [SalesController::class, 'leadsDiscard']);     // 新
        Route::post('{lead}/convert',         [SalesController::class, 'leadsConvert']);     // 新 — 转商机
    });
    // 商机
    Route::prefix('opps')->group(function () {
        Route::get('/',                       [SalesController::class, 'oppsIndex']);
        Route::get('stage-options',           [SalesController::class, 'oppsStageOptions']);
        Route::get('funnel',                  [SalesController::class, 'oppsFunnel']);
        Route::get('lost-reasons',            [SalesController::class, 'oppsLostReasons']);
        Route::post('/',                      [SalesController::class, 'oppsStore']);        // 新
        Route::get('{opp}',                   [SalesController::class, 'oppsShow']);
        Route::put('{opp}',                   [SalesController::class, 'oppsUpdate']);       // 新
        Route::delete('{opp}',                [SalesController::class, 'oppsDestroy']);      // 新
        Route::put('{opp}/stage',             [SalesController::class, 'oppsUpdateStage']);  // 新
        Route::put('{opp}/lose',              [SalesController::class, 'oppsLose']);         // 新
        Route::post('{opp}/win',              [SalesController::class, 'oppsWin']);          // 新 — 成交（建项目池）
    });
    // 报价单
    Route::prefix('quotes')->group(function () {
        Route::get('/',                       [SalesController::class, 'quotesIndex']);
        Route::get('status-options',          [SalesController::class, 'quotesStatusOptions']);
        Route::get('{quote}',                 [SalesController::class, 'quotesShow']);
        Route::post('/',                      [SalesController::class, 'quotesStore']);      // 新
        Route::put('{quote}',                 [SalesController::class, 'quotesUpdate']);     // 新
        Route::delete('{quote}',              [SalesController::class, 'quotesDestroy']);    // 新
        Route::put('{quote}/status',          [SalesController::class, 'quotesUpdateStatus']); // 新
        Route::post('{quote}/items',          [SalesController::class, 'quotesStoreItems']);  // 新
    });
    // 推荐人
    Route::prefix('referrers')->group(function () {
        Route::get('/',                       [SalesController::class, 'referrersIndex']);
        Route::post('/',                      [SalesController::class, 'referrersStore']);   // 新
        Route::get('{referrer}',              [SalesController::class, 'referrersShow']);    // 新
        Route::put('{referrer}',              [SalesController::class, 'referrersUpdate']);  // 新
        Route::delete('{referrer}',           [SalesController::class, 'referrersDestroy']); // 新
    });
    // 项目池（已有路由保留，convert 改成真实实现）
    Route::prefix('pool')->group(function () {
        Route::get('/',                       [SalesController::class, 'poolIndex']);
        Route::get('{pool}',                  [SalesController::class, 'poolShow']);
        Route::post('{pool}/convert-to-project', [SalesController::class, 'poolConvertToProject']); // 改真实实现
    });
    // 跟进记录
    Route::prefix('follow-ups')->group(function () {
        Route::get('/',                       [SalesController::class, 'followUpsIndex']);
        Route::post('/',                      [SalesController::class, 'followUpsStore']);    // 新
        Route::get('{followUp}',              [SalesController::class, 'followUpsShow']);     // 新
        Route::put('{followUp}',              [SalesController::class, 'followUpsUpdate']);   // 新
        Route::delete('{followUp}',           [SalesController::class, 'followUpsDestroy']);  // 新
        Route::post('{followUp}/attachments', [SalesController::class, 'followUpsUploadAttachment']); // 新
        Route::delete('attachments/{att}',    [SalesController::class, 'followUpsDeleteAttachment']);  // 新
    });
});
```

**注意**：`{lead}` `{opp}` `{quote}` `{referrer}` `{pool}` `{followUp}` 等通配必须放在各自 group 最后一行（子路由先注册）；`attachments/{att}` 之前是 `{followUp}`，但 `{followUp}/attachments` 实际是子路径，会优先匹配 — 此处为绝对安全，**`attachments/{att}` 放在 group 最后**。

#### 2.1.3 兼容性：分页解包

```ts
// ✅ 正确（拦截器已解包，res = paginator）
const r: any = await get('/sales/leads', { page: 1, per_page: 20 })
const d = r?.data || r           // 兜底未解包的情况
list.value = d.data || d || []   // d.data 才是数组
total.value = d?.total ?? list.value.length
```

---

### 2.2 转化闭环（线索 → 商机 → 项目池 → 项目）

#### 2.2.1 状态机实现

**统一用 BackedEnum（`App\Enums\LeadStage` / `OppStage`） + DB 字符串字段**

| 实体 | 状态枚举 | 流转 |
|-----|---------|------|
| Lead | `new / contacting / qualified / converted / discarded` | `new → contacting → qualified → converted` （可任意丢弃） |
| Opportunity | `requirement / solution / negotiation / contracting / won / lost` | 单向流动（不可回退） |
| ProjectPool | `pending / active / archived` | `pending → active`（转施工项目）→ `archived`（终止） |
| Project | 7 阶段（合同 → 采购 → 施工 → 调试 → 验收 → 结算 → 维保） | 转施工项目时初始为 `contract` |

#### 2.2.2 数据库变更

**新增 1 张表 `referral_payouts`**（居间费结算），其余表结构已存在无需改动：

```php
// 2026_06_20_100001_create_referral_payouts_table.php
Schema::create('referral_payouts', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('referrer_id');
    $table->foreign('referrer_id')->references('id')->on('referrers')->onDelete('cascade');
    $table->unsignedBigInteger('project_id');
    $table->foreign('project_id')->references('id')->on('projects')->onDelete('cascade');
    $table->decimal('contract_amount', 12, 2);     // 触发结算时的合同金额
    $table->decimal('commission_rate', 5, 2);      // 当时推荐人的比例（快照）
    $table->decimal('commission_amount', 12, 2);   // 应结金额
    $table->string('status', 20)->default('pending'); // pending / approved / paid / cancelled
    $table->string('trigger_event', 30);            // signing / first_payment / full_payment
    $table->date('trigger_date');
    $table->unsignedBigInteger('approved_by')->nullable();
    $table->timestamp('approved_at')->nullable();
    $table->timestamp('paid_at')->nullable();
    $table->string('payment_voucher', 500)->nullable();
    $table->text('notes')->nullable();
    $table->timestamps();

    $table->index('referrer_id');
    $table->index('project_id');
    $table->index('status');
});
```

**修改 `projects` 表加 `referrer_id` 字段**（关联推荐人，用于触发居间费）：

```php
// 2026_06_20_100002_add_referrer_to_projects_table.php
Schema::table('projects', function (Blueprint $table) {
    $table->unsignedBigInteger('referrer_id')->nullable()->after('manager_id');
    $table->foreign('referrer_id')->references('id')->on('referrers')->onDelete('set null');
});
```

#### 2.2.3 事务设计

**4 段转化路径，全部用 `DB::transaction(...)` 包裹**：

| 触发 | API | 事务内容 |
|------|-----|---------|
| 线索 → 商机 | `POST /sales/leads/{id}/convert` | ① 校验 lead.status ≠ converted ② 创建 opportunities 记录（name/customer_id/lead_id 拷贝）③ 标记 lead.status = converted |
| 商机 → 项目池 | `POST /sales/opps/{id}/win` | ① 校验 opp.stage = won ② 创建 project_pool 记录（contract_amount = opp.estimated_amount）③ 更新 opp.pool_id |
| 项目池 → 项目 | `POST /sales/pool/{id}/convert-to-project` | ① 校验 pool.status = pending ② 创建 projects 记录（name/customer_id/contract_amount=pool.contract_amount/manager_id=当前用户/起始阶段=contract）③ 更新 project_pool.related_project_id + status = active ④ **若 pool.opportunity.referrer_id 存在 → 触发居间费生成（详见 2.5）** |
| 商机 → 战败 | `PUT /sales/opps/{id}/lose` | ① 校验当前 stage ≠ lost ② 记录 lost_reason ③ 不创建任何下游实体 |

#### 2.2.4 关键 API 实现（pool 转 project）

```php
// SalesController::poolConvertToProject
public function poolConvertToProject(ProjectPool $pool, Request $request): JsonResponse
{
    return DB::transaction(function () use ($pool, $request) {
        if ($pool->status !== 'pending') {
            throw new \Exception('项目池状态非 pending，不可转换');
        }
        $pool->load('opportunity');

        // 1) 创建 projects 记录
        $project = Project::create([
            'name'           => $pool->name,
            'customer_id'    => $pool->customer_id,
            'type'           => 'comprehensive',
            'stage'          => ProjectStage::Contract,  // 合同阶段
            'status'         => 'active',
            'manager_id'     => $request->user()->id,
            'contract_amount'=> $pool->contract_amount,   // 从 pool 同步
            'start_date'     => $pool->signed_at ?: today(),
            'priority'       => 'medium',
        ]);

        // 2) 更新项目池
        $pool->update([
            'related_project_id' => $project->id,
            'status'             => 'active',
        ]);

        // 3) 同步商机关联
        if ($pool->opportunity) {
            $pool->opportunity->update(['project_id' => $project->id, 'pool_id' => $pool->id]);
        }

        // 4) 触发居间费生成（详见 2.5）
        ReferralObserver::onProjectSigned($project, $pool->opportunity?->referrer_id);

        return response()->json(['code' => 0, 'data' => $project]);
    });
}
```

#### 2.2.5 触发器 vs 主动调用

| 方案 | 优劣 | 推荐 |
|-----|------|-----|
| PG 触发器 | 数据强一致，但 SQL 触发器难调试 + 跨语言堆栈难追踪 + Laravel 事件链无法触发 | ❌ 不推荐 |
| Eloquent Observer | Laravel 原生、可读性高、可链式触发其他副作用（通知/审计）| ✅ **推荐** |
| 显式 API 调用 | 简单直接，但容易漏调 | ✅ 用于「业务可观察」的关键路径（如 convert） |

**结论**：转化路径用**显式 API 调用**（业务可追踪）；**居间费结算**用 **Eloquent Observer**（项目签约/付款状态变化自动触发）。

#### 2.2.6 错误处理

```php
// 统一业务异常
try {
    return DB::transaction(...);
} catch (\Illuminate\Database\QueryException $e) {
    if ($e->getCode() === '23505') {  // PG unique violation
        return response()->json(['code' => 1, 'message' => '数据已存在'], 422);
    }
    throw $e;
} catch (\Exception $e) {
    return response()->json(['code' => 1, 'message' => $e->getMessage()], 400);
}
```

---

### 2.3 报价单完整逻辑

#### 2.3.1 数据模型（无需修改 migration）

`quotations` 表已有字段：`subtotal / discount_rate / discount_amount / tax_rate / tax_amount / total_amount` → 已满足。

**计算公式（后端权威）**：
```
subtotal          = Σ(item.quantity × item.unit_price)
discount_amount   = subtotal × (discount_rate / 100)
amount_after_disc = subtotal − discount_amount
tax_amount        = amount_after_disc × (tax_rate / 100)
total_amount      = amount_after_disc + tax_amount
```

#### 2.3.2 折扣存储策略

| 方案 | 优劣 | 推荐 |
|-----|------|-----|
| 只存 `discount_rate` | 计算灵活，但用户改 rate 时数据库需要重算 discount_amount | ✅ |
| 只存 `discount_amount` | 数据直观，但回溯困难（不知道是 5% 还是 8%）| ❌ |
| 两者都存 | **冗余但可读**，前端可直接显示两个数 | ✅ **推荐（当前 schema 已用此方案）** |

**策略**：存两者 + 提交时**后端强制重算**覆盖（防止前端篡改）：
```php
$quote->discount_amount = round($subtotal * $quote->discount_rate / 100, 2);
$quote->tax_amount      = round(($subtotal - $quote->discount_amount) * $quote->tax_rate / 100, 2);
$quote->total_amount    = $subtotal - $quote->discount_amount + $quote->tax_amount;
```

#### 2.3.3 税额策略

- `tax_rate` 默认 13%（一般纳税人）；普通纳税人 3%；免税 0%
- 报价单显示含税价；客户发票分开处理（P2 关注）
- 提交时**前端 + 后端**都计算，前端做实时预览，**后端是权威**

#### 2.3.4 产品库多选 API

**单个保存**（简单方案）：

```
GET    /api/sales/quotes/{id}/items        列出所有产品项
POST   /api/sales/quotes/{id}/items        批量添加（请求体 { items: [...] }）
PUT    /api/sales/quotes/{id}/items/{item} 修改单条
DELETE /api/sales/quotes/{id}/items/{item} 删除单条
```

**提交请求体**：
```json
{
  "items": [
    {"inventory_item_id": 1, "name": "海康摄像头", "specification": "DS-2CD2143", "unit": "台", "quantity": 10, "unit_price": 350.00, "remark": ""},
    {"inventory_item_id": 5, "name": "硬盘录像机", "specification": "DS-7816", "unit": "台", "quantity": 1, "unit_price": 2800.00, "remark": ""}
  ]
}
```

**前端批量提交流程**：
1. 弹窗中显示产品库搜索 + 多选表格
2. 选完后点击「保存」→ 调 `POST /quotes/{id}/items` 一次性提交
3. 调 `GET /quotes/{id}` 重新拉取完整报价单（带计算后的 total）

#### 2.3.5 价格计算：前端 vs 后端

| 维度 | 前端实时 | 后端权威 |
|-----|---------|---------|
| 实时性 | 用户输入即时反馈 | 必须提交后才看 |
| 可篡改性 | 易被攻击 | 安全 |
| 性能 | 客户端零延迟 | 每次提交重算 |
| 一致性 | 与后端可能不一致 | 数据库存的是真值 |

**结论**：**前端实时预览 + 后端权威重算**（双轨）。
- 前端：用户在表格里改 quantity/price/rate → 立刻显示小计/折扣/税/总额
- 提交时后端 `POST /quotes/{id}/items` → 用 `DB::transaction` 删除旧 items + 插入新 items + 重算汇总字段

#### 2.3.6 状态机

```
draft ──提交──→ submitted ──开始谈──→ negotiating
  │                │                     │
  │                │                     ├── 接受→ accepted
  │                │                     └── 拒绝→ rejected
  │                └─ 过期 ─────────────→ expired
  └── 直接废弃 → expired
```

**触发规则**：
- `draft → submitted`：`PUT /quotes/{id}/status` body: `{status: 'submitted', sent_at: now()}`
- `negotiating → accepted/rejected`：`PUT /quotes/{id}/status` body: `{status, responded_at: now()}`
- **`accepted` 触发商机 stage 推进**到 `contracting`（用 Opportunity Observer 监听）
- `expired` 定时检查：报价超过 valid_until 30 天未响应 → 标记 expired（可用 schedule 命令每日 0 点跑）

---

### 2.4 跟进记录附件上传

#### 2.4.1 存储方案对比

| 方案 | 优劣 | 推荐 |
|-----|------|-----|
| **Laravel Storage (public disk)** | 一行代码、本地文件系统、免费、足够 1-2 年使用 | ✅ **P1 阶段推荐** |
| 对象存储 (OSS / COS) | 容量无限、CDN 加速、贵、需配置 | P2 阶段（>50GB 后迁移） |
| base64 存数据库 | 数据库膨胀、查询慢 | ❌ 严禁 |

**结论**：**Storage public disk**，目录 `storage/app/public/follow-ups/{year}/{month}/{uuid}.{ext}`，外链用 `Storage::url($path)` 生成 `/storage/follow-ups/...` 软链。

#### 2.4.2 文件大小 / 类型限制

- **单文件最大 20 MB**（中等图片 + 文档足够）
- **每日上传限 50 个**（按用户）
- **支持类型**：
  - 图片：`jpg / jpeg / png / gif / webp`
  - 文档：`pdf / doc / docx / xls / xlsx / ppt / pptx / txt / md`
- **不支持**：`exe / bat / sh / html / php / js`（防 XSS/上传 Webshell）

#### 2.4.3 表设计（已有）

`sales_follow_up_attachments` 表字段：`follow_up_id / name / path / mime / size / timestamps` — 满足。

#### 2.4.4 API 设计

| 方法 | 路径 | 说明 |
|-----|------|------|
| POST | `/api/sales/follow-ups/{followUp}/attachments` | `multipart/form-data` 上传单个文件，**单请求**（避免多文件上传一致性问题） |
| GET | `/api/sales/follow-ups/attachments/{id}/download` | 鉴权后返回文件流（带 `Content-Disposition: attachment`） |
| DELETE | `/api/sales/follow-ups/attachments/{id}` | 删除（同时删磁盘文件 + DB 记录） |

#### 2.4.5 安全校验

```php
$request->validate([
    'file' => 'required|file|max:20480|mimes:jpg,jpeg,png,gif,webp,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,md',
]);
$file = $request->file('file');

// 二次校验：MIME 真实类型 vs 扩展名
$realMime = $file->getMimeType();    // finfo 读取文件头
$ext      = strtolower($file->getClientOriginalExtension());
$allowed  = ['image/jpeg','image/png','image/gif','image/webp','application/pdf',
             'application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             'application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
if (!in_array($realMime, $allowed, true)) {
    throw ValidationException::withMessages(['file' => '文件类型不被允许']);
}

$path = $file->storeAs(
    'follow-ups/' . date('Y/m'),
    Str::uuid() . '.' . $ext,
    'public'
);

$attachment = SalesFollowUpAttachment::create([
    'follow_up_id' => $followUp->id,
    'name'         => $file->getClientOriginalName(),
    'path'         => $path,
    'mime'         => $realMime,
    'size'         => $file->getSize(),
]);
```

#### 2.4.6 前端上传组件

```vue
<el-upload :http-request="customUpload" :show-file-list="false" :before-upload="validateFile">
  <el-button :icon="Upload">上传附件</el-button>
</el-upload>
```

```ts
const customUpload = async (options: any) => {
  const fd = new FormData()
  fd.append('file', options.file)
  const r = await upload(`/sales/follow-ups/${followUpId}/attachments`, fd)
  // upload 是项目封装的 axios (Content-Type: multipart/form-data 自动)
  if (r.code === 0) {
    ElMessage.success('上传成功')
    attachments.value.push(r.data)
  }
}
```

---

### 2.5 推荐人居间费自动结算

#### 2.5.1 结算模型

| 触发时机 | trigger_event | 触发条件 |
|---------|--------------|---------|
| 项目签约（首笔合同款已收）| `signing` | projects.contract_amount > 0 AND 首次有 PaymentReceived 记录 |
| 全款回款完成 | `full_payment` | 累计已收 ≥ contract_amount |
| 手动调整（异常兜底）| `manual` | 财务/管理员手动触发 |

**计算公式**：
```
commission_amount = contract_amount × (commission_rate / 100)
```
- `commission_rate` 取 `referrers.commission_rate` **快照**（结算时复制到 `referral_payouts.commission_rate`）
- 避免后续改 commission_rate 影响历史结算

#### 2.5.2 数据库设计

见 2.2.2 节（`referral_payouts` 新表）。

#### 2.5.3 事务设计

`ReferralObserver` 监听 `Project` 模型：

```php
// app/Observers/ReferralObserver.php
class ReferralObserver
{
    public static function onProjectSigned(Project $project, ?int $referrerId = null): void
    {
        if (!$referrerId) {
            $referrerId = DB::table('opportunities')
                ->where('id', $project->opportunity_id ?? 0)
                ->value('referrer_id') ?? $project->referrer_id;
        }
        if (!$referrerId) return;

        $referrer = Referrer::find($referrerId);
        if (!$referrer) return;

        // 幂等：同一 trigger_event 不重复生成
        $exists = ReferralPayout::where('project_id', $project->id)
            ->where('trigger_event', 'signing')
            ->exists();
        if ($exists) return;

        DB::transaction(function () use ($project, $referrer) {
            ReferralPayout::create([
                'referrer_id'        => $referrer->id,
                'project_id'         => $project->id,
                'contract_amount'    => $project->contract_amount,
                'commission_rate'    => $referrer->commission_rate,    // 快照
                'commission_amount'  => round($project->contract_amount * $referrer->commission_rate / 100, 2),
                'status'             => 'pending',
                'trigger_event'      => 'signing',
                'trigger_date'       => today(),
            ]);
            $referrer->increment('total_commission', round($project->contract_amount * $referrer->commission_rate / 100, 2));
        });
    }
}
```

**在 AppServiceProvider 注册**：
```php
Project::observe(\App\Observers\ProjectObserver::class);
```

#### 2.5.4 Observer vs 显式 API

| 方案 | 优劣 | 推荐 |
|-----|------|-----|
| **Eloquent Observer** | 任何创建/更新项目的地方都自动触发 + 幂等保护 + 集中逻辑 | ✅ **推荐（自动）** |
| 显式 API 触发 | 简单但容易漏调（如批量导入项目历史数据时）| ❌ 漏调风险高 |

**结论**：**主用 Observer 自动触发**（项目签约时），**保留一个手动 API**（`POST /api/sales/referral-payouts`）给财务异常调整。

#### 2.5.5 手动调整 API

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/sales/referral-payouts` | 列出所有结算单（按 referrer_id / project_id / status 过滤） |
| POST | `/api/sales/referral-payouts` | 手动新增（trigger_event = manual） |
| PUT | `/api/sales/referral-payouts/{id}/approve` | 状态 pending → approved |
| PUT | `/api/sales/referral-payouts/{id}/pay` | 状态 approved → paid（记录 paid_at + 上传付款凭证 URL） |
| DELETE | `/api/sales/referral-payouts/{id}` | 取消（仅 pending 状态可删） |

---

## 三、关键技术决策（重点）

| 决策 | 推荐 | 备选 | 理由 |
|-----|------|------|------|
| **文件存储** | Storage public disk | 对象存储 (OSS) | 1-2 年内 < 50GB 没必要 OSS；零依赖、零成本、零配置；后期可平滑迁移 |
| **转化闭环触发** | 显式 API 调用 | Eloquent Observer | 转化是「业务可观察」的关键路径，要可追踪、可回滚；Observer 难调试 |
| **价格计算** | 前端实时 + 后端权威 | 全部前端 | 前端体验好 + 后端安全；后端覆盖防篡改 |
| **居间费触发** | Eloquent Observer | 显式 API | 任何地方创建项目都要结算；Observer 集中 + 幂等 |
| **跨表事务** | DB::transaction | Saga / 分布式事务 | 单库单服务够用；事务是 Laravel 标准做法；出错自动回滚 |
| **折扣字段** | rate + amount 都存 | 只存一个 | 显示直观 + 数据库可读；提交时后端重算保证一致 |
| **附件大小** | 20MB | 50MB / 100MB | 平衡常见文档 + 性能；100MB 拉上传慢、占用多 |
| **附件单/多文件** | 单次单文件 | 多文件并行 | 失败时部分成功的清理麻烦；多文件用多次请求简单 |
| **路由分组** | prefix + 子 group | 平面路由 | 保持现有风格；按子资源嵌套清晰 |
| **引用类自动加载** | composer.json files | 单文件每类 | 现有项目用 `ProjectModels.php` 多类单文件，5 个 Model 文件装 80+ 类；保持风格 |

---

## 四、API 清单（新增/修改）

| 模块 | 方法 | 路径 | 说明 | Controller@方法 | 路由位置 |
|------|------|------|------|------------------|----------|
| 线索 | GET | `/api/sales/leads` | 列表（已存在）| `SalesController::leadsIndex` | sales/leads/1 |
| 线索 | POST | `/api/sales/leads` | 新建 | `leadsStore` | sales/leads/2 |
| 线索 | GET | `/api/sales/leads/{lead}` | 详情（已存在）| `leadsShow` | sales/leads/3 |
| 线索 | PUT | `/api/sales/leads/{lead}` | 更新 | `leadsUpdate` | sales/leads/4 |
| 线索 | DELETE | `/api/sales/leads/{lead}` | 删除 | `leadsDestroy` | sales/leads/5 |
| 线索 | PUT | `/api/sales/leads/{lead}/stage` | 改 stage | `leadsUpdateStage` | sales/leads/6 |
| 线索 | PUT | `/api/sales/leads/{lead}/discard` | 丢弃 | `leadsDiscard` | sales/leads/7 |
| 线索 | POST | `/api/sales/leads/{lead}/convert` | 转商机 | `leadsConvert` | sales/leads/8 |
| 商机 | POST | `/api/sales/opps` | 新建 | `oppsStore` | sales/opps/2 |
| 商机 | PUT | `/api/sales/opps/{opp}` | 更新 | `oppsUpdate` | sales/opps/4 |
| 商机 | DELETE | `/api/sales/opps/{opp}` | 删除 | `oppsDestroy` | sales/opps/5 |
| 商机 | PUT | `/api/sales/opps/{opp}/stage` | 改 stage | `oppsUpdateStage` | sales/opps/6 |
| 商机 | PUT | `/api/sales/opps/{opp}/lose` | 标记战败 | `oppsLose` | sales/opps/7 |
| 商机 | POST | `/api/sales/opps/{opp}/win` | 成交（建项目池）| `oppsWin` | sales/opps/8 |
| 报价 | POST | `/api/sales/quotes` | 新建报价单 | `quotesStore` | sales/quotes/2 |
| 报价 | PUT | `/api/sales/quotes/{quote}` | 更新 | `quotesUpdate` | sales/quotes/4 |
| 报价 | DELETE | `/api/sales/quotes/{quote}` | 删除 | `quotesDestroy` | sales/quotes/5 |
| 报价 | PUT | `/api/sales/quotes/{quote}/status` | 改状态 | `quotesUpdateStatus` | sales/quotes/6 |
| 报价 | POST | `/api/sales/quotes/{quote}/items` | 批量保存产品 | `quotesStoreItems` | sales/quotes/7 |
| 推荐人 | POST | `/api/sales/referrers` | 新建 | `referrersStore` | sales/referrers/2 |
| 推荐人 | GET | `/api/sales/referrers/{referrer}` | 详情 | `referrersShow` | sales/referrers/3 |
| 推荐人 | PUT | `/api/sales/referrers/{referrer}` | 更新 | `referrersUpdate` | sales/referrers/4 |
| 推荐人 | DELETE | `/api/sales/referrers/{referrer}` | 删除 | `referrersDestroy` | sales/referrers/5 |
| 项目池 | POST | `/api/sales/pool/{pool}/convert-to-project` | 转施工项目（真实实现）| `poolConvertToProject` | sales/pool/2 |
| 跟进 | POST | `/api/sales/follow-ups` | 新建 | `followUpsStore` | sales/follow-ups/2 |
| 跟进 | GET | `/api/sales/follow-ups/{followUp}` | 详情 | `followUpsShow` | sales/follow-ups/3 |
| 跟进 | PUT | `/api/sales/follow-ups/{followUp}` | 更新 | `followUpsUpdate` | sales/follow-ups/4 |
| 跟进 | DELETE | `/api/sales/follow-ups/{followUp}` | 删除 | `followUpsDestroy` | sales/follow-ups/5 |
| 跟进 | POST | `/api/sales/follow-ups/{followUp}/attachments` | 上传附件 | `followUpsUploadAttachment` | sales/follow-ups/6 |
| 跟进 | GET | `/api/sales/follow-ups/attachments/{att}/download` | 下载 | `followUpsDownloadAttachment` | sales/follow-ups/7 |
| 跟进 | DELETE | `/api/sales/follow-ups/attachments/{att}` | 删除附件 | `followUpsDeleteAttachment` | sales/follow-ups/8 |
| 居间费 | GET | `/api/sales/referral-payouts` | 列表 | `referralPayoutsIndex` | sales/referral-payouts/1 |
| 居间费 | POST | `/api/sales/referral-payouts` | 手动新增 | `referralPayoutsStore` | sales/referral-payouts/2 |
| 居间费 | PUT | `/api/sales/referral-payouts/{payout}/approve` | 审批 | `referralPayoutsApprove` | sales/referral-payouts/3 |
| 居间费 | PUT | `/api/sales/referral-payouts/{payout}/pay` | 标记已付 | `referralPayoutsPay` | sales/referral-payouts/4 |
| 居间费 | DELETE | `/api/sales/referral-payouts/{payout}` | 取消 | `referralPayoutsDestroy` | sales/referral-payouts/5 |

**总新增/修改 API：36 个**（其中 1 个修改实现，35 个全新）

---

## 五、数据库变更清单

| Migration 名 | 操作 | 表名 | 关键字段 |
|-------------|------|------|----------|
| `2026_06_20_100001_create_referral_payouts_table.php` | CREATE | referral_payouts | referrer_id, project_id, contract_amount, commission_rate, commission_amount, status, trigger_event |
| `2026_06_20_100002_add_referrer_to_projects_table.php` | ALTER | projects | + referrer_id (FK → referrers) |

**2 个 migration 全部需要 PG 手动 GRANT**（见 部署 章节）：
```sql
GRANT ALL PRIVILEGES ON TABLE referral_payouts TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE referral_payouts_id_seq TO oa_user;
```

**注意**：`quotations` / `quotation_items` / `sales_follow_up_attachments` 字段已完整，**不再加字段**。

---

## 六、前端组件/页面变更

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `views/sales/Leads.vue` | 修改 | 把 `handleConvert` `handleDiscard` `新建` 换成真实 API 调用 + 加 el-dialog 表单 |
| `views/sales/LeadsBoard.vue` | 修改 | 拖拽后调 `PUT /leads/{id}/stage` |
| `views/sales/Opps.vue` | 修改 | `handleWin` → `POST /opps/{id}/win` + 加新建商机弹窗 |
| `views/sales/OppsBoard.vue` | 修改 | 拖拽 → `PUT /opps/{id}/stage`；战败 → 弹窗选 reason + `PUT /opps/{id}/lose` |
| `views/sales/Quotes.vue` | 修改 | `新建版本` `提交审批` `客户接受` 全部换真实 API；加 el-table 行内编辑（产品/数量/单价） + 实时计算小计/折扣/税/总额 |
| `views/sales/Referrers.vue` | 修改 | 加 CRUD 弹窗（CRUD 表格 + 表单） |
| `views/project/Pool.vue` | 修改 | `handleConvert` → 调真实 API，跳转到项目详情页 |
| **新增** `views/sales/FollowUpDialog.vue` | 新增 | 跟进记录弹窗组件（el-form + 跟进方式/内容/结果/下一步/附件上传） |
| **新增** `views/sales/ProductPickerDialog.vue` | 新增 | 产品库多选弹窗（按分类树筛选 + 搜索 + 多选表格） |
| **新增** `views/sales/ReferralPayouts.vue` | 新增 | 居间费结算单列表页（按状态过滤 + 审批/支付按钮） |
| `api/modules.ts` | 修改 | 加 `sales` 模块导出（CRUD 函数） |
| `router/index.ts` | 修改 | 加 `/sales/referral-payouts` 路由；`/sales/opps/:id/quote` 已存在 |

---

## 七、部署注意事项

### 7.1 部署到 172 的具体命令

```bash
# 1) 本地后端打包
cd pc-api
# 文件已 git tracked，直接 rsync 到 172

# 2) 上传（ubuntu 凭据走 paramiko）
python .workbuddy/deploy_to_172.py

# 3) 服务器端跑 migration
ssh ubuntu@172.20.0.139
cd /var/www/oa-api
sudo -u www-data php artisan migrate
# 若报「class 重复」先 composer dump-autoload

# 4) 手动 GRANT（PG 新表）
sudo -u postgres psql security_oa <<EOF
GRANT ALL PRIVILEGES ON TABLE referral_payouts TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE referral_payouts_id_seq TO oa_user;
EOF

# 5) 重启 PHP-FPM（opcache 必须 restart）
sudo systemctl restart php8.3-fpm

# 6) 前端打包 + 同步
cd pc-web
npm run build
python .workbuddy/sync_web_172.py

# 7) 验证
curl -X POST http://172.20.0.139:3001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
```

### 7.2 路由顺序陷阱（再次提醒）

**`/api/sales/leads/{lead}/convert` 必须在 `Route::get('{lead}')` 之前注册**。具体见 2.1.2 节路由代码 — 子路径路由全部先注册，通配放最后。

**`/api/sales/pool/{pool}/convert-to-project` 必须在 `Route::get('{pool}')` 之后**？**不**！`{pool}/convert-to-project` 是子路径，会优先匹配。所以顺序应是：
```
Route::get('{pool}', ...)           // 先注册通配
Route::post('{pool}/convert-to-project', ...)  // 子路径在通配后也 OK
```
但为安全起见，**子路径路由优先注册**：
```
Route::post('{pool}/convert-to-project', ...)
Route::get('{pool}', ...)
```

### 7.3 Composer 依赖

**本 P1 无新增 Composer 包**。所有用到功能（Laravel Storage / Eloquent / Sanctum）已存在。

**潜在需要**（视开发情况）：
- `intervention/image` — 图片压缩（**P2 再考虑**，P1 直接存原图）
- `maatwebsite/excel` — Excel 导入/导出（**P2**，P1 用 CSV）

### 7.4 测试数据补充

`BusinessLogicTestDataSeeder.php` 需追加：
```php
// 3 个 lead
Lead::factory()->count(3)->create();
// 2 个 opp
Opportunity::factory()->count(2)->create();
// 5 个 quotation（1 个 opp 多版本）
Quotation::factory()->count(5)->has(QuotationItem::factory()->count(8), 'items')->create();
// 3 个 sales_follow_up
SalesFollowUp::factory()->count(3)->create();
// 2 个 referrer
Referrer::factory()->count(2)->create();
```

---

## 八、风险与依赖

### 8.1 技术风险

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|-----|
| 路由顺序错误导致 404 | 中 | 阻断全模块 | 部署后 `php artisan route:list` 逐一核对 |
| 转化闭环事务回滚不彻底 | 低 | 数据脏 | `DB::transaction` + 测试覆盖 4 条转化路径 |
| 附件上传 OSS 切换时迁移 | 低 | 需手动迁移 | Storage 封装统一接口 `Storage::disk('xxx')->url()` |
| ProjectObserver 误触发 | 中 | 居间费重复生成 | **幂等保护**：`where project_id + trigger_event` 查重 |
| 商机 stage 流转规则被绕过 | 中 | 数据不一致 | 后端 `oppsUpdateStage` 内强校验合法目标值 |
| 前端编辑报价单时计算与服务端不一致 | 低 | 体验差 | 提交后端覆盖前端 → 前端重拉显示 |

### 8.2 第三方依赖

- 无新增 Composer 包
- 无外部 API 调用
- 无新前端 npm 包（Element Plus 已有 Upload/Dialog/Form）

### 8.3 现有模块影响范围

| 模块 | 影响 |
|------|------|
| `ProjectController` | 增加 `createFromPool` 调用（不修改现有方法）|
| `Project` Model | 加 `referrer_id` 字段（fillable + cast）|
| `Opportunity` Model | 加 `opportunity_id` 反查（不需要新字段，pool_id 已有）|
| `wipeData` 清理函数 | 加 `referral_payouts` 到 tables 数组（避免重置失败）|
| `Project` 创建业务 | 任何创建项目的地方都会触发 Observer → 测试需关注 |
| 销售前链路 7 个 Vue 页面 | 全部去掉 mock 提示文案 + 接真实 API |

---

## 九、迭代计划建议

**总周期：5 个迭代 × 3-5 天 = 15-25 天（约 3-4 周）**

| 迭代 | 内容 | 工期 | 交付物 |
|------|------|------|--------|
| **迭代 1** | 1) API 真实 CRUD（线索/商机基础 CRUD）| 3-4 天 | 后端 16 端点 + 前端 Leads/Opps 列表/看板接 API |
| **迭代 2** | 2) 转化闭环（线索→商机→项目池→项目 4 段）| 4-5 天 | 4 个转化 API + DB 事务 + 前端按钮 + Pool 转项目 |
| **迭代 3** | 3) 报价单完整逻辑 + 4) 跟进记录附件上传 | 5 天 | 报价 CRUD + 折扣/税额重算 + 产品库多选 + 附件上传/下载/删除 |
| **迭代 4** | 5) 推荐人居间费自动结算 | 3-4 天 | referral_payouts 表 + Observer + 结算单列表/审批/支付页 |
| **迭代 5** | 全模块联调 + E2E 测试 + 172 部署 | 3-4 天 | puppeteer 跑通 5 模块主流程 + 验证部署 |

**关键依赖**：
- 迭代 1 是基础，必须先完成
- 迭代 2 依赖迭代 1（lead.status=converted 后才能转商机）
- 迭代 3 与迭代 4 可并行（无共享代码）
- 迭代 5 收尾

---

## 十、附录

### 10.1 关键代码示例

#### 10.1.1 转化事务

```php
use Illuminate\Support\Facades\DB;

public function oppsWin(Opportunity $opp, Request $request): JsonResponse
{
    return DB::transaction(function () use ($opp, $request) {
        if ($opp->stage === 'won' || $opp->stage === 'lost') {
            throw new \Exception('商机已终结，不可重复操作');
        }
        $pool = ProjectPool::create([
            'pool_no'         => 'POOL-' . date('Ymd') . '-' . str_pad(ProjectPool::whereDate('created_at', today())->count() + 1, 3, '0', STR_PAD_LEFT),
            'opportunity_id'  => $opp->id,
            'name'            => $opp->name,
            'customer_id'     => $opp->customer_id,
            'contract_amount' => $opp->estimated_amount,
            'signed_at'       => today(),
            'status'          => 'pending',
        ]);
        $opp->update(['stage' => 'won', 'pool_id' => $pool->id, 'probability' => 100]);
        return response()->json(['code' => 0, 'data' => $pool]);
    });
}
```

#### 10.1.2 Observer 自动结算

```php
namespace App\Observers;

use App\Models\Project;
use App\Models\ReferralPayout;
use App\Models\Referrer;
use Illuminate\Support\Facades\DB;

class ProjectObserver
{
    public function created(Project $project): void
    {
        // 触发居间费（自动）
        \App\Services\ReferralService::generateSigningPayout($project);
    }

    public function updated(Project $project): void
    {
        // 若 contract_amount 变化（合同修改），重新计算
        if ($project->wasChanged('contract_amount') && $project->getOriginal('contract_amount') > 0) {
            // 取消原 pending 结算单 + 重新生成
            DB::transaction(function () use ($project) {
                ReferralPayout::where('project_id', $project->id)
                    ->where('status', 'pending')
                    ->update(['status' => 'cancelled']);
                \App\Services\ReferralService::generateSigningPayout($project);
            });
        }
    }
}
```

**注册**（`app/Providers/AppServiceProvider.php`）：
```php
public function boot(): void
{
    \App\Models\Project::observe(\App\Observers\ProjectObserver::class);
}
```

#### 10.1.3 文件上传（Storage public disk）

```php
public function followUpsUploadAttachment(SalesFollowUp $followUp, Request $request): JsonResponse
{
    $request->validate([
        'file' => 'required|file|max:20480',  // 20MB
    ]);
    $file = $request->file('file');
    $ext  = strtolower($file->getClientOriginalExtension());
    $allowed = ['jpg','jpeg','png','gif','webp','pdf','doc','docx','xls','xlsx','ppt','pptx','txt','md'];
    if (!in_array($ext, $allowed, true)) {
        throw \Illuminate\Validation\ValidationException::withMessages(['file' => '文件类型不允许']);
    }
    $path = $file->storeAs('follow-ups/' . date('Y/m'), \Illuminate\Support\Str::uuid() . '.' . $ext, 'public');
    $att = SalesFollowUpAttachment::create([
        'follow_up_id' => $followUp->id,
        'name'         => $file->getClientOriginalName(),
        'path'         => $path,
        'mime'         => $file->getMimeType(),
        'size'         => $file->getSize(),
    ]);
    return response()->json(['code' => 0, 'data' => $att]);
}
```

### 10.2 错误码定义

| 业务错误 | HTTP | message |
|---------|------|---------|
| 转化前置条件不满足（如 lead 已是 converted）| 422 | 「线索已转商机」 |
| 战败必填原因缺失 | 422 | 「请选择战败原因」 |
| 报价单产品数量为 0 | 422 | 「请至少添加 1 个产品项」 |
| 折扣率非法（<0 或 >100）| 422 | 「折扣率必须在 0-100 之间」 |
| 附件超 20MB | 422 | 「单文件最大 20MB」 |
| 附件类型不允许 | 422 | 「文件类型 {ext} 不支持」 |
| 推荐人已被关联项目 | 422 | 「该推荐人已关联项目，不可删除」 |
| 转化失败（事务回滚）| 500 | 「系统繁忙，请重试」 + Laravel 异常 ID |

### 10.3 API 限流策略（建议）

| 端点 | 限制 | 理由 |
|------|------|------|
| `POST /auth/login` | 5 次/分钟/IP | 防爆破（**已有 Sanctum throttle**）|
| `POST /follow-ups/{id}/attachments` | 50 次/天/用户 | 防止恶意刷附件 |
| `POST /sales/opps/{id}/win` 等转化类 | 10 次/分钟/用户 | 防误操作 |
| `GET /sales/*` 列表类 | 60 次/分钟/用户 | 防止前端死循环 |

**实现方式**：Laravel `throttle:60,1` 中间件 + 自定义 RateLimiter。

### 10.4 PostgreSQL 部署必跑 SQL（新增表后）

```sql
-- referral_payouts 表 GRANT
GRANT ALL PRIVILEGES ON TABLE referral_payouts TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE referral_payouts_id_seq TO oa_user;
-- projects 新字段 referrer_id 的约束已由 migration 自带 FK
```

### 10.5 兼容性 checklist

- [x] 单文件多类 — 销售 8 个 Model 全部进 `ProjectModels.php`（已有 240 行，+80 行 ≈ 320 行）
- [x] 路由顺序 — 所有通配在 group 末尾
- [x] PG 表名自动复数化 — 所有新 Model 显式 `protected $table = '...'`（已确认 sales_follow_ups / sales_follow_up_attachments / project_pool / referral_payouts 显式声明）
- [x] 前端分页解包 — `d.data || d` + `d?.total ?? list.length`
- [x] Sanctum 中间件 — 所有路由包在 `auth:sanctum` group 内
- [x] PG 22P02 兜底 — `bootstrap/app.php` 已有
- [x] Composer — 无新增依赖
- [x] 172 部署 — 走 `deploy_to_172.py` 自动 + 手动 GRANT
