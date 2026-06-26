"""Fix AuthController.userInfo to remove bad relations."""
import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()

# Read current file
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'r') as f:
    content = f.read().decode('utf-8')

# Find current userInfo method
m = re.search(r'public function userInfo.*?\n    \}', content, re.DOTALL)
if m:
    print('OLD:')
    print(m.group(0))
else:
    print('NOT FOUND')

# Replace with clean version (no profile/roles load, returns flat user)
new_method = '''    public function userInfo(Request $request): JsonResponse
    {
        $user = $request->user()->load(['department', 'position']);
        return response()->json([
            'code' => 0,
            'data' => [
                'user' => [
                    'id' => $user->id,
                    'name' => $user->name,
                    'username' => $user->username,
                    'avatar' => $user->avatar,
                    'phone' => $user->phone,
                    'email' => $user->email,
                    'department' => $user->department?->name,
                    'position' => $user->position?->name,
                ],
            ],
        ]);
    }'''

content_new = re.sub(r'public function userInfo.*?\n    \}', new_method, content, count=1, flags=re.DOTALL)

# Verify replacement happened
m2 = re.search(r'public function userInfo.*?\n    \}', content_new, re.DOTALL)
print('\nNEW:')
print(m2.group(0) if m2 else 'STILL NOT FOUND')

# Write back
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'w') as f:
    f.write(content_new)
sftp.close()

# Restart FPM
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=15)
so.read()
print('\nfpm restarted')

# Test
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        body = json.loads(r.read().decode('utf-8'))
        token = body.get('data', {}).get('token', '')
        print(f'\nlogin HTTP {r.status}, token: {token[:30]}...')

        # Now test userinfo
        req2 = urllib.request.Request('http://172.20.0.139:3000/api/auth/userinfo', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req2, timeout=10) as r2:
            body2 = r2.read().decode('utf-8')
            print(f'userinfo HTTP {r2.status}: {body2[:400]}')
except urllib.error.HTTPError as e:
    print(f'HTTPError {e.code}: {e.read().decode()[:400]}')
except Exception as e:
    print(f'Error: {e}')

ssh.close()
