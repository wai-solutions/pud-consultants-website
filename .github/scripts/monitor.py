#!/usr/bin/env python3
"""PA-024: hourly health check for www.pudconsultants.com. Standard library only, no secrets.
Exit 1 on any FAIL, so the scheduled workflow fails and GitHub emails the repository admins."""
import json, re, socket, ssl, sys, time, urllib.request, urllib.error, datetime

BASE = 'https://www.pudconsultants.com'
KEY = ['/', '/about.html', '/projects.html', '/contact.html', '/people.html', '/amr-attia.html', '/abdallah-attia.html', '/60-years.html',
       '/partners.html', '/faq.html', '/news.html', '/insights.html', '/destinations/red-sea.html', '/sitemap.xml', '/robots.txt', '/llms.txt']
MIN_SITEMAP = 250
results = []

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None

def get(url, follow=True, timeout=20):
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={'User-Agent': 'pud-monitor/1.0'})
    t = time.time()
    try:
        r = opener.open(req, timeout=timeout); body = r.read(); return r.status, dict(r.headers), body, time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read() if e.fp else b'', time.time() - t

def check(name, ok, detail='', warn=False):
    results.append({'check': name, 'status': 'OK' if ok else ('WARN' if warn else 'FAIL'), 'detail': detail})

def main():
    try:
        s, h, b, dt = get(BASE + '/')
        check('uptime', s == 200, 'HTTP %s in %.1fs' % (s, dt))
        check('uptime-speed', dt < 3, '%.1fs' % dt, warn=True)
        check('noindex', b'noindex' not in b[:6000] and 'noindex' not in h.get('X-Robots-Tag', ''), 'home page must be indexable')
    except Exception as e: check('uptime', False, str(e))
    for src in ('http://pudconsultants.com/', 'https://pudconsultants.com/', 'http://www.pudconsultants.com/'):
        try:
            s, h, _, _ = get(src, follow=False)
            check('redirect ' + src, s in (301, 308) and h.get('Location', '').startswith('https://www.pudconsultants.com'), 'HTTP %s -> %s' % (s, h.get('Location')))
        except Exception as e: check('redirect ' + src, False, str(e))
    for path in KEY:
        try:
            s, _, b, dt = get(BASE + path)
            check('page ' + path, s == 200 and len(b) > 200, 'HTTP %s, %d bytes, %.1fs' % (s, len(b), dt))
        except Exception as e: check('page ' + path, False, str(e))
    try:
        s, _, b, _ = get(BASE + '/sitemap.xml'); locs = re.findall(rb'<loc>([^<]+)</loc>', b)
        check('sitemap', s == 200 and len(locs) >= MIN_SITEMAP and len(set(locs)) == len(locs), '%d URLs' % len(locs))
    except Exception as e: check('sitemap', False, str(e))
    try:
        s, _, b, _ = get(BASE + '/no-such-page-%d' % int(time.time()))
        check('not-found', s == 404 and b'Page not found' in b, 'HTTP %s' % s)
    except Exception as e: check('not-found', False, str(e))
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection(('www.pudconsultants.com', 443), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname='www.pudconsultants.com') as ss: cert = ss.getpeercert()
        exp = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z'); days = (exp - datetime.datetime.utcnow()).days
        check('tls', days > 7, '%d days left' % days); check('tls-soon', days > 21, '%d days left' % days, warn=True)
    except Exception as e: check('tls', False, str(e))
    print(json.dumps(results, indent=1))
    return 1 if any(r['status'] == 'FAIL' for r in results) else 0

if __name__ == '__main__': sys.exit(main())
