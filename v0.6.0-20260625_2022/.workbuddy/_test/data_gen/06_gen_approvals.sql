BEGIN;
SET LOCAL synchronous_commit = OFF;
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (121, 'Project', 25, 76, 'pending', 'pending', 'Project 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (122, 'Project', 50, 77, 'approved', 'approved', 'Project 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (123, 'Project', 75, 78, 'rejected', 'rejected', 'Project 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (124, 'Project', 100, 79, 'pending', 'pending', 'Project 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (125, 'Project', 125, 76, 'approved', 'approved', 'Project 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (126, 'Project', 150, 77, 'rejected', 'rejected', 'Project 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (127, 'Project', 175, 78, 'pending', 'pending', 'Project 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (128, 'Project', 200, 79, 'approved', 'approved', 'Project 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (129, 'ProjectContract', 14, 76, 'pending', 'pending', 'ProjectContract 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (130, 'ProjectContract', 28, 77, 'approved', 'approved', 'ProjectContract 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (131, 'ProjectContract', 42, 78, 'rejected', 'rejected', 'ProjectContract 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (132, 'ProjectContract', 56, 79, 'pending', 'pending', 'ProjectContract 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (133, 'ProjectContract', 70, 76, 'approved', 'approved', 'ProjectContract 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (134, 'ProjectContract', 84, 77, 'rejected', 'rejected', 'ProjectContract 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (135, 'ProjectContract', 98, 78, 'pending', 'pending', 'ProjectContract 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (136, 'ProjectContract', 112, 79, 'approved', 'approved', 'ProjectContract 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (137, 'ProjectSettlement', 3, 76, 'pending', 'pending', 'ProjectSettlement 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (138, 'ProjectSettlement', 6, 77, 'approved', 'approved', 'ProjectSettlement 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (139, 'ProjectSettlement', 9, 78, 'rejected', 'rejected', 'ProjectSettlement 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (140, 'ProjectSettlement', 12, 79, 'pending', 'pending', 'ProjectSettlement 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (141, 'ProjectSettlement', 15, 76, 'approved', 'approved', 'ProjectSettlement 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (142, 'ProjectSettlement', 18, 77, 'rejected', 'rejected', 'ProjectSettlement 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (143, 'ProjectSettlement', 21, 78, 'pending', 'pending', 'ProjectSettlement 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (144, 'ProjectSettlement', 24, 79, 'approved', 'approved', 'ProjectSettlement 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (145, 'PurchaseRequirement', 3, 76, 'pending', 'pending', 'PurchaseRequirement 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (146, 'PurchaseRequirement', 6, 77, 'approved', 'approved', 'PurchaseRequirement 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (147, 'PurchaseRequirement', 9, 78, 'rejected', 'rejected', 'PurchaseRequirement 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (148, 'PurchaseRequirement', 12, 79, 'pending', 'pending', 'PurchaseRequirement 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (149, 'PurchaseRequirement', 15, 76, 'approved', 'approved', 'PurchaseRequirement 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (150, 'PurchaseRequirement', 18, 77, 'rejected', 'rejected', 'PurchaseRequirement 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (151, 'PurchaseRequirement', 21, 78, 'pending', 'pending', 'PurchaseRequirement 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (152, 'PurchaseRequirement', 24, 79, 'approved', 'approved', 'PurchaseRequirement 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (153, 'PurchaseOrder', 3, 76, 'pending', 'pending', 'PurchaseOrder 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (154, 'PurchaseOrder', 6, 77, 'approved', 'approved', 'PurchaseOrder 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (155, 'PurchaseOrder', 9, 78, 'rejected', 'rejected', 'PurchaseOrder 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (156, 'PurchaseOrder', 12, 79, 'pending', 'pending', 'PurchaseOrder 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (157, 'PurchaseOrder', 15, 76, 'approved', 'approved', 'PurchaseOrder 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (158, 'PurchaseOrder', 18, 77, 'rejected', 'rejected', 'PurchaseOrder 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (159, 'PurchaseOrder', 21, 78, 'pending', 'pending', 'PurchaseOrder 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (160, 'PurchaseOrder', 24, 79, 'approved', 'approved', 'PurchaseOrder 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (161, 'PurchaseContract', 1, 76, 'pending', 'pending', 'PurchaseContract 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (162, 'PurchaseContract', 2, 77, 'approved', 'approved', 'PurchaseContract 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (163, 'PurchaseContract', 3, 78, 'rejected', 'rejected', 'PurchaseContract 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (164, 'PurchaseContract', 4, 79, 'pending', 'pending', 'PurchaseContract 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (165, 'PurchaseContract', 5, 76, 'approved', 'approved', 'PurchaseContract 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (166, 'PurchaseContract', 6, 77, 'rejected', 'rejected', 'PurchaseContract 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (167, 'PurchaseContract', 7, 78, 'pending', 'pending', 'PurchaseContract 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (168, 'PurchaseContract', 8, 79, 'approved', 'approved', 'PurchaseContract 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (169, 'PurchasePayment', 6, 76, 'pending', 'pending', 'PurchasePayment 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (170, 'PurchasePayment', 12, 77, 'approved', 'approved', 'PurchasePayment 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (171, 'PurchasePayment', 18, 78, 'rejected', 'rejected', 'PurchasePayment 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (172, 'PurchasePayment', 24, 79, 'pending', 'pending', 'PurchasePayment 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (173, 'PurchasePayment', 30, 76, 'approved', 'approved', 'PurchasePayment 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (174, 'PurchasePayment', 36, 77, 'rejected', 'rejected', 'PurchasePayment 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (175, 'PurchasePayment', 42, 78, 'pending', 'pending', 'PurchasePayment 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (176, 'PurchasePayment', 48, 79, 'approved', 'approved', 'PurchasePayment 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (177, 'ExpenseClaim', 8, 76, 'pending', 'pending', 'ExpenseClaim 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (178, 'ExpenseClaim', 16, 77, 'approved', 'approved', 'ExpenseClaim 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (179, 'ExpenseClaim', 24, 78, 'rejected', 'rejected', 'ExpenseClaim 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (180, 'ExpenseClaim', 32, 79, 'pending', 'pending', 'ExpenseClaim 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (181, 'ExpenseClaim', 40, 76, 'approved', 'approved', 'ExpenseClaim 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (182, 'ExpenseClaim', 48, 77, 'rejected', 'rejected', 'ExpenseClaim 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (183, 'ExpenseClaim', 56, 78, 'pending', 'pending', 'ExpenseClaim 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (184, 'ExpenseClaim', 64, 79, 'approved', 'approved', 'ExpenseClaim 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (185, 'LeaveRequest', 7, 76, 'pending', 'pending', 'LeaveRequest 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (186, 'LeaveRequest', 14, 77, 'approved', 'approved', 'LeaveRequest 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (187, 'LeaveRequest', 21, 78, 'rejected', 'rejected', 'LeaveRequest 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (188, 'LeaveRequest', 28, 79, 'pending', 'pending', 'LeaveRequest 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (189, 'LeaveRequest', 35, 76, 'approved', 'approved', 'LeaveRequest 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (190, 'LeaveRequest', 42, 77, 'rejected', 'rejected', 'LeaveRequest 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (191, 'LeaveRequest', 49, 78, 'pending', 'pending', 'LeaveRequest 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (192, 'LeaveRequest', 56, 79, 'approved', 'approved', 'LeaveRequest 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (193, 'OvertimeRequest', 4, 76, 'pending', 'pending', 'OvertimeRequest 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (194, 'OvertimeRequest', 8, 77, 'approved', 'approved', 'OvertimeRequest 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (195, 'OvertimeRequest', 12, 78, 'rejected', 'rejected', 'OvertimeRequest 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (196, 'OvertimeRequest', 16, 79, 'pending', 'pending', 'OvertimeRequest 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (197, 'OvertimeRequest', 20, 76, 'approved', 'approved', 'OvertimeRequest 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (198, 'OvertimeRequest', 24, 77, 'rejected', 'rejected', 'OvertimeRequest 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (199, 'OvertimeRequest', 28, 78, 'pending', 'pending', 'OvertimeRequest 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (200, 'OvertimeRequest', 32, 79, 'approved', 'approved', 'OvertimeRequest 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (201, 'VehicleUsage', 16, 76, 'pending', 'pending', 'VehicleUsage 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (202, 'VehicleUsage', 32, 77, 'approved', 'approved', 'VehicleUsage 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (203, 'VehicleUsage', 48, 78, 'rejected', 'rejected', 'VehicleUsage 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (204, 'VehicleUsage', 64, 79, 'pending', 'pending', 'VehicleUsage 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (205, 'VehicleUsage', 80, 76, 'approved', 'approved', 'VehicleUsage 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (206, 'VehicleUsage', 96, 77, 'rejected', 'rejected', 'VehicleUsage 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (207, 'VehicleUsage', 112, 78, 'pending', 'pending', 'VehicleUsage 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (208, 'VehicleUsage', 128, 79, 'approved', 'approved', 'VehicleUsage 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (209, 'MaintenanceContract', 1, 76, 'pending', 'pending', 'MaintenanceContract 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (210, 'MaintenanceContract', 2, 77, 'approved', 'approved', 'MaintenanceContract 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (211, 'MaintenanceContract', 3, 78, 'rejected', 'rejected', 'MaintenanceContract 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (212, 'MaintenanceContract', 4, 79, 'pending', 'pending', 'MaintenanceContract 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (213, 'MaintenanceContract', 5, 76, 'approved', 'approved', 'MaintenanceContract 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (214, 'MaintenanceContract', 6, 77, 'rejected', 'rejected', 'MaintenanceContract 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (215, 'MaintenanceContract', 7, 78, 'pending', 'pending', 'MaintenanceContract 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (216, 'MaintenanceContract', 8, 79, 'approved', 'approved', 'MaintenanceContract 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (217, 'Refund', 7, 76, 'pending', 'pending', 'Refund 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (218, 'Refund', 14, 77, 'approved', 'approved', 'Refund 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (219, 'Refund', 21, 78, 'rejected', 'rejected', 'Refund 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (220, 'Refund', 28, 79, 'pending', 'pending', 'Refund 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (221, 'Refund', 35, 76, 'approved', 'approved', 'Refund 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (222, 'Refund', 42, 77, 'rejected', 'rejected', 'Refund 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (223, 'Refund', 49, 78, 'pending', 'pending', 'Refund 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (224, 'Refund', 56, 79, 'approved', 'approved', 'Refund 审批 #8', NOW() - INTERVAL '14 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (225, 'FuelRecharge', 6, 76, 'pending', 'pending', 'FuelRecharge 审批 #1', NOW() - INTERVAL '0 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (226, 'FuelRecharge', 12, 77, 'approved', 'approved', 'FuelRecharge 审批 #2', NOW() - INTERVAL '2 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (227, 'FuelRecharge', 18, 78, 'rejected', 'rejected', 'FuelRecharge 审批 #3', NOW() - INTERVAL '4 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (228, 'FuelRecharge', 24, 79, 'pending', 'pending', 'FuelRecharge 审批 #4', NOW() - INTERVAL '6 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (229, 'FuelRecharge', 30, 76, 'approved', 'approved', 'FuelRecharge 审批 #5', NOW() - INTERVAL '8 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (230, 'FuelRecharge', 36, 77, 'rejected', 'rejected', 'FuelRecharge 审批 #6', NOW() - INTERVAL '10 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (231, 'FuelRecharge', 42, 78, 'pending', 'pending', 'FuelRecharge 审批 #7', NOW() - INTERVAL '12 days', NOW());
INSERT INTO approval_records (id, approvable_type, approvable_id, user_id, action, status, comment, created_at, updated_at)
                VALUES (232, 'FuelRecharge', 48, 79, 'approved', 'approved', 'FuelRecharge 审批 #8', NOW() - INTERVAL '14 days', NOW());
COMMIT;