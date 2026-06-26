"""修 LedgerController agingByModel — 用 str 替换而非 regex"""
import os

path = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\LedgerController.php'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找 247 行
lines = content.split('\n')
# 找 'private function agingByModel' 所在行
for i, line in enumerate(lines):
    if 'private function agingByModel' in line:
        start = i
        # 找 '$buckets = [' 行
        for j in range(i+1, min(i+15, len(lines))):
            if '$buckets = [' in lines[j]:
                end = j
                # 替换 行 i+1 到 行 j
                new_block = """    {
        $today = now()->startOfDay();
        $isSupplier = str_contains(get_class($query->getModel()), 'SupplierPayable');
        $items = $query->whereIn('status', ['pending', 'partial', 'overdue'])->get();
"""
                lines[i+1] = new_block
                # 删除中间行
                for k in range(end-1, i+1, -1):
                    del lines[k]
                break
        break

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('OK, lines:', len(lines))
