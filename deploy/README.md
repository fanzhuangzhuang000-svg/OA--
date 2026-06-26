# deploy/

> 统一部署入口。前任的 80+ 个 fix_*/step*/deploy_v* 脚本已归档到 [`_archive/`](./_archive/)（保留不删，便于回查前任的踩坑过程）。

## 用法

```powershell
cd D:\work\website\OA
python deploy/deploy.py <子命令> [参数]
```

## 子命令

| 命令 | 说明 | 调用的脚本 |
|---|---|---|
| `web` | 部署前端 (build + sftp) | `.workbuddy/deploy_web.py` |
| `api` | 显示后端部署步骤（首次用 `deploy_full.sh`） | - |
| `full` | 全栈部署 (web + api 提示) | `.workbuddy/deploy_web.py` |
| `status` | 服务器状态总览 | `.workbuddy/ssh.py` |
| `health` | 41 端点自动化回归 | `.workbuddy/regression.py` |
| `backup [TAG]` | 全量备份到本地 | `.workbuddy/backup_full.py` |
| `shell` | 交互式 SSH 进服务器 | paramiko |

## 典型流程

```powershell
# 1. 改完代码
python deploy/deploy.py web        # 部署前端
python deploy/deploy.py api        # 提示步骤 (SSH 进服务器手动操作)
python deploy/deploy.py health     # 跑 41 端点回归
python deploy/deploy.py backup     # 备份
```

## 历史

2026-06-16 重构：80+ 散落脚本统一归到 `deploy.py` 一处入口。
