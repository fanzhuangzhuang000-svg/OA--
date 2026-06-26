-- D:\work\website\OA\.workbuddy\insert_test_data.sql
-- 直接插入测试数据的SQL脚本，时间跨度2025-12-01至2026-06-22

-- 设置时间跨度
SELECT '2025-12-01'::date AS start_date, '2026-06-22'::date AS end_date;

-- 1. 插入更多员工数据（如果少于30个）
INSERT INTO employee_profiles (user_id, employee_id, position, department, phone, hire_date, status, created_at, updated_at)
SELECT 
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    'EMP' || LPAD(ROW_NUMBER() OVER () + COALESCE((SELECT MAX(SUBSTRING(employee_id FROM 4)::int) FROM employee_profiles), 0)::text, 4, '0'),
    (ARRAY['软件工程师', '项目经理', '销售代表', '财务分析师', '人事专员', '运维工程师', '测试工程师', '产品经理', 'UI设计师', '网络工程师'])[floor(random() * 10 + 1)],
    (ARRAY['技术部', '销售部', '财务部', '人事部', '运维部', '产品部'])[floor(random() * 6 + 1)],
    '1' || (floor(random() * 900000000) + 1000000000)::text,
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::date,
    'active',
    NOW(),
    NOW()
WHERE (SELECT COUNT(*) FROM employee_profiles) < 30
LIMIT 30 - (SELECT COUNT(*) FROM employee_profiles);

-- 2. 插入更多服务工单数据（如果少于100条）
INSERT INTO service_tickets (customer_id, project_id, type, title, description, priority, status, assigned_to, created_by, created_at, updated_at)
SELECT 
    (SELECT id FROM customers ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM projects ORDER BY RANDOM() LIMIT 1),
    (ARRAY['repair', 'maintenance', 'installation', 'consultation', 'emergency'])[floor(random() * 5 + 1)],
    '服务工单 #' || (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER () FROM service_tickets),
    '这是服务工单的详细描述，用于测试系统功能。',
    (ARRAY['low', 'medium', 'high', 'urgent'])[floor(random() * 4 + 1)],
    (ARRAY['open', 'in_progress', 'resolved', 'closed'])[floor(random() * 4 + 1)],
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM service_tickets) < 100
LIMIT 100 - (SELECT COUNT(*) FROM service_tickets);

-- 3. 插入更多采购订单数据（如果少于50条）
INSERT INTO purchase_orders (supplier_id, order_number, order_date, total_amount, status, created_by, created_at, updated_at)
SELECT 
    (SELECT id FROM suppliers ORDER BY RANDOM() LIMIT 1),
    'PO-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(COALESCE((SELECT MAX(SUBSTRING(order_number FROM '-([0-9]+)$')::int) FROM purchase_orders), 0) + ROW_NUMBER() OVER ()::text, 4, '0'),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::date,
    (random() * 49000 + 1000)::numeric(10,2),
    (ARRAY['draft', 'pending', 'approved', 'received', 'cancelled'])[floor(random() * 5 + 1)],
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM purchase_orders) < 50
LIMIT 50 - (SELECT COUNT(*) FROM purchase_orders);

-- 4. 插入更多销售机会数据（如果少于100条）
INSERT INTO sales_opportunities (customer_id, title, description, estimated_value, probability, status, expected_close_date, assigned_to, created_at, updated_at)
SELECT 
    (SELECT id FROM customers ORDER BY RANDOM() LIMIT 1),
    '销售机会 #' || (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER () FROM sales_opportunities),
    '这是销售机会的详细描述。',
    (random() * 195000 + 5000)::numeric(10,2),
    floor(random() * 81 + 10)::int,
    (ARRAY['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'])[floor(random() * 6 + 1)],
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::date,
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM sales_opportunities) < 100
LIMIT 100 - (SELECT COUNT(*) FROM sales_opportunities);

-- 5. 插入更多车辆数据（如果少于20辆）
INSERT INTO vehicles (plate_number, brand, model, type, year, color, status, purchase_date, created_at, updated_at)
SELECT 
    '粤B' || LPAD(floor(random() * 90000 + 10000)::text, 5, '0'),
    (ARRAY['丰田', '本田', '大众', '奔驰', '宝马', '奥迪', '特斯拉', '比亚迪', '蔚来', '小鹏'])[floor(random() * 10 + 1)],
    'Model-' || CHR(floor(random() * 26 + 65)::int) || floor(random() * 9 + 1)::text,
    (ARRAY['sedan', 'suv', 'truck', 'van', 'electric'])[floor(random() * 5 + 1)],
    floor(random() * 8 + 2018)::int,
    (ARRAY['黑色', '白色', '灰色', '蓝色', '红色'])[floor(random() * 5 + 1)],
    (ARRAY['available', 'in_use', 'maintenance', 'retired'])[floor(random() * 4 + 1)],
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::date,
    NOW(),
    NOW()
WHERE (SELECT COUNT(*) FROM vehicles) < 20
LIMIT 20 - (SELECT COUNT(*) FROM vehicles);

-- 6. 插入更多库存物品数据（如果少于100个）
INSERT INTO inventory_items (name, category_id, warehouse_id, quantity, unit, unit_price, status, created_at, updated_at)
SELECT 
    (ARRAY['笔记本电脑', '台式电脑', '显示器', '键盘', '鼠标', '打印机', '路由器', '交换机', '网线', '硬盘', '内存条', 'CPU', '主板', '显卡', '电源'])[floor(random() * 15 + 1)] || ' ' || CHR(floor(random() * 26 + 65)::int) || floor(random() * 99 + 1)::text,
    (SELECT id FROM inventory_categories ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM warehouses ORDER BY RANDOM() LIMIT 1),
    floor(random() * 100 + 1)::int,
    (ARRAY['台', '个', '件', '套', '箱'])[floor(random() * 5 + 1)],
    (random() * 4900 + 100)::numeric(10,2),
    (ARRAY['in_stock', 'out_of_stock', 'reserved'])[floor(random() * 3 + 1)],
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM inventory_items) < 100
LIMIT 100 - (SELECT COUNT(*) FROM inventory_items);

-- 7. 插入更多网盘文件夹数据（如果少于50个）
INSERT INTO disk_folders (name, parent_id, created_by, created_at, updated_at)
SELECT 
    '文件夹 ' || (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER () FROM disk_folders),
    NULL,
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM disk_folders) < 50
LIMIT 50 - (SELECT COUNT(*) FROM disk_folders);

-- 8. 插入更多知识库文章数据（如果少于50篇）
INSERT INTO knowledge_articles (title, content, category_id, created_by, status, created_at, updated_at)
SELECT 
    (ARRAY['技术文档', '操作手册', '常见问题', '最佳实践', '培训材料', '产品说明', 'API文档', '设计规范', '测试用例', '项目总结'])[floor(random() * 10 + 1)] || ' ' || (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER () FROM knowledge_articles),
    '这是知识库文章的详细内容。可以使用Markdown格式编写。',
    (SELECT id FROM knowledge_categories ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (ARRAY['draft', 'published', 'archived'])[floor(random() * 3 + 1)],
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM knowledge_articles) < 50
LIMIT 50 - (SELECT COUNT(*) FROM knowledge_articles);

-- 9. 插入更多考勤数据（确保时间跨度，如果少于2000条）
INSERT INTO attendance_records (employee_id, date, check_in_time, check_out_time, status, created_at, updated_at)
SELECT 
    (SELECT id FROM employee_profiles ORDER BY RANDOM() LIMIT 1),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::date,
    ((DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp + floor(random() * 7200 + 25200) * INTERVAL '1 second'),
    ((DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp + floor(random() * 7200 + 61200) * INTERVAL '1 second'),
    (ARRAY['normal', 'late', 'early_leave', 'absent'])[floor(random() * 4 + 1)],
    NOW(),
    NOW()
WHERE (SELECT COUNT(*) FROM attendance_records) < 2000
LIMIT 2000 - (SELECT COUNT(*) FROM attendance_records);

-- 10. 插入更多报销数据（确保时间跨度，如果少于500条）
INSERT INTO expense_claims (user_id, category, amount, description, expense_date, status, created_at, updated_at)
SELECT 
    (SELECT id FROM users ORDER BY RANDOM() LIMIT 1),
    (ARRAY['差旅费', '交通费', '住宿费', '餐饮费', '办公用品', '培训费', '其他'])[floor(random() * 7 + 1)],
    (random() * 4900 + 100)::numeric(10,2),
    '报销描述 #' || (SELECT COALESCE(MAX(id), 0) + ROW_NUMBER() OVER () FROM expense_claims),
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::date,
    (ARRAY['draft', 'submitted', 'approved', 'rejected', 'reimbursed'])[floor(random() * 5 + 1)],
    (DATE '2025-12-01' + floor(random() * 200) * INTERVAL '1 day')::timestamp,
    NOW()
WHERE (SELECT COUNT(*) FROM expense_claims) < 500
LIMIT 500 - (SELECT COUNT(*) FROM expense_claims);

-- 显示最终统计
SELECT 'users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL
SELECT 'inventory_items', COUNT(*) FROM inventory_items
UNION ALL
SELECT 'finance_accounts', COUNT(*) FROM finance_accounts
UNION ALL
SELECT 'disk_folders', COUNT(*) FROM disk_folders
UNION ALL
SELECT 'knowledge_articles', COUNT(*) FROM knowledge_articles
UNION ALL
SELECT 'employee_profiles', COUNT(*) FROM employee_profiles
UNION ALL
SELECT 'attendance_records', COUNT(*) FROM attendance_records
UNION ALL
SELECT 'expense_claims', COUNT(*) FROM expense_claims
UNION ALL
SELECT 'receivables', COUNT(*) FROM receivables
UNION ALL
SELECT 'payables', COUNT(*) FROM payables
UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL
SELECT 'service_tickets', COUNT(*) FROM service_tickets
UNION ALL
SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
UNION ALL
SELECT 'sales_opportunities', COUNT(*) FROM sales_opportunities;