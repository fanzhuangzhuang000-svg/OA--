import re
valid_users = sorted({1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,19,20})

with open('04_gen_projects.sql', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
state = None  # 'projects' / 'project_members' / 'construction_logs' / None

for line in lines:
    new_line = line
    if 'INSERT INTO projects' in line:
        state = 'projects'
    elif 'INSERT INTO project_members' in line:
        state = 'project_members'
    elif 'INSERT INTO construction_logs' in line:
        state = 'construction_logs'
    elif line.startswith('INSERT INTO'):
        state = None

    if state == 'projects' and ', DATE' in line:
        m = re.match(r'^(\s+)(\d+)(, DATE)', line)
        if m and 1 <= int(m.group(2)) <= 200 and int(m.group(2)) not in valid_users:
            new_id = valid_users[(int(m.group(2)) - 1) % len(valid_users)]
            new_line = m.group(1) + str(new_id) + m.group(3) + line[m.end():]

    if state == 'project_members' and line.strip().startswith('VALUES'):
        m = re.match(r'^(\s+VALUES\s+\(\d+,\s+\d+,\s+)(\d+)(,)', line)
        if m and int(m.group(2)) not in valid_users:
            new_id = valid_users[(int(m.group(2)) - 1) % len(valid_users)]
            new_line = m.group(1) + str(new_id) + m.group(3) + line[m.end():]

    if state == 'construction_logs' and line.strip().startswith('VALUES'):
        # VALUES (id, project_id, user_id, work_date, weather,...)
        # 数字-数字-数字-DATE-字符串
        m = re.match(r"^(\s+VALUES\s+\(\d+,\s+\d+,\s+)(\d+)(,\s*DATE)", line)
        if m and int(m.group(2)) not in valid_users:
            new_id = valid_users[(int(m.group(2)) - 1) % len(valid_users)]
            new_line = m.group(1) + str(new_id) + m.group(3) + line[m.end():]

    new_lines.append(new_line)

with open('04_gen_projects.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print('done')
