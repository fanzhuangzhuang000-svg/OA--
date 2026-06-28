# GitHub Secrets 配置指南

> 安防运维OA系统 — CI/CD 自动化部署所需 Secrets 配置说明

---

## 目录

1. [概述](#概述)
2. [Secrets 清单](#secrets-清单)
3. [配置步骤（图文说明）](#配置步骤)
4. [每个 Secret 详细说明](#每个-secret-详细说明)
5. [验证配置](#验证配置)
6. [安全注意事项](#安全注意事项)
7. [故障排查](#故障排查)

---

## 概述

GitHub Secrets 用于在 CI/CD 流水线中安全存储敏感信息（如 SSH 密钥、数据库密码等）。这些值在 Actions 日志中会被自动遮盖，不会泄露。

本项目的自动化部署需要配置以下 **7 个 Secrets**：

---

## Secrets 清单

| # | Secret 名称 | 用途 | 必填 |
|---|-------------|------|:----:|
| 1 | `SSH_PRIVATE_KEY` | 服务器 SSH 私钥，用于远程部署 | ✅ |
| 2 | `SSH_HOST` | 目标服务器 IP 或域名 | ✅ |
| 3 | `SSH_USER` | SSH 登录用户名 | ✅ |
| 4 | `DB_DATABASE` | PostgreSQL 数据库名 | ✅ |
| 5 | `DB_USERNAME` | 数据库用户名 | ✅ |
| 6 | `DB_PASSWORD` | 数据库密码 | ✅ |
| 7 | `APP_KEY` | Laravel 应用加密密钥 | ✅ |

---

## 配置步骤

### 步骤 1：进入仓库 Settings

1. 打开仓库页面：https://github.com/fanzhuangzhuang000-svg/OA--
2. 点击顶部导航栏 **Settings**
3. 左侧菜单找到 **Secrets and variables** → **Actions**

### 步骤 2：添加 Secret

1. 点击 **New repository secret** 按钮
2. 在 **Name** 输入框填写 Secret 名称（如 `SSH_PRIVATE_KEY`）
3. 在 **Secret** 输入框填写对应的值
4. 点击 **Add secret** 保存

### 步骤 3：重复操作

对以下所有 7 个 Secret 重复步骤 2。

> 💡 **提示**：可以使用 GitHub CLI 批量添加（见下方 [CLI 方式](#cli-方式批量添加)）

---

## 每个 Secret 详细说明

### 1. `SSH_PRIVATE_KEY`

| 项目 | 说明 |
|------|------|
| **用途** | CI/CD 流水线通过 SSH 连接目标服务器执行部署脚本 |
| **格式** | OpenSSH 格式的完整私钥（含 `-----BEGIN OPENSSH PRIVATE KEY-----` 头尾） |
| **获取方式** | 见下方 [生成 SSH 密钥对](#生成-ssh-密钥对) |

**⚠️ 注意事项：**
- 复制时确保包含完整的头尾标记，不要有多余空格或换行
- 私钥如果有 passphrase，需要一并提供或使用无密码的密钥

---

### 2. `SSH_HOST`

| 项目 | 说明 |
|------|------|
| **用途** | 指定部署目标服务器地址 |
| **格式** | IP 地址或域名 |
| **示例值** | `172.20.0.139` 或 `afjsw.cn` |
| **获取方式** | 服务器管理员提供，或从云服务商控制台获取 |

**⚠️ 注意事项：**
- 确保 GitHub Actions Runner 能访问该地址（防火墙/安全组放行 SSH 端口 22）
- 如果使用域名，确保 DNS 解析正确

---

### 3. `SSH_USER`

| 项目 | 说明 |
|------|------|
| **用途** | SSH 登录服务器的用户名 |
| **格式** | 普通用户名字符串 |
| **示例值** | `root` 或 `deploy` |
| **获取方式** | 服务器管理员提供 |

**⚠️ 注意事项：**
- 推荐使用专用部署账号（非 root），通过 sudo 授权
- 确保该用户有权限操作项目目录和 Docker

---

### 4. `DB_DATABASE`

| 项目 | 说明 |
|------|------|
| **用途** | Laravel 应用连接的 PostgreSQL 数据库名 |
| **格式** | 数据库名称字符串 |
| **默认值** | `oa_security`（参考 `.env.docker`） |
| **获取方式** | 数据库管理员创建，或自行创建：`CREATE DATABASE oa_security;` |

---

### 5. `DB_USERNAME`

| 项目 | 说明 |
|------|------|
| **用途** | 数据库连接用户名 |
| **格式** | 用户名字符串 |
| **默认值** | `oa_user`（参考 `.env.docker`） |
| **获取方式** | 数据库管理员创建，或自行创建：`CREATE USER oa_user WITH PASSWORD 'xxx';` |

---

### 6. `DB_PASSWORD`

| 项目 | 说明 |
|------|------|
| **用途** | 数据库连接密码 |
| **格式** | 密码字符串 |
| **默认值** | `oa_secret_2024`（仅开发环境，生产环境必须更换强密码） |
| **获取方式** | 在创建数据库用户时设定 |

**⚠️ 安全要求：**
- 生产环境必须使用强密码（≥16位，含大小写字母、数字、特殊字符）
- 禁止使用 `.env.docker` 中的默认密码

---

### 7. `APP_KEY`

| 项目 | 说明 |
|------|------|
| **用途** | Laravel 应用加密密钥，用于加密 session、cookie、密码重置令牌等 |
| **格式** | `base64:` 开头的 32 字节 base64 编码字符串 |
| **示例值** | `base64:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=` |
| **获取方式** | 见下方 [生成 APP_KEY](#生成-app_key) |

---

## 辅助操作

### 生成 SSH 密钥对

```bash
# 在本地机器执行（或服务器上）
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key -N ""

# 查看私钥（复制此内容作为 SSH_PRIVATE_KEY）
cat ~/.ssh/deploy_key

# 将公钥添加到目标服务器的授权列表
ssh-copy-id -i ~/.ssh/deploy_key.pub user@172.20.0.139

# 或手动追加到服务器
cat ~/.ssh/deploy_key.pub | ssh user@172.20.0.139 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

**在服务器上验证连通性：**
```bash
ssh -i ~/.ssh/deploy_key user@172.20.0.139 "echo 'SSH OK'"
```

---

### 生成 APP_KEY

```bash
# 方式 1：在 Laravel 项目目录下执行
php artisan key:generate --show

# 方式 2：使用 PHP 直接生成
php -r "echo 'base64:' . base64_encode(random_bytes(32)) . PHP_EOL;"

# 方式 3：使用 OpenSSL
echo "base64:$(openssl rand -base64 32)"
```

---

### CLI 方式（批量添加）

使用 [GitHub CLI](https://cli.github.com/) 可以快速批量添加 Secrets：

```bash
# 安装 GitHub CLI（Windows）
winget install GitHub.cli

# 登录
gh auth login

# 在仓库目录下逐个添加
cd ~/OA--

gh secret set SSH_PRIVATE_KEY < ~/.ssh/deploy_key
gh secret set SSH_HOST --body "172.20.0.139"
gh secret set SSH_USER --body "root"
gh secret set DB_DATABASE --body "oa_security"
gh secret set DB_USERNAME --body "oa_user"
gh secret set DB_PASSWORD --body "your-strong-password"
gh secret set APP_KEY --body "base64:your-generated-key"
```

**验证所有 Secrets 已添加：**
```bash
gh secret list
```

预期输出：
```
NAME              UPDATED
SSH_PRIVATE_KEY   2024-xx-xxTxx:xx:xxZ
SSH_HOST          2024-xx-xxTxx:xx:xxZ
SSH_USER          2024-xx-xxTxx:xx:xxZ
DB_DATABASE       2024-xx-xxTxx:xx:xxZ
DB_USERNAME       2024-xx-xxTxx:xx:xxZ
DB_PASSWORD       2024-xx-xxTxx:xx:xxZ
APP_KEY           2024-xx-xxTxx:xx:xxZ
```

---

## 验证配置

配置完成后，可以通过以下方式验证：

### 方法 1：创建测试 Workflow

在 `.github/workflows/test-secrets.yml` 中添加：

```yaml
name: Test Secrets
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Verify secrets exist
        run: |
          echo "SSH_HOST is set: ${{ secrets.SSH_HOST != '' }}"
          echo "SSH_USER is set: ${{ secrets.SSH_USER != '' }}"
          echo "DB_DATABASE is set: ${{ secrets.DB_DATABASE != '' }}"
          echo "DB_USERNAME is set: ${{ secrets.DB_USERNAME != '' }}"
          echo "SSH_PRIVATE_KEY length: ${{ length(secrets.SSH_PRIVATE_KEY) }}"
          echo "APP_KEY is set: ${{ secrets.APP_KEY != '' }}"
          # 注意：不要 echo 密码和密钥的实际值
```

### 方法 2：实际部署测试

触发一次完整部署流水线，观察是否能成功 SSH 连接并部署。

---

## 安全注意事项

| 规则 | 说明 |
|------|------|
| 🔒 最小权限 | SSH 用户仅授予部署所需权限，避免使用 root |
| 🔄 定期轮换 | 每 90 天轮换一次 SSH 密钥和数据库密码 |
| 📋 审计日志 | GitHub 会记录 Secret 的更新操作，定期检查 |
| 🚫 禁止硬编码 | 永远不要在代码或 Workflow 文件中明文写入密码 |
| 🔐 强密码 | 数据库密码至少 16 位，包含大小写、数字、特殊字符 |
| 👥 限制访问 | 仅仓库管理员可以查看/修改 Secrets |

---

## 故障排查

### SSH 连接失败

```
Permission denied (publickey,password)
```

**排查步骤：**
```bash
# 1. 验证公钥已添加到服务器
ssh -i deploy_key -o StrictHostKeyChecking=no user@172.20.0.139 "whoami"

# 2. 检查服务器 SSH 配置
# /etc/ssh/sshd_config 需要：
#   PubkeyAuthentication yes
#   AuthorizedKeysFile .ssh/authorized_keys

# 3. 检查文件权限（服务器上）
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 数据库连接失败

```
SQLSTATE[08006] Connection refused
```

**排查步骤：**
1. 确认数据库服务正在运行
2. 确认 PostgreSQL 监听地址包含部署服务器 IP
3. 检查 `pg_hba.conf` 允许远程连接
4. 确认防火墙放行 PostgreSQL 端口（默认 5432）

### APP_KEY 错误

```
No application encryption key has been specified.
```

**解决方式：**
```bash
# 确保 APP_KEY 格式正确（base64: 开头）
# 重新生成并更新 Secret
php artisan key:generate --show
```

---

## 参考链接

- [GitHub Actions Secrets 文档](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-for-github-actions/using-secrets-in-github-actions)
- [GitHub CLI Secret 管理](https://cli.github.com/manual/gh_secret)
- [Laravel 环境配置](https://laravel.com/docs/11.x/configuration)
- [PostgreSQL 远程连接配置](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

---

> 📅 最后更新：2024-06
> 
> 维护者：DevOps Team
