# 备份清单: v0.6.0-20260625_2022

## Git 状态
- **Commit**: `6e0a5f3b1eda67164d951f0fc0a2b29e94a6bf29 feat(tender): 招标中心 V0.6.0 Sprint 1 (后端 API + 4 张新表)`
- **Branch**: `main`
- **Tags on HEAD**: `v0.6.0`
- **Total commits**: 48
- **Uncommitted**: M pc-web/src/router/index.ts
?? .workbuddy/_add_contact_deleted.png
?? .workbuddy/_add_contact_filled.png
?? .workbuddy/_add_contact_saved.png
?? .workbuddy/_edit_cust_after_save.png
?? .workbuddy/_edit_cust_detail.png
?? .workbuddy/_edit_cust_detail_after.png
?? .workbuddy/_edit_cust_dialog_filled.png
?? .workbuddy/_edit_cust_dialog_open.png
?? .workbuddy/_edit_cust_list.png
?? .workbuddy/_edit_cust_login_filled.png
?? .workbuddy/_grep_customer_path.py
?? .workbuddy/_invoice_filled1.png
?? .workbuddy/_invoice_filled2.png
?? .workbuddy/_invoice_mark_deleted.png
?? .workbuddy/_invoice_saved.png
?? .workbuddy/_probe_supplier.py
?? .workbuddy/_verify_edit_customer.py
?? .workbuddy/_verify_login.png
?? .workbuddy/_verify_login_filled.png
?? .workbuddy/_verify_onboard_step0.png
?? .workbuddy/_verify_onboard_step1.png
?? .workbuddy/_verify_onboard_step1_filled.png
?? .workbuddy/_verify_onboard_step2.png
?? .workbuddy/_verify_onboard_step2_filled.png
?? .workbuddy/_verify_onboard_step3.png
?? .workbuddy/backup_local.py
?? .workbuddy/node_modules/
?? pc-web/src/api/portal-tender.ts
?? pc-web/src/api/tender.ts
?? pc-web/src/views/business/
?? pc-web/src/views/external-quote/components/ProductPickerDialog.vue
?? pc-web/src/views/portal/tender/

## 内容
| 模块 | 文件数 | 大小 |
|---|---|---|
| pc-api | 416 | 2.0MB |
| pc-web | 432 | 3.6MB |
| pc-desktop | 5 | 3.0KB |
| mobile-app | 0 | 0.0B |
| mp-miniapp | 0 | 0.0B |
| deploy | 105 | 781.1KB |
| docs | 3 | 75.9KB |
| README.md | 1 | 4.1KB |
| 安防运维OA系统设计大纲V2.html | 1 | 64.7KB |
| .workbuddy/_archive | 487 | 2.1MB |
| .workbuddy/_exports | 0 | 0.0B |
| .workbuddy/_test | 135 | 1.4MB |
| .workbuddy/cert_staging | 8 | 33.0KB |
| .workbuddy/memory | 53 | 496.7KB |
| .workbuddy/nginx | 1 | 1.2KB |
| .workbuddy/planning | 4 | 161.1KB |
| .workbuddy/screenshots | 45 | 4.9MB |
| .workbuddy/shots | 347 | 33.7MB |
| .workbuddy/skills | 4 | 14.9KB |
| .workbuddy/staging | 8 | 12.4KB |
| .workbuddy/(root files) | 1 | 0.0B |
| **总计** | **2056** | **49.4MB** |

## 备份元数据
- **开始时间**: 2026-06-25 20:22:02
- **耗时**: 118.1s
- **脚本**: `D:/work/website/OA/.workbuddy/backup_local.py`

## 排除规则
- 目录: vendor / node_modules / dist / .git / __pycache__ / storage/logs / storage/framework/{cache,sessions,testing,views} / storage/app/public
- 文件: .env / .env.local / Thumbs.db / .DS_Store

## 恢复
```bash
# 解包到任意目录即可运行（不含 vendor/node_modules，需重装）
tar -czf v0.6.0-20260625_2022.tar.gz -C D:\work\website\OA\.workbuddy\backups v0.6.0-20260625_2022
```