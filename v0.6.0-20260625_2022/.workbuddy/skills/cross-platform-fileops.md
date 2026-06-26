# 跨平台文件操作规范 (Git Bash + Windows Python 3.14)

## 关键陷阱
- **Bash 工具在每个 subshell 都会重置 cwd** — 不能依赖 `cd` 后面的状态
- **Git Bash 把 `/x/...` 自动转成 `D:\x\...` 给 Windows Python** — Python 不认 `/d/`，但认 `D:/...` 或 `D:\...`
- **混合调用时**：`ls /d/...` 看得到文件，但 `python3 -c "open('/d/...')"` 找不到（路径解析层不同）
- **脚本路径传递**：`python3 /d/foo.py` 会失败，**必须用 Windows 路径** `python3 "D:\foo.py"`

## 稳态模板
```python
# 写到 .workbuddy/*.py
# 内部 open() / os.chdir() 用 Windows 风格: r'D:\work\website\OA\xxx'
# 跑的时候:
cd /d/work/website/OA/xxx && python3 "D:\work\website\OA\.workbuddy\my_script.py"
```

## 文件操作的可靠方式
| 操作 | 推荐 |
|------|------|
| 写文件 | Python with `open(local, 'wb')` 用 `r'D:\...'` 路径 |
| 删文件 | Python `os.remove()` 用 Windows 路径 |
| 列文件 | Bash `ls /d/...` 没问题（Git Bash 自身转换） |
| 跑 Python | 必须用 Windows 路径 `python3 "D:\...\script.py"` |
| SSH | paramiko 用 `/var/www/...` 正常 |

## 调试信号
- `FileNotFoundError: [WinError 3]` → Python 跑的是 Windows 模式，路径需要 D:\ 风格
- `can't open file 'D:\\d\\work\\...'` → Git Bash 把 /d 转 D:\d 了，用 Windows 路径
- `exists: False` 但 `ls` 看得到 → Python 路径解析层 vs Git Bash 转换层不一致
