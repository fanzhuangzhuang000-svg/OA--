"""
冗余代码 / 永远为真 / 复制粘贴样板 检测器
"""
import re
from pathlib import Path
from collections import defaultdict

API_DIR = Path(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api')

REDUNDANT_PATTERNS = [
    # 1. if (!empty($x)) { ... }  但 $x 在前面 validate 已经保证存在
    (r'if\s*\(\s*!\s*empty\s*\(\s*\$(\w+)\[\s*[\'"](\w+)[\'"]\s*\]\s*\)\s*\)\s*\{([^}]+)\}', 'optional-field-redundant-if'),

    # 2. if (条件) { return A } else { return B }  等价 if(!条件) return B; return A;
    (r'if\s*\(([^)]+)\)\s*\{\s*return\s+([^;]+);?\s*\}\s*else\s*\{\s*return\s+([^;]+);?\s*\}', 'trivial-if-else'),

    # 3. array_key_exists 然后 isset 双重
    (r'array_key_exists\s*\(\s*[\'"](\w+)[\'"]', 'array-key-exists'),

    # 4. !!$x 强制 bool 转
    (r'\(bool\)\s*\$', 'bool-cast'),

    # 5. count() > 0 用 empty() 替代
    (r'count\s*\(\s*\$(\w+)\s*\)\s*>\s*0', 'count-vs-empty'),

    # 6. try { } catch (\\Exception $e) { Log::error($e->getMessage()) }  重复样板
    (r'catch\s*\(\s*\\\\?Exception\s+\$e\s*\)\s*\{[^}]*Log::error[^}]*\}', 'generic-catch-log'),

    # 7. Cache::forget() 后面立刻 for 5+ 个 key - 重复样板
    (r'Cache::forget', 'cache-forget-call'),

    # 8. $request->validate 后面立刻 if (条件) throw - 冗余
    (r'validate\([^)]+\);\s*if\s*\(', 'validate-then-if'),

    # 9. 永远为真: if (true) / if (1) / if (!empty($x)) 但前面已经 set $x = $x
    (r'if\s*\(\s*(true|1|!\s*empty)', 'always-true-if'),

    # 10. 三元运算 ?: 'default'  跟 ?? 'default' 重复
    (r'\?:\s*[\'"][^\'"]+[\'"]', 'ternary-default'),
]

print("=== 阶段 A: 冗余模式扫描 ===\n")

findings = defaultdict(list)
for f in sorted(API_DIR.glob('*.php')):
    text = f.read_text(encoding='utf-8')
    for i, line in enumerate(text.split('\n'), 1):
        # 跳过注释
        if line.strip().startswith('//') or line.strip().startswith('*'):
            continue
        for pattern, name in REDUNDANT_PATTERNS:
            if re.search(pattern, line):
                findings[name].append((f.name, i, line.strip()[:120]))

for name, hits in findings.items():
    if not hits:
        continue
    print(f"### {name}  ({len(hits)} 次)")
    for f, l, snippet in hits[:15]:  # 每个模式最多 15 个示例
        print(f"  {f}:{l}  →  {snippet}")
    if len(hits) > 15:
        print(f"  ... 还有 {len(hits)-15} 处")
    print()

# === 阶段 B: 复制粘贴样板检测 ===
print("\n=== 阶段 B: 复制粘贴样板检测 ===\n")

# 收集每个 Controller 里"非常相似"的连续 3 行
block_size = 3
block_counts = defaultdict(list)
for f in sorted(API_DIR.glob('*.php')):
    text = f.read_text(encoding='utf-8')
    lines = text.split('\n')
    for i in range(len(lines) - block_size + 1):
        block = tuple(l.strip() for l in lines[i:i+block_size])
        # 过滤太短
        if sum(len(b) for b in block) < 60:
            continue
        # 过滤变量差异
        normalized = tuple(re.sub(r'\$\w+', '$X', b) for b in block)
        block_counts[normalized].append((f.name, i + 1, block))

# 找出现 3+ 次的块
duplicates = [(k, v) for k, v in block_counts.items() if len(v) >= 3]
duplicates.sort(key=lambda x: -len(x[1]))

print(f"找到 {len(duplicates)} 个重复 3 行块 (>= 3 处出现)\n")
for normalized, locs in duplicates[:10]:
    sample = locs[0][2]
    print(f"### 重复 {len(locs)} 次:")
    for f, l, _ in locs:
        print(f"  {f}:{l}")
    print(f"  示例:")
    for s in sample:
        print(f"    {s}")
    print()

# === 阶段 C: 特定 Controller 内部问题 ===
print("\n=== 阶段 C: 特定 Controller 内部问题 ===\n")

# C1. ApprovalCenter 等 4 个 Controller 是否真的在用 HandlesApproval 的方法
trait_path = Path(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\Concerns\HandlesApproval.php')
if trait_path.exists():
    trait_text = trait_path.read_text(encoding='utf-8')
    trait_methods = set()
    for m in re.finditer(r'public\s+function\s+(\w+)\s*\(', trait_text):
        trait_methods.add(m.group(1))
    print(f"HandlesApproval trait 暴露的方法: {trait_methods}")
    for f in ['ApprovalCenterController.php', 'FinanceApprovalController.php', 'OperationApprovalController.php', 'ProjectApprovalController.php']:
        ctrl_text = (API_DIR / f).read_text(encoding='utf-8')
        used = []
        for m in trait_methods:
            if re.search(r'\$this->' + m + r'\s*\(', ctrl_text):
                used.append(m)
        print(f"  {f}: 用了 {used}")
