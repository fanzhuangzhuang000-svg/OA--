# API 接口文档

## 认证相关

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/logout | 用户登出 |
| GET | /api/auth/userinfo | 获取当前用户信息 |
| POST | /api/auth/change-password | 修改密码 |

## 系统监控

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/admin/monitor/backups | 备份列表 |
| GET | /api/admin/monitor/db | 数据库状态 |
| GET | /api/admin/monitor/disk | 磁盘状态 |
| GET | /api/admin/monitor/errors | 错误日志 |
| GET | /api/admin/monitor/metrics | 系统指标 |
| GET | /api/admin/monitor/services | 服务状态 |

## 员工管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/employees | 员工列表 |
| POST | /api/employees | 创建员工 |
| GET | /api/employees/{id} | 员工详情 |
| PUT | /api/employees/{id} | 更新员工 |
| DELETE | /api/employees/{id} | 删除员工 |

## 考勤管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/attendance/clock-in | 签到 |
| POST | /api/attendance/clock-out | 签退 |
| GET | /api/attendance/records | 考勤记录 |
| POST | /api/attendance/leave | 请假申请 |
| POST | /api/attendance/overtime | 加班申请 |

## 客户管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/customers | 客户列表 |
| POST | /api/customers | 创建客户 |
| GET | /api/customers/{id} | 客户详情 |
| PUT | /api/customers/{id} | 更新客户 |
| DELETE | /api/customers/{id} | 删除客户 |

## 项目管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/projects | 项目列表 |
| POST | /api/projects | 创建项目 |
| GET | /api/projects/{id} | 项目详情 |
| PUT | /api/projects/{id} | 更新项目 |
| DELETE | /api/projects/{id} | 删除项目 |

## 采购管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/purchases | 采购列表 |
| POST | /api/purchases | 创建采购 |
| GET | /api/purchases/{id} | 采购详情 |
| PUT | /api/purchases/{id} | 更新采购 |
| DELETE | /api/purchases/{id} | 删除采购 |

## 库存管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/inventory | 库存列表 |
| POST | /api/inventory | 创建库存 |
| GET | /api/inventory/{id} | 库存详情 |
| PUT | /api/inventory/{id} | 更新库存 |
| DELETE | /api/inventory/{id} | 删除库存 |

## 财务管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/finance | 财务列表 |
| POST | /api/finance | 创建财务记录 |
| GET | /api/finance/{id} | 财务详情 |
| PUT | /api/finance/{id} | 更新财务记录 |
| DELETE | /api/finance/{id} | 删除财务记录 |

## 售后维修

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/service | 服务工单列表 |
| POST | /api/service | 创建服务工单 |
| GET | /api/service/{id} | 服务工单详情 |
| PUT | /api/service/{id} | 更新服务工单 |
| DELETE | /api/service/{id} | 删除服务工单 |

## 车辆管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/vehicles | 车辆列表 |
| POST | /api/vehicles | 创建车辆 |
| GET | /api/vehicles/{id} | 车辆详情 |
| PUT | /api/vehicles/{id} | 更新车辆 |
| DELETE | /api/vehicles/{id} | 删除车辆 |

## 供应商管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/suppliers | 供应商列表 |
| POST | /api/suppliers | 创建供应商 |
| GET | /api/suppliers/{id} | 供应商详情 |
| PUT | /api/suppliers/{id} | 更新供应商 |
| DELETE | /api/suppliers/{id} | 删除供应商 |

## 审批中心

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/approvals | 审批列表 |
| POST | /api/approvals/{id}/approve | 审批通过 |
| POST | /api/approvals/{id}/reject | 审批驳回 |

## 系统设置

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/settings | 系统设置列表 |
| PUT | /api/settings/{id} | 更新系统设置 |
| POST | /api/settings/backup | 数据备份 |
| GET | /api/roles | 角色列表 |
| POST | /api/roles | 创建角色 |
| PUT | /api/roles/{id} | 更新角色 |
| DELETE | /api/roles/{id} | 删除角色 |

## 权限管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/permissions | 权限列表 |
| POST | /api/permissions | 创建权限 |
| PUT | /api/permissions/{id} | 更新权限 |
| DELETE | /api/permissions/{id} | 删除权限 |
| GET | /api/permissions/my | 当前用户权限 |

## 报表统计

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/dashboard/stats | 仪表盘统计数据 |
| GET | /api/reports/attendance | 考勤报表 |
| GET | /api/reports/finance | 财务报表 |
| GET | /api/reports/inventory | 库存报表 |

## 文件管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/files/upload | 文件上传 |
| GET | /api/files/{id} | 文件下载 |
| DELETE | /api/files/{id} | 文件删除 |

## 消息中心

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/messages | 消息列表 |
| PUT | /api/messages/{id}/read | 标记已读 |
| DELETE | /api/messages/{id} | 删除消息 |

## 知识库

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/knowledge | 知识库列表 |
| POST | /api/knowledge | 创建知识条目 |
| GET | /api/knowledge/{id} | 知识条目详情 |
| PUT | /api/knowledge/{id} | 更新知识条目 |
| DELETE | /api/knowledge/{id} | 删除知识条目 |

## 网盘

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/disk/files | 文件列表 |
| POST | /api/disk/upload | 文件上传 |
| GET | /api/disk/{id} | 文件下载 |
| DELETE | /api/disk/{id} | 文件删除 |

---

*本文档由系统自动生成，最后更新时间: 2026-06-28*

