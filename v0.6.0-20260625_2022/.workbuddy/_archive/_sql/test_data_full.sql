-- 172 服务器测试数据生成脚本（完整版，包含所有必填字段）
-- 运行方法: PGPASSWORD='your_password' psql -h 127.0.0.1 -U oa_user -d security_oa -f /tmp/test_data_full.sql

BEGIN;

-- 1. 插入用户数据（包含所有必填字段）
INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '张三', 'zhangsan', 'zhangsan@example.com', '13800000001', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'zhangsan@example.com');

INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '李四', 'lisi', 'lisi@example.com', '13800000002', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'lisi@example.com');

INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at)
SELECT '王五', 'wangwu', 'wangwu@example.com', '13800000003', '$2y$10$92IXUNAUbZ3SmHpNApNZOqtq.VzP/XDNoUcIrX7roKLWuZhRhCi', 'active', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'wangwu@example.com');

-- 2. 插入客户数据（包含所有必填字段：province, city, district, address）
INSERT INTO customers (name, category, source, status, assigned_user_id, province, city, district, address, created_at, updated_at)
SELECT '测试客户A', '企业', '网站留言', 'active', 1, '北京市', '北京市', '朝阳区', '测试地址A', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户A');

INSERT INTO customers (name, category, source, status, assigned_user_id, province, city, district, address, created_at, updated_at)
SELECT '测试客户B', '企业', '电话咨询', 'active', 1, '上海市', '上海市', '浦东新区', '测试地址B', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户B');

INSERT INTO customers (name, category, source, status, assigned_user_id, province, city, district, address, created_at, updated_at)
SELECT '测试客户C', '个人', '朋友介绍', 'active', 2, '广东省', '深圳市', '南山区', '测试地址C', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户C');

INSERT INTO customers (name, category, source, status, assigned_user_id, province, city, district, address, created_at, updated_at)
SELECT '测试客户D', '企业', '线上广告', 'active', 2, '浙江省', '杭州市', '西湖区', '测试地址D', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户D');

INSERT INTO customers (name, category, source, status, assigned_user_id, province, city, district, address, created_at, updated_at)
SELECT '测试客户E', '个人', '展会收集', 'active', 3, '四川省', '成都市', '武侯区', '测试地址E', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '测试客户E');

COMMIT;
