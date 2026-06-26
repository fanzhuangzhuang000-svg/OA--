import paramiko, sys, io
host='172.20.0.139'; user='nbcy'; pwd='admin123'; port=22
cli=paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(host, port=port, username=user, password=pwd, timeout=10, banner_timeout=10, auth_timeout=10)
cmds = sys.argv[1:] if len(sys.argv)>1 else ["echo OK"]
out=io.StringIO()
for c in cmds:
    out.write(f"\n$ {c}\n")
    sin,sout,serr=cli.exec_command(c, timeout=30)
    try:
        out.write(sout.read().decode('utf-8','replace'))
        e=serr.read().decode('utf-8','replace')
        if e: out.write("[STDERR] "+e)
    except Exception as e:
        out.write(f"[ERR] {e}\n")
print(out.getvalue())
cli.close()
