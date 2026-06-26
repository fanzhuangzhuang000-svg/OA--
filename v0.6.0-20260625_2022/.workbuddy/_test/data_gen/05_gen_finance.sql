BEGIN;
SET LOCAL synchronous_commit = OFF;
-- expense_claims
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (1, 'EXP-2026-00001', 81, 'travel', 500, 'travel类报销单 #1', 'draft', 76, NULL, NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (2, 'EXP-2026-00002', 82, 'meal', 637, 'meal类报销单 #2', 'submitted', 78, NULL, NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (3, 'EXP-2026-00003', 83, 'office', 774, 'office类报销单 #3', 'approved', 78, NULL, NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (4, 'EXP-2026-00004', 84, 'training', 911, 'training类报销单 #4', 'paid', 76, 911, NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (5, 'EXP-2026-00005', 85, 'other', 1048, 'other类报销单 #5', 'rejected', 78, NULL, NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (6, 'EXP-2026-00006', 86, 'travel', 1185, 'travel类报销单 #6', 'draft', 78, NULL, NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (7, 'EXP-2026-00007', 87, 'meal', 1322, 'meal类报销单 #7', 'submitted', 76, NULL, NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (8, 'EXP-2026-00008', 88, 'office', 1459, 'office类报销单 #8', 'approved', 78, NULL, NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (9, 'EXP-2026-00009', 81, 'training', 1596, 'training类报销单 #9', 'paid', 78, 1596, NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (10, 'EXP-2026-00010', 82, 'other', 1733, 'other类报销单 #10', 'rejected', 76, NULL, NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (11, 'EXP-2026-00011', 83, 'travel', 1870, 'travel类报销单 #11', 'draft', 78, NULL, NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (12, 'EXP-2026-00012', 84, 'meal', 2007, 'meal类报销单 #12', 'submitted', 78, NULL, NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (13, 'EXP-2026-00013', 85, 'office', 2144, 'office类报销单 #13', 'approved', 76, NULL, NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (14, 'EXP-2026-00014', 86, 'training', 2281, 'training类报销单 #14', 'paid', 78, 2281, NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (15, 'EXP-2026-00015', 87, 'other', 2418, 'other类报销单 #15', 'rejected', 78, NULL, NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (16, 'EXP-2026-00016', 88, 'travel', 2555, 'travel类报销单 #16', 'draft', 76, NULL, NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (17, 'EXP-2026-00017', 81, 'meal', 2692, 'meal类报销单 #17', 'submitted', 78, NULL, NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (18, 'EXP-2026-00018', 82, 'office', 2829, 'office类报销单 #18', 'approved', 78, NULL, NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (19, 'EXP-2026-00019', 83, 'training', 2966, 'training类报销单 #19', 'paid', 76, 2966, NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (20, 'EXP-2026-00020', 84, 'other', 3103, 'other类报销单 #20', 'rejected', 78, NULL, NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (21, 'EXP-2026-00021', 85, 'travel', 3240, 'travel类报销单 #21', 'draft', 78, NULL, NOW() - INTERVAL '20 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (22, 'EXP-2026-00022', 86, 'meal', 3377, 'meal类报销单 #22', 'submitted', 76, NULL, NOW() - INTERVAL '21 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (23, 'EXP-2026-00023', 87, 'office', 3514, 'office类报销单 #23', 'approved', 78, NULL, NOW() - INTERVAL '22 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (24, 'EXP-2026-00024', 88, 'training', 3651, 'training类报销单 #24', 'paid', 78, 3651, NOW() - INTERVAL '23 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (25, 'EXP-2026-00025', 81, 'other', 3788, 'other类报销单 #25', 'rejected', 76, NULL, NOW() - INTERVAL '24 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (26, 'EXP-2026-00026', 82, 'travel', 3925, 'travel类报销单 #26', 'draft', 78, NULL, NOW() - INTERVAL '25 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (27, 'EXP-2026-00027', 83, 'meal', 4062, 'meal类报销单 #27', 'submitted', 78, NULL, NOW() - INTERVAL '26 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (28, 'EXP-2026-00028', 84, 'office', 4199, 'office类报销单 #28', 'approved', 76, NULL, NOW() - INTERVAL '27 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (29, 'EXP-2026-00029', 85, 'training', 4336, 'training类报销单 #29', 'paid', 78, 4336, NOW() - INTERVAL '28 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (30, 'EXP-2026-00030', 86, 'other', 4473, 'other类报销单 #30', 'rejected', 78, NULL, NOW() - INTERVAL '29 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (31, 'EXP-2026-00031', 87, 'travel', 4610, 'travel类报销单 #31', 'draft', 76, NULL, NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (32, 'EXP-2026-00032', 88, 'meal', 4747, 'meal类报销单 #32', 'submitted', 78, NULL, NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (33, 'EXP-2026-00033', 81, 'office', 4884, 'office类报销单 #33', 'approved', 78, NULL, NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (34, 'EXP-2026-00034', 82, 'training', 521, 'training类报销单 #34', 'paid', 76, 521, NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (35, 'EXP-2026-00035', 83, 'other', 658, 'other类报销单 #35', 'rejected', 78, NULL, NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (36, 'EXP-2026-00036', 84, 'travel', 795, 'travel类报销单 #36', 'draft', 78, NULL, NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (37, 'EXP-2026-00037', 85, 'meal', 932, 'meal类报销单 #37', 'submitted', 76, NULL, NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (38, 'EXP-2026-00038', 86, 'office', 1069, 'office类报销单 #38', 'approved', 78, NULL, NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (39, 'EXP-2026-00039', 87, 'training', 1206, 'training类报销单 #39', 'paid', 78, 1206, NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (40, 'EXP-2026-00040', 88, 'other', 1343, 'other类报销单 #40', 'rejected', 76, NULL, NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (41, 'EXP-2026-00041', 81, 'travel', 1480, 'travel类报销单 #41', 'draft', 78, NULL, NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (42, 'EXP-2026-00042', 82, 'meal', 1617, 'meal类报销单 #42', 'submitted', 78, NULL, NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (43, 'EXP-2026-00043', 83, 'office', 1754, 'office类报销单 #43', 'approved', 76, NULL, NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (44, 'EXP-2026-00044', 84, 'training', 1891, 'training类报销单 #44', 'paid', 78, 1891, NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (45, 'EXP-2026-00045', 85, 'other', 2028, 'other类报销单 #45', 'rejected', 78, NULL, NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (46, 'EXP-2026-00046', 86, 'travel', 2165, 'travel类报销单 #46', 'draft', 76, NULL, NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (47, 'EXP-2026-00047', 87, 'meal', 2302, 'meal类报销单 #47', 'submitted', 78, NULL, NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (48, 'EXP-2026-00048', 88, 'office', 2439, 'office类报销单 #48', 'approved', 78, NULL, NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (49, 'EXP-2026-00049', 81, 'training', 2576, 'training类报销单 #49', 'paid', 76, 2576, NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO expense_claims (id, claim_no, user_id, category, total_amount, description, status, approver_id, paid_amount, created_at, updated_at)
            VALUES (50, 'EXP-2026-00050', 82, 'other', 2713, 'other类报销单 #50', 'rejected', 78, NULL, NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
-- receivables
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (1, 1, 72, 71, 50000, 0, 50000, DATE '2026-01-01', NULL, 0, 'pending', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (2, 2, 73, 72, 65000, 39000.0, 26000.0, DATE '2026-02-02', DATE '2026-02-02', 5, 'partial', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (3, 3, 74, 73, 80000, 80000, 0, DATE '2026-03-03', DATE '2026-03-03', 0, 'fully_paid', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (4, 4, 75, 74, 95000, 0, 95000, DATE '2026-04-04', NULL, 15, 'pending', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (5, 5, 76, 75, 110000, 66000.0, 44000.0, DATE '2026-05-05', DATE '2026-05-05', 20, 'partial', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (6, 6, 77, 76, 125000, 125000, 0, DATE '2026-06-06', DATE '2026-06-06', 0, 'fully_paid', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (7, 7, 78, 77, 140000, 0, 140000, DATE '2026-01-07', NULL, 30, 'pending', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (8, 8, 79, 78, 155000, 93000.0, 62000.0, DATE '2026-02-08', DATE '2026-02-08', 35, 'partial', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (9, 9, 80, 79, 170000, 170000, 0, DATE '2026-03-09', DATE '2026-03-09', 0, 'fully_paid', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (10, 10, 81, 80, 185000, 0, 185000, DATE '2026-04-10', NULL, 45, 'pending', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (11, 11, 82, 81, 200000, 120000.0, 80000.0, DATE '2026-05-11', DATE '2026-05-11', 50, 'partial', NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (12, 12, 83, 82, 215000, 215000, 0, DATE '2026-06-12', DATE '2026-06-12', 0, 'fully_paid', NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (13, 13, 84, 83, 230000, 0, 230000, DATE '2026-01-13', NULL, 0, 'pending', NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (14, 14, 85, 84, 245000, 147000.0, 98000.0, DATE '2026-02-14', DATE '2026-02-14', 5, 'partial', NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (15, 15, 86, 85, 60000, 60000, 0, DATE '2026-03-15', DATE '2026-03-15', 0, 'fully_paid', NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (16, 16, 87, 71, 75000, 0, 75000, DATE '2026-04-16', NULL, 15, 'pending', NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (17, 17, 88, 72, 90000, 54000.0, 36000.0, DATE '2026-05-17', DATE '2026-05-17', 20, 'partial', NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (18, 18, 89, 73, 105000, 105000, 0, DATE '2026-06-18', DATE '2026-06-18', 0, 'fully_paid', NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (19, 19, 90, 74, 120000, 0, 120000, DATE '2026-01-19', NULL, 30, 'pending', NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (20, 20, 91, 75, 135000, 81000.0, 54000.0, DATE '2026-02-20', DATE '2026-02-20', 35, 'partial', NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (21, 21, 92, 76, 150000, 150000, 0, DATE '2026-03-21', DATE '2026-03-21', 0, 'fully_paid', NOW() - INTERVAL '20 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (22, 22, 93, 77, 165000, 0, 165000, DATE '2026-04-22', NULL, 45, 'pending', NOW() - INTERVAL '21 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (23, 23, 94, 78, 180000, 108000.0, 72000.0, DATE '2026-05-23', DATE '2026-05-23', 50, 'partial', NOW() - INTERVAL '22 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (24, 24, 95, 79, 195000, 195000, 0, DATE '2026-06-24', DATE '2026-06-24', 0, 'fully_paid', NOW() - INTERVAL '23 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (25, 25, 96, 80, 210000, 0, 210000, DATE '2026-01-25', NULL, 0, 'pending', NOW() - INTERVAL '24 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (26, 26, 97, 81, 225000, 135000.0, 90000.0, DATE '2026-02-26', DATE '2026-02-26', 5, 'partial', NOW() - INTERVAL '25 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (27, 27, 98, 82, 240000, 240000, 0, DATE '2026-03-27', DATE '2026-03-27', 0, 'fully_paid', NOW() - INTERVAL '26 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (28, 29, 99, 83, 55000, 0, 55000, DATE '2026-04-28', NULL, 15, 'pending', NOW() - INTERVAL '27 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (29, 30, 100, 84, 70000, 42000.0, 28000.0, DATE '2026-05-01', DATE '2026-05-01', 20, 'partial', NOW() - INTERVAL '28 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (30, 31, 101, 85, 85000, 85000, 0, DATE '2026-06-02', DATE '2026-06-02', 0, 'fully_paid', NOW() - INTERVAL '29 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (31, 1, 72, 71, 100000, 0, 100000, DATE '2026-01-03', NULL, 30, 'pending', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (32, 2, 73, 72, 115000, 69000.0, 46000.0, DATE '2026-02-04', DATE '2026-02-04', 35, 'partial', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (33, 3, 74, 73, 130000, 130000, 0, DATE '2026-03-05', DATE '2026-03-05', 0, 'fully_paid', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (34, 4, 75, 74, 145000, 0, 145000, DATE '2026-04-06', NULL, 45, 'pending', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (35, 5, 76, 75, 160000, 96000.0, 64000.0, DATE '2026-05-07', DATE '2026-05-07', 50, 'partial', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (36, 6, 77, 76, 175000, 175000, 0, DATE '2026-06-08', DATE '2026-06-08', 0, 'fully_paid', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (37, 7, 78, 77, 190000, 0, 190000, DATE '2026-01-09', NULL, 0, 'pending', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (38, 8, 79, 78, 205000, 123000.0, 82000.0, DATE '2026-02-10', DATE '2026-02-10', 5, 'partial', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (39, 9, 80, 79, 220000, 220000, 0, DATE '2026-03-11', DATE '2026-03-11', 0, 'fully_paid', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO receivables (id, customer_id, project_id, contract_id, amount, received_amount, remaining_amount, due_date, received_date, overdue_days, status, created_at, updated_at)
            VALUES (40, 10, 81, 80, 235000, 0, 235000, DATE '2026-04-12', NULL, 15, 'pending', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
-- payables
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (1, 6, 72, 20000, 0, 20000, DATE '2026-01-01', NULL, 'monthly', 'pending', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (2, 7, 73, 28000, 14000.0, 14000.0, DATE '2026-02-02', DATE '2026-02-02', 'monthly', 'partial', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (3, 8, 74, 36000, 36000, 0, DATE '2026-03-03', DATE '2026-03-03', 'monthly', 'fully_paid', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (4, 9, 75, 44000, 0, 44000, DATE '2026-04-04', NULL, 'monthly', 'pending', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (5, 10, 76, 52000, 26000.0, 26000.0, DATE '2026-05-05', DATE '2026-05-05', 'monthly', 'partial', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (6, 6, 77, 60000, 60000, 0, DATE '2026-06-06', DATE '2026-06-06', 'monthly', 'fully_paid', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (7, 7, 78, 68000, 0, 68000, DATE '2026-01-07', NULL, 'monthly', 'pending', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (8, 8, 79, 76000, 38000.0, 38000.0, DATE '2026-02-08', DATE '2026-02-08', 'monthly', 'partial', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (9, 9, 80, 84000, 84000, 0, DATE '2026-03-09', DATE '2026-03-09', 'monthly', 'fully_paid', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (10, 10, 81, 92000, 0, 92000, DATE '2026-04-10', NULL, 'monthly', 'pending', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (11, 6, 82, 100000, 50000.0, 50000.0, DATE '2026-05-11', DATE '2026-05-11', 'monthly', 'partial', NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (12, 7, 83, 108000, 108000, 0, DATE '2026-06-12', DATE '2026-06-12', 'monthly', 'fully_paid', NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (13, 8, 84, 116000, 0, 116000, DATE '2026-01-13', NULL, 'monthly', 'pending', NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (14, 9, 85, 24000, 12000.0, 12000.0, DATE '2026-02-14', DATE '2026-02-14', 'monthly', 'partial', NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (15, 10, 86, 32000, 32000, 0, DATE '2026-03-15', DATE '2026-03-15', 'monthly', 'fully_paid', NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (16, 6, 87, 40000, 0, 40000, DATE '2026-04-16', NULL, 'monthly', 'pending', NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (17, 7, 88, 48000, 24000.0, 24000.0, DATE '2026-05-17', DATE '2026-05-17', 'monthly', 'partial', NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (18, 8, 89, 56000, 56000, 0, DATE '2026-06-18', DATE '2026-06-18', 'monthly', 'fully_paid', NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (19, 9, 90, 64000, 0, 64000, DATE '2026-01-19', NULL, 'monthly', 'pending', NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (20, 10, 91, 72000, 36000.0, 36000.0, DATE '2026-02-20', DATE '2026-02-20', 'monthly', 'partial', NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (21, 6, 92, 80000, 80000, 0, DATE '2026-03-21', DATE '2026-03-21', 'monthly', 'fully_paid', NOW() - INTERVAL '20 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (22, 7, 93, 88000, 0, 88000, DATE '2026-04-22', NULL, 'monthly', 'pending', NOW() - INTERVAL '21 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (23, 8, 94, 96000, 48000.0, 48000.0, DATE '2026-05-23', DATE '2026-05-23', 'monthly', 'partial', NOW() - INTERVAL '22 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (24, 9, 95, 104000, 104000, 0, DATE '2026-06-24', DATE '2026-06-24', 'monthly', 'fully_paid', NOW() - INTERVAL '23 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (25, 10, 96, 112000, 0, 112000, DATE '2026-01-25', NULL, 'monthly', 'pending', NOW() - INTERVAL '24 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (26, 6, 97, 20000, 10000.0, 10000.0, DATE '2026-02-26', DATE '2026-02-26', 'monthly', 'partial', NOW() - INTERVAL '25 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (27, 7, 98, 28000, 28000, 0, DATE '2026-03-27', DATE '2026-03-27', 'monthly', 'fully_paid', NOW() - INTERVAL '26 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (28, 8, 99, 36000, 0, 36000, DATE '2026-04-28', NULL, 'monthly', 'pending', NOW() - INTERVAL '27 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (29, 9, 100, 44000, 22000.0, 22000.0, DATE '2026-05-01', DATE '2026-05-01', 'monthly', 'partial', NOW() - INTERVAL '28 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (30, 10, 101, 52000, 52000, 0, DATE '2026-06-02', DATE '2026-06-02', 'monthly', 'fully_paid', NOW() - INTERVAL '29 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (31, 6, 72, 60000, 0, 60000, DATE '2026-01-03', NULL, 'monthly', 'pending', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (32, 7, 73, 68000, 34000.0, 34000.0, DATE '2026-02-04', DATE '2026-02-04', 'monthly', 'partial', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (33, 8, 74, 76000, 76000, 0, DATE '2026-03-05', DATE '2026-03-05', 'monthly', 'fully_paid', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (34, 9, 75, 84000, 0, 84000, DATE '2026-04-06', NULL, 'monthly', 'pending', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (35, 10, 76, 92000, 46000.0, 46000.0, DATE '2026-05-07', DATE '2026-05-07', 'monthly', 'partial', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (36, 6, 77, 100000, 100000, 0, DATE '2026-06-08', DATE '2026-06-08', 'monthly', 'fully_paid', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (37, 7, 78, 108000, 0, 108000, DATE '2026-01-09', NULL, 'monthly', 'pending', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (38, 8, 79, 116000, 58000.0, 58000.0, DATE '2026-02-10', DATE '2026-02-10', 'monthly', 'partial', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (39, 9, 80, 24000, 24000, 0, DATE '2026-03-11', DATE '2026-03-11', 'monthly', 'fully_paid', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO payables (id, supplier_id, project_id, amount, paid_amount, remaining_amount, due_date, paid_date, payment_term, status, created_at, updated_at)
            VALUES (40, 10, 81, 32000, 0, 32000, DATE '2026-04-12', NULL, 'monthly', 'pending', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
-- finance_payments
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (1, 1, NULL, 1, 5000, DATE '2026-01-01', 'transfer', 'V-2026-00001', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (2, 2, NULL, 2, 5700, DATE '2026-02-02', 'cash', 'V-2026-00002', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (3, 3, NULL, 3, 6400, DATE '2026-03-03', 'check', 'V-2026-00003', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (4, 4, NULL, 4, 7100, DATE '2026-04-04', 'transfer', 'V-2026-00004', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (5, 5, NULL, 1, 7800, DATE '2026-05-05', 'cash', 'V-2026-00005', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (6, 6, NULL, 2, 8500, DATE '2026-06-06', 'check', 'V-2026-00006', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (7, 7, NULL, 3, 9200, DATE '2026-01-07', 'transfer', 'V-2026-00007', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (8, 8, NULL, 4, 9900, DATE '2026-02-08', 'cash', 'V-2026-00008', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (9, 9, NULL, 1, 10600, DATE '2026-03-09', 'check', 'V-2026-00009', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (10, 10, NULL, 2, 11300, DATE '2026-04-10', 'transfer', 'V-2026-00010', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (11, 11, NULL, 3, 12000, DATE '2026-05-11', 'cash', 'V-2026-00011', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (12, 12, NULL, 4, 12700, DATE '2026-06-12', 'check', 'V-2026-00012', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (13, 13, NULL, 1, 13400, DATE '2026-01-13', 'transfer', 'V-2026-00013', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (14, 14, NULL, 2, 14100, DATE '2026-02-14', 'cash', 'V-2026-00014', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (15, 15, NULL, 3, 14800, DATE '2026-03-15', 'check', 'V-2026-00015', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (16, 16, NULL, 4, 15500, DATE '2026-04-16', 'transfer', 'V-2026-00016', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (17, 17, NULL, 1, 16200, DATE '2026-05-17', 'cash', 'V-2026-00017', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (18, 18, NULL, 2, 16900, DATE '2026-06-18', 'check', 'V-2026-00018', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (19, 19, NULL, 3, 17600, DATE '2026-01-19', 'transfer', 'V-2026-00019', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (20, 20, NULL, 4, 18300, DATE '2026-02-20', 'cash', 'V-2026-00020', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (21, 21, NULL, 1, 19000, DATE '2026-03-21', 'check', 'V-2026-00021', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (22, 22, NULL, 2, 19700, DATE '2026-04-22', 'transfer', 'V-2026-00022', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (23, 23, NULL, 3, 20400, DATE '2026-05-23', 'cash', 'V-2026-00023', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (24, 24, NULL, 4, 21100, DATE '2026-06-24', 'check', 'V-2026-00024', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (25, 25, NULL, 1, 21800, DATE '2026-01-25', 'transfer', 'V-2026-00025', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (26, 26, NULL, 2, 22500, DATE '2026-02-26', 'cash', 'V-2026-00026', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (27, 27, NULL, 3, 23200, DATE '2026-03-27', 'check', 'V-2026-00027', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (28, 28, NULL, 4, 23900, DATE '2026-04-28', 'transfer', 'V-2026-00028', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (29, 29, NULL, 1, 24600, DATE '2026-05-01', 'cash', 'V-2026-00029', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (30, 30, NULL, 2, 25300, DATE '2026-06-02', 'check', 'V-2026-00030', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (31, NULL, 1, 3, 26000, DATE '2026-01-03', 'transfer', 'V-2026-00031', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (32, NULL, 2, 4, 26700, DATE '2026-02-04', 'cash', 'V-2026-00032', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (33, NULL, 3, 1, 27400, DATE '2026-03-05', 'check', 'V-2026-00033', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (34, NULL, 4, 2, 28100, DATE '2026-04-06', 'transfer', 'V-2026-00034', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (35, NULL, 5, 3, 28800, DATE '2026-05-07', 'cash', 'V-2026-00035', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (36, NULL, 6, 4, 29500, DATE '2026-06-08', 'check', 'V-2026-00036', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (37, NULL, 7, 1, 30200, DATE '2026-01-09', 'transfer', 'V-2026-00037', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (38, NULL, 8, 2, 30900, DATE '2026-02-10', 'cash', 'V-2026-00038', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (39, NULL, 9, 3, 31600, DATE '2026-03-11', 'check', 'V-2026-00039', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (40, NULL, 10, 4, 32300, DATE '2026-04-12', 'transfer', 'V-2026-00040', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (41, NULL, 11, 1, 33000, DATE '2026-05-13', 'cash', 'V-2026-00041', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (42, NULL, 12, 2, 33700, DATE '2026-06-14', 'check', 'V-2026-00042', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (43, NULL, 13, 3, 34400, DATE '2026-01-15', 'transfer', 'V-2026-00043', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (44, NULL, 14, 4, 35100, DATE '2026-02-16', 'cash', 'V-2026-00044', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (45, NULL, 15, 1, 35800, DATE '2026-03-17', 'check', 'V-2026-00045', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (46, NULL, 16, 2, 36500, DATE '2026-04-18', 'transfer', 'V-2026-00046', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (47, NULL, 17, 3, 37200, DATE '2026-05-19', 'cash', 'V-2026-00047', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (48, NULL, 18, 4, 37900, DATE '2026-06-20', 'check', 'V-2026-00048', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (49, NULL, 19, 1, 38600, DATE '2026-01-21', 'transfer', 'V-2026-00049', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (50, NULL, 20, 2, 39300, DATE '2026-02-22', 'cash', 'V-2026-00050', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (51, NULL, 21, 3, 40000, DATE '2026-03-23', 'check', 'V-2026-00051', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (52, NULL, 22, 4, 40700, DATE '2026-04-24', 'transfer', 'V-2026-00052', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (53, NULL, 23, 1, 41400, DATE '2026-05-25', 'cash', 'V-2026-00053', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (54, NULL, 24, 2, 42100, DATE '2026-06-26', 'check', 'V-2026-00054', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (55, NULL, 25, 3, 42800, DATE '2026-01-27', 'transfer', 'V-2026-00055', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (56, NULL, 26, 4, 43500, DATE '2026-02-28', 'cash', 'V-2026-00056', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (57, NULL, 27, 1, 44200, DATE '2026-03-01', 'check', 'V-2026-00057', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (58, NULL, 28, 2, 44900, DATE '2026-04-02', 'transfer', 'V-2026-00058', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (59, NULL, 29, 3, 45600, DATE '2026-05-03', 'cash', 'V-2026-00059', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
INSERT INTO finance_payments (id, receivable_id, payable_id, account_id, amount, payment_date, method, voucher_no, operator, created_at, updated_at)
            VALUES (60, NULL, 30, 4, 46300, DATE '2026-06-04', 'check', 'V-2026-00060', 'finance_op', NOW(), NOW()) ON CONFLICT DO NOTHING;
-- purchase_payment_requests
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (1, 'PPR-2026-00001', 1, 6, 10000, 'installment', DATE '2026-01-01', 'pending', '申请人0', 75, 76, NOW() - INTERVAL '0 days', '采购付款申请 #1', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (2, 'PPR-2026-00002', 2, 7, 14000, 'installment', DATE '2026-02-02', 'approved', '申请人1', 76, 78, NOW() - INTERVAL '1 days', '采购付款申请 #2', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (3, 'PPR-2026-00003', 3, 8, 18000, 'installment', DATE '2026-03-03', 'paid', '申请人2', 77, 76, NOW() - INTERVAL '2 days', '采购付款申请 #3', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (4, 'PPR-2026-00004', 4, 9, 22000, 'installment', DATE '2026-04-04', 'rejected', '申请人3', 78, 78, NOW() - INTERVAL '3 days', '采购付款申请 #4', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (5, 'PPR-2026-00005', 5, 10, 26000, 'installment', DATE '2026-05-05', 'pending', '申请人4', 79, 76, NOW() - INTERVAL '4 days', '采购付款申请 #5', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (6, 'PPR-2026-00006', 6, 6, 30000, 'installment', DATE '2026-06-06', 'approved', '申请人5', 80, 78, NOW() - INTERVAL '5 days', '采购付款申请 #6', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (7, 'PPR-2026-00007', 7, 7, 34000, 'installment', DATE '2026-01-07', 'paid', '申请人6', 81, 76, NOW() - INTERVAL '6 days', '采购付款申请 #7', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (8, 'PPR-2026-00008', 8, 8, 38000, 'installment', DATE '2026-02-08', 'rejected', '申请人7', 82, 78, NOW() - INTERVAL '7 days', '采购付款申请 #8', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (9, 'PPR-2026-00009', 9, 9, 42000, 'installment', DATE '2026-03-09', 'pending', '申请人8', 83, 76, NOW() - INTERVAL '8 days', '采购付款申请 #9', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (10, 'PPR-2026-00010', 10, 10, 46000, 'installment', DATE '2026-04-10', 'approved', '申请人9', 84, 78, NOW() - INTERVAL '9 days', '采购付款申请 #10', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (11, 'PPR-2026-00011', 11, 6, 50000, 'installment', DATE '2026-05-11', 'paid', '申请人10', 75, 76, NOW() - INTERVAL '10 days', '采购付款申请 #11', NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (12, 'PPR-2026-00012', 12, 7, 54000, 'installment', DATE '2026-06-12', 'rejected', '申请人11', 76, 78, NOW() - INTERVAL '11 days', '采购付款申请 #12', NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (13, 'PPR-2026-00013', 13, 8, 58000, 'installment', DATE '2026-01-13', 'pending', '申请人12', 77, 76, NOW() - INTERVAL '12 days', '采购付款申请 #13', NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (14, 'PPR-2026-00014', 14, 9, 62000, 'installment', DATE '2026-02-14', 'approved', '申请人13', 78, 78, NOW() - INTERVAL '13 days', '采购付款申请 #14', NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (15, 'PPR-2026-00015', 15, 10, 66000, 'installment', DATE '2026-03-15', 'paid', '申请人14', 79, 76, NOW() - INTERVAL '14 days', '采购付款申请 #15', NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (16, 'PPR-2026-00016', 1, 6, 70000, 'installment', DATE '2026-04-16', 'rejected', '申请人15', 80, 78, NOW() - INTERVAL '15 days', '采购付款申请 #16', NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (17, 'PPR-2026-00017', 2, 7, 74000, 'installment', DATE '2026-05-17', 'pending', '申请人16', 81, 76, NOW() - INTERVAL '16 days', '采购付款申请 #17', NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (18, 'PPR-2026-00018', 3, 8, 78000, 'installment', DATE '2026-06-18', 'approved', '申请人17', 82, 78, NOW() - INTERVAL '17 days', '采购付款申请 #18', NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (19, 'PPR-2026-00019', 4, 9, 82000, 'installment', DATE '2026-01-19', 'paid', '申请人18', 83, 76, NOW() - INTERVAL '18 days', '采购付款申请 #19', NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (20, 'PPR-2026-00020', 5, 10, 86000, 'installment', DATE '2026-02-20', 'rejected', '申请人19', 84, 78, NOW() - INTERVAL '19 days', '采购付款申请 #20', NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (21, 'PPR-2026-00021', 6, 6, 10000, 'installment', DATE '2026-03-21', 'pending', '申请人20', 75, 76, NOW() - INTERVAL '0 days', '采购付款申请 #21', NOW() - INTERVAL '20 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (22, 'PPR-2026-00022', 7, 7, 14000, 'installment', DATE '2026-04-22', 'approved', '申请人21', 76, 78, NOW() - INTERVAL '1 days', '采购付款申请 #22', NOW() - INTERVAL '21 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (23, 'PPR-2026-00023', 8, 8, 18000, 'installment', DATE '2026-05-23', 'paid', '申请人22', 77, 76, NOW() - INTERVAL '2 days', '采购付款申请 #23', NOW() - INTERVAL '22 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (24, 'PPR-2026-00024', 9, 9, 22000, 'installment', DATE '2026-06-24', 'rejected', '申请人23', 78, 78, NOW() - INTERVAL '3 days', '采购付款申请 #24', NOW() - INTERVAL '23 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (25, 'PPR-2026-00025', 10, 10, 26000, 'installment', DATE '2026-01-25', 'pending', '申请人24', 79, 76, NOW() - INTERVAL '4 days', '采购付款申请 #25', NOW() - INTERVAL '24 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (26, 'PPR-2026-00026', 11, 6, 30000, 'installment', DATE '2026-02-26', 'approved', '申请人25', 80, 78, NOW() - INTERVAL '5 days', '采购付款申请 #26', NOW() - INTERVAL '25 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (27, 'PPR-2026-00027', 12, 7, 34000, 'installment', DATE '2026-03-27', 'paid', '申请人26', 81, 76, NOW() - INTERVAL '6 days', '采购付款申请 #27', NOW() - INTERVAL '26 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (28, 'PPR-2026-00028', 13, 8, 38000, 'installment', DATE '2026-04-28', 'rejected', '申请人27', 82, 78, NOW() - INTERVAL '7 days', '采购付款申请 #28', NOW() - INTERVAL '27 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (29, 'PPR-2026-00029', 14, 9, 42000, 'installment', DATE '2026-05-01', 'pending', '申请人28', 83, 76, NOW() - INTERVAL '8 days', '采购付款申请 #29', NOW() - INTERVAL '28 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payment_requests (id, code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, approver_id, approved_at, reason, created_at, updated_at)
            VALUES (30, 'PPR-2026-00030', 15, 10, 46000, 'installment', DATE '2026-06-02', 'approved', '申请人29', 84, 78, NOW() - INTERVAL '9 days', '采购付款申请 #30', NOW() - INTERVAL '29 days', NOW()) ON CONFLICT DO NOTHING;
-- purchase_payments
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (1, 'PP-2026-00001', 1, 1, 6, 10000, 'transfer', DATE '2026-01-01', 'PV-2026-00001', '周会计', 79, 'success', '采购付款记录 #1', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (2, 'PP-2026-00002', 2, 2, 7, 14000, 'transfer', DATE '2026-02-02', 'PV-2026-00002', '周会计', 79, 'success', '采购付款记录 #2', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (3, 'PP-2026-00003', 3, 3, 8, 18000, 'transfer', DATE '2026-03-03', 'PV-2026-00003', '周会计', 79, 'success', '采购付款记录 #3', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (4, 'PP-2026-00004', 4, 4, 9, 22000, 'transfer', DATE '2026-04-04', 'PV-2026-00004', '周会计', 79, 'success', '采购付款记录 #4', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (5, 'PP-2026-00005', 5, 5, 10, 26000, 'transfer', DATE '2026-05-05', 'PV-2026-00005', '周会计', 79, 'success', '采购付款记录 #5', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (6, 'PP-2026-00006', 6, 6, 6, 30000, 'transfer', DATE '2026-06-06', 'PV-2026-00006', '周会计', 79, 'success', '采购付款记录 #6', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (7, 'PP-2026-00007', 7, 7, 7, 34000, 'transfer', DATE '2026-01-07', 'PV-2026-00007', '周会计', 79, 'success', '采购付款记录 #7', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (8, 'PP-2026-00008', 8, 8, 8, 38000, 'transfer', DATE '2026-02-08', 'PV-2026-00008', '周会计', 79, 'success', '采购付款记录 #8', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (9, 'PP-2026-00009', 9, 9, 9, 42000, 'transfer', DATE '2026-03-09', 'PV-2026-00009', '周会计', 79, 'success', '采购付款记录 #9', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (10, 'PP-2026-00010', 10, 10, 10, 46000, 'transfer', DATE '2026-04-10', 'PV-2026-00010', '周会计', 79, 'success', '采购付款记录 #10', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (11, 'PP-2026-00011', 11, 11, 6, 50000, 'transfer', DATE '2026-05-11', 'PV-2026-00011', '周会计', 79, 'success', '采购付款记录 #11', NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (12, 'PP-2026-00012', 12, 12, 7, 54000, 'transfer', DATE '2026-06-12', 'PV-2026-00012', '周会计', 79, 'success', '采购付款记录 #12', NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (13, 'PP-2026-00013', 13, 13, 8, 58000, 'transfer', DATE '2026-01-13', 'PV-2026-00013', '周会计', 79, 'success', '采购付款记录 #13', NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (14, 'PP-2026-00014', 14, 14, 9, 62000, 'transfer', DATE '2026-02-14', 'PV-2026-00014', '周会计', 79, 'success', '采购付款记录 #14', NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (15, 'PP-2026-00015', 15, 15, 10, 66000, 'transfer', DATE '2026-03-15', 'PV-2026-00015', '周会计', 79, 'success', '采购付款记录 #15', NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (16, 'PP-2026-00016', 16, 1, 6, 70000, 'transfer', DATE '2026-04-16', 'PV-2026-00016', '周会计', 79, 'success', '采购付款记录 #16', NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (17, 'PP-2026-00017', 17, 2, 7, 74000, 'transfer', DATE '2026-05-17', 'PV-2026-00017', '周会计', 79, 'success', '采购付款记录 #17', NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (18, 'PP-2026-00018', 18, 3, 8, 78000, 'transfer', DATE '2026-06-18', 'PV-2026-00018', '周会计', 79, 'success', '采购付款记录 #18', NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (19, 'PP-2026-00019', 19, 4, 9, 82000, 'transfer', DATE '2026-01-19', 'PV-2026-00019', '周会计', 79, 'success', '采购付款记录 #19', NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (20, 'PP-2026-00020', 20, 5, 10, 86000, 'transfer', DATE '2026-02-20', 'PV-2026-00020', '周会计', 79, 'success', '采购付款记录 #20', NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (21, 'PP-2026-00021', 21, 6, 6, 10000, 'transfer', DATE '2026-03-21', 'PV-2026-00021', '周会计', 79, 'success', '采购付款记录 #21', NOW() - INTERVAL '20 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (22, 'PP-2026-00022', 22, 7, 7, 14000, 'transfer', DATE '2026-04-22', 'PV-2026-00022', '周会计', 79, 'success', '采购付款记录 #22', NOW() - INTERVAL '21 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (23, 'PP-2026-00023', 23, 8, 8, 18000, 'transfer', DATE '2026-05-23', 'PV-2026-00023', '周会计', 79, 'success', '采购付款记录 #23', NOW() - INTERVAL '22 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (24, 'PP-2026-00024', 24, 9, 9, 22000, 'transfer', DATE '2026-06-24', 'PV-2026-00024', '周会计', 79, 'success', '采购付款记录 #24', NOW() - INTERVAL '23 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (25, 'PP-2026-00025', 25, 10, 10, 26000, 'transfer', DATE '2026-01-25', 'PV-2026-00025', '周会计', 79, 'success', '采购付款记录 #25', NOW() - INTERVAL '24 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (26, 'PP-2026-00026', 26, 11, 6, 30000, 'transfer', DATE '2026-02-26', 'PV-2026-00026', '周会计', 79, 'success', '采购付款记录 #26', NOW() - INTERVAL '25 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (27, 'PP-2026-00027', 27, 12, 7, 34000, 'transfer', DATE '2026-03-27', 'PV-2026-00027', '周会计', 79, 'success', '采购付款记录 #27', NOW() - INTERVAL '26 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (28, 'PP-2026-00028', 28, 13, 8, 38000, 'transfer', DATE '2026-04-28', 'PV-2026-00028', '周会计', 79, 'success', '采购付款记录 #28', NOW() - INTERVAL '27 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (29, 'PP-2026-00029', 29, 14, 9, 42000, 'transfer', DATE '2026-05-01', 'PV-2026-00029', '周会计', 79, 'success', '采购付款记录 #29', NOW() - INTERVAL '28 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO purchase_payments (id, code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark, created_at, updated_at)
            VALUES (30, 'PP-2026-00030', 30, 15, 10, 46000, 'transfer', DATE '2026-06-02', 'PV-2026-00030', '周会计', 79, 'success', '采购付款记录 #30', NOW() - INTERVAL '29 days', NOW()) ON CONFLICT DO NOTHING;
-- fuel_card_recharges
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (1, 1, 500, DATE '2026-01-01', 'transfer', '财务操作员', 'FR-2026-00001', NOW() - INTERVAL '0 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (2, 2, 700, DATE '2026-02-02', 'cash', '财务操作员', 'FR-2026-00002', NOW() - INTERVAL '1 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (3, 3, 900, DATE '2026-03-03', 'transfer', '财务操作员', 'FR-2026-00003', NOW() - INTERVAL '2 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (4, 4, 1100, DATE '2026-04-04', 'cash', '财务操作员', 'FR-2026-00004', NOW() - INTERVAL '3 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (5, 5, 1300, DATE '2026-05-05', 'transfer', '财务操作员', 'FR-2026-00005', NOW() - INTERVAL '4 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (6, 6, 1500, DATE '2026-06-06', 'cash', '财务操作员', 'FR-2026-00006', NOW() - INTERVAL '5 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (7, 7, 1700, DATE '2026-01-07', 'transfer', '财务操作员', 'FR-2026-00007', NOW() - INTERVAL '6 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (8, 8, 1900, DATE '2026-02-08', 'cash', '财务操作员', 'FR-2026-00008', NOW() - INTERVAL '7 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (9, 1, 2100, DATE '2026-03-09', 'transfer', '财务操作员', 'FR-2026-00009', NOW() - INTERVAL '8 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (10, 2, 2300, DATE '2026-04-10', 'cash', '财务操作员', 'FR-2026-00010', NOW() - INTERVAL '9 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (11, 3, 2500, DATE '2026-05-11', 'transfer', '财务操作员', 'FR-2026-00011', NOW() - INTERVAL '10 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (12, 4, 2700, DATE '2026-06-12', 'cash', '财务操作员', 'FR-2026-00012', NOW() - INTERVAL '11 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (13, 5, 2900, DATE '2026-01-13', 'transfer', '财务操作员', 'FR-2026-00013', NOW() - INTERVAL '12 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (14, 6, 3100, DATE '2026-02-14', 'cash', '财务操作员', 'FR-2026-00014', NOW() - INTERVAL '13 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (15, 7, 3300, DATE '2026-03-15', 'transfer', '财务操作员', 'FR-2026-00015', NOW() - INTERVAL '14 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (16, 8, 500, DATE '2026-04-16', 'cash', '财务操作员', 'FR-2026-00016', NOW() - INTERVAL '15 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (17, 1, 700, DATE '2026-05-17', 'transfer', '财务操作员', 'FR-2026-00017', NOW() - INTERVAL '16 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (18, 2, 900, DATE '2026-06-18', 'cash', '财务操作员', 'FR-2026-00018', NOW() - INTERVAL '17 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (19, 3, 1100, DATE '2026-01-19', 'transfer', '财务操作员', 'FR-2026-00019', NOW() - INTERVAL '18 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (20, 4, 1300, DATE '2026-02-20', 'cash', '财务操作员', 'FR-2026-00020', NOW() - INTERVAL '19 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (21, 5, 1500, DATE '2026-03-21', 'transfer', '财务操作员', 'FR-2026-00021', NOW() - INTERVAL '20 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (22, 6, 1700, DATE '2026-04-22', 'cash', '财务操作员', 'FR-2026-00022', NOW() - INTERVAL '21 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (23, 7, 1900, DATE '2026-05-23', 'transfer', '财务操作员', 'FR-2026-00023', NOW() - INTERVAL '22 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (24, 8, 2100, DATE '2026-06-24', 'cash', '财务操作员', 'FR-2026-00024', NOW() - INTERVAL '23 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (25, 1, 2300, DATE '2026-01-25', 'transfer', '财务操作员', 'FR-2026-00025', NOW() - INTERVAL '24 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (26, 2, 2500, DATE '2026-02-26', 'cash', '财务操作员', 'FR-2026-00026', NOW() - INTERVAL '25 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (27, 3, 2700, DATE '2026-03-27', 'transfer', '财务操作员', 'FR-2026-00027', NOW() - INTERVAL '26 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (28, 4, 2900, DATE '2026-04-28', 'cash', '财务操作员', 'FR-2026-00028', NOW() - INTERVAL '27 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (29, 5, 3100, DATE '2026-05-01', 'transfer', '财务操作员', 'FR-2026-00029', NOW() - INTERVAL '28 days', NOW()) ON CONFLICT DO NOTHING;
INSERT INTO fuel_card_recharges (id, card_id, amount, recharge_date, payment_method, operator, voucher_no, created_at, updated_at)
            VALUES (30, 6, 3300, DATE '2026-06-02', 'cash', '财务操作员', 'FR-2026-00030', NOW() - INTERVAL '29 days', NOW()) ON CONFLICT DO NOTHING;
COMMIT;