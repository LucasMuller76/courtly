import urllib.request
import urllib.parse
import http.cookiejar
import json

BASE = 'http://127.0.0.1:8000'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def req(path, method='GET', data=None, headers=None):
    url = BASE + path
    if data is not None:
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if headers:
        for k,v in headers.items():
            req.add_header(k, v)
    try:
        resp = opener.open(req, timeout=5)
        content = resp.read().decode()
        return resp.getcode(), content
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)

print('HEALTH ->', req('/health'))

reg_body = {
    'name': 'Py User',
    'email': 'test+py@example.com',
    'password': 'password123',
    'club_name': 'Py Club',
    'club_slug': 'py-club-smoke'
}
print('REGISTER ->', req('/api/v1/auth/register', method='POST', data=reg_body))
print('LOGIN ->', req('/api/v1/auth/login', method='POST', data={'email': reg_body['email'], 'password': reg_body['password']}))
print('ME ->', req('/api/v1/auth/me', method='GET'))
# duplicate
print('DUP_REGISTER ->', req('/api/v1/auth/register', method='POST', data=reg_body))
# create court
court_body = {'name': 'Smoke Court', 'price_per_hour': 1000}
print('CREATE_COURT ->', req('/api/v1/courts', method='POST', data=court_body))
