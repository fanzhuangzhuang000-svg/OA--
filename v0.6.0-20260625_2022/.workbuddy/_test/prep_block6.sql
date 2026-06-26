-- 准备块六测试数据
-- 1. 把 lead 21 关联到 referrer 2
UPDATE leads SET referrer_id = 2 WHERE id = 21;
-- 2. 看 lead 21 是否已对应 opp
SELECT id, name, lead_id, stage FROM opportunities WHERE lead_id = 21;
-- 3. 若没有，建一个
INSERT INTO opportunities (opp_no, name, customer_id, lead_id, type, estimated_amount, stage, probability, sales_id, presale_id, created_at, updated_at)
SELECT 'OPP-TEST-' || to_char(now(), 'YYYYMMDDHH24MISS'), '块六测试商机', customer_id, 21, 'comprehensive', 100000, 'requirement', 20, sales_id, presale_id, now(), now()
FROM leads WHERE id = 21
RETURNING id;
