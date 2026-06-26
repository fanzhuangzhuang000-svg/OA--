-- 把 model_type 统一改成 'App\Models\User' (15字符单反斜杠)
-- 不管现是什么反斜杠写法
UPDATE model_has_roles SET model_type = replace(model_type, '\\', '') WHERE model_type LIKE '%\\%';
-- 现在所有都应该是 'AppModelsUser' 没用 \  - 重新组装
UPDATE model_has_roles SET model_type = 'App\Models\User' WHERE model_type = 'AppModelsUser';
SELECT model_type, length(model_type) AS len, count(*) FROM model_has_roles GROUP BY model_type, length(model_type) ORDER BY len;
