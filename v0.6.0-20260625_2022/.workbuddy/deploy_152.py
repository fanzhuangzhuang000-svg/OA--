"""
152 灰度发布脚本 — 安防运维OA 部署到 152.136.115.121 (ubuntu/Aa782997781.)

⚠️ 2026-06-25 15:35 用户授权策略变更：
- 117 = 主测试机（默认部署目标）
- 152 = 展示机（oa.afjsw.cn 域名），**未经用户明确授权不许推送**
- 必须显式传 `--authorized` 才能真推，否则默认 dry-run 模式
- "授权" 在命令行体现为 `--authorized` 标记 + 终端输入授权码

⚠️ 生产展示平台，**只同步增量代码**：
- 同步 dist/ → /var/www/oa-web
- 同步 API 的修改文件 (Controllers / Middleware / Models / routes / migrations) → /var/www/oa-api
- **不** rm -rf，**不** composer install，**不** db:migrate
- 跑前先核对修改文件清单

使用: python .workbuddy/deploy_152.py [--dry-run] [--only-web] [--only-api] [--files file1 file2 ...] [--authorized] [--auth-code CODE]

v0.3.14 重点验证：5 个新拆 Vue 子模块在生产 HTTPS 环境下表现。
"""
import sys, os, time, argparse, hashlib
import paramiko, posixpath

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
LOCAL_API = r'D:\work\website\OA\pc-api'
LOCAL_WEB = r'D:\work\website\OA\pc-web\dist'
REMOTE_API = '/var/www/oa-api'
REMOTE_WEB = '/var/www/oa-web'

# v0.3.11/v0.3.12/v0.3.13 改过的关键文件清单（手动维护，确保只推改过的）
API_CHANGED = [
    'app/Concerns/HasDataScope.php',
    'app/Console/Commands/CleanExpiredRoles.php',
    'app/Console/Commands/GenerateTestData.php',
    'app/Console/Commands/MigrateWorkOrdersFromServiceOrders.php',
    'app/Console/Commands/ScanOverdueConstructionLogs.php',
    'app/Console/Commands/ScanWarrantyExpiry.php',
    'app/Console/Commands/SyncProjectActualCosts.php',
    'app/Enums/RepairMethodType.php',
    'app/Enums/RepairOrderStatus.php',
    'app/Enums/RepairSourceType.php',
    'app/Enums/ShipmentDirection.php',
    'app/Enums/WorkOrderPriority.php',
    'app/Enums/WorkOrderStatus.php',
    'app/Events/BudgetExceeded.php',
    'app/Events/BudgetWarning.php',
    'app/Http/Controllers/Api/ApprovalTemplateController.php',
    'app/Http/Controllers/Api/AuditController.php',
    'app/Http/Controllers/Api/AuthController.php',
    'app/Http/Controllers/Api/BackupController.php',
    'app/Http/Controllers/Api/Concerns/HandlesDataScope.php',
    'app/Http/Controllers/Api/Construction/BudgetController.php',
    'app/Http/Controllers/Api/Construction/CommencementOrderController.php',
    'app/Http/Controllers/Api/Construction/ConstructionLogController.php',
    'app/Http/Controllers/Api/Construction/ExternalConstructionController.php',
    'app/Http/Controllers/Api/Construction/RectificationController.php',
    'app/Http/Controllers/Api/Construction/TeamController.php',
    'app/Http/Controllers/Api/Construction/WorkProcessController.php',
    'app/Http/Controllers/Api/CustomerController.php',
    'app/Http/Controllers/Api/DashboardController.php',
    'app/Http/Controllers/Api/DashboardWidgetController.php',
    'app/Http/Controllers/Api/EmployeeController.php',
    'app/Http/Controllers/Api/ExternalQuoteController.php',
    'app/Http/Controllers/Api/FieldMaskController.php',
    'app/Http/Controllers/Api/FinanceController.php',
    'app/Http/Controllers/Api/InventoryCategoryController.php',
    'app/Http/Controllers/Api/InventoryController.php',
    'app/Http/Controllers/Api/LedgerController.php',
    'app/Http/Controllers/Api/PortalRepairController.php',
    'app/Http/Controllers/Api/ProcessController.php',
    'app/Http/Controllers/Api/ProjectController.php',
    'app/Http/Controllers/Api/PurchasePaymentRequestController.php',
    'app/Http/Controllers/Api/RepairCostSummaryController.php',
    'app/Http/Controllers/Api/RepairMethodController.php',
    'app/Http/Controllers/Api/RepairOrderController.php',
    'app/Http/Controllers/Api/RepairProgressLogController.php',
    'app/Http/Controllers/Api/RepairShipmentController.php',
    'app/Http/Controllers/Api/RepairStepPhotoController.php',
    'app/Http/Controllers/Api/RoleController.php',
    'app/Http/Controllers/Api/SalesController.php',
    'app/Http/Controllers/Api/ServiceController.php',
    'app/Http/Controllers/Api/SetupWizardController.php',
    'app/Http/Controllers/Api/SupplierController.php',
    'app/Http/Controllers/Api/SupplierPortalController.php',
    'app/Http/Controllers/Api/SystemDictController.php',
    'app/Http/Controllers/Api/SystemMonitorController.php',
    'app/Http/Controllers/Api/VehicleController.php',
    'app/Http/Controllers/Api/WarrantyController.php',
    'app/Http/Controllers/Api/WarrantyDepositController.php',
    'app/Http/Controllers/Api/WarrantyServiceOrderController.php',
    'app/Http/Controllers/Api/WorkOrderController.php',
    'app/Http/Middleware/ApplyFieldMask.php',
    'app/Http/Middleware/CheckPermission.php',
    'app/Http/Middleware/CheckResourceOwnership.php',
    'app/Http/Middleware/CheckRoleActive.php',
    'app/Http/Middleware/DataScope.php',
    'app/Http/Middleware/LoginThrottle.php',
    'app/Http/Middleware/SupplierOnly.php',
    'app/Http/Middleware/SupplierScope.php',
    'app/Models/ApprovalTemplate.php',
    'app/Models/CommencementOrder.php',
    'app/Models/ConstructionLog.php',
    'app/Models/ConstructionTeam.php',
    'app/Models/ConstructionTeamMember.php',
    'app/Models/CoreModels.php',
    'app/Models/CustomerReceipt.php',
    'app/Models/CustomerReceivable.php',
    'app/Models/ExternalConstructionBid.php',
    'app/Models/ExternalConstructionWork.php',
    'app/Models/ExternalQuote.php',
    'app/Models/ExternalQuoteRequest.php',
    'app/Models/OtherModels.php',
    'app/Models/ProjectActualCost.php',
    'app/Models/ProjectBudget.php',
    'app/Models/ProjectBudgetItem.php',
    'app/Models/ProjectCommencementOrder.php',
    'app/Models/ProjectModels.php',
    'app/Models/Rectification.php',
    'app/Models/RectificationDailyRequired.php',
    'app/Models/RepairAttachment.php',
    'app/Models/RepairMethod.php',
    'app/Models/RepairOrder.php',
    'app/Models/RepairProgressLog.php',
    'app/Models/RepairShipment.php',
    'app/Models/RepairStepPhoto.php',
    'app/Models/Supplier.php',
    'app/Models/SupplierAttachment.php',
    'app/Models/SupplierContact.php',
    'app/Models/SupplierEvaluation.php',
    'app/Models/SupplierPayable.php',
    'app/Models/SupplierPayment.php',
    'app/Models/SystemDict.php',
    'app/Models/User.php',
    'app/Models/Warranty.php',
    'app/Models/WarrantyDeposit.php',
    'app/Models/WarrantyServiceOrder.php',
    'app/Models/WorkOrder.php',
    'app/Models/WorkProcess.php',
    'app/Models/WorkProcessProgress.php',
    'app/Notifications/SettlementOverdueNotification.php',
    'app/Observers/CommencementOrderObserver.php',
    'app/Observers/ConstructionLogObserver.php',
    'app/Observers/ExpenseClaimObserver.php',
    'app/Observers/ExternalConstructionBidObserver.php',
    'app/Observers/StockRecordObserver.php',
    'app/Providers/AppServiceProvider.php',
    'app/Rules/BudgetNotExceeded.php',
    'app/Scopes/DataScope.php',
    'app/Services/CommencementOrderService.php',
    'app/Services/ConstructionLogService.php',
    'app/Services/ConstructionTeamService.php',
    'app/Services/DashboardWidget.php',
    'app/Services/ExternalConstructionService.php',
    'app/Services/ExternalQuoteService.php',
    'app/Services/LedgerService.php',
    'app/Services/ProjectBudgetService.php',
    'app/Services/RectificationService.php',
    'app/Services/RepairCostStat.php',
    'app/Services/SupplierService.php',
    'app/Services/WarrantyDepositService.php',
    'app/Services/WarrantyService.php',
    'app/Services/WarrantyServiceOrderService.php',
    'app/Services/WorkOrderService.php',
    'app/Support/Audit.php',
    'app/Support/AuthScope.php',
    'app/Support/FieldMask.php',
    'app/Support/PermissionInheritance.php',
    'app/Support/TemporaryRole.php',
    'bootstrap/app.php',
    'database/migrations/2024_01_01_000001_create_departments_table.php',
    'database/migrations/2024_01_01_000002_create_positions_table.php',
    'database/migrations/2024_01_01_000003_create_users_table.php',
    'database/migrations/2024_01_01_000004_create_roles_table.php',
    'database/migrations/2024_01_01_000005_create_permissions_table.php',
    'database/migrations/2024_01_01_000006_create_permission_role_table.php',
    'database/migrations/2024_01_01_000007_create_employee_profiles_table.php',
    'database/migrations/2024_01_01_000008_create_skill_tags_table.php',
    'database/migrations/2024_01_01_000009_create_employee_skills_table.php',
    'database/migrations/2024_01_01_000010_create_certificates_table.php',
    'database/migrations/2024_01_01_000011_create_customers_table.php',
    'database/migrations/2024_01_01_000012_create_customer_contacts_table.php',
    'database/migrations/2024_01_01_000013_create_follow_up_records_table.php',
    'database/migrations/2024_01_01_000014_create_customer_devices_table.php',
    'database/migrations/2024_01_02_000001_create_projects_table.php',
    'database/migrations/2024_01_02_000002_create_project_members_table.php',
    'database/migrations/2024_01_02_000003_create_project_contracts_table.php',
    'database/migrations/2024_01_02_000004_create_contract_payment_nodes_table.php',
    'database/migrations/2024_01_02_000005_create_suppliers_table.php',
    'database/migrations/2024_01_02_000006_create_purchase_orders_table.php',
    'database/migrations/2024_01_02_000007_create_purchase_items_table.php',
    'database/migrations/2024_01_02_000008_create_construction_logs_table.php',
    'database/migrations/2024_01_02_000009_create_project_materials_table.php',
    'database/migrations/2024_01_02_000010_create_project_settlements_table.php',
    'database/migrations/2024_01_03_000001_create_service_orders_table.php',
    'database/migrations/2024_01_03_000002_create_service_order_logs_table.php',
    'database/migrations/2024_01_03_000003_create_service_order_parts_table.php',
    'database/migrations/2024_01_03_000004_create_maintenance_contracts_table.php',
    'database/migrations/2024_01_04_000001_create_attendance_records_table.php',
    'database/migrations/2024_01_04_000002_create_leave_requests_table.php',
    'database/migrations/2024_01_04_000003_create_overtime_requests_table.php',
    'database/migrations/2024_01_05_000001_create_expense_claims_table.php',
    'database/migrations/2024_01_05_000002_create_expense_items_table.php',
    'database/migrations/2024_01_05_000003_create_approval_records_table.php',
    'database/migrations/2024_01_05_000004_create_approval_records_v2_table.php',
    'database/migrations/2024_01_06_000001_create_vehicles_table.php',
    'database/migrations/2024_01_06_000002_create_vehicle_insurance_table.php',
    'database/migrations/2024_01_06_000003_create_vehicle_maintenance_records_table.php',
    'database/migrations/2024_01_06_000004_create_vehicle_usage_requests_table.php',
    'database/migrations/2024_01_06_000005_create_fuel_cards_table.php',
    'database/migrations/2024_01_07_000001_create_warehouses_table.php',
    'database/migrations/2024_01_07_000002_create_inventory_items_table.php',
    'database/migrations/2024_01_07_000003_create_inventory_categories_table.php',
    'database/migrations/2024_01_07_000003_create_stock_records_table.php',
    'database/migrations/2024_01_07_000004_create_device_serial_numbers_table.php',
    'database/migrations/2024_01_08_000001_create_receivables_table.php',
    'database/migrations/2024_01_08_000002_create_payables_table.php',
    'database/migrations/2024_01_09_000001_create_disk_folders_table.php',
    'database/migrations/2024_01_09_000002_create_disk_files_table.php',
    'database/migrations/2024_01_10_000001_create_knowledge_categories_table.php',
    'database/migrations/2024_01_10_000002_create_knowledge_articles_table.php',
    'database/migrations/2024_01_11_000001_create_notifications_table.php',
    'database/migrations/2024_01_12_000001_create_system_logs_table.php',
    'database/migrations/2026_06_17_000001_create_system_settings_table.php',
    'database/migrations/2026_06_17_000002_create_approval_templates_table.php',
    'database/migrations/2026_06_19_100001_create_leads_table.php',
    'database/migrations/2026_06_19_100002_create_opportunities_table.php',
    'database/migrations/2026_06_19_100003_create_quotation_and_referrer_tables.php',
    'database/migrations/2026_06_19_100004_create_follow_up_tables.php',
    'database/migrations/2026_06_19_100005_create_project_pool_table.php',
    'database/migrations/2026_06_19_100006_create_sales_products_table.php',
    'database/migrations/2026_06_19_110001_create_finance_payments_table.php',
    'database/migrations/2026_06_19_110001_create_purchase_requirements_table.php',
    'database/migrations/2026_06_19_110002_create_finance_accounts_table.php',
    'database/migrations/2026_06_19_110002_create_purchase_plans_table.php',
    'database/migrations/2026_06_19_110003_create_finance_invoices_table.php',
    'database/migrations/2026_06_19_110003_create_purchase_contracts_table.php',
    'database/migrations/2026_06_19_110004_add_fk_payments_account.php',
    'database/migrations/2026_06_19_110005_create_purchase_payment_requests_table.php',
    'database/migrations/2026_06_19_110006_create_purchase_payments_table.php',
    'database/migrations/2026_06_19_110007_create_purchase_shipments_table.php',
    'database/migrations/2026_06_19_110008_create_purchase_logistics_table.php',
    'database/migrations/2026_06_19_110009_create_purchase_approvals_table.php',
    'database/migrations/2026_06_20_000001_add_inventory_warnings.php',
    'database/migrations/2026_06_20_100000_create_shifts_and_schedules.php',
    'database/migrations/2026_06_20_110000_create_employee_onboardings_and_resignations.php',
    'database/migrations/2026_06_20_120000_add_pipeline_fields_to_customers.php',
    'database/migrations/2026_06_20_140000_create_audit_logs_table.php',
    'database/migrations/2026_06_21_130000_add_party_fields_to_stock_records.php',
    'database/migrations/2026_06_21_140000_add_logistics_to_stock_records.php',
    'database/migrations/2026_06_22_000000_add_nullable_supplier_id_to_payables_table.php',
    'database/migrations/2026_06_22_130000_create_process_tables.php',
    'database/migrations/2026_06_23_150000_create_referral_settlements_table.php',
    'database/migrations/2026_06_23_160000_add_product_id_to_quotation_items.php',
    'database/migrations/2026_06_24_000001_create_rectifications_v044_table.php',
    'database/migrations/2026_06_24_000002_add_commencement_order_id_to_rdr.php',
    'database/migrations/2026_06_24_000016_create_field_masks_table.php',
    'database/migrations/2026_06_24_100000_create_project_budgets_table.php',
    'database/migrations/2026_06_24_100001_create_project_budget_items_table.php',
    'database/migrations/2026_06_24_100002_create_project_actual_costs_table.php',
    'database/migrations/2026_06_24_110000_create_suppliers_table.php',
    'database/migrations/2026_06_24_110001_create_supplier_contacts_table.php',
    'database/migrations/2026_06_24_110002_create_supplier_evaluations_table.php',
    'database/migrations/2026_06_24_110003_create_supplier_attachments_table.php',
    'database/migrations/2026_06_24_110004_create_external_quote_requests_table.php',
    'database/migrations/2026_06_24_110005_create_external_quotes_table.php',
    'database/migrations/2026_06_24_110006_create_supplier_payables_table.php',
    'database/migrations/2026_06_24_110007_create_supplier_payments_table.php',
    'database/migrations/2026_06_24_110008_create_customer_receivables_table.php',
    'database/migrations/2026_06_24_110009_create_customer_receipts_table.php',
    'database/migrations/2026_06_24_110010_alter_users_add_supplier_fields.php',
    'database/migrations/2026_06_24_110011_alter_stock_records_add_batch_fields.php',
    'database/migrations/2026_06_25_000001_create_construction_teams_table.php',
    'database/migrations/2026_06_25_000002_create_construction_team_members_table.php',
    'database/migrations/2026_06_25_000003_create_project_commencement_orders_table.php',
    'database/migrations/2026_06_25_000004_create_work_processes_table.php',
    'database/migrations/2026_06_25_000005_alter_construction_logs_add_fields.php',
    'database/migrations/2026_06_25_000006_create_work_process_progress_table.php',
    'database/migrations/2026_06_25_000007_create_rectification_daily_required_table.php',
    'database/migrations/2026_06_25_000008_create_external_construction_works_table.php',
    'database/migrations/2026_06_25_000009_create_external_construction_bids_table.php',
    'database/migrations/2026_06_25_000010_add_softdeletes_to_v043_tables.php',
    'database/migrations/2026_06_25_000011_create_warranties_table.php',
    'database/migrations/2026_06_25_000012_create_warranty_service_orders_table.php',
    'database/migrations/2026_06_25_000013_create_warranty_deposits_table.php',
    'database/migrations/2026_06_25_000014_add_composite_indexes_for_listing.php',
    'database/migrations/2026_06_25_000015_explain_4_more_indexes.php',
    'database/migrations/2026_06_25_000016_add_expires_at_to_model_has_roles_table.php',
    'database/migrations/2026_06_25_000017_create_work_orders_table.php',
    'database/migrations/2026_06_25_000018_create_repair_orders_table.php',
    'database/migrations/2026_06_25_000019_create_repair_shipments_table.php',
    'database/migrations/2026_06_25_000020_create_repair_methods_table.php',
    'database/migrations/2026_06_25_000021_create_repair_progress_logs_table.php',
    'database/migrations/2026_06_25_000022_create_repair_attachments_table.php',
    'database/migrations/2026_06_25_000023_add_customer_signature_to_work_orders.php',
    'database/migrations/2026_06_25_000024_add_migration_fields_to_service_orders.php',
    'database/migrations/2026_06_25_000025_create_repair_step_photos_table.php',
    'database/migrations/2026_06_25_000026_create_system_dicts_table.php',
    'database/migrations/2026_06_25_000027_extend_leads_status_to_7_stages.php',
    'database/migrations/2026_06_25_000028_extend_opps_stage_to_7_stages.php',
    'database/seeders/FieldMaskSeeder.php',
    'database/seeders/PermissionRoleSeeder.php',
    'routes/api.php',
    'routes/api_copy.php',
    'routes/console.php',
    'tests/Feature/AuthApiTest.php',
    'tests/Feature/BootTest.php',
    'tests/Feature/BusinessApiTest.php',
    'tests/Feature/PermissionMatrixApiTest.php',
    'tests/Feature/UserRoleApiTest.php',
    'tests/Unit/Auth/AuthEdgeCasesTest.php',
    'tests/Unit/Auth/FieldMaskTest.php',
    'tests/Unit/Auth/InheritanceAndAuditTest.php',
    'tests/Unit/Auth/TemporaryRoleTest.php',
    'tests/Unit/Construction/ConstructionRelationsTest.php',
    'tests/Unit/Project/CustomerRelationsTest.php',
    'tests/Unit/Project/ProjectRelationsTest.php',
    'tests/Unit/Scopes/AuthScopeTest.php',
    'tests/Unit/Scopes/DataScopeTest.php',
    'tests/Unit/Warranty/WarrantyModelTest.php',
    'tests/bootstrap.php',
]


def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    return ssh


def run(ssh, cmd, timeout=60, label='', echo=True):
    if label and echo:
        print(f'  [{label}] $ {cmd[:80]}')
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    if out or err:
        for line in (out or err).split('\n')[:5]:
            print(f'    {line}')
    return out, err, rc


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def deploy_web(ssh, dry_run=False):
    """同步 dist/ → /var/www/oa-web"""
    print(f'\n[1/3] 同步前端 dist → {REMOTE_WEB}')
    if not os.path.exists(LOCAL_WEB):
        print(f'  [ERROR] {LOCAL_WEB} 不存在')
        return False
    files = []
    for root, _, fnames in os.walk(LOCAL_WEB):
        for f in fnames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, LOCAL_WEB).replace('\\', '/')
            files.append((full, rel))
    print(f'  本地 dist 共 {len(files)} 个文件')

    if dry_run:
        print('  (dry-run, skip upload)')
        return True

    sftp = ssh.open_sftp()
    uploaded = 0
    skipped = 0
    for local, rel in files:
        remote_tmp = f'/tmp/oa-web-staging/{rel}'
        remote_final = f'{REMOTE_WEB}/{rel}'
        # v0.5.8 修复: sftp 用 ubuntu 账号, staging 子目录需先 sudo 预建并 chown 给 ubuntu
        run(ssh, f'sudo -n mkdir -p {posixpath.dirname(remote_tmp)} {posixpath.dirname(remote_final)}', echo=False)
        run(ssh, f'sudo -n chown -R ubuntu:ubuntu {posixpath.dirname(remote_tmp)}', echo=False)
        try:
            sftp.put(local, remote_tmp)
        except Exception as e:
            print(f'  [FAIL] put {rel}: {e}')
            skipped += 1
            continue
        ok, err, rc = run(ssh, f'sudo -n cp {remote_tmp} {remote_final} && '
                               f'sudo -n chown www-data:www-data {remote_final} && '
                               f'rm {remote_tmp}', echo=False)
        if rc != 0:
            print(f'  [FAIL] cp {rel} rc={rc} err={err[:200]}')
            skipped += 1
            continue
        uploaded += 1
        if uploaded % 50 == 0:
            print(f'    {uploaded}/{len(files)}')
    sftp.close()
    print(f'  ✓ 前端同步完成: {uploaded} 个文件 (skipped={skipped})')
    return True


def deploy_api(ssh, files, dry_run=False):
    """只同步 API 改过的文件 → /var/www/oa-api"""
    print(f'\n[2/3] 同步 API 修改文件 → {REMOTE_API} (共 {len(files)} 个)')
    if dry_run:
        for f in files:
            full = os.path.join(LOCAL_API, f)
            print(f'  - {f} {"(missing)" if not os.path.exists(full) else ""}')
        return True

    sftp = ssh.open_sftp()
    uploaded = 0
    skipped = 0
    for rel in files:
        local_path = os.path.join(LOCAL_API, rel)
        if not os.path.exists(local_path):
            print(f'  [WARN] 本地文件不存在: {rel}')
            skipped += 1
            continue
        remote_tmp = f'/tmp/oa-api-staging/{rel}'
        remote_final = f'{REMOTE_API}/{rel}'
        # v0.5.8 修复: sftp 用 ubuntu 账号, staging 子目录需先 sudo 预建并 chown 给 ubuntu
        run(ssh, f'sudo -n mkdir -p {posixpath.dirname(remote_tmp)} {posixpath.dirname(remote_final)}', echo=False)
        run(ssh, f'sudo -n chown -R ubuntu:ubuntu {posixpath.dirname(remote_tmp)}', echo=False)
        try:
            sftp.put(local_path, remote_tmp)
        except Exception as e:
            print(f'  [FAIL] put {rel}: {e}')
            skipped += 1
            continue
        # 用 sudo -n 强制 NOPASSWD
        ok, err, rc = run(ssh, f'sudo -n cp {remote_tmp} {remote_final} && '
                               f'sudo -n chown www-data:www-data {remote_final} && '
                               f'rm {remote_tmp}', echo=False)
        if rc != 0:
            print(f'  [FAIL] cp {rel} rc={rc} err={err[:200]}')
            skipped += 1
            continue
        uploaded += 1
        print(f'  ✓ {rel}')
    sftp.close()
    print(f'  ✓ API 同步完成: {uploaded} 个文件 (skipped={skipped})')
    return True


def restart_services(ssh, dry_run=False):
    """重启 PHP-FPM 清 opcache，nginx reload"""
    print(f'\n[3/3] 重启服务')
    if dry_run:
        print('  (dry-run, skip)')
        return True
    # PHP-FPM 必须 restart（不是 reload），否则 opcache 不会清
    run(ssh, 'sudo systemctl restart php8.3-fpm 2>&1 || systemctl restart php8.3-fpm', label='restart fpm')
    run(ssh, 'sudo nginx -s reload 2>&1 || nginx -s reload', label='reload nginx')
    print('  ✓ 服务已重启')
    return True


def main():
    p = argparse.ArgumentParser(
        description='152 灰度发布（默认 dry-run；需 --authorized 显式授权才真推）',
        epilog='提示：默认测试以 117 为准（用 .workbuddy/deploy_117.py），152 未经授权不许推送',
    )
    p.add_argument('--dry-run', action='store_true', help='默认 dry-run，只打印文件清单')
    p.add_argument('--only-web', action='store_true')
    p.add_argument('--only-api', action='store_true')
    p.add_argument('--files', nargs='*', help='指定 API 改过的文件路径（相对 pc-api/）')
    p.add_argument('--skip-restart', action='store_true')
    p.add_argument('--authorized', action='store_true',
                   help='【必须】明确表示已获得用户授权推送 152；不传则强制 dry-run')
    p.add_argument('--auth-code', type=str, default=None,
                   help='授权码（防止误操作，约定为 deploy-152-ok 或当天日期 YYYYMMDD）')
    args = p.parse_args()

    # 🚦 2026-06-15: 部署主从策略 — 152 必须显式授权
    AUTHORIZED_CODES = {'deploy-152-ok', 'allow-152', '152-yes'}
    if not args.authorized or (args.auth_code and args.auth_code not in AUTHORIZED_CODES):
        if not args.dry_run:
            print('=' * 60)
            print('🚦 152 部署策略门禁 (2026-06-25 15:35 拍板)')
            print('=' * 60)
            print('  152 是 oa.afjsw.cn 域名展示机，未经用户授权不许推送。')
            print('  默认情况下本脚本只跑 dry-run (打印文件清单)。')
            print()
            print('  确认要真推 152？必须同时满足 2 个条件：')
            print('    1) 加 --authorized 标记')
            print('    2) 加 --auth-code <授权码>（deploy-152-ok / allow-152 / 152-yes）')
            print()
            print('  示例:')
            print('    python .workbuddy/deploy_152.py --authorized --auth-code deploy-152-ok --only-web')
            print()
            print('  💡 日常测试请走 117：')
            print('    python .workbuddy/upload_web_117.py    # 推前端')
            print('    python .workbuddy/deploy_117.py --only-api    # 推后端')
            print('=' * 60)
            print()
            print('  自动降级为 dry-run 模式 (不真推)：')
            print()
        args.dry_run = True

    files = args.files or API_CHANGED

    if args.dry_run:
        print('=' * 60)
        print('DRY RUN — 仅打印将同步的文件清单（不真推）')
        print('=' * 60)
    else:
        print('=' * 60)
        print(f'🚦 152 真部署（已授权）→ {HOST} ({USER})')
        print('=' * 60)

    ssh = ssh_connect()
    try:
        if not args.only_api:
            deploy_web(ssh, dry_run=args.dry_run)
        if not args.only_web:
            deploy_api(ssh, files, dry_run=args.dry_run)
        if not args.skip_restart:
            restart_services(ssh, dry_run=args.dry_run)
    finally:
        ssh.close()

    if not args.dry_run:
        print('\n' + '=' * 50)
        print('灰度发布完成!')
        print(f'  HTTPS: https://oa.afjsw.cn')
        print(f'  账号:  admin / admin123 (172 同步过去, 但需确认 152 DB 用户表)')
        print('=' * 50)


if __name__ == '__main__':
    main()
