BEGIN;
SET LOCAL synchronous_commit = OFF;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (303, 74, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (304, 75, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (305, 76, DATE '2026-05-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (306, 77, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (307, 78, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (308, 79, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (309, 80, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (310, 81, DATE '2026-05-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (311, 82, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (312, 83, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (313, 84, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (314, 85, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (315, 86, DATE '2026-05-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (316, 87, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (317, 88, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (318, 74, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (319, 75, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (320, 76, DATE '2026-05-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (321, 77, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (322, 78, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (323, 79, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (324, 80, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (325, 81, DATE '2026-05-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (326, 82, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (327, 83, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (328, 84, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (329, 85, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (330, 86, DATE '2026-05-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (331, 87, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (332, 88, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (333, 74, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (334, 75, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (335, 76, DATE '2026-05-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (336, 77, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (337, 78, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (338, 79, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (339, 80, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (340, 81, DATE '2026-05-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (341, 82, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (342, 83, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (343, 84, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (344, 85, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (345, 86, DATE '2026-05-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (346, 87, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (347, 88, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (348, 74, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (349, 75, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (350, 76, DATE '2026-05-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (351, 77, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (352, 78, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (353, 79, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (354, 80, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (355, 81, DATE '2026-05-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (356, 82, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (357, 83, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (358, 84, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (359, 85, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (360, 86, DATE '2026-05-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (361, 87, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (362, 88, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (363, 74, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (364, 75, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (365, 76, DATE '2026-05-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (366, 77, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (367, 78, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (368, 79, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (369, 80, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (370, 81, DATE '2026-05-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (371, 82, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (372, 83, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (373, 84, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (374, 85, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (375, 86, DATE '2026-05-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (376, 87, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (377, 88, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (378, 74, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (379, 75, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (380, 76, DATE '2026-05-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (381, 77, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (382, 78, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (383, 79, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (384, 80, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (385, 81, DATE '2026-05-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (386, 82, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (387, 83, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (388, 84, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (389, 85, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (390, 86, DATE '2026-05-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (391, 87, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (392, 88, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (393, 74, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (394, 75, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (395, 76, DATE '2026-05-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (396, 77, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (397, 78, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (398, 79, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (399, 80, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (400, 81, DATE '2026-05-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (401, 82, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (402, 83, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (403, 84, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (404, 85, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (405, 86, DATE '2026-05-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (406, 87, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (407, 88, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (408, 74, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (409, 75, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (410, 76, DATE '2026-05-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (411, 77, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (412, 78, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (413, 79, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (414, 80, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (415, 81, DATE '2026-05-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (416, 82, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (417, 83, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (418, 84, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (419, 85, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (420, 86, DATE '2026-05-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (421, 87, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (422, 88, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (423, 74, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (424, 75, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (425, 76, DATE '2026-05-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (426, 77, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (427, 78, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (428, 79, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (429, 80, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (430, 81, DATE '2026-05-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (431, 82, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (432, 83, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (433, 84, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (434, 85, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (435, 86, DATE '2026-05-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (436, 87, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (437, 88, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (438, 74, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (439, 75, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (440, 76, DATE '2026-05-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (441, 77, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (442, 78, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (443, 79, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (444, 80, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (445, 81, DATE '2026-05-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (446, 82, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (447, 83, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (448, 84, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (449, 85, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (450, 86, DATE '2026-05-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (451, 87, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (452, 88, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (453, 74, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (454, 75, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (455, 76, DATE '2026-05-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (456, 77, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (457, 78, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (458, 79, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (459, 80, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (460, 81, DATE '2026-05-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (461, 82, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (462, 83, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (463, 84, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (464, 85, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (465, 86, DATE '2026-05-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (466, 87, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (467, 88, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (468, 74, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (469, 75, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (470, 76, DATE '2026-05-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (471, 77, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (472, 78, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (473, 79, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (474, 80, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (475, 81, DATE '2026-05-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (476, 82, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (477, 83, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (478, 84, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (479, 85, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (480, 86, DATE '2026-05-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (481, 87, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (482, 88, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (483, 74, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (484, 75, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (485, 76, DATE '2026-05-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (486, 77, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (487, 78, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (488, 79, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (489, 80, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (490, 81, DATE '2026-05-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (491, 82, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (492, 83, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (493, 84, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (494, 85, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (495, 86, DATE '2026-05-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (496, 87, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (497, 88, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (498, 74, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (499, 75, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (500, 76, DATE '2026-05-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (501, 77, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (502, 78, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (503, 79, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (504, 80, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (505, 81, DATE '2026-05-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (506, 82, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (507, 83, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (508, 84, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (509, 85, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (510, 86, DATE '2026-05-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (511, 87, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (512, 88, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (513, 74, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (514, 75, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (515, 76, DATE '2026-05-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (516, 77, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (517, 78, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (518, 79, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (519, 80, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (520, 81, DATE '2026-05-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (521, 82, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (522, 83, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (523, 84, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (524, 85, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (525, 86, DATE '2026-05-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (526, 87, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (527, 88, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (528, 74, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (529, 75, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (530, 76, DATE '2026-05-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (531, 77, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (532, 78, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (533, 79, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (534, 80, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (535, 81, DATE '2026-05-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (536, 82, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (537, 83, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (538, 84, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (539, 85, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (540, 86, DATE '2026-05-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (541, 87, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (542, 88, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (543, 74, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (544, 75, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (545, 76, DATE '2026-05-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (546, 77, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (547, 78, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (548, 79, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (549, 80, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (550, 81, DATE '2026-05-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (551, 82, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (552, 83, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (553, 84, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (554, 85, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (555, 86, DATE '2026-05-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (556, 87, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (557, 88, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (558, 74, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (559, 75, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (560, 76, DATE '2026-05-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (561, 77, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (562, 78, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (563, 79, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (564, 80, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (565, 81, DATE '2026-05-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (566, 82, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (567, 83, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (568, 84, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (569, 85, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (570, 86, DATE '2026-05-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (571, 87, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (572, 88, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (573, 74, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (574, 75, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (575, 76, DATE '2026-05-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (576, 77, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (577, 78, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (578, 79, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (579, 80, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (580, 81, DATE '2026-05-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (581, 82, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (582, 83, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (583, 84, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (584, 85, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (585, 86, DATE '2026-05-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (586, 87, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (587, 88, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (588, 74, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (589, 75, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (590, 76, DATE '2026-05-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (591, 77, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (592, 78, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (593, 79, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (594, 80, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (595, 81, DATE '2026-05-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (596, 82, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (597, 83, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (598, 84, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (599, 85, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (600, 86, DATE '2026-05-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (601, 87, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (602, 88, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (603, 74, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (604, 75, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (605, 76, DATE '2026-05-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (606, 77, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (607, 78, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (608, 79, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (609, 80, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (610, 81, DATE '2026-05-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (611, 82, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (612, 83, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (613, 84, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (614, 85, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (615, 86, DATE '2026-05-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (616, 87, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (617, 88, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (618, 74, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (619, 75, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (620, 76, DATE '2026-05-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (621, 77, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (622, 78, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (623, 79, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (624, 80, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (625, 81, DATE '2026-05-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (626, 82, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (627, 83, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (628, 84, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (629, 85, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (630, 86, DATE '2026-05-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (631, 87, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (632, 88, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (633, 74, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (634, 75, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (635, 76, DATE '2026-05-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (636, 77, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (637, 78, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (638, 79, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (639, 80, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (640, 81, DATE '2026-05-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (641, 82, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (642, 83, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (643, 84, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (644, 85, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (645, 86, DATE '2026-05-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (646, 87, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (647, 88, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (648, 74, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (649, 75, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (650, 76, DATE '2026-05-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (651, 77, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (652, 78, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (653, 79, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (654, 80, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (655, 81, DATE '2026-05-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (656, 82, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (657, 83, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (658, 84, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (659, 85, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (660, 86, DATE '2026-05-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (661, 87, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (662, 88, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (663, 74, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (664, 75, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (665, 76, DATE '2026-05-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (666, 77, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (667, 78, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (668, 79, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (669, 80, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (670, 81, DATE '2026-05-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (671, 82, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (672, 83, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (673, 84, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (674, 85, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (675, 86, DATE '2026-05-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (676, 87, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (677, 88, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (678, 74, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (679, 75, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (680, 76, DATE '2026-05-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (681, 77, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (682, 78, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (683, 79, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (684, 80, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (685, 81, DATE '2026-05-20', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (686, 82, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (687, 83, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (688, 84, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (689, 85, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (690, 86, DATE '2026-05-20', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (691, 87, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (692, 88, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (693, 74, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (694, 75, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (695, 76, DATE '2026-05-20', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (696, 77, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (697, 78, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (698, 79, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (699, 80, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (700, 81, DATE '2026-05-20', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (701, 82, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (702, 83, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (703, 84, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (704, 85, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (705, 86, DATE '2026-05-21', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (706, 87, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (707, 88, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (708, 74, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (709, 75, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (710, 76, DATE '2026-05-21', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (711, 77, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (712, 78, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (713, 79, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (714, 80, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (715, 81, DATE '2026-05-21', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (716, 82, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (717, 83, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (718, 84, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (719, 85, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (720, 86, DATE '2026-05-21', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (721, 87, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (722, 88, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (723, 74, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (724, 75, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (725, 76, DATE '2026-05-22', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (726, 77, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (727, 78, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (728, 79, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (729, 80, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (730, 81, DATE '2026-05-22', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (731, 82, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (732, 83, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (733, 84, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (734, 85, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (735, 86, DATE '2026-05-22', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (736, 87, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (737, 88, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (738, 74, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (739, 75, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (740, 76, DATE '2026-05-22', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (741, 77, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (742, 78, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (743, 79, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (744, 80, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (745, 81, DATE '2026-05-23', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (746, 82, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (747, 83, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (748, 84, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (749, 85, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (750, 86, DATE '2026-05-23', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (751, 87, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (752, 88, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (753, 74, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (754, 75, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (755, 76, DATE '2026-05-23', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (756, 77, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (757, 78, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (758, 79, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (759, 80, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (760, 81, DATE '2026-05-23', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (761, 82, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (762, 83, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (763, 84, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (764, 85, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (765, 86, DATE '2026-05-24', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (766, 87, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (767, 88, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (768, 74, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (769, 75, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (770, 76, DATE '2026-05-24', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (771, 77, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (772, 78, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (773, 79, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (774, 80, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (775, 81, DATE '2026-05-24', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (776, 82, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (777, 83, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (778, 84, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (779, 85, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (780, 86, DATE '2026-05-24', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (781, 87, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (782, 88, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (783, 74, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (784, 75, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (785, 76, DATE '2026-05-25', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (786, 77, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (787, 78, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (788, 79, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (789, 80, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (790, 81, DATE '2026-05-25', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (791, 82, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (792, 83, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (793, 84, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (794, 85, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (795, 86, DATE '2026-05-25', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (796, 87, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (797, 88, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (798, 74, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (799, 75, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (800, 76, DATE '2026-05-25', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (801, 77, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (802, 78, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (803, 79, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (804, 80, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (805, 81, DATE '2026-05-26', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (806, 82, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (807, 83, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (808, 84, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (809, 85, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (810, 86, DATE '2026-05-26', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (811, 87, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (812, 88, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (813, 74, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (814, 75, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (815, 76, DATE '2026-05-26', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (816, 77, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (817, 78, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (818, 79, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (819, 80, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (820, 81, DATE '2026-05-26', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (821, 82, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (822, 83, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (823, 84, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (824, 85, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (825, 86, DATE '2026-05-27', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (826, 87, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (827, 88, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (828, 74, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (829, 75, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (830, 76, DATE '2026-05-27', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (831, 77, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (832, 78, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (833, 79, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (834, 80, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (835, 81, DATE '2026-05-27', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (836, 82, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (837, 83, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (838, 84, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (839, 85, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (840, 86, DATE '2026-05-27', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (841, 87, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (842, 88, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (843, 74, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (844, 75, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (845, 76, DATE '2026-05-28', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (846, 77, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (847, 78, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (848, 79, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (849, 80, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (850, 81, DATE '2026-05-28', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (851, 82, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (852, 83, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (853, 84, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (854, 85, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (855, 86, DATE '2026-05-28', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (856, 87, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (857, 88, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (858, 74, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (859, 75, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (860, 76, DATE '2026-05-28', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (861, 77, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (862, 78, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (863, 79, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (864, 80, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (865, 81, DATE '2026-05-29', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (866, 82, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (867, 83, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (868, 84, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (869, 85, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (870, 86, DATE '2026-05-29', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (871, 87, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (872, 88, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (873, 74, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (874, 75, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (875, 76, DATE '2026-05-29', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (876, 77, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (877, 78, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (878, 79, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (879, 80, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (880, 81, DATE '2026-05-29', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (881, 82, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (882, 83, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (883, 84, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (884, 85, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (885, 86, DATE '2026-05-30', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (886, 87, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (887, 88, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (888, 74, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (889, 75, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (890, 76, DATE '2026-05-30', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (891, 77, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (892, 78, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (893, 79, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (894, 80, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (895, 81, DATE '2026-05-30', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (896, 82, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (897, 83, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (898, 84, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (899, 85, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (900, 86, DATE '2026-05-30', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (901, 87, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (902, 88, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (903, 74, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (904, 75, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (905, 76, DATE '2026-05-31', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (906, 77, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (907, 78, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (908, 79, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (909, 80, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (910, 81, DATE '2026-05-31', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (911, 82, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (912, 83, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (913, 84, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (914, 85, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (915, 86, DATE '2026-05-31', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (916, 87, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (917, 88, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (918, 74, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (919, 75, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (920, 76, DATE '2026-05-31', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (921, 77, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (922, 78, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (923, 79, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (924, 80, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (925, 81, DATE '2026-06-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (926, 82, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (927, 83, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (928, 84, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (929, 85, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (930, 86, DATE '2026-06-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (931, 87, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (932, 88, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (933, 74, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (934, 75, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (935, 76, DATE '2026-06-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (936, 77, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (937, 78, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (938, 79, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (939, 80, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (940, 81, DATE '2026-06-01', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (941, 82, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (942, 83, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (943, 84, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (944, 85, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (945, 86, DATE '2026-06-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (946, 87, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (947, 88, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (948, 74, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (949, 75, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (950, 76, DATE '2026-06-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (951, 77, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (952, 78, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (953, 79, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (954, 80, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (955, 81, DATE '2026-06-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (956, 82, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (957, 83, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (958, 84, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (959, 85, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (960, 86, DATE '2026-06-02', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (961, 87, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (962, 88, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (963, 74, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (964, 75, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (965, 76, DATE '2026-06-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (966, 77, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (967, 78, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (968, 79, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (969, 80, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (970, 81, DATE '2026-06-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (971, 82, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (972, 83, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (973, 84, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (974, 85, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (975, 86, DATE '2026-06-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (976, 87, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (977, 88, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (978, 74, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (979, 75, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (980, 76, DATE '2026-06-03', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (981, 77, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (982, 78, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (983, 79, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (984, 80, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (985, 81, DATE '2026-06-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (986, 82, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (987, 83, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (988, 84, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (989, 85, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (990, 86, DATE '2026-06-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (991, 87, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (992, 88, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (993, 74, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (994, 75, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (995, 76, DATE '2026-06-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (996, 77, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (997, 78, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (998, 79, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (999, 80, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1000, 81, DATE '2026-06-04', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1001, 82, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1002, 83, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1003, 84, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1004, 85, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1005, 86, DATE '2026-06-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1006, 87, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1007, 88, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1008, 74, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1009, 75, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1010, 76, DATE '2026-06-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1011, 77, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1012, 78, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1013, 79, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1014, 80, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1015, 81, DATE '2026-06-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1016, 82, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1017, 83, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1018, 84, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1019, 85, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1020, 86, DATE '2026-06-05', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1021, 87, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1022, 88, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1023, 74, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1024, 75, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1025, 76, DATE '2026-06-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1026, 77, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1027, 78, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1028, 79, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1029, 80, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1030, 81, DATE '2026-06-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1031, 82, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1032, 83, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1033, 84, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1034, 85, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1035, 86, DATE '2026-06-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1036, 87, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1037, 88, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1038, 74, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1039, 75, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1040, 76, DATE '2026-06-06', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1041, 77, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1042, 78, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1043, 79, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1044, 80, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1045, 81, DATE '2026-06-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1046, 82, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1047, 83, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1048, 84, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1049, 85, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1050, 86, DATE '2026-06-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1051, 87, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1052, 88, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1053, 74, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1054, 75, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1055, 76, DATE '2026-06-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1056, 77, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1057, 78, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1058, 79, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1059, 80, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1060, 81, DATE '2026-06-07', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1061, 82, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1062, 83, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1063, 84, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1064, 85, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1065, 86, DATE '2026-06-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1066, 87, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1067, 88, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1068, 74, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1069, 75, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1070, 76, DATE '2026-06-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1071, 77, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1072, 78, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1073, 79, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1074, 80, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1075, 81, DATE '2026-06-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1076, 82, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1077, 83, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1078, 84, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1079, 85, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1080, 86, DATE '2026-06-08', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1081, 87, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1082, 88, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1083, 74, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1084, 75, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1085, 76, DATE '2026-06-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1086, 77, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1087, 78, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1088, 79, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1089, 80, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1090, 81, DATE '2026-06-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1091, 82, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1092, 83, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1093, 84, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1094, 85, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1095, 86, DATE '2026-06-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1096, 87, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1097, 88, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1098, 74, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1099, 75, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1100, 76, DATE '2026-06-09', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1101, 77, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1102, 78, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1103, 79, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1104, 80, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1105, 81, DATE '2026-06-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1106, 82, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1107, 83, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1108, 84, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1109, 85, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1110, 86, DATE '2026-06-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1111, 87, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1112, 88, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1113, 74, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1114, 75, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1115, 76, DATE '2026-06-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1116, 77, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1117, 78, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1118, 79, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1119, 80, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1120, 81, DATE '2026-06-10', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1121, 82, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1122, 83, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1123, 84, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1124, 85, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1125, 86, DATE '2026-06-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1126, 87, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1127, 88, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1128, 74, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1129, 75, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1130, 76, DATE '2026-06-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1131, 77, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1132, 78, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1133, 79, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1134, 80, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1135, 81, DATE '2026-06-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1136, 82, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1137, 83, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1138, 84, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1139, 85, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1140, 86, DATE '2026-06-11', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1141, 87, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1142, 88, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1143, 74, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1144, 75, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1145, 76, DATE '2026-06-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1146, 77, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1147, 78, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1148, 79, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1149, 80, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1150, 81, DATE '2026-06-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1151, 82, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1152, 83, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1153, 84, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1154, 85, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1155, 86, DATE '2026-06-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1156, 87, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1157, 88, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1158, 74, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1159, 75, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1160, 76, DATE '2026-06-12', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1161, 77, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1162, 78, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1163, 79, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1164, 80, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1165, 81, DATE '2026-06-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1166, 82, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1167, 83, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1168, 84, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1169, 85, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1170, 86, DATE '2026-06-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1171, 87, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1172, 88, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1173, 74, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1174, 75, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1175, 76, DATE '2026-06-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1176, 77, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1177, 78, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1178, 79, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1179, 80, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1180, 81, DATE '2026-06-13', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1181, 82, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1182, 83, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1183, 84, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1184, 85, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1185, 86, DATE '2026-06-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1186, 87, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1187, 88, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1188, 74, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1189, 75, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1190, 76, DATE '2026-06-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1191, 77, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1192, 78, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1193, 79, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1194, 80, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1195, 81, DATE '2026-06-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1196, 82, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1197, 83, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1198, 84, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1199, 85, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1200, 86, DATE '2026-06-14', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1201, 87, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1202, 88, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1203, 74, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1204, 75, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1205, 76, DATE '2026-06-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1206, 77, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1207, 78, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1208, 79, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1209, 80, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1210, 81, DATE '2026-06-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1211, 82, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1212, 83, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1213, 84, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1214, 85, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1215, 86, DATE '2026-06-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1216, 87, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1217, 88, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1218, 74, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1219, 75, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1220, 76, DATE '2026-06-15', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1221, 77, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1222, 78, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1223, 79, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1224, 80, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1225, 81, DATE '2026-06-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1226, 82, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1227, 83, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1228, 84, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1229, 85, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1230, 86, DATE '2026-06-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1231, 87, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1232, 88, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1233, 74, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1234, 75, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1235, 76, DATE '2026-06-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1236, 77, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1237, 78, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1238, 79, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1239, 80, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1240, 81, DATE '2026-06-16', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1241, 82, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1242, 83, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1243, 84, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1244, 85, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1245, 86, DATE '2026-06-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1246, 87, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1247, 88, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1248, 74, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1249, 75, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1250, 76, DATE '2026-06-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1251, 77, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1252, 78, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1253, 79, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1254, 80, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1255, 81, DATE '2026-06-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1256, 82, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1257, 83, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 76, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1258, 84, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1259, 85, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1260, 86, DATE '2026-06-17', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1261, 87, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1262, 88, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 81, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1263, 74, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1264, 75, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1265, 76, DATE '2026-06-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1266, 77, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1267, 78, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 86, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1268, 79, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1269, 80, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1270, 81, DATE '2026-06-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1271, 82, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1272, 83, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 91, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1273, 84, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1274, 85, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1275, 86, DATE '2026-06-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1276, 87, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1277, 88, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 96, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1278, 74, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1279, 75, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1280, 76, DATE '2026-06-18', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1281, 77, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1282, 78, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 101, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1283, 79, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1284, 80, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1285, 81, DATE '2026-06-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1286, 82, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1287, 83, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 106, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1288, 84, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1289, 85, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1290, 86, DATE '2026-06-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1291, 87, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1292, 88, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 111, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1293, 74, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 2.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1294, 75, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1295, 76, DATE '2026-06-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1296, 77, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1297, 78, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 116, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1298, 79, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'normal', 8.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1299, 80, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'late', 4.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1300, 81, DATE '2026-06-19', NULL, NULL, 'absent', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1301, 82, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'leave', 0.0, 0.0, NULL, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO attendance_records (id, user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, project_id, created_at, updated_at)
            VALUES (1302, 83, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', 'field', 0.0, 0.0, 121, NOW(), NOW()) ON CONFLICT (user_id, date) DO NOTHING;
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (62, 74, 'personal', DATE '2026-05-01', DATE '2026-05-02', 2, 'personal类请假 #1', 'pending', 76, NOW() - INTERVAL '0 days', NOW() - INTERVAL '5 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (63, 75, 'sick', DATE '2026-05-02', DATE '2026-05-04', 3, 'sick类请假 #2', 'approved', 78, NOW() - INTERVAL '1 days', NOW() - INTERVAL '6 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (64, 76, 'annual', DATE '2026-05-03', DATE '2026-05-06', 4, 'annual类请假 #3', 'rejected', 76, NOW() - INTERVAL '2 days', NOW() - INTERVAL '7 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (65, 77, 'marriage', DATE '2026-05-04', DATE '2026-05-05', 2, 'marriage类请假 #4', 'pending', 78, NOW() - INTERVAL '3 days', NOW() - INTERVAL '8 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (66, 78, 'maternity', DATE '2026-05-05', DATE '2026-05-07', 3, 'maternity类请假 #5', 'approved', 76, NOW() - INTERVAL '4 days', NOW() - INTERVAL '9 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (67, 79, 'personal', DATE '2026-05-06', DATE '2026-05-09', 4, 'personal类请假 #6', 'rejected', 78, NOW() - INTERVAL '5 days', NOW() - INTERVAL '10 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (68, 80, 'sick', DATE '2026-05-07', DATE '2026-05-08', 2, 'sick类请假 #7', 'pending', 76, NOW() - INTERVAL '6 days', NOW() - INTERVAL '11 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (69, 81, 'annual', DATE '2026-05-08', DATE '2026-05-10', 3, 'annual类请假 #8', 'approved', 78, NOW() - INTERVAL '7 days', NOW() - INTERVAL '12 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (70, 82, 'marriage', DATE '2026-05-09', DATE '2026-05-12', 4, 'marriage类请假 #9', 'rejected', 76, NOW() - INTERVAL '8 days', NOW() - INTERVAL '13 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (71, 83, 'maternity', DATE '2026-05-10', DATE '2026-05-11', 2, 'maternity类请假 #10', 'pending', 78, NOW() - INTERVAL '9 days', NOW() - INTERVAL '14 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (72, 84, 'personal', DATE '2026-05-11', DATE '2026-05-13', 3, 'personal类请假 #11', 'approved', 76, NOW() - INTERVAL '10 days', NOW() - INTERVAL '15 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (73, 85, 'sick', DATE '2026-05-12', DATE '2026-05-15', 4, 'sick类请假 #12', 'rejected', 78, NOW() - INTERVAL '11 days', NOW() - INTERVAL '16 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (74, 86, 'annual', DATE '2026-05-13', DATE '2026-05-14', 2, 'annual类请假 #13', 'pending', 76, NOW() - INTERVAL '12 days', NOW() - INTERVAL '17 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (75, 87, 'marriage', DATE '2026-05-14', DATE '2026-05-16', 3, 'marriage类请假 #14', 'approved', 78, NOW() - INTERVAL '13 days', NOW() - INTERVAL '18 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (76, 88, 'maternity', DATE '2026-05-15', DATE '2026-05-18', 4, 'maternity类请假 #15', 'rejected', 76, NOW() - INTERVAL '14 days', NOW() - INTERVAL '19 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (77, 74, 'personal', DATE '2026-05-16', DATE '2026-05-17', 2, 'personal类请假 #16', 'pending', 78, NOW() - INTERVAL '15 days', NOW() - INTERVAL '20 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (78, 75, 'sick', DATE '2026-05-17', DATE '2026-05-19', 3, 'sick类请假 #17', 'approved', 76, NOW() - INTERVAL '16 days', NOW() - INTERVAL '21 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (79, 76, 'annual', DATE '2026-05-18', DATE '2026-05-21', 4, 'annual类请假 #18', 'rejected', 78, NOW() - INTERVAL '17 days', NOW() - INTERVAL '22 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (80, 77, 'marriage', DATE '2026-05-19', DATE '2026-05-20', 2, 'marriage类请假 #19', 'pending', 76, NOW() - INTERVAL '18 days', NOW() - INTERVAL '23 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (81, 78, 'maternity', DATE '2026-05-20', DATE '2026-05-22', 3, 'maternity类请假 #20', 'approved', 78, NOW() - INTERVAL '19 days', NOW() - INTERVAL '24 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (82, 79, 'personal', DATE '2026-05-21', DATE '2026-05-24', 4, 'personal类请假 #21', 'rejected', 76, NOW() - INTERVAL '20 days', NOW() - INTERVAL '25 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (83, 80, 'sick', DATE '2026-05-22', DATE '2026-05-23', 2, 'sick类请假 #22', 'pending', 78, NOW() - INTERVAL '21 days', NOW() - INTERVAL '26 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (84, 81, 'annual', DATE '2026-05-23', DATE '2026-05-25', 3, 'annual类请假 #23', 'approved', 76, NOW() - INTERVAL '22 days', NOW() - INTERVAL '27 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (85, 82, 'marriage', DATE '2026-05-24', DATE '2026-05-27', 4, 'marriage类请假 #24', 'rejected', 78, NOW() - INTERVAL '23 days', NOW() - INTERVAL '28 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (86, 83, 'maternity', DATE '2026-05-25', DATE '2026-05-26', 2, 'maternity类请假 #25', 'pending', 76, NOW() - INTERVAL '24 days', NOW() - INTERVAL '29 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (87, 84, 'personal', DATE '2026-05-26', DATE '2026-05-28', 3, 'personal类请假 #26', 'approved', 78, NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (88, 85, 'sick', DATE '2026-05-27', DATE '2026-05-30', 4, 'sick类请假 #27', 'rejected', 76, NOW() - INTERVAL '26 days', NOW() - INTERVAL '31 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (89, 86, 'annual', DATE '2026-05-28', DATE '2026-05-29', 2, 'annual类请假 #28', 'pending', 78, NOW() - INTERVAL '27 days', NOW() - INTERVAL '32 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (90, 87, 'marriage', DATE '2026-05-29', DATE '2026-05-31', 3, 'marriage类请假 #29', 'approved', 76, NOW() - INTERVAL '28 days', NOW() - INTERVAL '33 days', NOW());
INSERT INTO leave_requests (id, user_id, type, start_date, end_date, days, reason, status, approver_id, approved_at, created_at, updated_at)
            VALUES (91, 88, 'maternity', DATE '2026-05-30', DATE '2026-06-02', 4, 'maternity类请假 #30', 'rejected', 78, NOW() - INTERVAL '29 days', NOW() - INTERVAL '34 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (36, 74, DATE '2026-05-01', TIME '18:00:00', TIME '19:00:00', 2.0, '加班 #1', 'leave', 'pending', 76, NOW() - INTERVAL '0 days', NOW() - INTERVAL '5 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (37, 75, DATE '2026-05-02', TIME '18:00:00', TIME '20:00:00', 3.0, '加班 #2', 'money', 'approved', 76, NOW() - INTERVAL '1 days', NOW() - INTERVAL '6 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (38, 76, DATE '2026-05-03', TIME '18:00:00', TIME '21:00:00', 4.0, '加班 #3', 'leave', 'rejected', 76, NOW() - INTERVAL '2 days', NOW() - INTERVAL '7 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (39, 77, DATE '2026-05-04', TIME '18:00:00', TIME '22:00:00', 5.0, '加班 #4', 'money', 'pending', 76, NOW() - INTERVAL '3 days', NOW() - INTERVAL '8 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (40, 78, DATE '2026-05-05', TIME '18:00:00', TIME '19:00:00', 6.0, '加班 #5', 'leave', 'approved', 76, NOW() - INTERVAL '4 days', NOW() - INTERVAL '9 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (41, 79, DATE '2026-05-06', TIME '18:00:00', TIME '20:00:00', 2.0, '加班 #6', 'money', 'rejected', 76, NOW() - INTERVAL '5 days', NOW() - INTERVAL '10 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (42, 80, DATE '2026-05-07', TIME '18:00:00', TIME '21:00:00', 3.0, '加班 #7', 'leave', 'pending', 76, NOW() - INTERVAL '6 days', NOW() - INTERVAL '11 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (43, 81, DATE '2026-05-08', TIME '18:00:00', TIME '22:00:00', 4.0, '加班 #8', 'money', 'approved', 76, NOW() - INTERVAL '7 days', NOW() - INTERVAL '12 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (44, 82, DATE '2026-05-09', TIME '18:00:00', TIME '19:00:00', 5.0, '加班 #9', 'leave', 'rejected', 76, NOW() - INTERVAL '8 days', NOW() - INTERVAL '13 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (45, 83, DATE '2026-05-10', TIME '18:00:00', TIME '20:00:00', 6.0, '加班 #10', 'money', 'pending', 76, NOW() - INTERVAL '9 days', NOW() - INTERVAL '14 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (46, 84, DATE '2026-05-11', TIME '18:00:00', TIME '21:00:00', 2.0, '加班 #11', 'leave', 'approved', 76, NOW() - INTERVAL '10 days', NOW() - INTERVAL '15 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (47, 85, DATE '2026-05-12', TIME '18:00:00', TIME '22:00:00', 3.0, '加班 #12', 'money', 'rejected', 76, NOW() - INTERVAL '11 days', NOW() - INTERVAL '16 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (48, 86, DATE '2026-05-13', TIME '18:00:00', TIME '19:00:00', 4.0, '加班 #13', 'leave', 'pending', 76, NOW() - INTERVAL '12 days', NOW() - INTERVAL '17 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (49, 87, DATE '2026-05-14', TIME '18:00:00', TIME '20:00:00', 5.0, '加班 #14', 'money', 'approved', 76, NOW() - INTERVAL '13 days', NOW() - INTERVAL '18 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (50, 88, DATE '2026-05-15', TIME '18:00:00', TIME '21:00:00', 6.0, '加班 #15', 'leave', 'rejected', 76, NOW() - INTERVAL '14 days', NOW() - INTERVAL '19 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (51, 74, DATE '2026-05-16', TIME '18:00:00', TIME '22:00:00', 2.0, '加班 #16', 'money', 'pending', 76, NOW() - INTERVAL '15 days', NOW() - INTERVAL '20 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (52, 75, DATE '2026-05-17', TIME '18:00:00', TIME '19:00:00', 3.0, '加班 #17', 'leave', 'approved', 76, NOW() - INTERVAL '16 days', NOW() - INTERVAL '21 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (53, 76, DATE '2026-05-18', TIME '18:00:00', TIME '20:00:00', 4.0, '加班 #18', 'money', 'rejected', 76, NOW() - INTERVAL '17 days', NOW() - INTERVAL '22 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (54, 77, DATE '2026-05-19', TIME '18:00:00', TIME '21:00:00', 5.0, '加班 #19', 'leave', 'pending', 76, NOW() - INTERVAL '18 days', NOW() - INTERVAL '23 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (55, 78, DATE '2026-05-20', TIME '18:00:00', TIME '22:00:00', 6.0, '加班 #20', 'money', 'approved', 76, NOW() - INTERVAL '19 days', NOW() - INTERVAL '24 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (56, 79, DATE '2026-05-21', TIME '18:00:00', TIME '19:00:00', 2.0, '加班 #21', 'leave', 'rejected', 76, NOW() - INTERVAL '20 days', NOW() - INTERVAL '25 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (57, 80, DATE '2026-05-22', TIME '18:00:00', TIME '20:00:00', 3.0, '加班 #22', 'money', 'pending', 76, NOW() - INTERVAL '21 days', NOW() - INTERVAL '26 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (58, 81, DATE '2026-05-23', TIME '18:00:00', TIME '21:00:00', 4.0, '加班 #23', 'leave', 'approved', 76, NOW() - INTERVAL '22 days', NOW() - INTERVAL '27 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (59, 82, DATE '2026-05-24', TIME '18:00:00', TIME '22:00:00', 5.0, '加班 #24', 'money', 'rejected', 76, NOW() - INTERVAL '23 days', NOW() - INTERVAL '28 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (60, 83, DATE '2026-05-25', TIME '18:00:00', TIME '19:00:00', 6.0, '加班 #25', 'leave', 'pending', 76, NOW() - INTERVAL '24 days', NOW() - INTERVAL '29 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (61, 84, DATE '2026-05-26', TIME '18:00:00', TIME '20:00:00', 2.0, '加班 #26', 'money', 'approved', 76, NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (62, 85, DATE '2026-05-27', TIME '18:00:00', TIME '21:00:00', 3.0, '加班 #27', 'leave', 'rejected', 76, NOW() - INTERVAL '26 days', NOW() - INTERVAL '31 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (63, 86, DATE '2026-05-28', TIME '18:00:00', TIME '22:00:00', 4.0, '加班 #28', 'money', 'pending', 76, NOW() - INTERVAL '27 days', NOW() - INTERVAL '32 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (64, 87, DATE '2026-05-29', TIME '18:00:00', TIME '19:00:00', 5.0, '加班 #29', 'leave', 'approved', 76, NOW() - INTERVAL '28 days', NOW() - INTERVAL '33 days', NOW());
INSERT INTO overtime_requests (id, user_id, overtime_date, start_time, end_time, hours, reason, compensation_type, status, approver_id, approved_at, created_at, updated_at)
            VALUES (65, 88, DATE '2026-05-30', TIME '18:00:00', TIME '20:00:00', 6.0, '加班 #30', 'money', 'rejected', 76, NOW() - INTERVAL '29 days', NOW() - INTERVAL '34 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (131, 1, 74, DATE '2026-05-01', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #1', 1, true, 'pending', 76, NOW() - INTERVAL '0 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (132, 2, 75, DATE '2026-05-02', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #2', 2, true, 'approved', 76, NOW() - INTERVAL '1 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (133, 3, 76, DATE '2026-05-03', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #3', 3, true, 'rejected', 76, NOW() - INTERVAL '2 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (134, 4, 77, DATE '2026-05-04', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #4', 4, true, 'completed', 76, NOW() - INTERVAL '3 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (135, 5, 78, DATE '2026-05-05', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #5', 1, true, 'pending', 76, NOW() - INTERVAL '4 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (136, 1, 79, DATE '2026-05-06', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #6', 2, true, 'approved', 76, NOW() - INTERVAL '5 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (137, 2, 80, DATE '2026-05-07', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #7', 3, true, 'rejected', 76, NOW() - INTERVAL '6 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (138, 3, 81, DATE '2026-05-08', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #8', 4, true, 'completed', 76, NOW() - INTERVAL '7 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (139, 4, 82, DATE '2026-05-09', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #9', 1, true, 'pending', 76, NOW() - INTERVAL '8 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (140, 5, 83, DATE '2026-05-10', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #10', 2, true, 'approved', 76, NOW() - INTERVAL '9 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (141, 1, 84, DATE '2026-05-11', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #11', 3, true, 'rejected', 76, NOW() - INTERVAL '10 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (142, 2, 85, DATE '2026-05-12', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #12', 4, true, 'completed', 76, NOW() - INTERVAL '11 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (143, 3, 86, DATE '2026-05-13', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #13', 1, true, 'pending', 76, NOW() - INTERVAL '12 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (144, 4, 87, DATE '2026-05-14', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #14', 2, true, 'approved', 76, NOW() - INTERVAL '13 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (145, 5, 88, DATE '2026-05-15', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #15', 3, true, 'rejected', 76, NOW() - INTERVAL '14 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (146, 1, 74, DATE '2026-05-16', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #16', 4, true, 'completed', 76, NOW() - INTERVAL '15 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (147, 2, 75, DATE '2026-05-17', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #17', 1, true, 'pending', 76, NOW() - INTERVAL '16 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (148, 3, 76, DATE '2026-05-18', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #18', 2, true, 'approved', 76, NOW() - INTERVAL '17 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (149, 4, 77, DATE '2026-05-19', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #19', 3, true, 'rejected', 76, NOW() - INTERVAL '18 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (150, 5, 78, DATE '2026-05-20', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #20', 4, true, 'completed', 76, NOW() - INTERVAL '19 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (151, 1, 79, DATE '2026-05-21', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #21', 1, true, 'pending', 76, NOW() - INTERVAL '20 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (152, 2, 80, DATE '2026-05-22', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #22', 2, true, 'approved', 76, NOW() - INTERVAL '21 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (153, 3, 81, DATE '2026-05-23', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #23', 3, true, 'rejected', 76, NOW() - INTERVAL '22 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (154, 4, 82, DATE '2026-05-24', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #24', 4, true, 'completed', 76, NOW() - INTERVAL '23 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (155, 5, 83, DATE '2026-05-25', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #25', 1, true, 'pending', 76, NOW() - INTERVAL '24 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (156, 1, 84, DATE '2026-05-26', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #26', 2, true, 'approved', 76, NOW() - INTERVAL '25 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (157, 2, 85, DATE '2026-05-27', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #27', 3, true, 'rejected', 76, NOW() - INTERVAL '26 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (158, 3, 86, DATE '2026-05-28', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #28', 4, true, 'completed', 76, NOW() - INTERVAL '27 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (159, 4, 87, DATE '2026-05-29', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #29', 1, true, 'pending', 76, NOW() - INTERVAL '28 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (160, 5, 88, DATE '2026-05-30', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #30', 2, true, 'approved', 76, NOW() - INTERVAL '29 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (161, 1, 74, DATE '2026-05-31', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #31', 3, true, 'rejected', 76, NOW() - INTERVAL '30 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (162, 2, 75, DATE '2026-06-01', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #32', 4, true, 'completed', 76, NOW() - INTERVAL '31 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (163, 3, 76, DATE '2026-06-02', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #33', 1, true, 'pending', 76, NOW() - INTERVAL '32 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (164, 4, 77, DATE '2026-06-03', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #34', 2, true, 'approved', 76, NOW() - INTERVAL '33 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (165, 5, 78, DATE '2026-06-04', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #35', 3, true, 'rejected', 76, NOW() - INTERVAL '34 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (166, 1, 79, DATE '2026-06-05', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #36', 4, true, 'completed', 76, NOW() - INTERVAL '35 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (167, 2, 80, DATE '2026-06-06', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #37', 1, true, 'pending', 76, NOW() - INTERVAL '36 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (168, 3, 81, DATE '2026-06-07', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #38', 2, true, 'approved', 76, NOW() - INTERVAL '37 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (169, 4, 82, DATE '2026-06-08', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #39', 3, true, 'rejected', 76, NOW() - INTERVAL '38 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (170, 5, 83, DATE '2026-06-09', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #40', 4, true, 'completed', 76, NOW() - INTERVAL '39 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (171, 1, 84, DATE '2026-06-10', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #41', 1, true, 'pending', 76, NOW() - INTERVAL '40 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (172, 2, 85, DATE '2026-06-11', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #42', 2, true, 'approved', 76, NOW() - INTERVAL '41 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (173, 3, 86, DATE '2026-06-12', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #43', 3, true, 'rejected', 76, NOW() - INTERVAL '42 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (174, 4, 87, DATE '2026-06-13', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #44', 4, true, 'completed', 76, NOW() - INTERVAL '43 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (175, 5, 88, DATE '2026-06-14', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #45', 1, true, 'pending', 76, NOW() - INTERVAL '44 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (176, 1, 74, DATE '2026-06-15', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #46', 2, true, 'approved', 76, NOW() - INTERVAL '45 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (177, 2, 75, DATE '2026-06-16', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #47', 3, true, 'rejected', 76, NOW() - INTERVAL '46 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (178, 3, 76, DATE '2026-06-17', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #48', 4, true, 'completed', 76, NOW() - INTERVAL '47 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (179, 4, 77, DATE '2026-06-18', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #49', 1, true, 'pending', 76, NOW() - INTERVAL '48 days', NOW());
INSERT INTO vehicle_usage_requests (id, vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, approver_id, created_at, updated_at)
            VALUES (180, 5, 78, DATE '2026-06-19', TIME '09:00:00', TIME '18:00:00', '北京某地', '用车 #50', 2, true, 'approved', 76, NOW() - INTERVAL '49 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (251, 'approval_pending', 'approval_pending 通知 #1', '通知内容 #1', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '0 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (252, 'project_update', 'project_update 通知 #2', '通知内容 #2', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '1 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (253, 'payment_due', 'payment_due 通知 #3', '通知内容 #3', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '2 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (254, 'leave_result', 'leave_result 通知 #4', '通知内容 #4', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '3 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (255, 'attendance_reminder', 'attendance_reminder 通知 #5', '通知内容 #5', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '4 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (256, 'approval_pending', 'approval_pending 通知 #6', '通知内容 #6', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '5 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (257, 'project_update', 'project_update 通知 #7', '通知内容 #7', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '6 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (258, 'payment_due', 'payment_due 通知 #8', '通知内容 #8', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '7 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (259, 'leave_result', 'leave_result 通知 #9', '通知内容 #9', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '8 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (260, 'attendance_reminder', 'attendance_reminder 通知 #10', '通知内容 #10', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '9 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (261, 'approval_pending', 'approval_pending 通知 #11', '通知内容 #11', 84, 'App\Models\User', 1, 'info', NOW() - INTERVAL '10 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (262, 'project_update', 'project_update 通知 #12', '通知内容 #12', 85, 'App\Models\User', 1, 'info', NOW() - INTERVAL '11 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (263, 'payment_due', 'payment_due 通知 #13', '通知内容 #13', 86, 'App\Models\User', 1, 'info', NOW() - INTERVAL '12 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (264, 'leave_result', 'leave_result 通知 #14', '通知内容 #14', 87, 'App\Models\User', 1, 'info', NOW() - INTERVAL '13 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (265, 'attendance_reminder', 'attendance_reminder 通知 #15', '通知内容 #15', 88, 'App\Models\User', 1, 'info', NOW() - INTERVAL '14 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (266, 'approval_pending', 'approval_pending 通知 #16', '通知内容 #16', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '15 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (267, 'project_update', 'project_update 通知 #17', '通知内容 #17', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '16 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (268, 'payment_due', 'payment_due 通知 #18', '通知内容 #18', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '17 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (269, 'leave_result', 'leave_result 通知 #19', '通知内容 #19', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '18 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (270, 'attendance_reminder', 'attendance_reminder 通知 #20', '通知内容 #20', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '19 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (271, 'approval_pending', 'approval_pending 通知 #21', '通知内容 #21', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '20 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (272, 'project_update', 'project_update 通知 #22', '通知内容 #22', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '21 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (273, 'payment_due', 'payment_due 通知 #23', '通知内容 #23', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '22 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (274, 'leave_result', 'leave_result 通知 #24', '通知内容 #24', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '23 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (275, 'attendance_reminder', 'attendance_reminder 通知 #25', '通知内容 #25', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '24 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (276, 'approval_pending', 'approval_pending 通知 #26', '通知内容 #26', 84, 'App\Models\User', 1, 'info', NOW() - INTERVAL '25 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (277, 'project_update', 'project_update 通知 #27', '通知内容 #27', 85, 'App\Models\User', 1, 'info', NOW() - INTERVAL '26 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (278, 'payment_due', 'payment_due 通知 #28', '通知内容 #28', 86, 'App\Models\User', 1, 'info', NOW() - INTERVAL '27 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (279, 'leave_result', 'leave_result 通知 #29', '通知内容 #29', 87, 'App\Models\User', 1, 'info', NOW() - INTERVAL '28 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (280, 'attendance_reminder', 'attendance_reminder 通知 #30', '通知内容 #30', 88, 'App\Models\User', 1, 'info', NOW() - INTERVAL '29 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (281, 'approval_pending', 'approval_pending 通知 #31', '通知内容 #31', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '0 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (282, 'project_update', 'project_update 通知 #32', '通知内容 #32', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '1 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (283, 'payment_due', 'payment_due 通知 #33', '通知内容 #33', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '2 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (284, 'leave_result', 'leave_result 通知 #34', '通知内容 #34', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '3 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (285, 'attendance_reminder', 'attendance_reminder 通知 #35', '通知内容 #35', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '4 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (286, 'approval_pending', 'approval_pending 通知 #36', '通知内容 #36', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '5 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (287, 'project_update', 'project_update 通知 #37', '通知内容 #37', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '6 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (288, 'payment_due', 'payment_due 通知 #38', '通知内容 #38', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '7 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (289, 'leave_result', 'leave_result 通知 #39', '通知内容 #39', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '8 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (290, 'attendance_reminder', 'attendance_reminder 通知 #40', '通知内容 #40', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '9 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (291, 'approval_pending', 'approval_pending 通知 #41', '通知内容 #41', 84, 'App\Models\User', 1, 'info', NOW() - INTERVAL '10 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (292, 'project_update', 'project_update 通知 #42', '通知内容 #42', 85, 'App\Models\User', 1, 'info', NOW() - INTERVAL '11 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (293, 'payment_due', 'payment_due 通知 #43', '通知内容 #43', 86, 'App\Models\User', 1, 'info', NOW() - INTERVAL '12 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (294, 'leave_result', 'leave_result 通知 #44', '通知内容 #44', 87, 'App\Models\User', 1, 'info', NOW() - INTERVAL '13 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (295, 'attendance_reminder', 'attendance_reminder 通知 #45', '通知内容 #45', 88, 'App\Models\User', 1, 'info', NOW() - INTERVAL '14 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (296, 'approval_pending', 'approval_pending 通知 #46', '通知内容 #46', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '15 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (297, 'project_update', 'project_update 通知 #47', '通知内容 #47', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '16 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (298, 'payment_due', 'payment_due 通知 #48', '通知内容 #48', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '17 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (299, 'leave_result', 'leave_result 通知 #49', '通知内容 #49', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '18 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (300, 'attendance_reminder', 'attendance_reminder 通知 #50', '通知内容 #50', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '19 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (301, 'approval_pending', 'approval_pending 通知 #51', '通知内容 #51', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '20 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (302, 'project_update', 'project_update 通知 #52', '通知内容 #52', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '21 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (303, 'payment_due', 'payment_due 通知 #53', '通知内容 #53', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '22 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (304, 'leave_result', 'leave_result 通知 #54', '通知内容 #54', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '23 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (305, 'attendance_reminder', 'attendance_reminder 通知 #55', '通知内容 #55', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '24 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (306, 'approval_pending', 'approval_pending 通知 #56', '通知内容 #56', 84, 'App\Models\User', 1, 'info', NOW() - INTERVAL '25 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (307, 'project_update', 'project_update 通知 #57', '通知内容 #57', 85, 'App\Models\User', 1, 'info', NOW() - INTERVAL '26 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (308, 'payment_due', 'payment_due 通知 #58', '通知内容 #58', 86, 'App\Models\User', 1, 'info', NOW() - INTERVAL '27 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (309, 'leave_result', 'leave_result 通知 #59', '通知内容 #59', 87, 'App\Models\User', 1, 'info', NOW() - INTERVAL '28 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (310, 'attendance_reminder', 'attendance_reminder 通知 #60', '通知内容 #60', 88, 'App\Models\User', 1, 'info', NOW() - INTERVAL '29 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (311, 'approval_pending', 'approval_pending 通知 #61', '通知内容 #61', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '0 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (312, 'project_update', 'project_update 通知 #62', '通知内容 #62', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '1 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (313, 'payment_due', 'payment_due 通知 #63', '通知内容 #63', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '2 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (314, 'leave_result', 'leave_result 通知 #64', '通知内容 #64', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '3 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (315, 'attendance_reminder', 'attendance_reminder 通知 #65', '通知内容 #65', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '4 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (316, 'approval_pending', 'approval_pending 通知 #66', '通知内容 #66', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '5 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (317, 'project_update', 'project_update 通知 #67', '通知内容 #67', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '6 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (318, 'payment_due', 'payment_due 通知 #68', '通知内容 #68', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '7 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (319, 'leave_result', 'leave_result 通知 #69', '通知内容 #69', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '8 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (320, 'attendance_reminder', 'attendance_reminder 通知 #70', '通知内容 #70', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '9 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (321, 'approval_pending', 'approval_pending 通知 #71', '通知内容 #71', 84, 'App\Models\User', 1, 'info', NOW() - INTERVAL '10 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (322, 'project_update', 'project_update 通知 #72', '通知内容 #72', 85, 'App\Models\User', 1, 'info', NOW() - INTERVAL '11 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (323, 'payment_due', 'payment_due 通知 #73', '通知内容 #73', 86, 'App\Models\User', 1, 'info', NOW() - INTERVAL '12 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (324, 'leave_result', 'leave_result 通知 #74', '通知内容 #74', 87, 'App\Models\User', 1, 'info', NOW() - INTERVAL '13 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (325, 'attendance_reminder', 'attendance_reminder 通知 #75', '通知内容 #75', 88, 'App\Models\User', 1, 'info', NOW() - INTERVAL '14 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (326, 'approval_pending', 'approval_pending 通知 #76', '通知内容 #76', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '15 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (327, 'project_update', 'project_update 通知 #77', '通知内容 #77', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '16 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (328, 'payment_due', 'payment_due 通知 #78', '通知内容 #78', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '17 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (329, 'leave_result', 'leave_result 通知 #79', '通知内容 #79', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '18 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (330, 'attendance_reminder', 'attendance_reminder 通知 #80', '通知内容 #80', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '19 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (331, 'approval_pending', 'approval_pending 通知 #81', '通知内容 #81', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '20 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (332, 'project_update', 'project_update 通知 #82', '通知内容 #82', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '21 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (333, 'payment_due', 'payment_due 通知 #83', '通知内容 #83', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '22 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (334, 'leave_result', 'leave_result 通知 #84', '通知内容 #84', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '23 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (335, 'attendance_reminder', 'attendance_reminder 通知 #85', '通知内容 #85', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '24 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (336, 'approval_pending', 'approval_pending 通知 #86', '通知内容 #86', 84, 'App\Models\User', 1, 'info', NOW() - INTERVAL '25 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (337, 'project_update', 'project_update 通知 #87', '通知内容 #87', 85, 'App\Models\User', 1, 'info', NOW() - INTERVAL '26 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (338, 'payment_due', 'payment_due 通知 #88', '通知内容 #88', 86, 'App\Models\User', 1, 'info', NOW() - INTERVAL '27 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (339, 'leave_result', 'leave_result 通知 #89', '通知内容 #89', 87, 'App\Models\User', 1, 'info', NOW() - INTERVAL '28 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (340, 'attendance_reminder', 'attendance_reminder 通知 #90', '通知内容 #90', 88, 'App\Models\User', 1, 'info', NOW() - INTERVAL '29 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (341, 'approval_pending', 'approval_pending 通知 #91', '通知内容 #91', 74, 'App\Models\User', 1, 'info', NOW() - INTERVAL '0 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (342, 'project_update', 'project_update 通知 #92', '通知内容 #92', 75, 'App\Models\User', 1, 'info', NOW() - INTERVAL '1 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (343, 'payment_due', 'payment_due 通知 #93', '通知内容 #93', 76, 'App\Models\User', 1, 'info', NOW() - INTERVAL '2 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (344, 'leave_result', 'leave_result 通知 #94', '通知内容 #94', 77, 'App\Models\User', 1, 'info', NOW() - INTERVAL '3 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (345, 'attendance_reminder', 'attendance_reminder 通知 #95', '通知内容 #95', 78, 'App\Models\User', 1, 'info', NOW() - INTERVAL '4 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (346, 'approval_pending', 'approval_pending 通知 #96', '通知内容 #96', 79, 'App\Models\User', 1, 'info', NOW() - INTERVAL '5 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (347, 'project_update', 'project_update 通知 #97', '通知内容 #97', 80, 'App\Models\User', 1, 'info', NOW() - INTERVAL '6 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (348, 'payment_due', 'payment_due 通知 #98', '通知内容 #98', 81, 'App\Models\User', 1, 'info', NOW() - INTERVAL '7 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (349, 'leave_result', 'leave_result 通知 #99', '通知内容 #99', 82, 'App\Models\User', 1, 'info', NOW() - INTERVAL '8 days', NOW());
INSERT INTO notifications (id, type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
            VALUES (350, 'attendance_reminder', 'attendance_reminder 通知 #100', '通知内容 #100', 83, 'App\Models\User', 1, 'info', NOW() - INTERVAL '9 days', NOW());
COMMIT;