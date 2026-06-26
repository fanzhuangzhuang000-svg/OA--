-- V0.5.7 E2E 演示环境 — 重新种入核心账号
-- admin1 / admin123  (id=1 已建, 这里用 UNIQUE 兜底)
-- fin_wu / admin123
-- sales_yang / admin123
-- tech_qian / admin123
-- const_zheng / admin123

-- 1) 用 raw password = 'admin123' 的 bcrypt (cost=10, 在 117 上实时生成)
-- Hash: $2y$10$dskHMlJA8ffaGcISrbNfjeV1kZEQDkSo.5IqEZfgnH7RJ4F43.lma

INSERT INTO users (id, username, name, password, type, status, email, phone, created_at, updated_at)
VALUES
  (1, 'admin1', '超级管理员', '$2y$10$dskHMlJA8ffaGcISrbNfjeV1kZEQDkSo.5IqEZfgnH7RJ4F43.lma', 'staff', 'active', 'admin@afjsw.cn', '13800000001', NOW(), NOW()),
  (2, 'fin_wu', '财务小吴', '$2y$10$dskHMlJA8ffaGcISrbNfjeV1kZEQDkSo.5IqEZfgnH7RJ4F43.lma', 'staff', 'active', 'fin@afjsw.cn', '13800000002', NOW(), NOW()),
  (3, 'sales_yang', '销售小杨', '$2y$10$dskHMlJA8ffaGcISrbNfjeV1kZEQDkSo.5IqEZfgnH7RJ4F43.lma', 'staff', 'active', 'sales@afjsw.cn', '13800000003', NOW(), NOW()),
  (4, 'tech_qian', '技术小钱', '$2y$10$dskHMlJA8ffaGcISrbNfjeV1kZEQDkSo.5IqEZfgnH7RJ4F43.lma', 'staff', 'active', 'tech@afjsw.cn', '13800000004', NOW(), NOW()),
  (5, 'const_zheng', '施工小郑', '$2y$10$dskHMlJA8ffaGcISrbNfjeV1kZEQDkSo.5IqEZfgnH7RJ4F43.lma', 'staff', 'active', 'const@afjsw.cn', '13800000005', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  password = EXCLUDED.password,
  name = EXCLUDED.name,
  email = EXCLUDED.email,
  phone = EXCLUDED.phone,
  type = EXCLUDED.type,
  status = EXCLUDED.status,
  updated_at = NOW();

-- 2) 设 sequence
SELECT setval(pg_get_serial_sequence('users','id'), GREATEST((SELECT MAX(id) FROM users), 1), true);

-- 3) 分配角色
INSERT INTO model_has_roles (role_id, model_type, model_id)
SELECT r.id, 'App\\Models\\User', u.id
FROM users u
JOIN roles r ON (
  (u.username = 'admin1'        AND r.name = 'admin') OR
  (u.username = 'fin_wu'        AND r.name = 'finance') OR
  (u.username IN ('sales_yang') AND r.name = 'sales') OR
  (u.username = 'tech_qian'     AND r.name = 'manager') OR
  (u.username = 'const_zheng'   AND r.name = 'manager')
)
ON CONFLICT DO NOTHING;

-- 4) 修正 users.sequence 防 23505
DO $$
BEGIN
    PERFORM setval(pg_get_serial_sequence('users','id'),
      COALESCE((SELECT MAX(id) FROM users), 1), true);
END $$;

SELECT '=== 种子账号已重建 ===' info;
SELECT id, username, name, type, status, email FROM users ORDER BY id;
