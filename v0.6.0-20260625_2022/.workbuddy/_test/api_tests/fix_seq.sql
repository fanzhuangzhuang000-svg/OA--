DO $$
DECLARE
    r RECORD;
    max_id bigint;
    seq_name text;
BEGIN
    FOR r IN
        SELECT c.relname AS tbl
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r' AND n.nspname = 'public'
          AND EXISTS (SELECT 1 FROM pg_attribute a WHERE a.attrelid = c.oid AND a.attname = 'id')
    LOOP
        EXECUTE format('SELECT COALESCE(MAX(id), 0) FROM %I', r.tbl) INTO max_id;
        seq_name := r.tbl || '_id_seq';
        EXECUTE format('SELECT setval(%L, %s, true)', seq_name, max_id);
        RAISE NOTICE 'Fixed %: seq=%', r.tbl, max_id;
    END LOOP;
END $$;
