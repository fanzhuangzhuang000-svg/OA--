DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..4 LOOP
        INSERT INTO disk_settings (key, value, created_at, updated_at)
        VALUES ('user_quota_' || i::text, json_build_object('quota', 1073741824, 'used', 100000), NOW(), NOW());
    END LOOP;
END $$;