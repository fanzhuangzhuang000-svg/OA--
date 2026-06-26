-- V0.5.7 E2E 演示环境 — 清空业务数据
-- 保留: users(只留 admin/fin/sales/tech/construction 5 种子) / roles/permissions/departments/positions/system_dicts/system_settings
-- 清空: 其他所有表 (业务数据)
-- 用动态方式避开表名映射问题

BEGIN;
SET session_replication_role = 'replica';

-- 1) 收集要保留的表
CREATE TEMP TABLE _keep (tablename text PRIMARY KEY);
INSERT INTO _keep VALUES
  ('users'),
  ('roles'),
  ('permissions'),
  ('model_has_roles'),
  ('model_has_permissions'),
  ('permission_role'),
  ('departments'),
  ('positions'),
  ('system_dicts'),
  ('system_settings'),
  ('system_configs'),
  ('migrations'),
  ('cache'),
  ('cache_locks'),
  ('jobs'),
  ('failed_jobs'),
  ('password_reset_tokens'),
  ('personal_access_tokens'),
  ('field_masks'),
  ('disk_folders'),
  ('disk_settings'),
  ('knowledge_categories'),
  ('process_templates'),
  ('inventory_categories');

-- 2) 动态生成 TRUNCATE 所有非保留表
DO $$
DECLARE
    t text;
    sql text := '';
BEGIN
    FOR t IN
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename NOT IN (SELECT tablename FROM _keep)
        ORDER BY tablename
    LOOP
        sql := sql || format('TRUNCATE TABLE %I CASCADE;', t) || E'\n';
    END LOOP;
    RAISE NOTICE '--- TRUNCATE SCRIPT ---';
    RAISE NOTICE '%', sql;
    EXECUTE sql;
END $$;

-- 3) 修所有 sequence
DO $$
DECLARE r RECORD;
BEGIN
    FOR r IN
        SELECT t.table_name, c.column_name
        FROM information_schema.tables t
        JOIN information_schema.columns c
          ON c.table_schema = t.table_schema
         AND c.table_name   = t.table_name
        WHERE t.table_schema = 'public'
          AND c.column_name  = 'id'
          AND c.data_type    IN ('integer','bigint')
          AND c.is_identity   = 'YES'
    LOOP
        EXECUTE format(
            'SELECT setval(pg_get_serial_sequence(%L,%L), COALESCE(MAX(id),1), true) FROM %I',
            r.table_name, r.column_name, r.table_name
        );
    END LOOP;
END $$;

-- 4) 保留 admin (id=1) + 4 个种子用户, 删其他用户
-- 不删 user — 保留种子, 用户名密码记录在交付报告

SET session_replication_role = 'origin';

-- 5) system_settings 标记未完成
UPDATE system_settings SET value = '0' WHERE key = 'setup_completed';
UPDATE system_settings SET value = NULL WHERE key IN ('setup_completed_at');

-- 6) 清 cache
TRUNCATE TABLE cache CASCADE;

COMMIT;

-- 7) 报表
SELECT '=== 清理完成 ===' AS info;
SELECT 'users (保留)' tbl, count(*) n FROM users
UNION ALL SELECT 'customers', count(*) FROM customers
UNION ALL SELECT 'projects', count(*) FROM projects
UNION ALL SELECT 'work_orders', count(*) FROM work_orders
UNION ALL SELECT 'repair_orders', count(*) FROM repair_orders
UNION ALL SELECT 'leads', count(*) FROM leads
UNION ALL SELECT 'opportunities', count(*) FROM opportunities
UNION ALL SELECT 'warranties', count(*) FROM warranties
UNION ALL SELECT 'approvals', count(*) FROM approval_records
UNION ALL SELECT 'expense_claims', count(*) FROM expense_claims
UNION ALL SELECT 'attendance_records', count(*) FROM attendance_records
UNION ALL SELECT 'purchases', count(*) FROM purchase_orders
UNION ALL SELECT 'departments', count(*) FROM departments
UNION ALL SELECT 'positions', count(*) FROM positions
UNION ALL SELECT 'system_dicts', count(*) FROM system_dicts
UNION ALL SELECT 'roles', count(*) FROM roles
UNION ALL SELECT 'permissions', count(*) FROM permissions
ORDER BY tbl;
