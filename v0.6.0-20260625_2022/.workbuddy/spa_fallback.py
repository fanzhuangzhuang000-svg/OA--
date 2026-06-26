"""SPA fallback server for /var/www/oa-web/ - any path not found → index.html"""
import http.server, socketserver, os, sys

WEB = '/var/www/oa-web'
PORT = 18080

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEB, **kw)
    def do_GET(self):
        # 把 URL 路径转成文件路径
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            # 找不到 → 200 + index.html (SPA fallback)
            self.path = '/index.html'
        return super().do_GET()
    def log_message(self, *a, **kw): pass

with socketserver.TCPServer(('127.0.0.1', PORT), SPAHandler) as httpd:
    print(f'SPA fallback on http://127.0.0.1:{PORT}', file=sys.stderr)
    httpd.serve_forever()
