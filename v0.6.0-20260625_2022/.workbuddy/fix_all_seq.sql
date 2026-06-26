DO $$
DECLARE r RECORD;
BEGIN
    FOR r IN
        SELECT t.table_name FROM information_schema.tables t
        JOIN information_schema.columns c ON c.table_schema=t.table_schema AND c.table_name=t.table_name
        WHERE t.table_schema='public' AND c.column_name='id' AND c.is_identity='YES'
    LOOP
        EXECUTE format('SELECT setval(pg_get_serial_sequence(%L,%L), COALESCE(MAX(id),1), true) FROM %I', r.table_name, 'id', r.table_name);
    END LOOP;
END $$;
