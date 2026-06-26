-- 172 服务器测试数据生成脚本
-- 运行方法: psql -U oa_user -d security_oa -f /tmp/test_data_172.sql

BEGIN;

-- 1. 插入用户数据（如果少于 10 个）
INSERT INTO users (name, email, password, role, department, created_at, updated_at)
SELECT * FROM (
    VALUES 
    ('张三', 'zhangsan@example.com', '123456', '员工', '技术部', NOW(), NOW()),
    ('李四', 'lisi@example.com', '123456', '员工', '销售部', NOW(), NOW()),
    ('王五', 'wangwu@example.com', '123456', '经理', '技术部', NOW(), NOW()),
    ('赵六', 'zhaoliu@example.com', '123456', '员工', '财务部', NOW(), NOW()),
    ('钱七', 'qianqi@example.com', '123456', '员工', '行政部', NOW(), NOW())
) AS new_users(name, email, password, role, department, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = new_users.email);

-- 2. 插入线索数据
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 1', '13800000001', 'lead1@example.com', '展会收集', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 2', '13800000002', 'lead2@example.com', '展会收集', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 3', '13800000003', 'lead3@example.com', '电话咨询', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 4', '13800000004', 'lead4@example.com', '线上广告', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 5', '13800000005', 'lead5@example.com', '网站留言', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 6', '13800000006', 'lead6@example.com', '朋友介绍', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 7', '13800000007', 'lead7@example.com', '网站留言', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 8', '13800000008', 'lead8@example.com', '网站留言', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 9', '13800000009', 'lead9@example.com', '线上广告', 'new', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 10', '13800000010', 'lead10@example.com', '朋友介绍', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 11', '13800000011', 'lead11@example.com', '网站留言', 'new', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 12', '13800000012', 'lead12@example.com', '展会收集', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 13', '13800000013', 'lead13@example.com', '线上广告', 'new', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 14', '13800000014', 'lead14@example.com', '朋友介绍', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 15', '13800000015', 'lead15@example.com', '电话咨询', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 16', '13800000016', 'lead16@example.com', '线上广告', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 17', '13800000017', 'lead17@example.com', '朋友介绍', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 18', '13800000018', 'lead18@example.com', '线上广告', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 19', '13800000019', 'lead19@example.com', '电话咨询', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 20', '13800000020', 'lead20@example.com', '线上广告', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 21', '13800000021', 'lead21@example.com', '线上广告', 'new', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 22', '13800000022', 'lead22@example.com', '线上广告', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 23', '13800000023', 'lead23@example.com', '网站留言', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 24', '13800000024', 'lead24@example.com', '线上广告', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 25', '13800000025', 'lead25@example.com', '网站留言', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 26', '13800000026', 'lead26@example.com', '电话咨询', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 27', '13800000027', 'lead27@example.com', '电话咨询', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 28', '13800000028', 'lead28@example.com', '展会收集', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 29', '13800000029', 'lead29@example.com', '网站留言', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 30', '13800000030', 'lead30@example.com', '展会收集', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 31', '13800000031', 'lead31@example.com', '朋友介绍', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 32', '13800000032', 'lead32@example.com', '朋友介绍', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 33', '13800000033', 'lead33@example.com', '朋友介绍', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 34', '13800000034', 'lead34@example.com', '网站留言', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 35', '13800000035', 'lead35@example.com', '朋友介绍', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 36', '13800000036', 'lead36@example.com', '电话咨询', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 37', '13800000037', 'lead37@example.com', '线上广告', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 38', '13800000038', 'lead38@example.com', '线上广告', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 39', '13800000039', 'lead39@example.com', '朋友介绍', 'new', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 40', '13800000040', 'lead40@example.com', '电话咨询', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 41', '13800000041', 'lead41@example.com', '网站留言', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 42', '13800000042', 'lead42@example.com', '展会收集', 'negotiating', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 43', '13800000043', 'lead43@example.com', '线上广告', 'contacted', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 44', '13800000044', 'lead44@example.com', '电话咨询', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 45', '13800000045', 'lead45@example.com', '电话咨询', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 46', '13800000046', 'lead46@example.com', '朋友介绍', 'proposal', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 47', '13800000047', 'lead47@example.com', '朋友介绍', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 48', '13800000048', 'lead48@example.com', '网站留言', 'lost', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 49', '13800000049', 'lead49@example.com', '电话咨询', 'won', NOW(), NOW());
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('线索客户 50', '13800000050', 'lead50@example.com', '电话咨询', 'won', NOW(), NOW());

-- 3. 插入商机数据
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 1', 489194, 'lost', 20, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 2', 267084, 'inquiry', 5, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 3', 167025, 'qualification', 26, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 4', 361827, 'qualification', 19, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 5', 152868, 'won', 10, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 6', 194182, 'inquiry', 18, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 7', 489355, 'qualification', 7, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 8', 452692, 'proposal', 16, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 9', 115517, 'qualification', 26, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 10', 496168, 'won', 6, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 11', 70446, 'negotiating', 25, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 12', 220224, 'proposal', 9, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 13', 117689, 'inquiry', 24, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 14', 463839, 'inquiry', 22, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 15', 158016, 'quoted', 25, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 16', 393587, 'won', 11, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 17', 434748, 'proposal', 27, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 18', 19014, 'won', 15, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 19', 490501, 'won', 23, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 20', 42764, 'negotiating', 11, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 21', 308223, 'negotiating', 1, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 22', 226268, 'inquiry', 8, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 23', 180232, 'quoted', 3, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 24', 93335, 'inquiry', 16, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 25', 441311, 'qualification', 5, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 26', 90574, 'qualification', 23, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 27', 285039, 'qualification', 27, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 28', 26222, 'qualification', 8, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 29', 25327, 'inquiry', 10, NOW(), NOW());
INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('商机项目 30', 230277, 'qualification', 13, NOW(), NOW());

-- 4. 插入考勤记录
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-06-22', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-06-21', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-06-20', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-06-19', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (1, '2026-06-18', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-06-17', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-06-16', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-06-15', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-06-14', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-06-13', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-06-12', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-06-11', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-06-10', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (3, '2026-06-09', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-06-08', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-06-07', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (3, '2026-06-06', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-06-05', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-06-04', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-06-03', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-06-02', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-06-01', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-05-31', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (1, '2026-05-30', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-05-29', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-05-28', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-05-27', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-05-26', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-05-25', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-05-24', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-05-23', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-05-22', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-05-21', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-05-20', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-05-19', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-05-18', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (3, '2026-05-17', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-05-16', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-05-15', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-05-14', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-05-13', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-05-12', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (3, '2026-05-11', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-05-10', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-05-09', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-05-08', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-05-07', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (3, '2026-05-06', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-05-05', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-05-04', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-05-03', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-05-02', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-05-01', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (5, '2026-04-30', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-04-29', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-04-28', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-27', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-04-26', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-25', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-04-24', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-04-23', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-04-22', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-04-21', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-20', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-04-19', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-04-18', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-04-17', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-04-16', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-15', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-14', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-04-13', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-04-12', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-04-11', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-04-10', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (2, '2026-04-09', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-08', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-04-07', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-04-06', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (1, '2026-04-05', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-04-04', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (1, '2026-04-03', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-04-02', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-04-01', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (3, '2026-03-31', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-03-30', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-03-29', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-03-28', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (10, '2026-03-27', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-03-26', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-03-25', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-03-24', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (9, '2026-03-23', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (1, '2026-03-22', '正常', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-03-21', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (7, '2026-03-20', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-03-19', '迟到', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-03-18', '缺勤', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (4, '2026-03-17', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (8, '2026-03-16', '早退', NOW(), NOW());
INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (6, '2026-03-15', '早退', NOW(), NOW());

-- 5. 插入车辆数据
INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ('京A12345', '奥迪A6', '可用', NOW(), NOW());
INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ('京B67890', '宝马5系', '可用', NOW(), NOW());
INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ('京C54321', '奔驰E级', '维修中', NOW(), NOW());
INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ('京D09876', '丰田凯美瑞', '可用', NOW(), NOW());
INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ('京E13579', '本田雅阁', '已分配', NOW(), NOW());

-- 6. 插入库存物品数据
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('笔记本', '办公用品', 100, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('签字笔', '办公用品', 500, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('A4纸', '办公用品', 50, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('订书机', '办公用品', 20, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('计算器', '办公用品', 15, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('打印纸', '办公用品', 200, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('文件夹', '办公用品', 80, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('胶带', '办公用品', 100, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('剪刀', '办公用品', 30, NOW(), NOW());
INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('胶水', '办公用品', 50, NOW(), NOW());

COMMIT;
