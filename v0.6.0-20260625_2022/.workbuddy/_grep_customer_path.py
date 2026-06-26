import re
data = open('/var/www/oa-web/assets/index-C82z6LNw.js').read()
for m in re.finditer(r'.{0,150}/customer/[^"]{0,50}', data):
    print(m.group())
    print('---')
