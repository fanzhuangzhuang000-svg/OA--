import os, re, json

# 找前端所有真实调用的API endpoint
api_calls = {}  # path -> [files]
for root, dirs, files in os.walk('pc-web/src'):
    for fn in files:
        if not fn.endswith(('.ts', '.vue', '.js')):
            continue
        path = os.path.join(root, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 匹配 request.get('/xxx') 或 api.xxx('/xxx') 或 `/xxx`
            for m in re.finditer(r"['\"`](/[a-z][a-z\-_/\{\}]+)['\"`]", content):
                url = m.group(1)
                # 标准化参数
                norm = re.sub(r'\$\{[^}]+\}', '{id}', url)
                norm = re.sub(r'/\d+', '/{id}', norm)
                if norm not in api_calls:
                    api_calls[norm] = []
                api_calls[norm].append(path.replace('pc-web/src/', ''))
        except:
            pass

print(f'前端真实API URL: {len(api_calls)} 个\n')
# 排序
for url in sorted(api_calls.keys()):
    if 'http' in url or url.startswith('//') or '_id' in url:
        continue
    print(f'{url:60s} ← {api_calls[url][0]}')
