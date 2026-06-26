import subprocess, os

out = subprocess.check_output(['git', 'diff', 'v1.0.0..HEAD', '--name-only', '--', 'pc-api/'], cwd='.').decode()
php_files = [f for f in out.split('\n') if f.endswith('.php') and f]
# 用绝对路径
out_path = os.path.abspath('D:/work/website/OA/.workbuddy/v058_php_files.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'# 共 {len(php_files)} 个 PHP 文件\n')
    for fp in sorted(php_files):
        f.write(fp[7:] + '\n')
print('done', len(php_files), '->', out_path)
