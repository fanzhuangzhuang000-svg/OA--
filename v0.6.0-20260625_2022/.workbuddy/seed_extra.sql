-- V0.5.7 E2E 数据补充 — 用 SQL 插入缺的表
-- leads / opportunities / approvals / expense_claims / attendance_records / warranties
-- FK 都用现有的 user/customer/project ID

BEGIN;
SET session_replication_role = 'replica';

-- 1. leads 20
INSERT INTO leads (id, lead_no, customer_id, source, contact_name, contact_phone, requirement, estimated_amount, status, owner_id, created_at, updated_at)
SELECT
    100 + i,
    'LD2026' || LPAD(i::text, 4, '0'),
    ((i * 7) % 40) + 1,
    (ARRAY['referral','exhibition','website','cold_call','partner'])[1 + (i % 5)],
    '联系人' || i,
    '138' || LPAD((10000000 + i)::text, 8, '0'),
    '需求 #' || i || ': 视频监控/门禁/报警系统集成',
    (50000 + (i * 17000) % 450000)::numeric(12,2),
    (ARRAY['contacting','qualified','converted','discarded'])[1 + (i % 4)],
    CASE WHEN i % 3 = 0 THEN 3 ELSE 4 END,  -- sales_yang / tech_qian
    NOW() - (i || ' days')::interval,
    NOW() - (i || ' days')::interval
FROM generate_series(1, 20) AS i
ON CONFLICT (id) DO NOTHING;

-- 2. opportunities 15
INSERT INTO opportunities (id, opp_no, customer_id, name, estimated_amount, stage, probability, expected_sign_date, sales_id, created_at, updated_at)
SELECT
    100 + i,
    'OPP2026' || LPAD(i::text, 4, '0'),
    ((i * 5) % 40) + 1,
    '商机 #' || i,
    (100000 + (i * 100000) % 1900000)::numeric(12,2),
    (ARRAY['requirement','proposal','negotiation','won','lost'])[1 + (i % 5)],
    20 + (i * 7) % 70,
    CURRENT_DATE + ((i * 15) || ' days')::interval,
    3,
    NOW() - (i || ' days')::interval,
    NOW() - (i || ' days')::interval
FROM generate_series(1, 15) AS i
ON CONFLICT (id) DO NOTHING;

-- 3. approvals 12 (用 approval_records_v2 master 表)
INSERT INTO approval_records_v2 (id, code, type, sub_type, title, priority, status, amount, applicant_id, current_approver_id, created_at, updated_at)
SELECT
    100 + i,
    'AP2026' || LPAD(i::text, 4, '0'),
    (ARRAY['expense','leave','purchase','project','contract'])[1 + (i % 5)],
    (ARRAY['travel','meal','equipment','contract_change'])[1 + (i % 4)],
    '审批 #' || i,
    (ARRAY['normal','urgent'])[1 + (i % 2)],
    (ARRAY['pending','approved','rejected'])[1 + (i % 3)],
    (500 + (i * 380) % 4500)::numeric(14,2),
    3,  -- sales_yang
    2,  -- fin_wu
    NOW() - (i || ' hours')::interval,
    NOW() - (i || ' hours')::interval
FROM generate_series(1, 12) AS i
ON CONFLICT (id) DO NOTHING;

-- 4. expense_claims 10
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, project_id, description, status, approver_id, created_at, updated_at)
SELECT
    100 + i,
    'EX2026' || LPAD(i::text, 4, '0'),
    3,
    (ARRAY['travel','meal','office','transport'])[1 + (i % 4)],
    (500 + (i * 380) % 4500)::numeric(12,2),
    72 + ((i * 5) % 50),
    '因公支出 #' || i,
    (ARRAY['draft','pending','approved','rejected'])[1 + (i % 4)],
    2,
    NOW() - (i || ' days')::interval,
    NOW() - (i || ' days')::interval
FROM generate_series(1, 10) AS i
ON CONFLICT (id) DO NOTHING;

-- 5. attendance_records 30
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, created_at, updated_at)
SELECT
    100 + i,
    ((i * 3) % 17) + 1,  -- 在 1-20 范围 (虽然 6/12/18 不存在, 用 ON CONFLICT DO NOTHING 兜底)
    (CURRENT_DATE - (i || ' days')::interval)::date,
    (CURRENT_DATE - (i || ' days')::interval)::date + interval '9 hours',
    (CURRENT_DATE - (i || ' days')::interval)::date + interval '18 hours',
    (ARRAY['normal','late','early_leave'])[1 + (i % 3)],
    NOW(),
    NOW()
FROM generate_series(1, 30) AS i
ON CONFLICT (id) DO NOTHING;

-- 6. warranties 8
INSERT INTO warranties (id, uuid, project_id, customer_id, warranty_no, warranty_type, start_date, end_date, period_months, status, amount, terms, created_by, created_at, updated_at)
SELECT
    100 + i,
    gen_random_uuid(),
    72 + ((i * 5) % 50),
    ((i * 3) % 40) + 1,
    'WR2026' || LPAD(i::text, 4, '0'),
    (ARRAY['basic','extended','lifetime'])[1 + (i % 3)],
    (CURRENT_DATE - ((180 + i * 30) || ' days')::interval)::date,
    (CURRENT_DATE + ((180 - i * 15) || ' days')::interval)::date,
    12,
    'active',
    (5000 + (i * 1500) % 15000)::numeric(12,2),
    '质保 #' || i || ' - 1年免费维修',
    1,
    NOW(),
    NOW()
FROM generate_series(1, 8) AS i
ON CONFLICT (id) DO NOTHING;

-- 7. work_orders +10
INSERT INTO work_orders (id, code, customer_id, project_id, service_type, priority, fault_description, contact_name, contact_phone, status, created_at, updated_at)
SELECT
    200 + i,
    'WO-2026-' || LPAD((200 + i)::text, 4, '0'),
    ((i * 3) % 40) + 1,
    72 + ((i * 5) % 50),
    (ARRAY['on_site','remote','shop'])[1 + (i % 3)],
    (ARRAY['low','medium','high','urgent'])[1 + (i % 4)],
    '设备异常 #' || i,
    '张' || i,
    '138' || LPAD((10000000 + i * 7)::text, 8, '0'),
    (ARRAY['pending','assigned','in_progress','closed'])[1 + (i % 4)],
    NOW() - (i || ' days')::interval,
    NOW() - (i || ' days')::interval
FROM generate_series(1, 10) AS i
ON CONFLICT (id) DO NOTHING;

-- 8. repair_orders +10
INSERT INTO repair_orders (id, code, customer_id, project_id, contact_name, contact_phone, equipment_brand, equipment_model, fault_description, method_type, parts_cost, labor_cost, shipping_cost, total_cost, status, received_at, created_at, updated_at)
SELECT
    200 + i,
    'RN-2026-' || LPAD((200 + i)::text, 4, '0'),
    ((i * 5) % 40) + 1,
    72 + ((i * 5) % 50),
    '李' || i,
    '137' || LPAD((10000000 + i * 11)::text, 8, '0'),
    (ARRAY['海康','大华','宇视','华为'])[1 + (i % 4)],
    'M-' || (1000 + i),
    '返修故障 #' || i,
    (ARRAY['free_warranty','free_contract','paid_repair','paid_replace'])[1 + (i % 4)],
    (100 + (i * 150) % 1900)::numeric(10,2),
    (100 + (i * 50) % 400)::numeric(10,2),
    (50 + (i * 15) % 150)::numeric(10,2),
    (250 + (i * 200) % 2400)::numeric(10,2),
    (ARRAY['received','in_repair','repaired','shipped_back','closed'])[1 + (i % 5)],
    NOW() - ((i * 3) || ' days')::interval,
    NOW() - (i || ' days')::interval,
    NOW() - (i || ' days')::interval
FROM generate_series(1, 10) AS i
ON CONFLICT (id) DO NOTHING;

-- 9. warranties 已加, 修 sequence
DO $$
DECLARE r RECORD;
BEGIN
    FOR r IN
        SELECT t.table_name FROM information_schema.tables t
        JOIN information_schema.columns c ON c.table_schema=t.table_schema AND c.table_name=t.table_name
        WHERE t.table_schema='public' AND c.column_name='id' AND c.is_identity='YES'
    LOOP
        EXECUTE format('SELECT setval(pg_get_serial_sequence(%L,%L), COALESCE(MAX(id),1), true) FROM %I', r.table_name, 'id', r.table_name);
    END LOOP;
END $$;

COMMIT;

-- 报表
SELECT '=== 补充完成 ===' info;
SELECT 'leads' k, count(*) n FROM leads
UNION ALL SELECT 'opps', count(*) FROM opportunities
UNION ALL SELECT 'approvals', count(*) FROM approval_records
UNION ALL SELECT 'expense', count(*) FROM expense_claims
UNION ALL SELECT 'attendance', count(*) FROM attendance_records
UNION ALL SELECT 'warranty', count(*) FROM warranties
UNION ALL SELECT 'work_orders', count(*) FROM work_orders
UNION ALL SELECT 'repair_orders', count(*) FROM repair_orders
UNION ALL SELECT 'customers', count(*) FROM customers
UNION ALL SELECT 'projects', count(*) FROM projects
UNION ALL SELECT 'users', count(*) FROM users
UNION ALL SELECT 'system_dicts', count(*) FROM system_dicts
UNION ALL SELECT 'project_members', count(*) FROM project_members
UNION ALL SELECT 'construction_logs', count(*) FROM construction_logs
UNION ALL SELECT 'contracts', count(*) FROM project_contracts
ORDER BY 1;
