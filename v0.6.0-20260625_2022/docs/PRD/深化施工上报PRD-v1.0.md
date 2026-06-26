# 深化施工上报 PRD v1.0

> **版本**: v1.0
> **作者**: Senior Developer
> **创建日期**: 2026-06-22
> **适用终端**: PC Web (V1.1-V1.4) → H5 业主门户 (V1.5) → 移动端 (V2.0)
> **关联模块**: 项目管理 7 阶段 / 售后服务 6 环节 / 财务 / 库存 / 考勤 / 公司网盘

---

## 目录

- [0. 文档说明](#0-文档说明)
- [1. 业务背景与目标](#1-业务背景与目标)
- [2. 4 大新模块总览](#2-4-大新模块总览)
- [3. V1.1 工序验收 + 影像档案](#3-v11-工序验收--影像档案-p0)
- [4. V1.2 产值上报 + 进度款联动](#4-v12-产值上报--进度款联动-p0)
- [5. V1.3 质量 + 安全巡检](#5-v13-质量--安全巡检-p1)
- [6. V1.4 现场打卡 + 定位](#6-v14-现场打卡--定位)
- [7. V1.5 业主 H5 门户](#7-v15-业主-h5-门户)
- [8. 数据库 ER 图](#8-数据库-er-图)
- [9. 通用数据表 (8 张)](#9-通用数据表-8-张)
- [10. V1.1 工序验收数据表 (5 张)](#10-v11-工序验收数据表-5-张)
- [11. V1.2 产值上报数据表 (4 张)](#11-v12-产值上报数据表-4-张)
- [12. V1.3 巡检数据表 (5 张)](#12-v13-巡检数据表-5-张)
- [13. V1.4 打卡数据表 (3 张)](#13-v14-打卡数据表-3-张)
- [14. V1.5 业主门户数据表 (3 张)](#14-v15-业主门户数据表-3-张)
- [15. 路由清单 (总)](#15-路由清单-总)
- [16. API 设计规范](#16-api-设计规范)
- [17. 前端页面清单](#17-前端页面清单)
- [18. 与现有模块的集成点](#18-与现有模块的集成点)
- [19. 部署与回滚方案](#19-部署与回滚方案)
- [20. 验收标准](#20-验收标准)

---

## 0. 文档说明

### 0.1 文档目的
为开发团队提供 **深化施工上报** 模块的详细业务+技术方案,包含:
- 业务规则与流程
- 完整数据库设计 (28 张新表)
- API 接口清单 (60+ 端点)
- 前端页面与组件清单
- 与现有模块的集成方案

### 0.2 设计原则
| 原则 | 说明 |
|------|------|
| **零破坏升级** | 现有 7 阶段项目/工序验收/变更申请全部保留,新功能以"扩展点"形式叠加 |
| **统一数据源** | 影像/产值/巡检都从"项目"维度聚合,不重复造轮子 |
| **业务可配置** | 巡检模板/工序模板/资料目录支持 admin 后台维护,不改代码 |
| **可降级** | 任何模块禁用都不影响其他模块跑 |
| **数据可溯** | 所有业务操作留痕(谁/什么时候/改了什么),支持审计 |

### 0.3 范围
**本期 V1.0 (PC 端)**:
- V1.1 工序验收 + 影像档案 (P0, 4 周)
- V1.2 产值上报 + 进度款联动 (P0, 3 周)
- V1.3 质量 + 安全巡检 (P1, 3 周)
- V1.4 现场打卡 + 定位 (2 周)

**下期 V2.0 (移动端 + 业主门户)**:
- V1.5 业主 H5 门户
- 微信小程序现场上报
- 班组长 APP

---

## 1. 业务背景与目标

### 1.1 现状
目前 PC 端已实现项目管理 7 阶段 + 售后服务 6 环节,但**施工现场一线业务**沉淀不足:
- 进度上报无影像,事后无据
- 隐蔽工程覆盖后查不到
- 产值靠 Excel 报,出错率高
- 巡检靠微信群,无闭环
- 出勤靠包工头报,纠纷多

### 1.2 目标
| 业务指标 | 当前值 | 目标值 |
|----------|--------|--------|
| 验收一次性通过率 | ~60% | ≥ 85% |
| 进度款回款周期 | 平均 90 天 | ≤ 45 天 |
| 巡检问题整改率 | 估 50% | ≥ 95% |
| 出勤数据准确率 | 估 70% | ≥ 98% |
| 客户满意度 | 无数据 | ≥ 90 分 |

### 1.3 用户角色
| 角色 | 关键能力 |
|------|----------|
| **施工员** | 工序报验/产值上报/打卡/巡检发起 |
| **项目经理** | 工序验收/产值审核/巡检派单/打卡审批 |
| **班组长** | 代班组打卡/工序预检/巡检回传 |
| **监理/甲方** | 工序电子签/巡检复核/产值确认 |
| **安全员** | 巡检发起/整改复核 |
| **财务** | 进度款审核/产值对账 |

---

## 2. 4 大新模块总览

```
┌──────────────────────────────────────────────────────────┐
│                    现有 7 阶段项目                          │
└────────────────────────┬─────────────────────────────────┘
                         │
       ┌────────┬───────┼───────┬──────────┬──────────┐
       ▼        ▼       ▼       ▼          ▼          ▼
   产值上报  工序验收   巡检    打卡      变更申请   (现有)
   V1.2     V1.1     V1.3    V1.4      ━━━━━━
       │        │       │       │
       ▼        ▼       ▼       ▼
   ┌────────────────────────────────────────────────┐
   │          公司网盘 (复用: 影像/资料归档)          │
   └────────────────────────────────────────────────┘
       │        │       │       │
       ▼        ▼       ▼       ▼
   ┌────────────────────────────────────────────────┐
   │       财务模块 (复用: 进度款自动触发)            │
   └────────────────────────────────────────────────┘
       │        │
       ▼        ▼
   ┌────────────────────────────────────────────────┐
   │       库存模块 (复用: 材料消耗归集)              │
   └────────────────────────────────────────────────┘
       │
       ▼
   ┌────────────────────────────────────────────────┐
   │       考勤模块 (复用: 出勤数据归集)              │
   └────────────────────────────────────────────────┘
       │
       ▼
   ┌────────────────────────────────────────────────┐
   │     V1.5 业主 H5 门户 (扫码只看只读视图)        │
   └────────────────────────────────────────────────┘
```

---

## 3. V1.1 工序验收 + 影像档案 (P0)

### 3.1 业务场景
- 隐蔽工程(管槽/线管/弱电井)被覆盖后再也看不到,验收扯皮无据
- 关键工序(管线预埋/设备安装/通电测试)无电子签,法律效力不足
- 业主看不到工地进度,信任感弱

### 3.2 业务规则
| 规则 | 说明 |
|------|------|
| **工序模板** | 5 大行业 × 每行业 15-25 个标准工序节点 |
| **必传规则** | 关键工序 ≥ 3 张照片 + 1 段视频 + 现场定位 |
| **覆盖前必检** | "隐蔽覆盖"类工序标记后,需监理验收通过才能进入下一道 |
| **电子签** | 甲方/监理/施工方三方手写签字 + 时间戳 + 哈希防篡改 |
| **影像归档** | 4 级树:项目 → 阶段 → 工序 → 部位 |
| **业主门户** | 二维码扫码,业主可看只读视图 |

### 3.3 业务对象
- **工序模板 (process_templates)**: 行业 / 工序名 / 是否关键 / 是否隐蔽 / 必传数
- **工序实例 (process_instances)**: 某项目的具体工序执行
- **工序报验单 (process_inspections)**: 某工序的验收记录
- **工序影像 (process_images)**: 关联报验单,4 级树
- **电子签名 (process_signatures)**: 关联报验单,三方签字

### 3.4 状态机
```
工序实例状态机:
  pending(待开始) → in_progress(进行中) → inspection(报验中)
  → passed(通过) | rejected(驳回) → in_progress(进行中) → ...
  → passed → next_process(进入下一道)
  → archived(归档)
```

### 3.5 关键流程
**工序报验闭环**:
1. 施工员现场施工 → 拍照 (水印相机) → 提交工序报验单
2. 系统自动校验必传项 (≥ 3 张图 + 1 视频 + 定位)
3. 班组长预检 (微信通知)
4. 监理/甲方电子签 (短信链接)
5. 通过 → 归档;不通过 → 整改 → 重新报验

---

## 4. V1.2 产值上报 + 进度款联动 (P0)

### 4.1 业务场景
- 包工头报进度"90% 完成",实际 60%,验收时扯皮
- 进度款支付无依据,老板不敢签
- 项目实际成本算不清,不知道哪些项目赚钱

### 4.2 业务规则
| 规则 | 说明 |
|------|------|
| **上报频次** | 日报 (项目维度) / 周报 (公司维度) |
| **产值分项** | 人工 / 材料 / 机械 / 管理费 4 项 |
| **自动汇总** | 累计产值 = 合同额 × 累计完成百分比 |
| **节点触发** | 达到 30/60/90/95% 自动生成"进度款申请" |
| **成本归集** | 从物资/车辆/人工/分包自动归集到项目 |
| **回款预警** | 进度款超期未回 → 财务大屏红牌 |

### 4.3 业务对象
- **产值上报 (production_reports)**: 项目/日期/完成百分比/产值分项
- **产值汇总 (project_production_summary)**: 项目维度,触发器自动更新
- **合同节点 (project_contract_milestones)**: 合同金额/各节点比例/已付/已开票
- **进度款申请 (progress_payment_requests)**: 节点触发/审批流

### 4.4 状态机
```
产值上报状态机:
  draft(草稿) → submitted(已提交) → approved(已审核) → settled(已结算)
                  → rejected(驳回) → draft
```

### 4.5 关键流程
**进度款自动触发**:
1. 产值上报累计完成 = 30% → 系统自动创建"30% 进度款申请"
2. 进入财务审批流 → 财务确认 → 自动生成付款单
3. 实际付款 → 财务回填 → 关闭申请

---

## 5. V1.3 质量 + 安全巡检 (P1)

### 5.1 业务场景
- 施工现场安全和质量问题靠微信群截图,事后追责无据
- 监理来一次签一次字,无系统性数据
- 不合格项整改无闭环

### 5.2 业务规则
| 规则 | 说明 |
|------|------|
| **巡检模板** | 安全 (10 类 80+ 项) + 质量 (8 类 60+ 项) 双库 |
| **巡检频次** | 项目级:每周至少 1 次;公司级:每月抽检 |
| **不合格派单** | 复用**售后工单 6 环节**,加"巡检来源"标记 |
| **整改闭环** | 责任人 → 整改 → 拍照回传 → 巡检人复核 |
| **风险热力** | 30 天巡检点热力图,问题高发区高亮 |

### 5.3 业务对象
- **巡检模板分类 (inspection_categories)**: 安全/质量
- **巡检模板项 (inspection_items)**: 分类/名称/标准/分值
- **巡检单 (inspections)**: 项目/模板/总分/结果
- **巡检明细 (inspection_results)**: 单项/合格/不合格/照片
- **巡检问题派单 (inspection_issues)**: 关联巡检单 + 售后工单

### 5.4 关键流程
**巡检问题整改闭环**:
1. 巡检员发起巡检 → 勾选 checklist → 拍照取证
2. 不合格项 → 系统自动创建"售后工单" (来源=巡检) → 派给责任人
3. 责任人整改 → 拍照回传 → 提交"已完成"
4. 巡检员复核 → 通过 → 关闭;不通过 → 二次整改

---

## 6. V1.4 现场打卡 + 定位

### 6.1 业务场景
- 工人到工地没打卡,包工头扯皮出勤天数
- 跨工地窜岗查不出来
- 真实工时数据没沉淀,成本核算不准

### 6.2 业务规则
| 规则 | 说明 |
|------|------|
| **围栏打卡** | 项目预设经纬度+半径(默认 200m),进入围栏可打卡 |
| **水印相机** | 拍照自动叠加项目名/时间/经纬度/拍摄人,水印不可关闭 |
| **多角色打卡** | 班组长 + 工人都要打(支持代班组打卡) |
| **出勤报表** | 自动生成项目维度工时表,作为成本核算依据 |
| **数据归集** | 每日 23:00 自动汇总到考勤模块 |

### 6.3 业务对象
- **项目围栏 (project_geofences)**: 项目/经纬度/半径
- **打卡记录 (attendance_checkins)**: 用户/项目/类型/经纬度/时间
- **代班组 (worker_groups)**: 班组长/成员/项目

### 6.4 关键流程
**现场打卡闭环**:
1. 班组长打开 APP → 选项目 → 进入围栏 → 上班打卡 (拍照)
2. 工人逐一打卡 (班组长可代打)
3. 下班 → 班组长统一收工打卡
4. 系统自动汇总 → 同步到考勤

---

## 7. V1.5 业主 H5 门户

### 7.1 业务场景
- 业主看不到工地进度,每周要跑来问
- 验收时无法回忆当时情况
- 投诉没证据

### 7.2 业务规则
| 规则 | 说明 |
|------|------|
| **入口** | 项目专属二维码 + 短信链接 |
| **权限** | 仅本项目相关数据,只读 |
| **内容** | 项目进度 + 工序验收 + 影像 + 巡检问题 + 产值 (脱敏) |
| **认证** | 项目编码 + 手机号 + 验证码 |
| **离线** | 关键数据支持离线缓存 |

### 7.3 业务对象
- **业主访问令牌 (owner_portal_tokens)**: 项目/手机/令牌/过期
- **业主访问日志 (owner_portal_logs)**: 谁/什么时候/看了什么
- **业主反馈 (owner_feedbacks)**: 项目/反馈内容/状态

---

## 8. 数据库 ER 图

> 详细 ER 图见 `docs/er/施工深化-ER-v1.0.svg` (待出)
> 这里给出文字版关系:

```
                    ┌──────────────────────┐
                    │   projects (现有)     │
                    └──────────┬───────────┘
                               │ 1:N
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
  process_instances     production_reports    project_geofences
  (工序实例)            (产值上报)            (项目围栏)
        │ 1:N                  │ 1:N                 │ 1:N
        ▼                      ▼                     ▼
  process_inspections  progress_payment_   attendance_checkins
  (工序报验)            _requests           (打卡记录)
        │ 1:N                  │
        ├─→ process_images    │
        ├─→ process_signatures│
        │                      │
        ▼                      ▼
  (公司网盘 - 复用)         finance_payments
                          (财务付款 - 复用)
                               ▲
                               │ 1:N
                          inspection_issues
                          (巡检问题派单)
                               ▲
                               │ N:1
                          inspections
                          (巡检单)
                               │ 1:N
                          inspection_results
                          (巡检明细)
                               ▲
                               │ N:1
                          inspection_items
                          (巡检项)
                               ▲
                               │ N:1
                          inspection_categories
                          (巡检分类)

        ┌──────────────────────────────────────┐
        │ 模板库 (独立,跨项目复用)               │
        ├─→ process_templates                 │
        │     process_template_items           │
        ├─→ inspection_categories             │
        │     inspection_items                 │
        └─→ project_contract_milestones       │
             (项目维度,合同自带)                │
        └──────────────────────────────────────┘

        ┌──────────────────────────────────────┐
        │ V1.5 业主门户                          │
        ├─→ owner_portal_tokens                │
        ├─→ owner_portal_logs                  │
        └─→ owner_feedbacks                    │
        └──────────────────────────────────────┘
```

---

## 9. 通用数据表 (8 张)

> 8 张通用配置表 + 8 个枚举常量,本节集中定义

### 9.1 枚举常量
```php
// app/Enums/ConstructionEnums.php (新建)
class ConstructionEnums {
  // 工序状态
  const PROCESS_STATUS_PENDING = 'pending';
  const PROCESS_STATUS_IN_PROGRESS = 'in_progress';
  const PROCESS_STATUS_INSPECTION = 'inspection';
  const PROCESS_STATUS_PASSED = 'passed';
  const PROCESS_STATUS_REJECTED = 'rejected';
  const PROCESS_STATUS_ARCHIVED = 'archived';

  // 影像类型
  const IMAGE_TYPE_PHOTO = 'photo';
  const IMAGE_TYPE_VIDEO = 'video';
  const IMAGE_TYPE_DRAWING = 'drawing';

  // 产值状态
  const PRODUCTION_STATUS_DRAFT = 'draft';
  const PRODUCTION_STATUS_SUBMITTED = 'submitted';
  const PRODUCTION_STATUS_APPROVED = 'approved';
  const PRODUCTION_STATUS_SETTLED = 'settled';
  const PRODUCTION_STATUS_REJECTED = 'rejected';

  // 巡检结果
  const INSPECTION_RESULT_PASS = 'pass';
  const INSPECTION_RESULT_FAIL = 'fail';
  const INSPECTION_RESULT_NA = 'na';

  // 巡检类型
  const INSPECTION_TYPE_SAFETY = 'safety';
  const INSPECTION_TYPE_QUALITY = 'quality';

  // 打卡类型
  const CHECKIN_TYPE_START = 'start';
  const CHECKIN_TYPE_END = 'end';
  const CHECKIN_TYPE_BREAK_START = 'break_start';
  const CHECKIN_TYPE_BREAK_END = 'break_end';
}
```

### 9.2 模板分类表
```php
// migration: 2026_07_01_000001_create_construction_templates_tables.php
Schema::create('construction_template_categories', function (Blueprint $table) {
    $table->id();
    $table->string('code', 50)->unique()->comment('分类编码:PROCESS/INSPECTION/...');
    $table->string('name', 100)->comment('分类名:工序模板/巡检模板');
    $table->string('industry', 50)->nullable()->comment('行业:综合布线/视频监控/门禁/...');
    $table->text('description')->nullable();
    $table->boolean('is_active')->default(true);
    $table->integer('sort_order')->default(0);
    $table->timestamps();

    $table->index(['code', 'industry']);
});
```

### 9.3 工序模板主表
```php
Schema::create('process_templates', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('category_id')->comment('分类ID');
    $table->string('code', 50)->comment('工序编码');
    $table->string('name', 200)->comment('工序名');
    $table->text('description')->nullable();
    $table->boolean('is_critical')->default(false)->comment('是否关键工序');
    $table->boolean('is_concealed')->default(false)->comment('是否隐蔽工程');
    $table->integer('min_photos')->default(0)->comment('最少照片数');
    $table->integer('min_videos')->default(0)->comment('最少视频数');
    $table->boolean('require_signature')->default(false)->comment('是否需电子签');
    $table->boolean('require_geofence')->default(false)->comment('是否需围栏内');
    $table->integer('estimated_hours')->default(0)->comment('预计工时');
    $table->integer('sort_order')->default(0);
    $table->boolean('is_active')->default(true);
    $table->timestamps();

    $table->unique(['category_id', 'code']);
    $table->index(['is_active', 'is_critical']);
});
```

### 9.4 工序模板子项
```php
Schema::create('process_template_items', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('template_id');
    $table->string('name', 200)->comment('检查项名');
    $table->text('standard')->nullable()->comment('合格标准');
    $table->boolean('required')->default(true);
    $table->integer('sort_order')->default(0);
    $table->timestamps();

    $table->index('template_id');
});
```

### 9.5 巡检分类表
```php
Schema::create('inspection_categories', function (Blueprint $table) {
    $table->id();
    $table->string('code', 50)->comment('SAFE/QULTY/MECH/ELEC...');
    $table->string('name', 100)->comment('安全/质量/机械/用电/...');
    $table->enum('type', ['safety', 'quality'])->comment('巡检类型');
    $table->text('description')->nullable();
    $table->boolean('is_active')->default(true);
    $table->integer('sort_order')->default(0);
    $table->timestamps();

    $table->unique(['type', 'code']);
});
```

### 9.6 巡检模板项
```php
Schema::create('inspection_items', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('category_id');
    $table->string('name', 200)->comment('检查项:安全帽佩戴/灭火器有效期');
    $table->text('standard')->nullable()->comment('合格标准');
    $table->integer('score')->default(10)->comment('分值');
    $table->boolean('is_must_check')->default(false)->comment('是否必检');
    $table->boolean('is_active')->default(true);
    $table->integer('sort_order')->default(0);
    $table->timestamps();

    $table->index(['category_id', 'is_active']);
});
```

### 9.7 系统配置表 (复用)
> 复用现有 `system_settings` 表,新增 key:
- `production_payment_triggers`: 进度款触发节点 JSON (默认 [30,60,90,95])
- `geofence_default_radius`: 围栏默认半径米 (默认 200)
- `image_max_size_mb`: 影像最大 MB (默认 50)
- `signature_expire_days`: 电子签链接有效期天 (默认 7)

### 9.8 字典表 (复用)
> 复用现有字典/枚举机制,在 `dict_items` 加:
- `construction_process_status` (工序状态)
- `production_report_status` (产值状态)
- `inspection_result` (巡检结果)

---

## 10. V1.1 工序验收数据表 (5 张)

### 10.1 工序实例表
```php
Schema::create('process_instances', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id')->comment('项目ID');
    $table->unsignedBigInteger('template_id')->comment('工序模板ID');
    $table->string('name', 200)->comment('实例名(可改)');
    $table->text('location_desc')->nullable()->comment('部位描述');
    $table->decimal('longitude', 10, 6)->nullable();
    $table->decimal('latitude', 10, 6)->nullable();
    $table->enum('status', [
        'pending', 'in_progress', 'inspection',
        'passed', 'rejected', 'archived'
    ])->default('pending');
    $table->unsignedBigInteger('foreman_id')->nullable()->comment('班组长');
    $table->unsignedBigInteger('worker_id')->nullable()->comment('施工员');
    $table->date('planned_start_date')->nullable();
    $table->date('planned_end_date')->nullable();
    $table->date('actual_start_date')->nullable();
    $table->date('actual_end_date')->nullable();
    $table->decimal('estimated_cost', 12, 2)->default(0);
    $table->decimal('actual_cost', 12, 2)->default(0);
    $table->text('remarks')->nullable();
    $table->timestamps();
    $table->softDeletes();

    $table->index(['project_id', 'status']);
    $table->index(['template_id']);
});
```

### 10.2 工序报验单
```php
Schema::create('process_inspections', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('process_instance_id');
    $table->string('inspection_no', 50)->unique()->comment('报验单号');
    $table->enum('status', [
        'draft', 'submitted', 'prechecked',
        'inspecting', 'passed', 'rejected', 'archived'
    ])->default('draft');
    $table->unsignedBigInteger('submitter_id')->comment('提交人');
    $table->timestamp('submitted_at')->nullable();
    $table->unsignedBigInteger('prechecker_id')->nullable()->comment('预检人');
    $table->timestamp('prechecked_at')->nullable();
    $table->text('precheck_remarks')->nullable();
    $table->unsignedBigInteger('inspector_id')->nullable()->comment('验收人');
    $table->timestamp('inspected_at')->nullable();
    $table->text('inspection_remarks')->nullable();
    $table->decimal('longitude', 10, 6)->nullable()->comment('验收时定位');
    $table->decimal('latitude', 10, 6)->nullable();
    $table->text('address')->nullable()->comment('反查地址');
    $table->integer('reject_count')->default(0)->comment('累计驳回次数');
    $table->timestamps();
    $table->softDeletes();

    $table->index(['process_instance_id', 'status']);
    $table->index('inspection_no');
});
```

### 10.3 工序影像表
```php
Schema::create('process_images', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('inspection_id')->nullable()->comment('关联报验单(可空=实例级)');
    $table->unsignedBigInteger('process_instance_id')->nullable();
    $table->string('file_path', 500)->comment('相对路径');
    $table->string('file_name', 200);
    $table->string('mime_type', 100);
    $table->bigInteger('file_size')->default(0);
    $table->enum('type', ['photo', 'video', 'drawing', 'document']);
    $table->string('category', 50)->default('process')->comment('process/before/after/hidden');
    $table->text('description')->nullable();
    $table->decimal('longitude', 10, 6)->nullable();
    $table->decimal('latitude', 10, 6)->nullable();
    $table->string('address')->nullable();
    $table->unsignedBigInteger('uploader_id');
    $table->timestamp('shot_at')->nullable()->comment('拍摄时间');
    $table->timestamps();
    $table->softDeletes();

    $table->index(['inspection_id', 'type']);
    $table->index(['process_instance_id', 'category']);
});
```

### 10.4 电子签名表
```php
Schema::create('process_signatures', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('inspection_id');
    $table->enum('role', ['owner', 'supervisor', 'contractor', 'worker', 'foreman']);
    $table->string('signer_name', 100)->comment('签字人姓名');
    $table->string('signer_phone', 20)->nullable();
    $table->string('signer_email', 100)->nullable();
    $table->string('signature_path', 500)->comment('手写签名图');
    $table->string('hash', 64)->comment('防篡改哈希: SHA256(签字图+时间戳+inspection_id)');
    $table->timestamp('signed_at');
    $table->string('ip_address', 45)->nullable();
    $table->string('user_agent', 500)->nullable();
    $table->decimal('longitude', 10, 6)->nullable();
    $table->decimal('latitude', 10, 6)->nullable();
    $table->timestamps();

    $table->index(['inspection_id', 'role']);
    $table->index('hash');
});
```

### 10.5 工序变更日志
```php
Schema::create('process_change_logs', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('process_instance_id');
    $table->unsignedBigInteger('inspection_id')->nullable();
    $table->unsignedBigInteger('user_id');
    $table->string('action', 50)->comment('submit/approve/reject/...');
    $table->json('from_value')->nullable();
    $table->json('to_value')->nullable();
    $table->text('remarks')->nullable();
    $table->timestamps();

    $table->index(['process_instance_id', 'created_at']);
});
```

---

## 11. V1.2 产值上报数据表 (4 张)

### 11.1 产值上报表
```php
Schema::create('production_reports', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->string('report_no', 50)->unique();
    $table->enum('report_type', ['daily', 'weekly', 'milestone']);
    $table->date('report_date')->comment('日报日期 / 周报开始日 / 节点日期');
    $table->date('period_end_date')->nullable()->comment('周报结束日');
    $table->decimal('completion_percent', 5, 2)->default(0)->comment('本期完成百分比');
    $table->decimal('cumulative_percent', 5, 2)->default(0)->comment('累计完成百分比');
    $table->decimal('labor_cost', 12, 2)->default(0)->comment('人工费');
    $table->decimal('material_cost', 12, 2)->default(0)->comment('材料费');
    $table->decimal('machine_cost', 12, 2)->default(0)->comment('机械费');
    $table->decimal('manage_cost', 12, 2)->default(0)->comment('管理费');
    $table->decimal('total_cost', 12, 2)->default(0)->comment('本期产值');
    $table->decimal('cumulative_cost', 12, 2)->default(0)->comment('累计产值');
    $table->text('description')->nullable();
    $table->enum('status', [
        'draft', 'submitted', 'approved', 'settled', 'rejected'
    ])->default('draft');
    $table->unsignedBigInteger('submitter_id');
    $table->timestamp('submitted_at')->nullable();
    $table->unsignedBigInteger('approver_id')->nullable();
    $table->timestamp('approved_at')->nullable();
    $table->text('approve_remarks')->nullable();
    $table->timestamps();
    $table->softDeletes();

    $table->index(['project_id', 'report_type', 'status']);
    $table->index(['report_date', 'status']);
});
```

### 11.2 项目产值汇总表
```php
Schema::create('project_production_summaries', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id')->unique();
    $table->decimal('contract_amount', 14, 2)->default(0)->comment('合同金额(冗余)');
    $table->decimal('total_completion_percent', 5, 2)->default(0);
    $table->decimal('total_labor_cost', 14, 2)->default(0);
    $table->decimal('total_material_cost', 14, 2)->default(0);
    $table->decimal('total_machine_cost', 14, 2)->default(0);
    $table->decimal('total_manage_cost', 14, 2)->default(0);
    $table->decimal('total_cost', 14, 2)->default(0)->comment('累计产值');
    $table->decimal('material_actual_cost', 14, 2)->default(0)->comment('物资实际成本(库存归集)');
    $table->decimal('vehicle_actual_cost', 14, 2)->default(0)->comment('车辆实际成本(车辆归集)');
    $table->decimal('labor_actual_cost', 14, 2)->default(0)->comment('人工实际成本(考勤归集)');
    $table->decimal('gross_profit', 14, 2)->default(0)->comment('毛利 = 累计产值 - 实际成本');
    $table->decimal('gross_profit_rate', 5, 2)->default(0)->comment('毛利率%');
    $table->timestamp('last_report_at')->nullable();
    $table->timestamps();

    $table->index('project_id');
});
```

### 11.3 合同节点表
```php
Schema::create('project_contract_milestones', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->string('name', 100)->comment('30% 预付款 / 60% 进度款 / ...');
    $table->decimal('milestone_percent', 5, 2)->comment('节点百分比');
    $table->decimal('milestone_amount', 14, 2)->comment('节点金额');
    $table->date('expected_date')->nullable()->comment('预计完成日');
    $table->date('actual_date')->nullable()->comment('实际完成日');
    $table->enum('status', [
        'pending', 'reached', 'requested', 'approved', 'paid', 'overdue'
    ])->default('pending');
    $table->unsignedBigInteger('payment_request_id')->nullable()->comment('关联付款申请');
    $table->text('remarks')->nullable();
    $table->integer('sort_order')->default(0);
    $table->timestamps();

    $table->index(['project_id', 'status']);
    $table->index(['milestone_percent']);
});
```

### 11.4 进度款申请表
```php
Schema::create('progress_payment_requests', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->unsignedBigInteger('milestone_id')->nullable()->comment('触发的合同节点');
    $table->unsignedBigInteger('production_report_id')->nullable()->comment('触发的产值上报');
    $table->string('request_no', 50)->unique();
    $table->decimal('request_amount', 14, 2)->comment('申请金额');
    $table->enum('trigger_type', ['milestone', 'manual', 'milestone_plus']);
    $table->enum('status', [
        'draft', 'submitted', 'manager_approved', 'finance_approved',
        'paid', 'rejected', 'cancelled'
    ])->default('draft');
    $table->unsignedBigInteger('submitter_id');
    $table->timestamp('submitted_at')->nullable();
    $table->unsignedBigInteger('manager_approver_id')->nullable();
    $table->timestamp('manager_approved_at')->nullable();
    $table->unsignedBigInteger('finance_approver_id')->nullable();
    $table->timestamp('finance_approved_at')->nullable();
    $table->text('remarks')->nullable();
    $table->timestamps();
    $table->softDeletes();

    $table->index(['project_id', 'status']);
    $table->index('request_no');
});
```

---

## 12. V1.3 巡检数据表 (5 张)

### 12.1 巡检单主表
```php
Schema::create('inspections', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->string('inspection_no', 50)->unique();
    $table->enum('type', ['safety', 'quality', 'comprehensive']);
    $table->string('title', 200);
    $table->date('inspection_date');
    $table->unsignedBigInteger('inspector_id')->comment('巡检人');
    $table->unsignedBigInteger('companion_id')->nullable()->comment('陪同人');
    $table->decimal('total_score', 6, 2)->default(0)->comment('实际得分');
    $table->decimal('full_score', 6, 2)->default(0)->comment('满分');
    $table->decimal('pass_rate', 5, 2)->default(0)->comment('合格率%');
    $table->integer('total_items')->default(0);
    $table->integer('pass_items')->default(0);
    $table->integer('fail_items')->default(0);
    $table->integer('recheck_count')->default(0)->comment('复检次数');
    $table->text('summary')->nullable();
    $table->enum('status', [
        'draft', 'in_progress', 'submitted', 'rechecking', 'closed', 'cancelled'
    ])->default('draft');
    $table->timestamp('submitted_at')->nullable();
    $table->timestamp('closed_at')->nullable();
    $table->timestamps();
    $table->softDeletes();

    $table->index(['project_id', 'type', 'status']);
    $table->index(['inspection_date']);
});
```

### 12.2 巡检明细
```php
Schema::create('inspection_results', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('inspection_id');
    $table->unsignedBigInteger('item_id')->comment('检查项ID');
    $table->enum('result', ['pass', 'fail', 'na'])->default('pass');
    $table->integer('score')->default(0)->comment('本项得分');
    $table->text('description')->nullable()->comment('问题描述');
    $table->string('location')->nullable()->comment('具体位置');
    $table->unsignedBigInteger('recheck_result_id')->nullable()->comment('复检结果ID');
    $table->boolean('is_issue')->default(false)->comment('是否产生工单');
    $table->unsignedBigInteger('work_order_id')->nullable()->comment('关联售后工单');
    $table->timestamps();

    $table->index(['inspection_id', 'result']);
    $table->index(['item_id', 'is_issue']);
});
```

### 12.3 巡检影像
```php
Schema::create('inspection_images', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('inspection_id');
    $table->unsignedBigInteger('result_id')->nullable()->comment('关联明细');
    $table->string('file_path', 500);
    $table->enum('type', ['photo', 'video']);
    $table->text('description')->nullable();
    $table->decimal('longitude', 10, 6)->nullable();
    $table->decimal('latitude', 10, 6)->nullable();
    $table->unsignedBigInteger('uploader_id');
    $table->timestamp('shot_at')->nullable();
    $table->timestamps();

    $table->index(['inspection_id', 'type']);
});
```

### 12.4 巡检问题派单
> 复用 `work_orders` (售后工单),不另建表
```php
// 在 work_orders 表加字段
Schema::table('work_orders', function (Blueprint $table) {
    $table->unsignedBigInteger('source_inspection_id')->nullable()->after('id');
    $table->string('source_type', 50)->default('customer')->after('source_inspection_id');
    // source_type 枚举: customer / inspection / self / ...
});
```

### 12.5 巡检模板关联 (中间表)
```php
Schema::create('inspection_templates', function (Blueprint $table) {
    $table->id();
    $table->string('name', 200);
    $table->enum('type', ['safety', 'quality', 'comprehensive']);
    $table->unsignedBigInteger('project_id')->nullable()->comment('NULL=全局模板');
    $table->text('description')->nullable();
    $table->boolean('is_active')->default(true);
    $table->timestamps();

    $table->index(['type', 'is_active']);
});

Schema::create('inspection_template_items', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('template_id');
    $table->unsignedBigInteger('category_id');
    $table->unsignedBigInteger('item_id');
    $table->boolean('is_must')->default(false);
    $table->integer('sort_order')->default(0);
    $table->timestamps();

    $table->index(['template_id', 'category_id']);
});
```

---

## 13. V1.4 打卡数据表 (3 张)

### 13.1 项目围栏表
```php
Schema::create('project_geofences', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id')->unique();
    $table->decimal('center_longitude', 10, 6)->comment('中心点经度');
    $table->decimal('center_latitude', 10, 6)->comment('中心点纬度');
    $table->integer('radius_meters')->default(200)->comment('半径米');
    $table->string('address')->nullable()->comment('中心点地址');
    $table->json('polygon')->nullable()->comment('可选:多边形围栏 [[[lng,lat],...]]');
    $table->boolean('is_active')->default(true);
    $table->timestamps();
});
```

### 13.2 打卡记录
```php
Schema::create('attendance_checkins', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('user_id');
    $table->unsignedBigInteger('project_id');
    $table->unsignedBigInteger('foreman_id')->nullable()->comment('班组长(代打时)');
    $table->enum('checkin_type', ['start', 'end', 'break_start', 'break_end']);
    $table->timestamp('checkin_at');
    $table->decimal('longitude', 10, 6);
    $table->decimal('latitude', 10, 6);
    $table->string('address')->nullable();
    $table->decimal('distance_to_center', 8, 2)->nullable()->comment('距围栏中心米');
    $table->boolean('is_in_geofence')->default(false)->comment('是否在围栏内');
    $table->string('photo_path', 500)->nullable()->comment('打卡拍照');
    $table->string('device_id', 100)->nullable();
    $table->string('ip_address', 45)->nullable();
    $table->unsignedBigInteger('attendance_record_id')->nullable()->comment('归集到的考勤记录');
    $table->boolean('is_synced_to_attendance')->default(false);
    $table->timestamp('synced_at')->nullable();
    $table->timestamps();

    $table->index(['user_id', 'checkin_at']);
    $table->index(['project_id', 'checkin_at']);
    $table->index(['attendance_record_id', 'is_synced_to_attendance']);
});
```

### 13.3 工班组表
```php
Schema::create('worker_groups', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->unsignedBigInteger('foreman_id')->comment('班组长');
    $table->string('name', 100)->comment('班组名:水电班/网线班/调试班');
    $table->text('description')->nullable();
    $table->date('start_date');
    $table->date('end_date')->nullable();
    $table->boolean('is_active')->default(true);
    $table->timestamps();

    $table->index(['project_id', 'is_active']);
});

Schema::create('worker_group_members', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('group_id');
    $table->unsignedBigInteger('worker_id')->comment('工人ID(users.id)');
    $table->date('join_date');
    $table->date('leave_date')->nullable();
    $table->boolean('is_active')->default(true);
    $table->timestamps();

    $table->index(['group_id', 'is_active']);
});
```

---

## 14. V1.5 业主门户数据表 (3 张)

### 14.1 业主访问令牌
```php
Schema::create('owner_portal_tokens', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->string('phone', 20)->comment('业主手机号');
    $table->string('token', 64)->unique()->comment('访问令牌');
    $table->enum('auth_type', ['sms', 'password', 'link']);
    $table->string('code_hash', 100)->nullable()->comment('验证码 hash');
    $table->timestamp('code_expires_at')->nullable();
    $table->timestamp('token_expires_at')->nullable();
    $table->timestamp('last_used_at')->nullable();
    $table->integer('access_count')->default(0);
    $table->boolean('is_active')->default(true);
    $table->timestamps();

    $table->index(['project_id', 'phone']);
    $table->index('token');
});
```

### 14.2 业主访问日志
```php
Schema::create('owner_portal_logs', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('token_id');
    $table->unsignedBigInteger('project_id');
    $table->string('phone', 20);
    $table->string('action', 50)->comment('view_progress/view_image/view_inspection');
    $table->string('resource_type', 50)->nullable();
    $table->unsignedBigInteger('resource_id')->nullable();
    $table->string('ip_address', 45)->nullable();
    $table->string('user_agent', 500)->nullable();
    $table->timestamp('accessed_at');

    $table->index(['token_id', 'accessed_at']);
    $table->index(['project_id', 'action']);
});
```

### 14.3 业主反馈
```php
Schema::create('owner_feedbacks', function (Blueprint $table) {
    $table->id();
    $table->unsignedBigInteger('project_id');
    $table->string('phone', 20);
    $table->string('name', 100)->nullable();
    $table->enum('type', ['suggestion', 'complaint', 'praise', 'question']);
    $table->string('title', 200);
    $table->text('content');
    $table->json('attachments')->nullable();
    $table->enum('status', [
        'pending', 'processing', 'resolved', 'closed', 'rejected'
    ])->default('pending');
    $table->unsignedBigInteger('handler_id')->nullable();
    $table->timestamp('handled_at')->nullable();
    $table->text('reply')->nullable();
    $table->timestamps();

    $table->index(['project_id', 'status']);
});
```

---

## 15. 路由清单 (总)

### V1.1 工序验收
```
# 模板
GET    /api/construction/templates              # 列表(分页+筛选)
GET    /api/construction/templates/{id}        # 详情
POST   /api/construction/templates             # 新建
PUT    /api/construction/templates/{id}        # 更新
DELETE /api/construction/templates/{id}        # 删除

# 工序实例
GET    /api/construction/processes             # 列表(按项目筛选)
POST   /api/construction/processes             # 创建实例
GET    /api/construction/processes/{id}        # 详情(含工序步骤+报验历史)
PUT    /api/construction/processes/{id}        # 更新
POST   /api/construction/processes/{id}/start  # 开工
POST   /api/construction/processes/{id}/finish # 完工

# 报验
GET    /api/construction/inspections           # 报验单列表
POST   /api/construction/inspections           # 提交报验
GET    /api/construction/inspections/{id}
PUT    /api/construction/inspections/{id}/precheck    # 预检
PUT    /api/construction/inspections/{id}/inspect     # 验收
PUT    /api/construction/inspections/{id}/reject      # 驳回
POST   /api/construction/inspections/{id}/archive     # 归档

# 影像
GET    /api/construction/images                # 影像列表(按项目/工序/报验)
POST   /api/construction/images                # 上传(支持分块)
DELETE /api/construction/images/{id}

# 电子签
POST   /api/construction/signatures            # 提交签名
GET    /api/construction/signatures/{id}       # 查看签名图
GET    /api/construction/sign-redirect/{token}  # 短信链接跳转(返回 H5 页面)

# 统计
GET    /api/construction/dashboard             # 施工总览
GET    /api/construction/project/{id}/progress # 单项目工序进度
```

### V1.2 产值上报
```
# 产值上报
GET    /api/production/reports
POST   /api/production/reports
GET    /api/production/reports/{id}
PUT    /api/production/reports/{id}
PUT    /api/production/reports/{id}/submit
PUT    /api/production/reports/{id}/approve
PUT    /api/production/reports/{id}/reject

# 项目产值汇总
GET    /api/production/projects/{id}/summary
GET    /api/production/dashboard               # 公司维度汇总

# 合同节点
GET    /api/contracts/{id}/milestones
POST   /api/contracts/{id}/milestones
PUT    /api/contracts/milestones/{id}

# 进度款
GET    /api/production/payment-requests
POST   /api/production/payment-requests
GET    /api/production/payment-requests/{id}
PUT    /api/production/payment-requests/{id}/approve-manager
PUT    /api/production/payment-requests/{id}/approve-finance
PUT    /api/production/payment-requests/{id}/mark-paid
```

### V1.3 巡检
```
# 巡检单
GET    /api/inspections
POST   /api/inspections
GET    /api/inspections/{id}
PUT    /api/inspections/{id}
POST   /api/inspections/{id}/submit
POST   /api/inspections/{id}/close

# 巡检明细
POST   /api/inspections/{id}/results           # 批量提交
GET    /api/inspections/{id}/results

# 巡检影像
POST   /api/inspections/{id}/images

# 巡检模板
GET    /api/inspections/templates
POST   /api/inspections/templates
PUT    /api/inspections/templates/{id}
GET    /api/inspections/categories             # 分类
GET    /api/inspections/items                 # 检查项
```

### V1.4 打卡
```
# 围栏
GET    /api/checkin/geofences
POST   /api/checkin/geofences
PUT    /api/checkin/geofences/{id}
GET    /api/checkin/geofences/{project_id}    # 项目维度

# 打卡
POST   /api/checkin/check                      # 打卡(参数:project_id, type, lng, lat, photo)
GET    /api/checkin/today                      # 今日打卡记录
GET    /api/checkin/recent                     # 最近打卡

# 工班组
GET    /api/checkin/worker-groups
POST   /api/checkin/worker-groups
PUT    /api/checkin/worker-groups/{id}
GET    /api/checkin/worker-groups/{id}/members
POST   /api/checkin/worker-groups/{id}/members

# 考勤归集 (定时任务)
POST   /api/checkin/sync-to-attendance         # 手动触发
```

### V1.5 业主门户
```
# 公开 API (无 token, 验证码)
POST   /api/owner-portal/request-code          # 请求验证码
POST   /api/owner-portal/verify                # 验证+获取 token
GET    /api/owner-portal/projects              # 业主项目列表
GET    /api/owner-portal/projects/{id}/progress  # 项目进度
GET    /api/owner-portal/projects/{id}/images    # 项目影像
GET    /api/owner-portal/projects/{id}/inspections

# 业主反馈
POST   /api/owner-portal/feedbacks
GET    /api/owner-portal/feedbacks
```

---

## 16. API 设计规范

### 16.1 通用响应格式
```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

### 16.2 错误码
| 码 | 含义 |
|----|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 业务冲突(如状态不允许) |
| 422 | 验证失败 |
| 500 | 服务器内部错误 |

### 16.3 分页
```json
{
  "current_page": 1,
  "per_page": 20,
  "total": 100,
  "data": [...]
}
```

### 16.4 文件上传
- 单文件最大 50MB(配置项)
- 支持断点续传(分块 5MB/块)
- 影像类型:jpg/png/mp4/mov
- 路径规则: `/uploads/construction/{year}/{month}/{uuid}.{ext}`

### 16.5 地理围栏距离计算
```php
// app/Helpers/GeoHelper.php
function geoDistance($lng1, $lat1, $lng2, $lat2) {
    $earthRadius = 6371000; // 米
    $latRad1 = deg2rad($lat1);
    $latRad2 = deg2rad($lat2);
    $latDiff = deg2rad($lat2 - $lat1);
    $lngDiff = deg2rad($lng2 - $lng1);

    $a = sin($latDiff / 2) * sin($latDiff / 2) +
         cos($latRad1) * cos($latRad2) *
         sin($lngDiff / 2) * sin($lngDiff / 2);
    $c = 2 * atan2(sqrt($a), sqrt(1 - $a));
    return $earthRadius * $c; // 米
}
```

---

## 17. 前端页面清单

### 17.1 PC 端新页面 (14 个)

| 路径 | 页面名 | 模块 |
|------|--------|------|
| `/construction/templates` | 工序模板管理 | V1.1 |
| `/construction/processes` | 工序实例列表 | V1.1 |
| `/construction/processes/:id` | 工序详情(含报验/影像/签字) | V1.1 |
| `/construction/inspections` | 报验单列表 | V1.1 |
| `/construction/inspections/:id` | 报验单详情 | V1.1 |
| `/production/reports` | 产值上报列表 | V1.2 |
| `/production/reports/new` | 产值上报表单 | V1.2 |
| `/production/reports/:id` | 产值详情 | V1.2 |
| `/production/payment-requests` | 进度款申请列表 | V1.2 |
| `/production/contracts` | 合同节点管理 | V1.2 |
| `/inspections` | 巡检单列表 | V1.3 |
| `/inspections/new` | 发起巡检 | V1.3 |
| `/inspections/:id` | 巡检详情(checklist) | V1.3 |
| `/checkin/dashboard` | 现场打卡看板 | V1.4 |

### 17.2 PC 端组件 (12 个)
- `ProcessTimeline.vue` - 工序时间轴
- `ProcessInspectionForm.vue` - 报验单表单
- `ImageUploader.vue` - 影像上传(支持水印)
- `ImageGallery.vue` - 影像画廊(4 级树)
- `SignaturePad.vue` - H5 手写板
- `SignatureViewer.vue` - 签名查看
- `ProductionReportForm.vue` - 产值上报表单
- `ProductionChart.vue` - 产值图表
- `PaymentRequestCard.vue` - 进度款卡片
- `InspectionChecklist.vue` - checklist 组件
- `InspectionHeatmap.vue` - 巡检热力图
- `GeofenceMap.vue` - 围栏地图(高德/百度)

### 17.3 V1.5 业主 H5 页面 (5 个)
- `/owner/login` - 业主登录
- `/owner/projects` - 我的项目
- `/owner/progress` - 进度查看
- `/owner/gallery` - 影像画廊
- `/owner/feedback` - 我的反馈

---

## 18. 与现有模块的集成点

### 18.1 项目管理
| 集成点 | 说明 |
|--------|------|
| `projects.id` | 工序实例/产值/巡检/打卡全部关联 |
| `projects.contract_amount` | 产值汇总冗余合同金额 |
| `projects.stage` | 工序状态联动项目阶段 |

### 18.2 售后工单 (复用)
```php
// 巡检不合格 → 售后工单
WorkOrder::create([
    'source_type' => 'inspection',
    'source_inspection_id' => $inspection->id,
    'project_id' => $inspection->project_id,
    'type' => 'rework',  // 整改
    ...
]);
```

### 18.3 财务模块 (复用)
```php
// 进度款 → 财务付款
FinancePayment::create([
    'source_type' => 'progress_payment',
    'source_id' => $request->id,
    'project_id' => $request->project_id,
    'amount' => $request->request_amount,
    ...
]);
```

### 18.4 库存模块 (复用)
```php
// 物资出库 → 项目实际成本归集
$materialCost = InventoryOutbound::where('project_id', $projectId)
    ->whereBetween('outbound_date', [$start, $end])
    ->sum('total_amount');
```

### 18.5 考勤模块 (复用)
```php
// 打卡记录 → 考勤记录
$attendance = AttendanceRecord::create([
    'user_id' => $checkin->user_id,
    'project_id' => $checkin->project_id,
    'check_in_at' => $checkin->start_time,
    'check_out_at' => $checkin->end_time,
    'source' => 'checkin',
]);
```

### 18.6 公司网盘 (复用)
```php
// 影像归档
NetdiskFile::create([
    'folder_path' => "/projects/{$projectId}/processes/{$processId}",
    'file_path' => $image->file_path,
    'source_type' => 'construction',
    'source_id' => $image->id,
]);
```

### 18.7 消息中心 (复用)
```php
// 工序报验通知
Message::create([
    'type' => 'process_inspection',
    'title' => "{$project->name} - {$process->name} 待验收",
    'target_user_id' => $inspector->id,
    'link_url' => "/construction/inspections/{$id}",
]);
```

---

## 19. 部署与回滚方案

### 19.1 部署顺序
```
1. 备份当前 pc-api + pc-web
2. 上传 migration 文件 (28 个)
3. 运行 migration (一次性)
4. 初始化模板数据 (工序/巡检 seeder)
5. 上传 controller (15 个)
6. 上传 model (10 个)
7. 上传 frontend (14 页面 + 12 组件)
8. route:clear + optimize
9. 前端 build + 部署
10. php-fpm restart
11. 端到端冒烟测试
```

### 19.2 初始化数据 (Seeder)
```php
// database/seeders/ConstructionTemplateSeeder.php
- 5 大行业 × 各 15-25 个工序
- 8 大巡检分类 × 各 8-12 个检查项
- 5 套预置巡检模板 (安全/质量/综合)
- 3 套预置工序模板 (弱电/安防/智能)
```

### 19.3 回滚方案
```bash
# 回滚 migration (只回滚本次新增的 28 张)
cd /var/www/oa-api
php artisan migrate:rollback --step=28

# 回滚代码
cp -r .workbuddy/backups/v0.3.7.9/* pc-api/
php artisan route:clear
systemctl restart php8.3-fpm

# 回滚前端
cp -r .workbuddy/backups/v0.3.7.9/web/* pc-web/dist/
nginx -s reload
```

---

## 20. 验收标准

### 20.1 功能验收
- [ ] V1.1: 5 大行业工序模板可维护
- [ ] V1.1: 工序报验可强制 ≥ 3 张图 + 1 视频 + 定位
- [ ] V1.1: 三方电子签可正常生成 + 防篡改
- [ ] V1.2: 产值上报累计完成 = 30% 自动触发进度款申请
- [ ] V1.2: 进度款走完审批后自动入账
- [ ] V1.3: 巡检不合格自动创建售后工单
- [ ] V1.3: 整改闭环 5 步流程可走完
- [ ] V1.4: 围栏外打卡拒绝 + 报警
- [ ] V1.4: 打卡数据自动归集到考勤
- [ ] V1.5: 业主扫码可看项目进度 + 影像

### 20.2 性能验收
- [ ] 影像上传 50MB ≤ 10 秒 (千兆网)
- [ ] 报验单列表 1000 条 ≤ 1 秒
- [ ] 产值汇总 100 项目 ≤ 2 秒
- [ ] 围栏判断 ≤ 50ms

### 20.3 安全验收
- [ ] 影像访问权限严格控制
- [ ] 电子签 hash 不可伪造
- [ ] 业主门户 token 过期不可用
- [ ] 业主反馈脱敏(隐藏成本/利润)

### 20.4 兼容性验收
- [ ] Chrome 90+ / Edge 90+
- [ ] PC 端 1280px+ / Pad 1024px
- [ ] 影像支持主流格式 (jpg/png/mp4/mov)

---

## 附录 A: 与现有 v0.3.7.x 兼容性说明

| 现有模块 | 影响 | 处理方式 |
|----------|------|----------|
| `work_orders` 表 | 加 2 个字段 | 增量 migration |
| `projects` 表 | 不动 | 0 影响 |
| `processes` (旧工序) | 保留 + 迁移到 `process_instances` | 数据迁移脚本 |
| `users` 表 | 0 影响 | - |
| 路由文件 | 新增 60+ 路由 | 不影响现有 |
| 权限 | 加新模块权限 | 复用 RBAC |

## 附录 B: 待确认事项 (TODO)

- [ ] 影像存储:本地服务器路径 vs MinIO
- [ ] 地图服务:高德/百度/腾讯
- [ ] 短信平台:阿里云/腾讯云 (待选型)
- [ ] 业主门户是否要独立的子域名
- [ ] 班组长 APP 是 Flutter 还是 uni-app

---

**文档结束。共 20 章, 28 张新表, 60+ API 端点, 14 个前端页面, 12 个组件。**
