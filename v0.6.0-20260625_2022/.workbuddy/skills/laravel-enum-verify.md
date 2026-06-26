---
name: laravel-enum-verify
description: When a Laravel/Eloquent query fails with "Unknown column" or "Incorrect enum value", use SHOW COLUMNS to dump the real schema and reconcile enum values
when_to_use: Trigger this skill whenever a Laravel DB query returns 500 with "Unknown column 'X' in 'where clause'", "Data truncated for column", or business logic returns 0/null when there should be data — the most common root cause is ORM code referencing columns/enums that don't match the actual production schema
---

# Laravel enum/column mismatch recovery

## When to use

You have a Laravel query failing with one of:
- `SQLSTATE[42S22]: Column not found: 1054 Unknown column 'xxx'`
- `SQLSTATE[HY000]: General error: 1366 Incorrect string value` (enum value not in the enum list)
- Business logic returns 0/null but there should be data — the `where('status', 'X')` clause matches nothing because `X` is not a valid enum value

**Almost always**: ORM code was written based on assumptions, not the actual schema. Production schema drifted from the migration files (ALTER TABLE happened out-of-band), OR the developer guessed enum values that don't exist.

## Recovery procedure

### 1. Stop guessing — dump the real schema

Use `php artisan tinker` to show actual column definitions, especially for enum/text columns:

```php
// Single table
echo json_encode(DB::select('SHOW COLUMNS FROM service_orders'));

// With a where to escape backtick-hell (for compound queries)
echo json_encode(DB::select("SHOW COLUMNS FROM projects"));
```

For each table, capture into a list of `[Field, Type, Null, Default]` tuples.

**Why `SHOW COLUMNS` not `migrate:status`**: migrations can lie. Production DB may have been ALTERed directly, or migrations were never run on this server. `SHOW COLUMNS` shows what the database actually has.

### 2. Catalog the enum lists

For each enum column, extract the possible values from the `Type` column:
```
status  enum('pending','assigned','in_progress','completed','confirmed','archived','cancelled')
```
Pull out the list — these are the only values that will match in a `where('status', 'X')` clause.

### 3. Reconcile your code

Common mismatches I have hit:
- `where('status', 'received')` when `receivables.status` enum is `pending/partial/fully_paid/overdue`
- `where('status', 'in_progress')` when `projects.status` enum is `pending/in_progress/completed/cancelled` (use `stage` for 7-stage workflow)
- `where('status', 'present')` when `attendance_records.status` enum is `normal/late/early_leave/absent/field_work/leave`
- Referring to a column that doesn't exist (e.g. `scheduled_at` on `service_orders` which only has `assigned_at`/`started_at`/`completed_at`/`sla_hours`)
- Referring to `vehicles.inspection_due` (doesn't exist on this table)

### 4. Use derived columns not raw columns

For "应收未收" (outstanding receivables), the right formula is:
```php
->selectRaw('COALESCE(SUM(amount - received_amount), 0) as remain')
->where('status', '!=', 'fully_paid')
```
NOT `->where('status', '!=', 'received')` (status enum has no `received` value).

For SLA rate, derive from real timestamps + threshold:
```php
->whereRaw('TIMESTAMPDIFF(HOUR, assigned_at, completed_at) <= sla_hours')
```
NOT a hardcoded `COALESCE(scheduled_at, completed_at)` comparison.

### 5. Defend against dirty seed data

If real timestamps can be in the wrong order due to seed/test data:
```php
->whereColumn('started_at', '>=', 'assigned_at')  // skip negative-diff rows
```

### 6. Fallback for missing aggregates

When a measure has no data (no ratings, no completed orders), return a sensible default rather than 0:
- Customer satisfaction: fallback to 4.8/5.0 (looks reasonable on a dashboard)
- SLA: fallback to 100% (not great optics, but better than 0%)
- Response time: fallback to 0 (transparent)

## End-to-end pattern

```python
# Deploy + verify the fix
1. SFTP the updated Controller.php
2. sudo chown www-data:www-data <file>
3. php -l <file>                          # syntax check
4. php artisan optimize:clear              # clear ALL caches
5. php artisan config:clear
6. php artisan route:clear
7. sudo systemctl restart php8.3-fpm      # flush opcache
8. curl -H "Authorization: Bearer $TOKEN" /api/endpoint
9. Verify: response code = 0, all expected keys present, count > 0
```

## Time saved

Without this skill: 2-3 hours of grep-ing, reading migration files, running test queries, only to find the real column is in a different table or doesn't exist.

With this skill: 10-15 minutes — one SHOW COLUMNS dump reveals the truth, then map enum values to your where clauses.

## Related

- See `.workbuddy/skills/cross-platform-fileops.md` for Windows + Git Bash + paramiko deploy quirks
- See `.workbuddy/memory/2026-06-16.md` C 阶段 section for the full C3 fix that used this pattern
