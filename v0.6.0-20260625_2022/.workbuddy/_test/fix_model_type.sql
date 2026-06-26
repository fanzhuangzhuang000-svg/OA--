-- 把 model_has_roles 里的 model_type 反斜杠去掉
-- 当前存的是 'App\\Models\\User' (双反斜杠), 应该是 'App\Models\User' (单反斜杠)
UPDATE model_has_roles SET model_type = 'App\Models\User' WHERE model_type = 'App\\Models\\User';
SELECT model_type, count(*) FROM model_has_roles GROUP BY model_type;
