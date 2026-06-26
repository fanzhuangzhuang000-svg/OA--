"""Audit each Vue view for mock vs real API integration."""
import os, re

VIEWS_DIR = r"D:\work\website\OA\pc-web\src\views"
EXEMPT = {'NotFound.vue', 'login/index.vue', 'dashboard/index.vue', 'screen/index.vue'}

def is_real(content):
    return bool(re.search(r"from\s+['\"]@/utils/request['\"]", content) or
                re.search(r"\brequest\.(get|post|put|delete|patch)\s*\(", content) or
                re.search(r"\baxios\.(get|post|put|delete|patch)\s*\(", content))

def has_mock_save(content):
    return bool(re.search(r"ElMessage\.success\([^)]*(?:已创建|已更新|已删除|保存成功|提交成功)", content)) and not is_real(content)

results = []
for root, _, files in os.walk(VIEWS_DIR):
    for f in files:
        if not f.endswith('.vue'):
            continue
        path = os.path.join(root, f)
        with open(path, encoding='utf-8') as fh:
            content = fh.read()
        rel = os.path.relpath(path, VIEWS_DIR).replace('\\', '/')
        if rel in EXEMPT:
            continue
        real = is_real(content)
        mock = has_mock_save(content)
        handlers = re.findall(r"@click=\"(handle[A-Z][\w]+)\"", content)
        results.append((rel, 'REAL' if real else 'MOCK', sorted(set(handlers))))

print('=' * 78)
print('BUTTON AUDIT REPORT')
print('=' * 78)
print()
real_count = sum(1 for r in results if r[1] == 'REAL')
mock_count = len(results) - real_count
print(f"Total views audited: {len(results)}")
print(f"  REAL (calls API): {real_count}")
print(f"  MOCK (only local data): {mock_count}")
print()

print('=' * 78)
print('MOCK VIEWS (buttons not actually saved to DB):')
print('=' * 78)
for rel, kind, handlers in results:
    if kind == 'MOCK' and handlers:
        print(f"  X {rel}")
        for h in handlers:
            print(f"      - @click={h}")

print()
print('=' * 78)
print('REAL VIEWS (wired up to backend):')
print('=' * 78)
for rel, kind, _ in results:
    if kind == 'REAL':
        print(f"  V {rel}")
