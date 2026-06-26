-- 172 服务器测试数据生成脚本（简化版，无 ON CONFLICT）
-- 运行方法: PGPASSWORD='your_password' psql -h 127.0.0.1 -U oa_user -d security_oa -f /tmp/test_data_simple.sql

BEGIN;

-- 1. 插入用户数据（简化，不用 ON CONFLICT）
INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '张三', 'zhangsan', 'zhangsan@example.com', '13800000001', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'zhangsan@example.com');

INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '李四', 'lisi', 'lisi@example.com', '13800000002', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'lisi@example.com');

INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '王五', 'wangwu', 'wangwu@example.com', '13800000003', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'wangwu@example.com');

INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '赵六', 'zhaoliu', 'zhaoliu@example.com', '13800000004', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'zhaoliu@example.com');

INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '钱七', 'qianqi', 'qianqi@example.com', '13800000005', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'qianqi@example.com');

-- 2. 插入客户数据
INSERT INTO customers (name, category, source, status, assigned_user_id, created_at, updated_at)
SELECT '测试客户A', '企业', '网站留言', 'active', 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户A');

INSERT INTO customers (name, category, source, status, assigned_user_id, created_at, updated_at)
SELECT '测试客户B', '企业', '电话咨询', 'active', 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户B');

INSERT INTO customers (name, category, source, status, assigned_user_id, created_at, updated_at)
SELECT '测试客户C', '个人', '朋友介绍', 'active', 2, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户C');

INSERT INTO customers (name, category, source, status, assigned_user_id, created_at, updated_at)
SELECT '测试客户D', '企业', '线上广告', 'active', 2, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户D');

INSERT INTO customers (name, category, source, status, assigned_user_id, created_at, updated_at)
SELECT '测试客户E', '个人', '展会收集', 'active', 3, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户E');

COMMIT;
