"""通用化 SQL 修复工具: 把所有外键 user_id/manager_id 引用替换为 valid IDs"""
import re
import paramiko
import sys

VALID_USERS    = sorted({1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,19,20})
VALID_CUST     = sorted(set(range(1, 41)))
VALID_PROJ     = sorted(set(range(72, 122)))
VALID_DEPT     = [10, 11, 12, 13, 14, 15]
VALID_POS      = [1, 2, 3, 4, 5, 6, 7, 8]

def fix_id(value, valid_pool):
    """把 value 映射到 valid_pool (mod 循环)"""
    if value in valid_pool:
        return value
    return valid_pool[(value - valid_pool[0]) % len(valid_pool)]

def patch_file(path, rules):
    """
    rules: list of dicts
      {
        'state': 'in_table_name',  # 触发此规则的 INSERT INTO 表名
        'pattern': r'^(\s+VALUES\s+\(\d+,\s+\d+,\s+)(\d+)(,)',  # 哪一列是数字 (这里是第3个)
        'valid': valid_pool,  # 允许的值池
        'col_index': 2,  # 用第几个分组
      }
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    current_state = None

    for line in lines:
        new_line = line
        # 状态机: 跟踪当前在哪个 INSERT
        m_state = re.match(r'^INSERT INTO (\w+)', line)
        if m_state:
            current_state = m_state.group(1)

        for rule in rules:
            if current_state == rule['state']:
                m = re.match(rule['pattern'], line)
                if m:
                    val = int(m.group(rule['col_index']))
                    if val not in rule['valid']:
                        new_val = fix_id(val, rule['valid'])
                        # 替换 m.group(col_index)
                        new_line = m.group(0)[:m.start(rule['col_index'])] + str(new_val) + m.group(0)[m.end(rule['col_index']):]
                        # 因为替换后 m 失效, 用新行重做
                        m2 = re.match(rule['pattern'], new_line)
                        if m2:
                            new_line = line[:m2.start(rule['col_index'])] + str(new_val) + line[m2.end(rule['col_index']):]
                        else:
                            new_line = line
        new_lines.append(new_line)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f'patched {path}')

if __name__ == '__main__':
    file = sys.argv[1] if len(sys.argv) > 1 else '04_gen_projects.sql'
    table = sys.argv[2] if len(sys.argv) > 2 else None

    rules = [
        # projects.manager_id (第 12 个 VALUES 列: 紧接 progress 数字 + , DATE 前)
        {
            'state': 'projects',
            'pattern': r'^(\s+)(\d+)(,\s*DATE\s+\')',
            'valid': VALID_USERS,
            'col_index': 2,
        },
        # project_members.user_id (VALUES (id, project_id, user_id, role,...)
        {
            'state': 'project_members',
            'pattern': r'^(\s+VALUES\s+\(\d+,\s+\d+,\s+)(\d+)(,)',
            'valid': VALID_USERS,
            'col_index': 2,
        },
        # construction_logs.user_id
        {
            'state': 'construction_logs',
            'pattern': r'^(\s+VALUES\s+\(\d+,\s+\d+,\s+)(\d+)(,\s*DATE)',
            'valid': VALID_USERS,
            'col_index': 2,
        },
        # users.id
        {
            'state': 'users',
            'pattern': r'^(\s+VALUES\s+\()(\d+)(,',
            'valid': VALID_USERS,
            'col_index': 2,
        },
        # customers.id
        {
            'state': 'customers',
            'pattern': r'^(\s+VALUES\s+\()(\d+)(,',
            'valid': VALID_CUST,
            'col_index': 2,
        },
        # projects.id
        {
            'state': 'projects',
            'pattern': r'^(\s+VALUES\s+\()(\d+)(,',
            'valid': VALID_PROJ,
            'col_index': 2,
        },
    ]
    patch_file(file, rules)
