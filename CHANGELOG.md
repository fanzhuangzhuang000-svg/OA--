# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.1] - 2026-06-28

### 🔒 Security
- 修复密码变更未 Hash 漏洞
- 设置 Token 过期时间 (24 小时)
- 关闭 APP_DEBUG
- 收紧 CORS 配置
- 清理 Sanctum Stateful domains

### 🐛 Bug Fixes
- 修复 model_has_roles 表缺失列导致的 403 错误
- 修复权限同步问题
- 修复 artisan 命令失败问题

### ⚡ Performance
- 优化 PostgreSQL 配置 (shared_buffers=256MB, work_mem=16MB)
- 优化 Redis 配置 (maxmemory=256MB)
- 修复 Redis 配置冲突

### 🛠️ Refactor
- 拆分聚合 Model 文件
- 创建 Form Request 验证类
- 创建 API Resource 类

### 📚 Documentation
- 生成 API 接口文档
- 生成数据库 ERD 文档
- 生成架构设计文档
- 补充代码注释

### 🚀 Features
- 添加自动备份脚本
- 添加容器健康检查
- 配置 Nginx Gzip 压缩

## [v1.0.0] - 2026-06-25

### Initial Release
- 安防运维 OA 综合管理平台
- 覆盖 CRM、项目管理、采购、施工、维修、库存、财务、HR 等 15+ 业务模块
- 基于 Laravel 11 + Vue3 + PostgreSQL 15
- Docker 容器化部署

