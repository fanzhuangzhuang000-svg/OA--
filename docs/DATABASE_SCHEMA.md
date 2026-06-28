# 数据库 ERD 文档

## 表结构概览

| 序号 | 表名 | 说明 |
|------|------|------|
| 1 | users | 用户表 |
| 2 | roles | 角色表 |
| 3 | permissions | 权限表 |
| 4 | model_has_roles | 用户角色关联表 |
| 5 | role_has_permissions | 角色权限关联表 |
| 6 | personal_access_tokens | API Token 表 |
| 7 | departments | 部门表 |
| 8 | positions | 职位表 |
| 9 | employees | 员工表 |
| 10 | attendance_records | 考勤记录表 |
| 11 | customers | 客户表 |
| 12 | opportunities | 商机表 |
| 13 | projects | 项目表 |
| 14 | project_budgets | 项目预算表 |
| 15 | purchase_orders | 采购订单表 |
| 16 | inventory_items | 库存商品表 |
| 17 | stock_records | 库存变动记录表 |
| 18 | finance_accounts | 财务账户表 |
| 19 | receivables | 应收账款表 |
| 20 | payables | 应付账款表 |
| 21 | service_orders | 服务工单表 |
| 22 | repair_orders | 维修订单表 |
| 23 | vehicles | 车辆表 |
| 24 | warranties | 质保表 |
| 25 | suppliers | 供应商表 |
| 26 | approvals | 审批记录表 |
| 27 | system_logs | 系统日志表 |
| 28 | system_settings | 系统设置表 |
| 29 | knowledge_entries | 知识库条目表 |
| 30 | disk_files | 网盘文件表 |

## ERD 图



## 主要关系说明

1. **用户与角色**: 一个用户可以有多个角色 (Many-to-Many)
2. **角色与权限**: 一个角色可以有多个权限 (Many-to-Many)
3. **客户与项目**: 一个客户可以有多个项目 (One-to-Many)
4. **项目与预算**: 一个项目可以有多个预算项 (One-to-Many)
5. **库存与记录**: 一个库存商品有多条变动记录 (One-to-Many)
6. **供应商与采购**: 一个供应商可以提供多个采购订单 (One-to-Many)

---

*本文档由系统自动生成，最后更新时间: 2026-06-28*

