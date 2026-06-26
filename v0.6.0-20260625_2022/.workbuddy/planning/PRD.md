# v0.3.9 销售前链路 P1 业务逻辑 PRD

> 文档版本：v1.0
> 编写日期：2026-06-19
> 适用范围：安防运维OA系统 v0.3.9 销售前链路 P1
> 上游依赖：v0.3.9 P0 界面（已完成）
> 下游读者：后端开发、前端开发、测试、运维

---

## 一、背景与目标

### 1.1 现状（P0 已完成）
v0.3.9 P0 已交付**只读型界面**，11 个 API 全部为 GET，**没有 POST/PUT/DELETE**。
- **7 个 Vue 页面**：线索池 / 线索看板 / 商机池 / 商机看板 / 报价单 / 推荐人 / 项目池
- **5 张新表**：leads / opportunities / quotations + quotation_items / referrers / project_pool / sales_follow_ups + sales_follow_up_attachments
- **11 个 GET 接口**：线索列表+详情+来源、商机列表+详情+阶段+漏斗+战败原因、报价单列表+详情+状态、推荐人、项目池+详情、跟进记录

**核心问题**（P0 留的"占位"）：
- 所有「新建/编辑/删除/转商机/转项目池/拖拽改阶段/报价新建版本/客户接受/上传附件」按钮**全部是 ElMessage.success("...P1 实现")**假成功提示
- 后端 SalesController 顶部注释直接写明：「**界面优先，所有方法只返回数据，转化闭环逻辑 P1 再做**」

### 1.2 目标（P1 要达成）
1. **API 真实 CRUD**：所有 P0 占位按钮接通真实后端，落库生效
2. **转化闭环**：线索→商机→项目池→施工项目，全链路状态机 + 自动数据同步
3. **报价单业务化**：支持产品库多选、折扣 / 税额自动计算、状态流转
4. **跟进记录附件**：上传 / 列表 / 下载 / 删除，存网盘
5. **推荐人居间费**：项目签约 / 回款触发自动结算，生成结算记录

### 1.3 业务价值
- 销售从「线索录入」到「项目签约」全流程在系统内闭环
- 报价单数学化：折扣 / 税额自动算，零手工
- 居间费自动结算，财务不用再 Excel 拉
- 跟进附件留存，知识资产不丢

---

## 二、范围与非范围

### 2.1 P1 包含（IN SCOPE）

| # | 功能 | 范围 |
|---|---|---|
| 4.1 | API 真实 CRUD | leads / opps / quotations / quotation_items / referrers / project_pool / sales_follow_ups 全部 POST/PUT/DELETE + 上传接口 |
| 4.2 | 转化闭环 | 状态机定义 + 4 个触发动作：转商机 / 战败 / 商机成交 / 项目池转施工项目 |
| 4.3 | 报价单 | 多版本 + 产品库多选对话框 + 折扣 / 税额计算 + 状态机 |
| 4.4 | 跟进附件 | 单文件 / 多文件上传 + 列表 + 下载 + 删除 + 容量限制 |
| 4.5 | 居间费自动结算 | 计算公式 + 触发条件 + 结算记录表 |

### 2.2 P1 不包含（OUT OF SCOPE）

- 微信小程序 / APP / Electron 端同步（P2）
- 报价单 PDF 导出（暂时只前端 window.print 即可）
- 多币种（只支持人民币）
- 复杂审批流（报价单提交后直接进入"已提交"状态，审批流对接统一审批中心 v0.4 再说）
- 商机自动分配规则（手动选 sales / presale）
- 线索公海机制（线索目前都归属 owner_id，不做公海）
- AI 智能跟进建议（P2+）

---

## 三、用户角色与场景

### 3.1 角色矩阵

| 角色 | 可操作 |
|---|---|
| **销售员** | 录入线索 / 转商机 / 上传跟进附件 / 录入报价 / 查看本人商机 / 看本部门漏斗 |
| **售前工程师** | 配合商机做方案 / 在商机详情被指定为 presale / 协助做报价 |
| **销售经理** | 上述所有 + 战败审核 / 商机强制改阶段 / 调整线索 owner / 看部门全量漏斗 |
| **项目经理** | 项目池列表可看 / 接收「转为施工项目」并分配 / 创建施工档案 |
| **财务** | 居间费结算记录只读 + 审核 / 标记「已发放」 |
| **管理员** | 推荐人 / 客户 / 产品库配置 + 所有数据读写 |

### 3.2 关键用户故事

**故事 1：销售员老张**
老张收到客户「XX 银行」咨询，通过电话陌拜录入线索（评级 B，状态：新线索）。2 周后客户确认有需求，他点「转商机」按钮 → 系统自动建商机（默认 stage=需求确认，probability=20%，销售=老张）→ 线索状态变「已转商机」。老张填写商机名称 / 预计金额 / 预计签约日，指定售前小李。

**故事 2：老张做报价**
老张进入商机详情 → 点「报价」→ 选产品库「海康 4K 摄像头 × 10」「线材 × 5」→ 系统自动加单价 / 小计 → 老张输折扣率 8% / 选税率 13% → 系统算：subtotal ¥35000 - discount ¥2800 + tax ¥4186 = 含税总价 ¥36386 → 保存为 V1 草稿。客户压价到 9 折，老张点「新建版本 V2」→ 系统自动复制 V1 + 应用新折扣 → 老张点「提交审批」→ 状态变「已提交」→ 客户回 OK → 老张点「客户接受」→ 状态变「客户接受」+ 商机 stage 自动推到「合同拟定」。

**故事 3：商机成交**
客户签合同，老张点「成交」→ 弹出 dialog 要求填「合同金额」「签约日期」→ 提交后：
- 商机 stage → won
- 自动在 project_pool 建一条（status=pending）
- projects.contract_amount ← opp.estimated_amount
- 若商机有 referrer_id，自动在 referral_settlements 建一条「待结算」

**故事 4：项目经理转施工**
项目经理看到项目池有条「XX 银行监控项目 pending」→ 点「转为施工项目」→ 弹 dialog 选工期 / 团队 / 预算 → 提交：
- project_pool.status → active
- related_project_id ← 新建 projects.id
- projects 立刻进入 7 阶段流程的「合同阶段」

**故事 5：居间费发放**
财务看到「待结算」结算记录 × 1（金额 ¥3,000，关联推荐人老陈）→ 核对无误 → 标记「已发放」+ 填「发放日期」+ 上传银行回单附件 → referrer.total_commission += 3000。

---

## 四、5 个功能模块的详细需求

### 4.1 API 真实 CRUD

#### 现状：所有 7 个 v0.3.9 页面 mock 位置

| 页面 | 文件 | mock 按钮 / 行为 | 后端现状 |
|---|---|---|---|
| Leads.vue | `pc-web/src/views/sales/Leads.vue` | 「新建线索」无 dialog、「转商机」「丢弃」`ElMessage.success('...P1 实现')` | 缺 POST/PUT/DELETE |
| LeadsBoard.vue | `pc-web/src/views/sales/LeadsBoard.vue` | onDrop 只改本地 `lead.status` 不持久化 | 缺 PATCH 改状态 |
| Opps.vue | `pc-web/src/views/sales/Opps.vue` | 「新建商机」无 dialog、「成交」假成功 | 缺 POST/PUT |
| OppsBoard.vue | `pc-web/src/views/sales/OppsBoard.vue` | onDrop 只改本地 `opp.stage` | 缺 PATCH 改 stage |
| Quotes.vue | `pc-web/src/views/sales/Quotes.vue` | 「新建版本」「提交审批」「客户接受」假成功 + 没有任何产品库 dialog | 缺 POST/PUT + items 增删 + 状态机 |
| Referrers.vue | `pc-web/src/views/sales/Referrers.vue` | 「新增 / 编辑 / 删除 / 查看」全部假成功 | 缺 POST/PUT/DELETE |
| Pool.vue | `pc-web/src/views/project/Pool.vue` | 「转为施工项目」假成功 | 缺 POST + 转施工项目端点 |

#### 目标

**总目标：所有 7 个页面 P0 占位按钮接通真实后端，落库生效，刷新后状态保持。**

#### 后端需补的 API（详细列表）

**线索 5 个**：
```
POST   /api/sales/leads                  新建线索
PUT    /api/sales/leads/{lead}           编辑线索
DELETE /api/sales/leads/{lead}           删除（仅 status=new/discarded）
PATCH  /api/sales/leads/{lead}/status    看板拖拽改 status
POST   /api/sales/leads/{lead}/convert-to-opp  转商机（返回新商机）
```

**商机 5 个**：
```
POST   /api/sales/opps                    新建商机
PUT    /api/sales/opps/{opp}              编辑商机
DELETE /api/sales/opps/{opp}              删除（仅 stage=requirement/lost）
PATCH  /api/sales/opps/{opp}/stage        看板拖拽改 stage（合法性校验见 4.2）
POST   /api/sales/opps/{opp}/mark-won     成交（弹 dialog 合同金额/签约日）
POST   /api/sales/opps/{opp}/mark-lost    战败（带战败原因）
```

**报价单 7 个**：
```
POST   /api/sales/quotes                       新建报价单（V1 草稿）
PUT    /api/sales/quotes/{quote}               编辑报价单基础信息
DELETE /api/sales/quotes/{quote}               删除（仅 draft）
POST   /api/sales/quotes/{quote}/items         批量保存产品清单
PUT    /api/sales/quotes/{quote}/status         状态流转（草稿→已提交→谈判中→接受/拒绝/过期）
POST   /api/sales/quotes/{quote}/new-version   复制当前版本为新版本号（+1）
```

**产品库（复用 inventory）**：
```
GET /api/inventory  → 报价单「从产品库选择」对话框用
   query: ?keyword=...&category_id=...&in_stock=1&per_page=20
   响应字段：id / name / specification / unit / unit_price / stock_qty
```

**推荐人 3 个**：
```
POST   /api/sales/referrers
PUT    /api/sales/referrers/{referrer}
DELETE /api/sales/referrers/{referrer}
```

**项目池 2 个**：
```
POST   /api/sales/pool/{pool}/convert-to-project   转施工项目（弹 dialog 选工期/团队/预算）
PUT    /api/sales/pool/{pool}                       编辑项目池信息
```

**跟进记录 3 个**：
```
POST   /api/sales/follow-ups                新建跟进
PUT    /api/sales/follow-ups/{followUp}     编辑
DELETE /api/sales/follow-ups/{followUp}     删除
POST   /api/sales/follow-ups/{followUp}/attachments  上传附件（multipart）
DELETE /api/sales/follow-ups/attachments/{att}        删除附件
GET    /api/sales/follow-ups/attachments/{att}/download   下载附件（stream）
```

**共 30 个新接口**（不算 GET / 不算产品库 GET）

#### 通用请求 / 响应规范

**请求**：JSON body / multipart，CSRF 由 Sanctum 自动处理
**响应成功**：`{code:0, data:{...}}`  列表分页：`{code:0, data:{current_page,data:[...],total,per_page,last_page}}`
**响应失败**：`{code:1, message:"错误信息"}` HTTP 4xx/5xx

#### 通用错误码（与现有项目对齐）

| 状态码 | 场景 |
|---|---|
| 400 | 参数校验失败（返回首个错误信息） |
| 401 | 未登录 / token 过期 |
| 403 | 无权限（如销售员删别人的线索） |
| 404 | 资源不存在 |
| 409 | 状态机非法（如「已转商机」线索不能再转） |
| 422 | 业务规则违反（如「已转项目」项目池不能再转） |
| 500 | 系统异常 |

#### 验收标准

- [ ] 销售员可创建线索 → 列表立即刷新显示新数据 → 刷新页面后仍存在
- [ ] 线索看板拖拽线索到「合格」列 → 后端 PATCH 返回 200 → 刷新后状态保持
- [ ] 销售员只能看到 owner_id=自己 的线索 + 部门共享线索（待 v0.4 决定，目前全可见）
- [ ] 报价单产品库对话框可多选 / 取消多选 → items 表正确增删
- [ ] 删除已被报价单引用的推荐人 → 返回 409「存在关联商机，不可删除」
- [ ] 跨用户操作：销售员 A 试图改销售员 B 的商机 → 403
- [ ] 30 个新接口全部在 Postman / curl 测试通过

---

### 4.2 转化闭环

#### 业务流程图

```
┌──────────┐    录入      ┌──────────┐   转商机    ┌──────────┐
│  线索池  │ ───────────→ │  线索池  │ ────────→ │  商机池  │
│          │              │ status=  │           │  stage=  │
│ (空)     │              │   new    │           │  require │
└──────────┘              └──────────┘           └────┬─────┘
                            │ 丢弃                    │ 推进
                            ▼                         ▼
                        ┌──────────┐            ┌──────────┐
                        │discarded │            │solution  │
                        └──────────┘            │negotia.. │
                                               │contract..│
                                               │   won    │
                                               │   lost   │
                                               └────┬─────┘
                                                    │ 成交（won）
                                                    ▼
                                               ┌──────────┐
                                               │ 项目池   │
                                               │ status=  │
                                               │ pending  │
                                               └────┬─────┘
                                                    │ 转施工
                                                    ▼
                                               ┌──────────┐
                                               │  施工管理 │
                                               │ 7 阶段   │
                                               └──────────┘
```

#### 4.2.1 线索状态机

**5 个状态**：new / contacting / qualified / converted / discarded

**合法流转**（任何其他流转 → 409）：
```
new          → contacting    （开始跟进）
new          → qualified     （一次沟通后判定合格）
new          → discarded     （判定无价值）
contacting   → qualified     （跟进达标）
contacting   → discarded     （跟进无果）
contacting   → new           （回退到新线索，限销售经理）
qualified    → converted     （转商机）
qualified    → discarded     （客户最终无意向）
```

**触发动作**：
- **录入新线索**：状态=「new」，source=「phone」, owner_id=当前用户
- **转商机**：状态=「qualified」时才可点「转商机」→ 调 `POST /api/sales/leads/{lead}/convert-to-opp` → 自动建商机（stage=requirement，probability=20，sales_id=当前用户）→ 线索状态 → converted
- **丢弃**：弹 dialog 选 discard_reason → 状态 → discarded
- **看板拖拽**：每列对应一个状态（除了 converted 不可拖入，只可由「转商机」按钮触发）

**业务规则**：
- 「converted」状态**不可再编辑**（只读）
- 评级 A / B 的线索不能直接「丢弃」（必须先经过 contacting 阶段）→ 销售经理可强制跳过
- 跟进人 owner_id 必填，新建时默认 = 当前用户
- 预计金额 estimated_amount 可空，0 也允许
- 跟进提醒 follow_up_at：转 contacting 时必填

**验收标准**：
- [ ] 状态机非法流转返回 409
- [ ] 看板 5 列拖拽各列有合理校验（如不允许「已转商机」被拖走）
- [ ] 转商机成功后，线索状态变「converted」+ 商机列表多一条 + 商机 lead_id 字段正确关联
- [ ] converted 线索操作列只剩「查看」按钮

#### 4.2.2 商机状态机

**6 个阶段**：requirement / solution / negotiation / contracting / won / lost

**合法流转**：
```
requirement  → solution      （方案确定）
requirement  → lost          （客户终止）
solution     → negotiation   （开始谈报价）
solution     → lost
negotiation  → contracting   （报价接受 / 拟合同）
negotiation  → lost
contracting  → won           （签约成功）
contracting  → lost
won          → （终态）
lost         → requirement   （战败复活，销售经理权限）
```

**触发动作**：
- **转商机**（来源线索）：stage=requirement，probability=20
- **看板拖拽**：每次拖拽自动重算 probability：
  - requirement=20 / solution=40 / negotiation=60 / contracting=80 / won=100 / lost=0
  - 用户可手动改 probability（0-100），覆盖默认值
- **成交（mark-won）**：弹 dialog 要求填「合同金额」「签约日期」→ 提交后：
  - stage=won
  - probability=100
  - 自动建 project_pool 记录（contract_amount=填的合同金额，signed_at=填的签约日，status=pending）
  - 商机有 referrer_id → 自动建 referral_settlement（详见 4.5）
  - 商机有 lead_id → 该线索保持「converted」状态
- **战败（mark-lost）**：弹 dialog 选 lost_reason（6 选 1）+ 备注 → stage=lost
  - probability → 0
  - **不动线索**（线索还是 converted 状态，因为曾转过商机）

**业务规则**：
- 阶段流转可前进也可后退（如 contracting → solution 改方案），由看板拖拽实现
- won / lost 阶段**只可由「成交 / 战败」按钮触发**，看板不能直接拖入
- expected_sign_date：合同拟定阶段必填
- 预计金额 estimated_amount：商机场必填，不可为 0
- 销售 sales_id + 售前 presale_id 都必填（presale 可与 sales 相同）
- last_contact_at：每次新建跟进记录后自动更新
- next_action / next_action_at：每次新建跟进若有下次计划，自动写入

**验收标准**：
- [ ] 看板 6 列拖拽各列有合理校验（won/lost 只能按钮进入）
- [ ] probability 自动按阶段设置
- [ ] 成交成功后项目池多 1 条 + 项目合同金额正确
- [ ] 战败后商机还可见，但 stage 标签变红，操作列只显示「查看」+「战败复活」（销售经理）
- [ ] 跨用户编辑：销售员 B 试图改销售员 A 的商机 → 403

#### 4.2.3 项目池状态机

**3 个状态**：pending / active / archived

**合法流转**：
```
pending  → active    （转为施工项目）
active   → archived  （项目结案后，销售经理可归档）
archived → （终态）
```

**触发动作**：
- **新建项目池**：商机 mark-won 时自动建（status=pending）
- **转为施工项目（convert-to-project）**：弹 dialog 必填：
  - project_name（默认 = pool.name）
  - manager_id（项目经理，下拉选 users 表 role=manager）
  - start_date / end_date
  - budget（默认 = contract_amount）
  - team_member_ids（多选 users，下限 1）
  → 提交后：
  - 事务内：INSERT projects（stage=contract，合同金额=pool.contract_amount，关联商机 opp_id，关联项目池 pool_id）→ UPDATE project_pool SET status=active, related_project_id=new_id → UPDATE opportunity.project_id
  - 项目进入 7 阶段流程的「合同阶段」(contract)
- **归档**：active 状态下销售经理 / 管理员可手动归档

**业务规则**：
- pending 状态项目池不可编辑，只可「转为施工项目」
- active 状态关联的 projects 不可删（要解绑先归档）
- 商机有 referrer_id 时，**必须在 convert-to-project 之前先结算居间费**（否则提示但不强制）
- 一个项目池只能转一次施工项目（幂等）

**验收标准**：
- [ ] 转施工项目后，project_pool.status=active + related_project_id 非空 + opportunity.project_id 非空
- [ ] 新建 projects 7 阶段初始为「contract」
- [ ] 转施工项目是事务，失败回滚（不留半成品）
- [ ] pending 状态时「转施工项目」按钮可点，active 状态变「查看施工档案」

#### 4.2.4 跨环节业务规则

| 规则 | 说明 |
|---|---|
| 合同金额自动同步 | 商机 mark-won 时 project_pool.contract_amount = 用户填的合同金额（不强制 = estimated_amount） |
| 客户自动同步 | 商机 customer_id 一路传到 projects（商机转施工时继承） |
| 销售/售前自动同步 | 商机 sales_id / presale_id 写入 projects 的对应字段（如果存在） |
| 推荐人自动关联 | 商机 mark-won 时若 lead.referrer_id 存在，project_pool 关联到 referrer |
| 跟进提醒倒推 | 线索 follow_up_at < 今天 → 列表标红（前端展示） |
| 商机预期签约日 | 商机 expected_sign_date 临近 7 天 → 看板卡片橙边 |

---

### 4.3 报价单完整逻辑

#### 业务场景

报价单是销售员对客户提交的产品 + 服务 + 价格的正式报价。一个商机可以有多版（V1 / V2 / V3），每版包含若干产品条目，含产品库关联 / 折扣 / 税额 / 状态。

#### 数据结构（已有）

```sql
quotations
  id, quote_no, opportunity_id, version
  subtotal, discount_rate, discount_amount
  tax_rate, tax_amount, total_amount
  valid_until, status, notes
  created_by, approved_by, sent_at, responded_at

quotation_items
  id, quotation_id, inventory_item_id (NULL 表示非标品)
  name, specification, unit, quantity, unit_price, total_price
  remark
```

#### 4.3.1 产品库多选规则

**产品库来源**：`/api/inventory` 接口（已有完整 CRUD），`status=active` 且 `stock_qty > 0` 的物品

**多选规则**：
- 对话框支持搜索（按 name / specification 模糊）、分类过滤
- 选中后加入 items 列表
- 同一 inventory_item_id 在一张报价单中**只可出现一次**（防重复）
- items 可调整 quantity（默认 1），可改 unit_price（默认取产品库当前价），可删
- 支持「非标品」：勾选「非标产品」可手填 name / spec / unit / price

**后端存储**：
- 选了产品库：inventory_item_id 非空，name/spec/unit/unit_price 默认 = 产品库
- 非标品：inventory_item_id = NULL，name / spec / unit / unit_price 全部手填
- 修改 items 时不修改 inventory_items 表（只读引用）

**业务规则**：
- 同张报价单 inventory_item_id 唯一约束（DB 唯一索引：quotation_id + inventory_item_id WHERE inventory_item_id IS NOT NULL）
- 报价单非 submitted / negotiating 状态可编辑 items，其他状态只读
- 报价单 status=draft 时可改 items；submitted / negotiating 时只能改 status；其他状态全只读

**验收标准**：
- [ ] 产品库对话框支持搜索 + 分类过滤 + 多选 + 反选
- [ ] 同一产品不能重复选（重复选时弹 toast 提示）
- [ ] 选完产品后 items 表格自动加一行（unit_price 默认产品库当前价）
- [ ] quantity 改 0 时该行小计=0，可手动删除该行
- [ ] 非标品模式下 name / spec 必填校验
- [ ] 已 submitted 的报价单 items 表格只读

#### 4.3.2 折扣 / 税额计算公式

**输入**：items（quantity + unit_price）
**输出**：subtotal / discount_rate / discount_amount / tax_rate / tax_amount / total_amount

```
subtotal       = Σ (item.quantity × item.unit_price)    保留 2 位小数
discount_rate  = 0-30（%），默认 0                    销售员输入
discount_amount= subtotal × discount_rate / 100      保留 2 位小数（四舍五入）
after_discount = subtotal - discount_amount
tax_rate       = 0 / 3 / 6 / 9 / 13（%），默认 13     销售员下拉选
tax_amount     = after_discount × tax_rate / 100      保留 2 位小数
total_amount   = after_discount + tax_amount          保留 2 位小数
```

**约束**：
- discount_rate 上限 30%（销售经理可放宽到 50%，需 admin 角色）
- tax_rate 必须是枚举值
- 修改任一 items 数量 / 单价 → 触发整体重算
- 修改 discount_rate → 触发重算
- 修改 tax_rate → 触发重算
- 全部计算后端验证（防前端绕过），返回 422 若不通过

**示例**：
```
items: 海康摄像头 × 10 单价 ¥2000 + 线材 × 5 单价 ¥1000
subtotal = 10×2000 + 5×1000 = ¥25,000
discount_rate = 8%   → discount_amount = 2,000
after_discount = 23,000
tax_rate = 13%   → tax_amount = 2,990
total_amount = ¥25,990
```

**验收标准**：
- [ ] 改任一 quantity → total_amount 自动重算（前端 watch + 后端再校验）
- [ ] 折扣 30% 限校验：销售员输 35% → 提示「折扣率不能超过 30%」
- [ ] 税额选项限定 5 个枚举值
- [ ] 保存时后端再算一次，前端显示的 total 与后端返回的 total 必须一致（一致性校验）
- [ ] 单价 / 数量支持小数（如 0.5 个工时）

#### 4.3.3 报价单状态机

**6 个状态**：draft / submitted / negotiating / accepted / rejected / expired

**合法流转**：
```
draft       → submitted       （提交审批/客户）
draft       → （删除）
submitted   → negotiating     （客户开始还价）
submitted   → accepted        （客户一次接受）
submitted   → rejected        （客户拒绝）
submitted   → expired         （30 天未响应自动过期，定时任务）
negotiating → accepted        （谈妥）
negotiating → rejected
negotiating → submitted       （回退到已提交，二次提交新版本）
negotiating → expired
accepted    → （终态）
rejected    → draft           （客户改主意，销售员另起一版）
rejected    → （终态）
expired     → draft           （续期）
expired     → （终态）
```

**触发动作**：
- **新建版本**：基于当前 quote 复制 → version=max(version)+1，status=draft，items 全量复制 → 旧版本不动
- **提交（submit）**：draft → submitted → sent_at=now()
- **谈判中（negotiate）**：submitted → negotiating
- **客户接受（accept）**：submitted/negotiating → accepted → responded_at=now() + 商机 stage 自动推到 contracting + 商机 probability 设为 80
- **客户拒绝（reject）**：submitted/negotiating → rejected → responded_at=now() + 备注
- **过期（expire）**：submitted/negotiating + valid_until < today → 自动 expired（定时任务每晚 1 点跑）

**业务规则**：
- **每张报价单必须显式选产品库**（至少 1 个 item），不允许空报价
- 客户接受后，**该报价单**置 accepted + **该商机下其他报价单**自动置为 rejected（互斥）
- 客户接受后，若商机有 project_pool 已建 → 不影响（按 4.2 流程）
- valid_until：销售员必填，默认 30 天
- 备注 notes：可选，500 字以内
- 删除只允许 draft 状态（已 submitted 强制走 reject 流程）

**验收标准**：
- [ ] 状态机非法流转返回 409
- [ ] 客户接受时其他报价单自动 rejected（事务）
- [ ] 新建版本自动 +1，旧版本号不变
- [ ] 过期定时任务（每日 01:00）跑通，状态自动更新
- [ ] valid_until 过期 7 天前弹提醒

---

### 4.4 跟进记录附件

#### 业务场景

销售员在跟进客户 / 商机过程中，需要保存沟通证据（聊天截图 / 合同草稿 / 报价单 PDF / 现场照片）。跟进记录支持附件上传。

#### 支持文件类型 / 大小

| 类型 | 允许 | 单文件大小 | 总大小 |
|---|---|---|---|
| 图片 | jpg / jpeg / png / gif / webp | 10 MB | 50 MB / 条跟进 |
| 文档 | pdf / doc / docx / xls / xlsx / ppt / pptx / txt | 20 MB | 同上 |
| 压缩包 | zip / rar / 7z | 50 MB | 同上 |
| 禁止 | exe / bat / sh / dll / so / 可执行文件 | - | - |

#### 存储位置

**复用现有网盘机制**（`pc-api` 已有 DiskController）：

```
/var/www/oa-api/storage/app/public/disk/sales/follow-up/{follow_up_id}/{yyyy}/{mm}/{uuid}.{ext}
```

- DB 表 `sales_follow_up_attachments`：name / path / mime / size / uploader_id / created_at
- 文件实际存盘，DB 只存元数据
- 提供下载 stream 接口（不走 nginx 直连，方便鉴权）

#### 列表 / 下载 / 删除规则

**列表**：
- 跟进详情页内嵌附件列表
- 字段：文件名 / 大小 / 上传者 / 上传时间 / 下载按钮 / 删除按钮
- 按 created_at 倒序

**下载**：
- `GET /api/sales/follow-ups/attachments/{att}/download`
- 后端检查：当前用户必须是该 follow_up 的 owner 或者 follow_up 对应 target 的 owner
- 返回文件 stream + 原始文件名（Content-Disposition: attachment）

**删除**：
- `DELETE /api/sales/follow-ups/attachments/{att}`
- 仅 follow_up 创建者 / 销售经理 / 管理员可删
- 软删除 DB 行 + 物理删文件（事务：先删文件再删 DB 行，DB 失败回滚重试文件）

#### 上传 UX 流程

```
点击「上传附件」按钮
  → el-upload 组件（多选、拖拽、显示进度条）
  → 客户端预检：单文件大小 / 类型
  → 调 POST /api/sales/follow-ups/{follow_up_id}/attachments (multipart)
  → 后端保存 + 返 200
  → 前端刷新附件列表
```

**前端用 el-upload 组件**：
- `multiple` 多选
- `:before-upload` 客户端预检
- `:on-success` / `:on-error` 处理响应
- `:show-file-list="false"`（自渲染列表，保留原始文件名）
- 上传中显示 loading

**业务规则**：
- 跟进 status 字段不存在（跟进没有 status 概念），但跟进被删除时其附件一起删
- 单条跟进最多 20 个附件
- 同一文件名可重复上传（自动加 uuid 防冲突）
- 客户端预检失败：单文件 > 限制 / 累计 > 50MB / 文件类型不在白名单 → 不发请求，直接 toast

**验收标准**：
- [ ] 上传 jpg / pdf / docx 全部成功，DB 落记录，文件落盘
- [ ] 上传 11MB 单文件 → toast 提示「单文件不能超过 10MB」不发请求
- [ ] 上传 6 个 9MB 文件（共 54MB）→ 提示「单条跟进附件总大小不能超过 50MB」
- [ ] 上传 .exe → 提示「不允许的文件类型」
- [ ] 下载附件：原文件名 / Content-Disposition 正确
- [ ] 删除附件：DB 行 + 文件都删
- [ ] 跟进被删除 → 其附件一起删
- [ ] 跨用户：销售员 B 下载销售员 A 的附件 → 403

---

### 4.5 推荐人居间费自动结算

#### 业务场景

推荐人（中间人 / 老客户转介绍人）介绍项目成功，按事前约定的居间费比例，从项目合同金额中提取一笔费用作为报酬。系统需要：
- 记录推荐人与项目关联
- 合同签约 / 回款时自动算出居间费
- 生成结算记录，财务审核后发放

#### 数据结构

**referrers**（已有）：
```
id, name, phone, customer_id (老客户), 
bank_name, bank_account, commission_rate (%)
total_commission (累计已发), notes
```

**新表 referral_settlements**：
```sql
CREATE TABLE referral_settlements (
    id BIGSERIAL PRIMARY KEY,
    settlement_no VARCHAR(32) UNIQUE NOT NULL,    -- 结算单号，格式 RF{yyyyMMdd}{0001}
    referrer_id BIGINT NOT NULL REFERENCES referrers(id),
    opportunity_id BIGINT NOT NULL REFERENCES opportunities(id),
    project_id BIGINT NULL REFERENCES projects(id),
    pool_id BIGINT NULL REFERENCES project_pool(id),
    contract_amount DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) NOT NULL,         -- 比例快照
    commission_amount DECIMAL(12,2) NOT NULL,      -- 实际计算金额
    trigger_event VARCHAR(32) NOT NULL,             -- 签约触发 / 回款触发 / 手动触发
    status VARCHAR(16) NOT NULL DEFAULT 'pending',  -- pending / approved / paid / cancelled
    approved_by BIGINT NULL REFERENCES users(id),
    approved_at TIMESTAMP NULL,
    paid_at TIMESTAMP NULL,
    payment_voucher VARCHAR(255) NULL,              -- 银行回单附件路径
    notes TEXT,
    created_at TIMESTAMP, updated_at TIMESTAMP
);
CREATE INDEX idx_rs_referrer ON referral_settlements(referrer_id);
CREATE INDEX idx_rs_status ON referral_settlements(status);
```

#### 4.5.1 居间费计算公式

```
commission_amount = contract_amount × referrer.commission_rate / 100
```

**约束**：
- 合同金额 < 1 万元 → 不结算（提示「金额过小，不结算」）
- commission_rate 范围 1% - 30%（DB CHECK）
- 同一商机 / 项目池只结算一次（DB 唯一索引 opportunity_id）

**示例**：
```
合同金额 ¥1,000,000，commission_rate 5%
commission_amount = 1,000,000 × 5 / 100 = ¥50,000
```

#### 4.5.2 结算触发条件

**P1 范围内只实现「签约触发」**（回款触发 P2 再做）。

| 触发事件 | 时机 | 业务规则 |
|---|---|---|
| **签约触发** | 商机 mark-won 时 | 若 lead.referrer_id 存在 → 自动建 referral_settlement（status=pending, trigger_event=签约触发） |
| **回款触发** | P2 | 项目收到首期款时按已回款金额 × 比例结算 |
| **手动触发** | 销售经理在推荐人页加按钮 | 特殊场景手动加一笔 |

**P1 简化方案**：P1 只在 mark-won 时建一条「签约触发」的结算记录，状态 pending，等财务审核。

#### 4.5.3 结算记录管理

**列表页**（`/referrer/settlements`）：
- 表格：结算单号 / 推荐人 / 商机 / 合同金额 / 比例 / 金额 / 触发事件 / 状态 / 创建时间
- 过滤：状态、推荐人、触发事件、时间范围
- 权限：销售经理 + 财务 + 管理员可见全部；销售员只看自己商机的

**操作**：
- **pending → approved**：财务点「审核通过」→ 填实际发放金额（可改，默认 = 计算值）+ 备注 → approved_by + approved_at
- **approved → paid**：财务点「标记已发放」→ 上传银行回单附件 + 填 paid_at → status=paid + referrer.total_commission += commission_amount
- **pending → cancelled**：销售经理点「取消结算」→ 填原因 → status=cancelled（不改 referrer.total_commission）

**业务规则**：
- pending 状态销售经理可改 commission_amount（如客户改价）
- approved 状态不可改金额，只可走「取消 + 新建」
- paid 状态完全只读（账已经出去了）
- 推荐人 total_commission 只在 paid 时累加（避免虚高）

**验收标准**：
- [ ] 商机 mark-won 时若 lead 有 referrer → 自动建一条 pending 结算记录
- [ ] 商机 mark-won 时若 lead 无 referrer → 不建结算记录（不报错）
- [ ] 财务审核：pending → approved，写入 approved_by / approved_at
- [ ] 财务发放：approved → paid，写入 paid_at + 上传回单 + referrer.total_commission += amount
- [ ] 列表分页 + 过滤 + 权限隔离
- [ ] 同一商机不会重复建结算（DB 唯一约束 + 应用层先查后建）

---

## 五、优先级与里程碑

### 5.1 里程碑划分

| 里程碑 | 周期 | 交付 | 关键路径 |
|---|---|---|---|
| **M1：API 真实 CRUD** | 3 天 | 30 个新接口 + 前端 7 页面接通 | 后端 controller → 路由 → 前端表单 / dialog |
| **M2：转化闭环** | 2 天 | 4 个状态机 + 4 个触发动作 + 数据自动同步 | DB 事务 + 后端 service 层 + 前端弹窗 |
| **M3：报价单业务化** | 2 天 | 产品库多选 + 折扣 / 税额 + 状态机 | 前端 dialog + watch + 后端校验 |
| **M4：跟进附件** | 1 天 | 上传 / 下载 / 删除 / 容量限制 | el-upload + multipart |
| **M5：居间费自动结算** | 1 天 | 新表 + 自动触发 + 审核流程 | migration + 结算列表页 + 财务审核 dialog |

**总周期：约 9 个工作日（2 周）**

### 5.2 依赖关系

```
M1 ─┬─→ M2 ─┐
    ├─→ M3 ─┤
    └─→ M4 ─┼─→ M5
            │
    M1 单独也可先上线（接通后所有按钮立刻可用）
```

**推荐顺序**：M1 → M3 → M2 → M4 → M5
- M3（报价单）依赖 M1
- M2（转化）依赖 M1
- M4（附件）独立，但 M1 做好后并行
- M5（居间费）依赖 M1 + M2

### 5.3 验收节点

| 节点 | 验证方法 |
|---|---|
| M1 完 | Postman 30 接口 + puppeteer 7 页面所有按钮 e2e |
| M2 完 | 端到端：录线索 → 转商机 → 战败 → 成交 → 转项目池 → 转施工，DB 各表数据正确 |
| M3 完 | 端到端：新建报价 V1 → 改折扣 → 新建 V2 → 客户接受 → 商机推到合同拟定 |
| M4 完 | 上传 / 下载 / 删除 / 容量 / 类型 / 鉴权 全部边界用例 |
| M5 完 | 商机成交 → 自动建结算 → 财务审核 → 标记发放 → 推荐人 total_commission 正确 |

---

## 六、风险与依赖

### 6.1 技术风险

| 风险 | 等级 | 应对 |
|---|---|---|
| **30 个接口一次性接入易出 bug** | 中 | 分批上线：M1 完成后每日 e2e 跑通，Postman 全覆盖 |
| 转化闭环事务复杂（多表 + 反向同步） | 中 | 用 `DB::transaction` 包裹，关键字段加 DB 约束兜底 |
| 报价单重算前后端不一致 | 低 | 后端再算一次，前端 computed 显示只用于预览 |
| 附件上传大文件 OOM | 中 | PHP `upload_max_filesize` 改 64M + nginx `client_max_body_size` 64M |
| el-upload 跨域 / cookie 问题 | 低 | 复用现有 request 拦截器（已带 Sanctum token） |
| DB 唯一约束 violation 时给前端友好提示 | 中 | 全局 23505 异常拦截器，提示「该 X 已存在」 |

### 6.2 业务依赖

| 依赖 | 说明 |
|---|---|
| 客户表 customers | 线索 / 商机 / 报价单都关联客户，客户必须先有 |
| 用户表 users | sales_id / presale_id / owner_id 都引用 users.id |
| 库存表 inventory_items | 报价单产品库多选来源 |
| 商机 7 阶段流程 | 转化闭环后商机进入施工管理 |
| 财务应收（receivables） | 居间费 P2 回款触发时要读 |
| 网盘 disk | 跟进附件复用 |

### 6.3 第三方依赖

- 无新增第三方依赖
- 沿用 Sanctum / Pinia / Element Plus

### 6.4 数据迁移

- 新增 `referral_settlements` 一张表，需要新建 migration
- 现有 5 张表结构不动
- 现有数据不需要回填（v0.3.9 P0 还没有真实业务数据）

---

## 七、附录

### 7.1 数据字典（新增 / 修改）

#### `referral_settlements`（P1 新增）

| 字段 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| id | bigint | 是 | auto | PK |
| settlement_no | varchar(32) | 是 | - | UNIQUE，格式 RF{yyyyMMdd}{0001} |
| referrer_id | bigint | 是 | - | FK → referrers.id |
| opportunity_id | bigint | 是 | - | FK → opportunities.id，UNIQUE |
| project_id | bigint | 否 | NULL | FK → projects.id，签约触发后回填 |
| pool_id | bigint | 否 | NULL | FK → project_pool.id |
| contract_amount | decimal(12,2) | 是 | - | 合同金额快照 |
| commission_rate | decimal(5,2) | 是 | - | 比例快照（防止后续推荐人改比例影响历史） |
| commission_amount | decimal(12,2) | 是 | - | 实际计算金额 |
| trigger_event | varchar(32) | 是 | - | 签约触发 / 回款触发 / 手动触发 |
| status | varchar(16) | 是 | pending | pending / approved / paid / cancelled |
| approved_by | bigint | 否 | NULL | FK → users.id |
| approved_at | timestamp | 否 | NULL | - |
| paid_at | timestamp | 否 | NULL | - |
| payment_voucher | varchar(255) | 否 | NULL | 银行回单附件路径 |
| notes | text | 否 | NULL | - |
| created_at | timestamp | 是 | auto | - |
| updated_at | timestamp | 是 | auto | - |

**索引**：
- UNIQUE(settlement_no)
- UNIQUE(opportunity_id)  -- 同一商机只可结算一次
- INDEX(referrer_id)
- INDEX(status)
- INDEX(created_at)

#### 现有表状态字段（用于状态机）

| 表 | 字段 | 枚举值 |
|---|---|---|
| leads | status | new / contacting / qualified / converted / discarded |
| opportunities | stage | requirement / solution / negotiation / contracting / won / lost |
| opportunities | probability | 0-100（int） |
| quotations | status | draft / submitted / negotiating / accepted / rejected / expired |
| project_pool | status | pending / active / archived |
| referral_settlements | status | pending / approved / paid / cancelled |

### 7.2 业务术语表

| 术语 | 解释 |
|---|---|
| **线索 Lead** | 销售前链路最早期，可能是客户咨询 / 电话陌拜 / 展会获取，未确认需求 |
| **商机 Opportunity** | 客户已确认有需求，进入销售跟进流程，关联 1 个客户 + 1 个销售 + 1 个售前 |
| **报价单 Quotation** | 销售员对客户提交的产品 + 服务 + 价格正式报价，1 个商机可有多版（V1/V2...） |
| **项目池 ProjectPool** | 商机成交后、施工前的中间状态，等待项目经理接收 |
| **跟进记录 FollowUp** | 销售 / 售前与客户沟通的留痕，可挂附件 |
| **推荐人 Referrer** | 项目介绍人 / 中间人，按比例拿居间费 |
| **居间费 Commission** | 推荐人报酬 = 合同金额 × 比例 |
| **结算单 Settlement** | 居间费发放流程的载体 |
| **施工项目 Project** | 项目池转过来后进入 7 阶段流程的工程项目 |
| **转化闭环** | 线索 → 商机 → 成交 → 项目池 → 施工项目的全链路数据贯通 |
| **产品库** | inventory_items 表中可被报价单引用的物品集合 |

### 7.3 API 总览（30 个新增 + 6 个 GET 复用）

#### 线索 5 个
```
POST   /api/sales/leads
PUT    /api/sales/leads/{lead}
DELETE /api/sales/leads/{lead}
PATCH  /api/sales/leads/{lead}/status
POST   /api/sales/leads/{lead}/convert-to-opp
```

#### 商机 6 个
```
POST   /api/sales/opps
PUT    /api/sales/opps/{opp}
DELETE /api/sales/opps/{opp}
PATCH  /api/sales/opps/{opp}/stage
POST   /api/sales/opps/{opp}/mark-won
POST   /api/sales/opps/{opp}/mark-lost
```

#### 报价单 7 个
```
POST   /api/sales/quotes
PUT    /api/sales/quotes/{quote}
DELETE /api/sales/quotes/{quote}
POST   /api/sales/quotes/{quote}/items
PUT    /api/sales/quotes/{quote}/status
POST   /api/sales/quotes/{quote}/new-version
GET    /api/sales/quotes/{quote}/items   （按需，必要时）
```

#### 产品库 1 个（复用）
```
GET    /api/inventory?keyword=...&category_id=...&in_stock=1
```

#### 推荐人 3 个
```
POST   /api/sales/referrers
PUT    /api/sales/referrers/{referrer}
DELETE /api/sales/referrers/{referrer}
```

#### 项目池 2 个
```
POST   /api/sales/pool/{pool}/convert-to-project
PUT    /api/sales/pool/{pool}
```

#### 跟进记录 + 附件 5 个
```
POST   /api/sales/follow-ups
PUT    /api/sales/follow-ups/{followUp}
DELETE /api/sales/follow-ups/{followUp}
POST   /api/sales/follow-ups/{followUp}/attachments     （multipart）
DELETE /api/sales/follow-ups/attachments/{att}
GET    /api/sales/follow-ups/attachments/{att}/download
```

#### 结算 5 个
```
GET    /api/sales/settlements
POST   /api/sales/settlements/{settlement}/approve
POST   /api/sales/settlements/{settlement}/mark-paid    （multipart，含回单）
POST   /api/sales/settlements/{settlement}/cancel
GET    /api/sales/referrers/{referrer}/settlements      （推荐人维度统计）
```

**总计：5+6+7+1+3+2+6+5 = 35 个新端点**（修正原 30 的估算）

### 7.4 状态机总图

```
                    ┌──── leads ────┐
                    │  new/contact/  │
                    │ qualified/     │
                    │ converted/     │
                    │ discarded      │
                    └────┬──────────┘
                         │ convert
                         ▼
                    ┌──── opps ─────┐
                    │ requirement→  │
                    │ solution→     │
                    │ negotiation→  │
                    │ contracting   │
                    │ →won / lost   │
                    └────┬──────────┘
                         │ mark-won
                         ▼
                    ┌──── pool ─────┐
                    │ pending/      │
                    │ active/       │
                    │ archived      │
                    └────┬──────────┘
                         │ convert-to-project
                         ▼
                    ┌──── projects ────┐
                    │  7 阶段流程      │
                    │  contract → ... │
                    └──────────────────┘

              ┌──── quotes ────┐
              │ draft→submitted │
              │ →negotiating→  │
              │ accepted /      │
              │ rejected /      │
              │ expired         │
              └─────────────────┘

              ┌──── settlements ────┐
              │ pending→approved→   │
              │ paid / cancelled    │
              └─────────────────────┘
```

### 7.5 部署检查清单

P1 上线前必须：
- [ ] 服务器 PHP `upload_max_filesize=64M` `post_max_size=64M`
- [ ] nginx `client_max_body_size=64M`
- [ ] 新建 storage 子目录 `disk/sales/follow-up/{yyyy}/{mm}/`（chown www-data）
- [ ] migration `referral_settlements` 已跑通
- [ ] 路由全部在 api.php 注册（POST/PUT/DELETE/新增端点）
- [ ] Controller 在 use { } 顶部 use 列表（最易漏）
- [ ] 7 个新页面 + 1 个新增结算列表页已部署
- [ ] e2e 全跑通

---

**文档结束。**

> 维护说明：本 PRD 是 v0.3.9 P1 业务逻辑开发的唯一真理来源。若开发过程中发现业务决策需调整，先回 PRD 评审，再改代码，避免代码与文档脱节。
