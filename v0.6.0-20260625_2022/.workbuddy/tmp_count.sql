SELECT 'users' tbl,count(*) n FROM users WHERE deleted_at IS NULL
UNION ALL SELECT 'customers',count(*) FROM customers
UNION ALL SELECT 'projects',count(*) FROM projects
UNION ALL SELECT 'work_orders',count(*) FROM work_orders
UNION ALL SELECT 'repair_orders',count(*) FROM repair_orders
UNION ALL SELECT 'repair_methods',count(*) FROM repair_methods
UNION ALL SELECT 'repair_shipments',count(*) FROM repair_shipments
UNION ALL SELECT 'repair_step_photos',count(*) FROM repair_step_photos
UNION ALL SELECT 'leads',count(*) FROM leads
UNION ALL SELECT 'opps',count(*) FROM opportunities
UNION ALL SELECT 'attendance',count(*) FROM attendance_records
UNION ALL SELECT 'expense',count(*) FROM expense_claims
UNION ALL SELECT 'approvals',count(*) FROM approval_records
UNION ALL SELECT 'warranty',count(*) FROM warranties
UNION ALL SELECT 'departments',count(*) FROM departments
UNION ALL SELECT 'positions',count(*) FROM positions
UNION ALL SELECT 'system_dicts',count(*) FROM system_dicts
ORDER BY tbl;
