# -*- coding: utf-8 -*-
"""PUD 60-years site generator (v5, SEO/GEO edition). MODE=prod strips noindex. Usage: python3 src/build.py"""
import json, os, re, shutil, sys, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); os.chdir(ROOT); sys.path.insert(0, HERE)
from content import *
from seo import *
import copy2
from copy2 import *
E = html.escape
SITE = os.environ.get('SITE_DIR', ROOT + '/site'); BASE = 'https://www.pudconsultants.com'; MODE = os.environ.get('MODE', 'preview'); TODAY = datetime.date.today().isoformat()

def load(p, default):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return default
def ex(path): return bool(path) and os.path.exists(os.path.join(ROOT, path))
def slugify(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def clip(t, n=156):
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= n: return t
    cut = t[:n]
    for sep in ('. ', '; ', ': ', ', '):
        i = cut.rfind(sep)
        if i > 80: return cut[:i].rstrip(',;:') + '.'
    return cut.rsplit(' ', 1)[0].rstrip(',;:') + '.'
def J(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':'))
def sclip(t, n=156):
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= n: return t
    i = t[:n].rfind('. ')
    return t[:i + 1] if i > 60 else clip(t, n)

PROJ = load('data/projects.public.json', [])
CENSUS = load('data/projects.census.json', [])
have = {p['slug'] for p in PROJ}
for c in CENSUS:
    if c['slug'] not in have: PROJ.append(c); have.add(c['slug'])
PART = load('data/partners.json', [])
CLIPM = load('data/clip-map.json', {})
IMGS = load('data/images-A.json', []) + load('data/images-B.json', []) + load('data/images-C.json', [])
FACTS = load('data/online-facts.json', [])
PLINKS = {x['project_slug']: x for x in load('data/project-links.json', [])}
BYSLUG = {p['slug']: p for p in PROJ}
OVERRIDE.update(OVERRIDE2)
for _s, _o in OVERRIDE.items():
    if _s in BYSLUG: BYSLUG[_s].update(_o)
for p in PROJ:
    if re.search(r'\((site not stated|national programme|rural settlements|nationwide)\)', p.get('city') or ''): p['city'] = ''
    p['year'] = '' if p['year'] in (None, 'None', '') else str(p['year']); p['cat1'] = (p.get('category') or ['Masterplan'])[0]
    p['noun'] = KIND_NOUN.get(p['cat1'], 'Project')

IMG2PROJ = {
 'fanarah':'fanarah-tourist-resort','heliopark':'heliopark-concept-masterplan','maria-heights':'maria-heights-tourist-complex-homs','new-najaf-city':'new-najaf-city',
 'city-of-knowledge':'city-of-knowledge-university-of-islamic-sciences-najaf','faculty-of-agriculture':'faculty-of-agriculture-urban-renewal-cairo-university',
 'organ-transplant':'organ-transplant-center-nasser-institute','rotana-offices':'rotana-offices-and-studios-nile-plaza','frankfurt':'frankfurt-book-fair-arab-world-galleries',
 'al-madinah-hotels':'al-madinah-hotels-detailed-designs','aqeelah-oasis':'al-aqeelah-oasis-damascus','aqeelah-oasis-web':'al-aqeelah-oasis-damascus','aqeeq-marina':'al-aqeeq-marina-al-khiran',
 'om-el-baneen-oasis':'om-el-baneen-oasis-najaf','ras-el-hekma':'madaar-ras-el-hekma','azha-north':'madaar-ras-el-hekma','alex-gate':'alex-gate-mixed-use-development',
 'marina-el-alamein-web':'marina-el-alamein','marina-el-alamein':'marina-el-alamein','royal-oasis':'royal-oasis-sheikh-zayed','royal-oasis-web':'royal-oasis-sheikh-zayed',
 'new-capital':'new-administrative-capital-phases-2-4','taj-al-riyadh':'taj-al-riyadh','al-jawhara-residence':'al-jawhara-residence','commercial-registry-branding':'commercial-registry-branding-manual',
 'port-said-tunnels':'suez-canal-tunnels-port-said','la-vista':'la-vista-town-new-cairo','prince-talal-majestic-hotel':'prince-talal-hurghada-waterfront','cairo-downtown':'downtown-cairo-regeneration',
 'jeddah-strategic-development-plan':'jeddah-spatial-framework-plan','saudi-railway-land-optimization':'saudi-railway-land-and-property-assets-strategy','taif-development-plan':'taif-development-plan',
 'al-khafji':'project-line-al-khafji-concept-master-plan','al-soudah':'al-soudah-master-plan-competition','alamein-riviera':'alamein-riviera-vision-master-plan','elysium':'elysium-mixed-use-development',
 'lusail':'simaisma-beach-and-lusail-islands','makkah-township':'makkah-township-vision-master-plan','najran-region':'najran-northern-border-design-guidelines','prime-dubai':'green-pearl-prime-dubai-competition',
 'ramla':'ramla-concept-master-plan','abu-qir':'abu-qir-city-and-port-extension','gargoub':'gargoub-new-port-city','khaybar':'khaybar-heritage-area-master-plan',
 'jadel-dhahran':'dhahran-investment-land-concept-master-plan','jadel-jeddah-hamdaniyah':'jeddah-hamdaniyah-investment-lands-concept-master-plan','hilton-dahab':'hilton-dahab-village-hotel',
}
IMG2PROJ.update(load('data/img2proj-extra.json', {}))
imgsets = {}
for s in IMGS:
    k = IMG2PROJ.get(s.get('slug_guess')) or (s.get('slug_guess') if s.get('slug_guess') in BYSLUG else None)
    if k in BYSLUG:
        got = {i['src'] for i in imgsets.get(k, [])}
        imgsets.setdefault(k, []).extend([i for i in s.get('items', []) if ex(i['src']) and i['src'] not in got])
DROP = set(load('data/drop-images.json', []))
for k in imgsets: imgsets[k] = [i for i in imgsets[k] if i['src'] not in DROP][:12]
clipof = {}
for f, sl in load('data/clip-map.json', {}).items():
    stem = re.sub(r'[^a-z0-9]+', '-', os.path.basename(f).rsplit('.', 1)[0].lower()).strip('-'); stem = re.sub(r'-(egypt|ksa)$', '', stem)
    if isinstance(sl, dict): sl = sl.get('slug')
    if sl: clipof.setdefault(sl, {})['png' if f.lower().endswith('.png') else 'mov'] = stem
def still_for(slug):
    c = clipof.get(slug, {})
    for st in (c.get('png'), c.get('mov')):
        if not st: continue
        for cand in ('assets/stills/%s.jpg' % st, 'assets/stills/%s-egypt.jpg' % st, 'assets/stills/%s-ksa.jpg' % st, 'assets/stills/%s.jpg' % re.sub(r'-(egypt|ksa)$', '', st)):
            if ex(cand): return cand
def clip_for(slug):
    st = clipof.get(slug, {}).get('mov')
    if st and ex('assets/clips/%s.mp4' % st): return 'assets/clips/%s.mp4' % st, 'assets/clips/%s.jpg' % st
    return None, None
def thumb(slug):
    s = imgsets.get(slug)
    if s: return s[0].get('thumb') or s[0]['src']
    st = still_for(slug)
    if st and ex(st[:-4] + '_t.jpg'): return st[:-4] + '_t.jpg'
    if st: return st
    c, pj = clip_for(slug)
    return pj if pj and ex(pj) else None
NO_PHOTO_HERO = {'saudi-railway-land-and-property-assets-strategy', 'najran-northern-border-design-guidelines'}
def hero_img(slug):
    if slug in NO_PHOTO_HERO: return None
    s = imgsets.get(slug)
    return (s[0]['src'] if s else (still_for(slug) or clip_for(slug)[1]))
pmap = {p['slug']: p for p in PART}
def has_logo(p): return bool(p and p.get('logo') and ex(p['logo']))
def client_logos(client):
    out = []; c = (client or '').lower()
    for p in PART:
        if p.get('type') != 'client' or not has_logo(p): continue
        nm = p['name'].lower(); short = re.sub(r'[^a-z0-9 ]', '', nm).strip()
        toks = {nm, short} | ({'nuca'} if 'nuca' in nm else set()) | ({'momrah'} if 'momrah' in nm else set())
        if any(t and len(t) > 2 and re.search(r'(?<![a-z])' + re.escape(t) + r'(?![a-z])', c) for t in toks): out.append(p)
    return out[:4]

# ---- places ----
FAQ[:] = [(q, a.replace('{N}', str(len(PROJ))).replace('{C}', str(len({p['country'] for p in PROJ})))) for q, a in FAQ]
PLACES = {}; COUNTRIES = {}
for p in PROJ:
    COUNTRIES.setdefault(p['country'], []).append(p)
    city = p.get('city') or ''
    if city in PLACE_ALIAS: pl = PLACE_ALIAS[city]
    else: pl = [(city.split(',')[0].strip(), p['country'])] if city and '(' not in city else []
    p['places'] = []
    for name, country in pl:
        sl = slugify(name)
        if sl == 'kuwait': sl, name = 'kuwait-city', 'Kuwait City'
        if sl in COUNTRY_SLUG.values(): sl += '-city'
        d = PLACES.setdefault(sl, dict(slug=sl, name=name, country=country, projects=[]))
        if p not in d['projects']: d['projects'].append(p)
        if sl not in p['places']: p['places'].append(sl)
for d in PLACES.values():
    ll = [(q['lat'], q['lon']) for q in d['projects'] if q.get('lat') is not None]
    d['lat'], d['lon'] = (sum(a for a, b in ll) / len(ll), sum(b for a, b in ll) / len(ll)) if ll else (None, None)
def cslug(c): return COUNTRY_SLUG.get(c, slugify(c))
def years(ps):
    ys = sorted(q['year_start'] for q in ps if q.get('year_start'))
    return (ys[0], ys[-1]) if ys else (None, None)


import zlib, math, random as _rnd
def plan_svg(slug, cats=None, w=400, h=300):
    r = _rnd.Random(zlib.crc32(slug.encode())); cats = cats or []
    style = r.choice(['grid', 'radial', 'organic', 'grid']); out = []
    S = 'stroke="#ffffff" stroke-opacity=".38" fill="none" stroke-width="1"'
    if style == 'grid':
        a = r.uniform(-.35, .35); n = r.randint(5, 8); m = r.randint(4, 6)
        for i in range(-2, n + 3):
            x = w * (i / n); out.append('<line x1="%.1f" y1="-60" x2="%.1f" y2="%d" %s transform="rotate(%.1f %d %d)"/>' % (x, x, h + 60, S, a * 57, w // 2, h // 2))
        for j in range(-2, m + 3):
            y = h * (j / m); out.append('<line x1="-60" y1="%.1f" x2="%d" y2="%.1f" %s transform="rotate(%.1f %d %d)"/>' % (y, w + 60, y, S, a * 57, w // 2, h // 2))
        for _ in range(r.randint(9, 16)):
            x, y = r.uniform(30, w - 60), r.uniform(25, h - 50); ww, hh = r.uniform(14, 44), r.uniform(10, 32)
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ffffff" fill-opacity=".07" stroke="#ffffff" stroke-opacity=".5" stroke-width=".8" transform="rotate(%.1f %d %d)"/>' % (x, y, ww, hh, a * 57, w // 2, h // 2))
    elif style == 'radial':
        cx, cy = r.uniform(.35, .65) * w, r.uniform(.35, .65) * h
        for k in range(1, r.randint(4, 6)): out.append('<circle cx="%.1f" cy="%.1f" r="%d" %s/>' % (cx, cy, k * r.randint(26, 36), S))
        for k in range(r.randint(8, 14)):
            t = k * 2 * math.pi / 12 + r.uniform(0, .2); out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (cx, cy, cx + 400 * math.cos(t), cy + 400 * math.sin(t), S))
        out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="#EF4223"/>' % (cx, cy))
    else:
        for k in range(r.randint(6, 9)):
            y0 = r.uniform(0, h); d = 'M-10 %.1f C %.1f %.1f, %.1f %.1f, %d %.1f' % (y0, w * .3, y0 + r.uniform(-90, 90), w * .65, y0 + r.uniform(-90, 90), w + 10, y0 + r.uniform(-60, 60)); out.append('<path d="%s" %s/>' % (d, S))
        for _ in range(r.randint(10, 18)): out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff" fill-opacity=".14"/>' % (r.uniform(10, w - 10), r.uniform(10, h - 10), r.uniform(3, 10)))
    if any(c in cats for c in ('Tourism', 'Hospitality')):
        y = h * r.uniform(.68, .82); out.append('<path d="M-10 %.1f Q %.1f %.1f %.1f %.1f T %d %.1f V %d H -10Z" fill="#ffffff" fill-opacity=".1" stroke="#ffffff" stroke-opacity=".6"/>' % (y, w * .25, y - 30, w * .5, y, w + 10, y - 8, h + 10))
    for _ in range(2): out.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="#EF4223"/>' % (r.uniform(40, w - 40), r.uniform(30, h - 70)))
    return '<svg class="planart" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">%s</svg>' % (w, h, ''.join(out))

# ---------- html helpers ----------
def ld(*objs): return ''.join('<script type="application/ld+json">%s</script>' % J(o) for o in objs if o)
def crumbs(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + '/' + u} for i, (n, u) in enumerate(items)]}
def faq_ld(qa): return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa]}
ORG = {'@type': ['Organization', 'ProfessionalService'], '@id': BASE + '/#org', 'name': 'PUD Consultants', 'alternateName': ['PUD', 'Planning & Urban Development Consultants'], 'url': BASE + '/', 'logo': BASE + '/assets/logo-mark.png', 'foundingDate': '1966',
       'description': 'PUD Consultants is an urban planning, master planning, architecture and sustainable tourism consultancy founded in Cairo in 1966, with offices in Cairo, Riyadh and Dubai.', 'legalName': 'Planning & Urban Development Consultants', 'disambiguatingDescription': 'Urban planning and architecture consultancy in Cairo. Not a planned unit development or public utility district, which share the acronym PUD.', 'foundingLocation': {'@type': 'Place', 'name': 'Cairo, Egypt'},
       'founder': {'@id': BASE + '/people.html#abdallah-attia'}, 'employee': {'@id': BASE + '/amr-attia.html#amr-attia'}, 'sameAs': ['https://share-architects.com/office/pud-consultants/'],
       'areaServed': ['Egypt', 'Saudi Arabia', 'United Arab Emirates', 'Kuwait', 'Iraq', 'Middle East and North Africa'],
       'knowsAbout': ['Urban planning', 'Regional planning', 'Master planning', 'Urban design', 'Sustainable tourism', 'Cultural heritage planning', 'Landscape design', 'Architecture', 'Sustainable development'],
       'location': [
                    {'@type': 'Place', 'name': 'PUD Cairo (Sheikh Zayed)', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Polygon Building 8, Office 208, SODIC, Beverly Hills', 'addressLocality': 'Sheikh Zayed City', 'postalCode': '12588', 'addressCountry': 'EG'}, 'telephone': '+20 100 198 1111'},
                    {'@type': 'Place', 'name': 'PUD Cairo (Heliopolis)', 'address': {'@type': 'PostalAddress', 'streetAddress': '115 El Thawra Street, 5th Floor, Heliopolis', 'addressLocality': 'Cairo', 'postalCode': '11757', 'addressCountry': 'EG'}, 'telephone': '+20 2 2414 7537'},
                    {'@type': 'Place', 'name': 'PUD Riyadh (Diplomatic Quarter)', 'address': {'@type': 'PostalAddress', 'streetAddress': '8620 Ibn Mousa Street, Diplomatic Quarter', 'addressLocality': 'Riyadh', 'postalCode': '2513', 'addressCountry': 'SA'}, 'telephone': '+966 540 39 8178'},
                    {'@type': 'Place', 'name': 'PUD Riyadh (Al Nakheel)', 'address': {'@type': 'PostalAddress', 'streetAddress': '7064 Salem bin Maaqil Street, Al Nakheel District', 'addressLocality': 'Riyadh', 'postalCode': '12393', 'addressCountry': 'SA'}, 'telephone': '800 111 0893'},
                    {'@type': 'Place', 'name': 'PUD Dubai (Palm Jumeirah)', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Shoreline 12, Al Anbara, PH 06, Palm Jumeirah', 'addressLocality': 'Dubai', 'addressCountry': 'AE'}, 'telephone': '+971 509 29 8178'}]}
WEB = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '/#site', 'url': BASE + '/', 'name': 'PUD Consultants', 'publisher': {'@id': BASE + '/#org'}, 'inLanguage': 'en'}

AMR = load('data/amr.public.json', {})
NAV = [('projects.html', 'Projects'), ('services.html', 'Services'), ('60-years.html', '60 years'), ('people.html', 'People'), ('partners.html', 'Partners'), ('insights.html', 'Insights'), ('contact.html', 'Contact')]
CHAPTERS = [('index.html', 'Home', 'Back to the start'), ('60-years.html', 'The 60-year story', 'Six decades of work'), ('people.html', 'The people', 'The founder and the practice'), ('projects.html', 'The work', 'Every project on one map'),
            ('services.html', 'What we do', 'Planning, design and advice'), ('partners.html', 'Who we plan with', 'Clients and partners'), ('contact.html', 'Talk to us', 'Five offices')]

def fit(*c):
    for t in c:
        if len(t) <= 66: return t
    return c[-1].rsplit(' | ', 1)[0]

def page(path, title, body, desc='', active='', schema=None, og_img=None, data=None, body_cls='', head_extra='', ms=None, noindex=False):
    R = '../' * path.count('/')
    d = sclip(desc or 'PUD Consultants: urban planning, master planning and sustainable development consultants since 1966, with offices in Cairo, Riyadh and Dubai.')
    lis = ''.join('<li><a href="%s%s"%s>%s</a></li>' % (R, h, ' aria-current="page"' if h == active else '', t) for h, t in NAV)
    url = BASE + '/' + ('' if path == 'index.html' else path)
    og = (BASE + '/' + og_img) if og_img else BASE + '/assets/og.jpg'
    robots = ('<meta name="robots" content="noindex,follow">' if noindex else '') if MODE == 'prod' else '<meta name="robots" content="noindex,nofollow,noarchive">'
    dat = ('<script>window.__PROJECTS=%s;window.__MILESTONES=%s</script>' % (J(data), J(ms or []))) if data is not None else ''
    sch = ld(*(schema or []))
    return ('<!doctype html><html lang="en" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">%s<link rel="canonical" href="%s"><link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="x-default" href="%s">'
            '<meta name="theme-color" content="#000000"><meta property="og:type" content="website"><meta property="og:site_name" content="PUD Consultants"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s"><meta property="og:locale" content="en_US">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">'
            '<link rel="icon" href="%sassets/logo-mark.png"><link rel="preload" href="%sfonts/antonio-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="%scss/style.css">%s%s</head>'
            '<body class="%s"><a class="skip" href="#main">Skip to content</a><header class="nav"><div class="wrap in"><a class="brand" href="%sindex.html" aria-label="PUD Consultants, home"><img src="%sassets/logo-mark.png" alt="PUD Consultants logo" width="25" height="40"><span><b>PUD Consultants</b><small>PLANNING &amp; URBAN DEVELOPMENT</small></span></a>'
            '<nav aria-label="Main"><ul>%s</ul></nav><a class="btn red film" href="%scontact.html">Talk to us</a><button class="burger" aria-label="Menu" aria-expanded="false"><i></i><i></i></button></div></header>'
            '<main id="main">%s</main>%s%s<script type="module" src="%sjs/app.js"></script></body></html>') % (
        E(title), E(d), robots, url, url, url, E(title), E(d), url, og, E(title), E(d), og, R, R, R, sch, head_extra, body_cls, R, R, lis, R, body, footer(R), dat, R)

# ---- v6: green #003737 touches for sustainability mentions and topics ----
ECO_SLUG = re.compile(r'(services|insights|destinations)/[^"]*(sustainab|environment|red-sea)')
ECO_WORDS = re.compile(r"\b(sustainab\w*|environmental|environment(?! and sustainability)|eco-?tourism|green infrastructure|low-carbon|climate[- ]resilien\w*|nature reserve)\b", re.I)
_SKIP = re.compile(r'(<head>.*?</head>|<script\b.*?</script>|<style\b.*?</style>|<svg\b.*?</svg>|<[^>]+>)', re.S)
def eco(path, html_):
    if ECO_SLUG.search(path):
        html_ = html_.replace('<body class="', '<body class="eco-page ', 1)
    def mark(tag):
        if tag.startswith('<a ') and ECO_SLUG.search(re.search(r'href="([^"]*)"', tag).group(1) if 'href="' in tag else ''):
            if 'class="svc' in tag: return tag.replace('class="svc', 'class="svc eco-card', 1)
            if 'class="chip' in tag: return tag.replace('class="chip', 'class="chip eco-chip', 1)
            if 'class=' not in tag: return tag.replace('<a ', '<a class="eco-link" ', 1)
        return tag
    out = []
    for part in _SKIP.split(html_):
        if not part: continue
        if part.startswith('<'): out.append(mark(part))
        else: out.append(ECO_WORDS.sub(lambda m: '<span class="eco">%s</span>' % m.group(0), part))
    return ''.join(out)

def footer(R):
    sv = ''.join('<a href="%sservices/%s.html">%s</a>' % (R, s['slug'], E(s['name'])) for s in SERVICES)
    cn = ''.join('<a href="%scountries/%s.html">%s</a>' % (R, cslug(c), E(c)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1])))
    top = sorted([d for d in PLACES.values() if len(d['projects']) >= 3], key=lambda d: -len(d['projects']))[:10]
    ct = ''.join('<a href="%scities/%s.html">%s</a>' % (R, d['slug'], E(d['name'])) for d in top) + '<a href="%sprojects.html#cities">All cities</a>' % R
    off = ''.join('<p><b style="color:#fff;font-weight:600">%s</b><br>%s<br><a href="tel:%s" style="display:inline">%s</a></p>' % (E(a), E(b), re.sub(r'[^+0-9]', '', c), E(c)) for a, b, c in OFFICES)
    return ('<footer><div class="wrap"><div class="cols"><div><a class="brand" href="%sindex.html"><img src="%sassets/logo-mark.png" alt="PUD Consultants logo" width="25" height="40"><span><b>PUD Consultants</b><small>SINCE 1966</small></span></a>'
            '<p style="margin-top:16px;max-width:30ch;color:#9a9a9a">Leadership · Harmony · Clarity. Shaping sustainable cities since 1966, from Cairo, Riyadh and Dubai.</p></div>'
            '<div><h4>Services</h4>%s</div><div><h4>Countries</h4>%s<h4 style="margin-top:22px">Resources</h4><a href="%sfaq.html">FAQ</a><a href="%sinsights.html">Insights</a></div><div><h4>Cities</h4>%s</div><div><h4>Offices</h4>%s</div></div>'
            '<div class="fine"><span>&copy; 2026 PUD Consultants. All rights reserved.</span><span>Client and partner logos belong to their owners.</span></div></div></footer>') % (R, R, sv, cn, R, R, ct, off)

def card(p, R, i=None, tag=None, cls=''):
    t = thumb(p['slug']); url = '%sprojects/%s.html' % (R, p['slug'])
    di = ' data-i="%d"' % i if i is not None else ''
    meta = ' · '.join(x for x in (E(p.get('city') or p['country']), E(str(p['year']))) if x)
    tg = '<span class="tag">%s</span>' % E(tag) if tag else ''
    if t: return '<a class="pcard %s" href="%s"%s><img src="%s%s" alt="%s, %s" loading="lazy">%s<span class="t"><b>%s</b><span>%s</span></span></a>' % (cls, url, di, R, t, E(p['name']), E(p.get('city') or p['country']), tg, E(p['name']), meta)
    return '<a class="pcard ph %s" href="%s"%s>%s<span class="yr">%s</span>%s<span class="t"><b>%s</b><span>%s</span></span></a>' % (cls, url, di, plan_svg(p['slug'], p.get('category')), E(str(p.get('year_start') or '')), tg, E(p['name']), meta)

def chapter(i, R=''):
    prv = CHAPTERS[i - 1] if i > 0 else None; nxt = CHAPTERS[i + 1] if i + 1 < len(CHAPTERS) else None
    a = '<a class="prev" href="%s%s"><span class="mono">Previous</span><b>%s</b></a>' % (R, prv[0], E(prv[1])) if prv else '<span></span>'
    b = '<a class="next" href="%s%s"><span class="mono">Next chapter · %s</span><b>%s</b><em>&rarr;</em></a>' % (R, nxt[0], E(nxt[2]), E(nxt[1])) if nxt else ''
    dots = ''.join('<i%s></i>' % (' class="on"' if k == i else '') for k in range(len(CHAPTERS)))
    return '<nav class="chapter" aria-label="Story chapters"><div class="wrap"><div class="dots" aria-hidden="true">%s</div><div class="row">%s%s</div></div></nav>' % (dots, a, b)

def welcome_strip(R=''):
    return '<div class="welcome" data-until="2026-11-26">Prof. Dr. Amr Attia speaks at SHARE Kazakhstan in Almaty on 24 and 25 November. <a href="%samr-attia.html">Read his profile</a></div>' % R

def cta(R='', text='Talk to us', head='Planning something that people will live in?'):
    return '<section class="sec ctaband"><div class="wrap"><h2 class="h-l">%s</h2><p style="margin-top:22px"><a class="btn red" href="%scontact.html">%s</a> <a class="btn ghost" href="%sprojects.html">See our work</a></p></div></section>' % (E(head), R, text, R)

def faq_html(qa, h='Questions people ask'):
    return '<section class="faq"><h2 class="h-m">%s</h2>%s</section>' % (E(h), ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in qa))

def decade_projects(d, n=3):
    outs = []
    for s in d['slugs']:
        if s in BYSLUG and s not in [o['slug'] for o in outs]: outs.append(BYSLUG[s])
    ys, ye = int(d['yr']), int(d['to'])
    pool = sorted([p for p in PROJ if ys <= (p.get('year_start') or 0) <= ye and thumb(p['slug'])], key=lambda p: (not p.get('featured'), -(len(imgsets.get(p['slug'], [])))))
    for p in pool:
        if len(outs) >= n: break
        if p['slug'] not in [o['slug'] for o in outs]: outs.append(p)
    return [o for o in outs if thumb(o['slug'])][:n]

def with_img_first(ps): return sorted(ps, key=lambda p: (not p.get('featured'), not thumb(p['slug']), -(p.get('year_start') or 0)))

# ---------- pages ----------
def founder_block(reel_first=True):
    tabs = ''.join('<button aria-pressed="%s" data-src="assets/founder/%s.mp4" data-poster="assets/founder/%s.jpg">%s</button>' % ('true' if i == 0 else 'false', k, k, lab) for i, (k, lab) in enumerate([('draw', 'Drawing'), ('point', 'The plan'), ('stand', 'The city model'), ('award', 'Recognition')]))
    return '<div class="reel" data-r><video muted loop playsinline preload="metadata" src="assets/founder/draw.mp4" poster="assets/founder/draw.jpg" aria-label="Illustrative recreation of Prof. Dr. Abdallah Attia at work"></video><div class="tabs">%s</div></div>' % tabs

def home():
    strip = [p for p in PART if has_logo(p)]
    tiles = ''.join('<span class="t"><img src="%s" alt="%s logo" loading="lazy"></span>' % (p['logo'], E(p['name'])) for p in strip)
    hero_html = ('<section class="hero" id="top"><img class="poster" fetchpriority="high" src="assets/founder/hero.jpg" alt="Prof. Dr. Abdallah Attia drawing a plan, then Marina El Alamein and the Pyramids"><video autoplay muted loop playsinline preload="auto" poster="assets/founder/hero.jpg" aria-hidden="true"><source src="assets/founder/hero-m.mp4" type="video/mp4" media="(max-width:700px)"><source src="assets/founder/hero.mp4" type="video/mp4"></video>'
        '<div class="wrap in"><p class="kicker mono" data-r>1966 to 2026 · 60 years · Cairo · Riyadh · Dubai</p>'
        '<h1 class="h-xl hero-h" data-r="0.1">60 years of shaping <em>sustainable cities.</em></h1>'
        '<p class="lede" data-r="0.2">A multidisciplinary planning and design practice, shaping cities, destinations and sacred landscapes from Alex to Aswan, and across the region. The legacy continues; the future begins.</p>'
        '<div class="row" data-r="0.3"><a class="btn red" href="projects.html">Explore the work</a><a class="btn ghost" href="projects.html#atlas">Play the 60-year map</a></div>'
        '<div class="stats" data-r="0.4"><div class="stat"><b>1966</b><span class="mono">Founded in Cairo</span></div><div class="stat"><b>+%d</b><span class="mono">Countries</span></div>'
        '<div class="stat"><b>+%d</b><span class="mono">Projects</span></div><div class="stat"><b>5</b><span class="mono">Offices: Cairo, Riyadh, Dubai</span></div></div></div>'
        '<p class="cap">Prof. Dr. Abdallah Attia, founder of PUD. Illustrative recreation, not archive footage.</p><i class="scrollcue"></i></section>') % (len(COUNTRIES), len(PROJ))
    marq = '<div class="logos-strip" aria-label="Clients and partners"><div class="track">%s%s</div></div>' % (tiles, tiles) if tiles else ''
    svc = ''.join('<a class="svc" href="services/%s.html"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (s['slug'], E(s['name']), E(SVC_CARD.get(s['slug']) or clip(s['lead'], 92))) for s in SERVICES)
    intro = ('<section class="sec"><div class="wrap"><div class="grid2"><div><p class="kicker mono" data-r>Our expertise</p><h2 class="h-l" data-r="0.1">Every place has <em>its own rhythm.</em></h2></div>'
        '<div class="stack" data-r="0.2"><p class="p-l">PUD Consultants (Planning & Urban Development Consultants) is a multidisciplinary planning and design practice, founded in Cairo in 1966 by Prof. Dr. Abdallah Attia and led today by Prof. Dr. Amr Attia. We lead urban and tourism transformation, decoding land and cultural narratives to shape resilient communities, iconic destinations and sacred landscapes, from visionary master planning to precise execution.</p>'
        '<p class="p-l">We don\'t believe in one-size-fits-all. Every project starts by listening, then curates the best-fit minds (planners, architects, economists and global experts) around a shared mission, for national authorities, royal commissions, developers and universities, with partners such as WATG and AECOM.</p></div></div>'
        '<div class="svcgrid" data-r="0.2">%s</div></div></section>') % svc
    steps = ''.join('<div class="step"><h2>%s</h2><p>%s</p></div>' % (E(b), E(c)) for a, b, c in STEPS)
    stage = ('<section class="stage" aria-label="From paper to place: how a plan becomes a city"><div class="pin"><canvas aria-hidden="true"></canvas><div class="vig"></div><div class="steps">%s</div>'
             '<div class="bar" aria-hidden="true"><i></i></div><p class="hint mono">Scroll</p></div></section>') % steps
    decs = ''
    for d in DECADES:
        th = ''.join('<a href="projects/%s.html"><img src="%s" alt="%s" loading="lazy"><span>%s</span></a>' % (p['slug'], thumb(p['slug']), E(p['name']), E(p['name'])) for p in decade_projects(d))
        bl = ''.join('<li><b>%s</b>%s</li>' % (a, E(t)) for a, t in d['beats'][:3])
        decs += '<article class="dec"><div class="yr">%s<small>to %s</small></div><h3>%s</h3><p>%s</p><ul>%s</ul><div class="th">%s</div></article>' % (d['yr'], d['to'], E(d['title']), E(d['text']), bl, th)
    tl = ('<section class="tl-outer" id="story"><div class="tl-wrap"><div class="wrap tl-head"><p class="kicker mono">The journey</p><h2 class="h-l">Six chapters. <em>One legacy.</em></h2></div>'
          '<div class="tl-track">%s<article class="dec" style="width:min(80vw,380px)"><div class="yr">2026</div><h3>And the next sixty.</h3><p>The legacy continues, the future begins. PUD is still shaping new cities, destinations and districts across the region.</p><p style="margin-top:22px"><a class="btn dark" href="60-years.html">Read the full story</a></p></article></div></div></section>') % decs
    facts = ''.join('<li><b>%s</b><span>%s</span></li>' % (a, E(b)) for a, b in sorted(FOUNDER_FACTS))
    founder = ('<section class="sec founder" id="founder"><div class="wrap"><div class="grid2">%s'
        '<div><p class="kicker mono" data-r>The founder · 1966</p><h2 class="h-l" data-r="0.1">Prof. Dr. Abdallah <em>Attia</em></h2><p class="p-l" style="margin-top:20px" data-r="0.2">%s</p>'
        '<ul class="facts" data-r="0.25">%s</ul><p class="note">The footage here is an illustrative recreation made for the 60-year celebration. It is not archive film.</p><p style="margin-top:22px"><a class="btn ghost" href="people.html">Read his story</a></p></div></div></div></section>') % (founder_block(), E(FOUNDER_LEAD), facts)
    feat = [p for p in PROJ if p.get('featured') and thumb(p['slug'])][:6]
    nac = BYSLUG.get('new-administrative-capital-phases-2-4')
    if nac and nac not in feat and thumb(nac['slug']): feat.insert(1, nac)  # Egypt's New Administrative Capital, always in Selected work
    bento = ''.join(card(p, '', tag=p['cat1'], cls='b%d' % (i + 1)) for i, p in enumerate(feat))
    featsec = ('<section class="sec" style="background:var(--ink)"><div class="wrap"><p class="kicker mono" data-r>Selected work</p><h2 class="h-l" data-r="0.1">Breadth, <em>with depth.</em></h2><p class="p-l" style="margin:18px 0 8px;max-width:58ch" data-r="0.15">From regional visions to city-making, from coastal destinations to the Holy Sites.</p><div class="bento">%s</div></div></section>') % bento if bento else ''
    cn_cards = ''.join('<a href="countries/%s.html"><b>%s</b><span>%d projects</span></a>' % (cslug(c), E(c), len(ps)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))[:6])
    teaser = ('<section class="sec mapteaser"><div class="wrap grid2"><div><p class="kicker mono" data-r>Where we work</p><h2 class="h-l" data-r="0.1">From Alex to Aswan. <em>Then across the Red Sea.</em></h2><p class="p-l" style="margin:18px 0 26px" data-r="0.2">From the Mediterranean to the Nile Valley, from Jeddah to the Holy Sites, and on to Kuwait, Iraq, Syria and Cameroon. Watch the practice spread from Cairo; every pin opens a project with its client, partners and facts.</p><p data-r="0.3"><a class="btn red" href="projects.html">Open the map</a></p></div>'
              '<a class="mapimg" href="projects.html" data-r="0.2"><img src="assets/stills/glowing-pins-across-the-middle-east.jpg" alt="Glowing map of the Middle East with PUD project locations" loading="lazy"></a></div>'
              '<div class="wrap"><div class="cnrow">%s</div></div></section>') % cn_cards
    pl = ''.join('<a href="partners.html"><img src="%s" alt="%s logo" loading="lazy"></a>' % (p['logo'], E(p['name'])) for p in strip[:18])
    partners = ('<section class="sec paper"><div class="wrap"><p class="kicker mono" data-r>Clients &amp; partners</p><h2 class="h-l" data-r="0.1">Trusted by clients. <em>Built with partners.</em></h2><p class="p-l" style="margin-top:18px;max-width:58ch" data-r="0.15">100+ clients and 90+ collaborations across six decades, from ministries and royal commissions to the world\'s leading design firms.</p><div class="pl" data-r="0.2">%s</div><p style="margin-top:28px"><a class="btn dark" href="partners.html">All clients and partners</a></p></div></section>') % pl if pl else ''
    fq = '<section class="sec"><div class="wrap">%s<p style="margin-top:24px"><a class="btn ghost" href="faq.html">More questions</a></p></div></section>' % faq_html(FAQ[:5])
    amr_card = ('<section class="sec amrcard"><div class="wrap"><div class="grid2 amrg"><div data-r>%s</div><div><p class="kicker" data-r>The new chapter</p><h2 class="h-l" data-r="0.1">Prof. Dr. Amr Attia</h2><p class="p-l" style="margin-top:18px" data-r="0.2">%s</p>%s'
        '<p style="margin-top:8px" data-r="0.3"><a class="btn red" href="amr-attia.html">Read his profile</a></p></div></div>'
        '<h3 class="h-m" style="margin-top:56px" data-r>Selected work</h3><div class="pgrid amrwork" data-r="0.1">%s</div></div></section>') % (amr_photo(), E(AMR_HEADLINE), stat_tiles(AMR_TILES), amr_work('', 3))
    film = ''
    body = welcome_strip() + hero_html + marq + featsec + intro + stage + tl + founder + amr_card + teaser + partners + cta('', 'Talk to us', 'Every place has a story. Let\'s shape its next chapter.') + fq + chapter(0) + film
    return page('index.html', 'PUD Consultants | Urban Planning & Master Planning since 1966', body,
                'PUD Consultants plans cities, destinations and campuses. Founded in Cairo in 1966, with work across the region. Offices in Cairo, Riyadh and Dubai.', 'index.html',
                schema=[dict(ORG, **{'@context': 'https://schema.org'}), WEB, faq_ld(FAQ[:5])])

def story():
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">1966 to 2026</p><h1 class="h-xl" style="max-width:16ch">Every legacy begins <em>with a vision.</em></h1><p class="lede">Two generations, six decades and one belief: planning should serve people, land and history.</p></div></section>'
    for d in DECADES:
        th = ''.join(card(p, '') for p in decade_projects(d, 4))
        beats = ''.join('<li><b>%s</b>%s</li>' % (a, E(b)) for a, b in d['beats'])
        body += ('<section class="sec paper" style="padding:80px 0"><div class="wrap"><div class="grid2" style="align-items:start"><div><div class="mono" style="color:var(--red)">%s to %s</div><h2 class="h-l" style="margin:10px 0 18px">%s</h2><p class="p-l">%s</p><div class="dec" style="width:auto;border:0;padding:0"><ul>%s</ul></div></div>'
                 '<div class="pgrid" style="grid-template-columns:1fr 1fr;margin-top:0">%s</div></div></div></section>') % (d['yr'], d['to'], E(d['title']), E(d['text']), beats, th)
    body += '<section class="sec"><div class="wrap" style="text-align:center"><p class="note" style="max-width:60ch;margin:0 auto">Dates come from PUD\'s project records and public sources. Where a project spans several years, the range is shown.</p></div></section>' + chapter(1)
    return page('60-years.html', 'PUD Consultants at 60: Urban Planning History, 1966 to 2026', body, 'Follow PUD from its first commissions in Cairo in 1966 and the North Coast of Egypt to AlUla, Makkah and the Pyramids Plateau today.', '60-years.html',
                schema=[crumbs([('Home', ''), ('60 years', '60-years.html')])])

def people():
    f = ''.join('<li><b>%s</b><span>%s</span></li>' % (a, E(b)) for a, b in sorted(FOUNDER_FACTS))
    loved = ''.join(card(BYSLUG[s], '', tag=lab.split(',')[0]) for s, lab in FOUNDER_LOVED if s in BYSLUG)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker">People</p><h1 class="h-xl" style="max-width:16ch">We don\'t just gather experts. <em>We orchestrate brilliance.</em></h1></div></section>'
        '<section class="sec founder" style="padding-top:70px"><div class="wrap"><div class="grid2" style="align-items:start">%s'
        '<div><p class="kicker">The founder</p><h2 class="h-l">Prof. Dr. Abdallah Attia</h2><p class="p-l" style="margin-top:16px;color:#fff">%s</p><p class="p-l" style="margin-top:14px">%s</p><ul class="facts">%s</ul>'
        '<p class="note">Footage is an illustrative recreation made for the 60-year celebration, not archive film.</p></div></div>'
        '<h2 class="h-m" style="margin-top:70px">Three projects the practice singles out</h2><p class="p-l" style="margin-top:10px">%s</p><div class="loved">%s</div></div></section>'
        '<section class="sec paper"><div class="wrap grid2 amrg"><div>%s</div><div><p class="kicker">Leadership</p><h2 class="h-l">Prof. Dr. Amr Attia</h2><p class="p-l" style="margin-top:16px">%s</p>%s<p style="margin-top:6px"><a class="btn dark" href="amr-attia.html">Read his full profile</a></p></div></div></section>') % (
        founder_block(), E(FOUNDER_LEAD), E(FOUNDER_BIO), f, E(FOUNDER_LOVED_NOTE), loved, amr_photo('', 'light'), E(AMR_HEADLINE), stat_tiles(AMR_TILES)) + chapter(2)
    pers = [{'@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/people.html#abdallah-attia', 'name': 'Abdallah Abdel Aziz Attia', 'description': 'Architect, professor and founder of PUD Consultants in 1966.', 'alumniOf': [{'@type': 'CollegeOrUniversity', 'name': 'Alexandria University'}, {'@type': 'CollegeOrUniversity', 'name': 'ETH Zurich'}], 'jobTitle': 'Professor of Architecture; founder of PUD Consultants', 'worksFor': {'@id': BASE + '/#org'}},
            {'@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/amr-attia.html#amr-attia', 'name': 'Amr A. Attia', 'jobTitle': 'Principal, PUD Consultants; Professor of Urban Planning, Ain Shams University', 'worksFor': {'@id': BASE + '/#org'}, 'url': BASE + '/amr-attia.html'}]
    return page('people.html', 'Prof. Dr. Abdallah Attia and Prof. Dr. Amr Attia | PUD Consultants', body, 'Meet Prof. Dr. Abdallah Attia, who founded PUD in Cairo in 1966, and Prof. Dr. Amr Attia, his son, who leads the practice today.', 'people.html',
                schema=pers + [crumbs([('Home', ''), ('People', 'people.html')])])



def amr_photo(R='', cls=''):
    return '<figure class="amrphoto %s"><img src="%sassets/people/amr-attia.jpg" alt="Prof. Dr. Amr Attia, principal of PUD Consultants" width="800" height="800" loading="lazy"><figcaption><b>Prof. Dr. Amr Attia</b><span>Principal, PUD Consultants</span></figcaption></figure>' % (cls, R)
def amr_work(R='', n=4):
    ps = [BYSLUG[s] for s in AMR_WORK if s in BYSLUG][:n]
    return ''.join(card(p, R, tag=p['cat1']) for p in ps)
def stat_tiles(L):
    return '<div class="tiles">%s</div>' % ''.join('<div><b>%s</b><span>%s</span></div>' % (E(a), E(c)) for a, c in L)

def amr_page():
    A = AMR
    def src(s):
        m = re.search(r'https?://[^\s;,)\]]+', str(s or ''))
        return (' <a class="srcl" href="%s" target="_blank" rel="noopener">Source</a>' % E(m.group(0))) if m else ''
    def rows(L, f):
        return ''.join('<li><b>%s</b><span>%s</span></li>' % (E(str(x.get('year') or x.get('years') or '')), f(x)) for x in L)
    paras = ''.join('<p class="p-l" style="margin-top:16px">%s</p>' % E(t) for t in AMR_PARAS)
    prizes = ''.join('<li>%s</li>' % E(x) for x in AMR_PRIZES)
    spot = ''.join('<a href="%s" target="_blank" rel="noopener"><img src="%s" alt="%s" loading="lazy"><span><b>%s</b>%s</span></a>' % (E(x['url']), x['img'], E(x['t']), E(x['t']), E(x['d'])) for x in AMR_SPOTLIGHT)
    giza = ''.join('<figure><img src="%s" alt="%s" loading="lazy"><figcaption><b>%s</b>%s</figcaption></figure>' % (x['img'], E(x['t']), E(x['t']), E(x['d'])) for x in AMR_GIZA)
    sp = sorted(A.get('speaking', []), key=lambda x: -int(re.sub(r'\D', '', str(x.get('year') or 0))[:4] or 0))
    stage = rows(sp, lambda x: '<em class="role">%s%s</em> %s%s%s' % (E((x.get('role') or 'speaker').title()), ' &middot; Upcoming' if x.get('status') == 'upcoming' else '', E(x['event']), (' &middot; ' + E(x['place'])) if x.get('place') else '', (' <span class="topic">' + E(x['topic']) + '</span>') if x.get('topic') else '') + src(x.get('source_url')))
    recog = rows(A.get('fellowships_awards', []), lambda x: E(x['text']) + src(x.get('source')))
    LEADK = ('Member of the SHARE', 'Led the local', 'Jabal Thabeer', 'According to PUD', 'The Eisenhower', 'Principal in charge', 'Co-founder of K2C', 'Technical coordinator', 'Part of the team')
    lead_items = [x for x in A.get('contributions', []) if x['text'].startswith(LEADK)]
    res_items = [x for x in A.get('contributions', []) if not x['text'].startswith(LEADK)]
    research = rows(res_items, lambda x: E(x['text']) + src(x.get('source')))
    leadrows = rows(lead_items, lambda x: E(x['text']) + src(x.get('source')))
    career = rows(A.get('education', []) + A.get('roles', []), lambda x: E(x['text']) + src(x.get('source')))
    media = ''.join('<li><b>%s</b><span><a class="srcl" style="margin:0" href="%s" target="_blank" rel="noopener">%s</a> &middot; %s</span></li>' % (E(str(x.get('year') or '')), E(re.search(r'https?://[^\s;,)\]]+', x['url']).group(0)), E(x['outlet']), E(re.sub(r'\s*\((?:rotating|the URL|names)[^)]*\)', '', x['title']))) for x in A.get('press_and_media', []))
    body = welcome_strip() + ('<section class="page-h"><div class="wrap grid2 amrg"><div><p class="crumb"><a href="people.html">People</a></p><p class="kicker">Leadership</p><h1 class="h-xl" style="max-width:15ch">Prof. Dr. Amr Attia</h1><p class="lede" style="max-width:34ch">%s</p></div><div>%s</div></div></section>'
            '<section class="sec" style="padding-top:20px"><div class="wrap">%s<div class="narrow2">%s</div>'
            '<h2 class="h-m" style="margin-top:70px">Selected work</h2><div class="pgrid">%s</div>'
            '<h2 class="h-m" style="margin-top:70px">Roles and projects</h2><ul class="facts wide">%s</ul>'
            '<h2 class="h-m" style="margin-top:70px">On stage</h2><div class="annc">%s</div><ul class="facts wide" style="margin-top:26px">%s</ul>'
            '<h2 class="h-m" style="margin-top:70px">Recognition</h2><ul class="facts wide">%s<li><b>Selected first prizes</b><span>%s</span></li></ul>'
            '<h2 class="h-m" style="margin-top:70px">The Giza Pyramids master plan</h2><div class="gfig">%s</div>'
            '<h2 class="h-m" style="margin-top:70px">Research and teaching</h2><ul class="facts wide">%s</ul>'
            '<details class="more"><summary>Full career and education</summary><ul class="facts wide">%s</ul></details>'
            '<details class="more"><summary>In the media</summary><ul class="facts wide">%s</ul></details>'
            '</div></section>') % (E(AMR_HEADLINE), amr_photo('', 'lead'), stat_tiles(AMR_TILES), paras, amr_work('', 6), leadrows, spot, stage, recog, E('; '.join(AMR_PRIZES) + '. As listed in SHARE Architects\' speaker announcement.'), giza, research, career, media) + cta('') + chapter(2)
    pers = {'@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/amr-attia.html#amr-attia', 'name': 'Amr A. Attia', 'jobTitle': 'Principal, PUD Consultants; Professor of Urban Planning, Ain Shams University', 'worksFor': {'@id': BASE + '/#org'}, 'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Ain Shams University'}, 'url': BASE + '/amr-attia.html', 'image': BASE + '/assets/people/amr-attia.jpg',
            'alumniOf': {'@type': 'CollegeOrUniversity', 'name': 'University College London'}, 'sameAs': ['https://www.linkedin.com/in/amr-attia-9181898/', 'https://share-architects.com/speaker/amr-attia/']}
    return page('amr-attia.html', 'Prof. Dr. Amr Attia | Urban Planner, PUD Consultants', body, 'Prof. Dr. Amr Attia leads PUD Consultants and teaches urban planning at Ain Shams University. Eisenhower Fellow. Board Chairman of SHARE Egypt 2026.', 'people.html', schema=[pers, crumbs([('Home', ''), ('People', 'people.html'), ('Amr Attia', 'amr-attia.html')])], og_img='assets/people/amr-attia.jpg')

def projects_page():
    cs = sorted({p['country'] for p in PROJ}); cats = sorted({c for p in PROJ for c in p.get('category', [])})
    ch = lambda k, vals: ''.join('<button class="chip" data-filter="%s:%s" aria-pressed="%s">%s</button>' % (k, E(v), 'true' if v == 'All' else 'false', E(v)) for v in ['All'] + vals)
    data = [dict(slug=p['slug'], name=p['name'], city=p.get('city', ''), country=p['country'], year=str(p['year']), year_start=p.get('year_start') or 2000, client=p.get('client', ''), category=p.get('category', []), lat=p.get('lat'), lon=p.get('lon'),
                 featured=bool(p.get('featured')), thumb=thumb(p['slug']) or '', url='projects/%s.html' % p['slug']) for p in PROJ]
    order = sorted(range(len(PROJ)), key=lambda i: (not PROJ[i].get('featured'), not thumb(PROJ[i]['slug']), -(PROJ[i].get('year_start') or 0)))
    grid = ''.join(card(PROJ[i], '', i=i) for i in order)
    ccs = ''.join('<a href="countries/%s.html"><b>%s</b><span>%d projects</span></a>' % (cslug(c), E(c), len(ps)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1])))
    cities = ''.join('<a class="chip" href="cities/%s.html">%s <small>%d</small></a>' % (d['slug'], E(d['name']), len(d['projects'])) for d in sorted(PLACES.values(), key=lambda d: d['name']))
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Projects</p><h1 class="h-xl" style="max-width:17ch">From regional visions <em>to the Holy Sites.</em></h1><p class="lede">Press play to watch the practice grow from Cairo across the region. Drag to turn the map and click a pin to open a project.</p></div></section>'
        '<section class="sec atlas" id="atlas" style="padding-top:30px"><div class="wrap"><div class="box" data-geo="data/countries.geojson"><canvas aria-label="Map of PUD projects"></canvas><div class="tip"></div><div class="story" aria-live="polite"><span class="mono"></span><b></b></div><div class="now"></div>'
        '<div class="side"><button class="chip" data-view="all">Region</button><button class="chip" data-view="egypt">Egypt</button><button class="chip" data-view="ksa">Saudi Arabia</button><button class="chip" data-view="makkah">Makkah</button><span style="display:flex;gap:6px"><button class="chip" data-view="in" aria-label="Zoom in">+</button><button class="chip" data-view="out" aria-label="Zoom out">&minus;</button></span></div>'
        '<div class="hud"><div class="yrbox"><div class="yr">2026</div><div class="n mono"></div></div><input type="range" min="1964" max="2026" value="2026" aria-label="Year"><button class="btn red play">Play the story</button><button class="chip speed">Speed 1x</button><div class="legend"><span>1964</span><i></i><span>2026</span></div></div></div>'
        '<div class="cardsel"><img alt=""><div><h3 class="h-m"></h3><p class="note" style="font-size:14px"></p></div><a class="btn ghost" href="#">Open project</a></div>'
        '<div class="tools"><input class="search" type="search" placeholder="Search projects, cities, clients" aria-label="Search projects"><span class="count"></span></div>'
        '<div class="tools" role="group" aria-label="Country">%s</div><div class="tools" role="group" aria-label="Type">%s</div>'
        '<div class="pgrid">%s</div>'
        '<h2 class="h-m" style="margin-top:70px">Browse by country</h2><div class="cnrow">%s</div><h2 class="h-m" id="cities" style="margin-top:50px">Browse by city and region</h2><div class="chiplist">%s</div>'
        '<p class="note" style="margin-top:26px">The map shows the Middle East at city-level positions. Projects in Germany, Cameroon and The Gambia appear in the list only.</p></div></section>') % (ch('country', cs), ch('cat', cats), grid, ccs, cities) + chapter(3)
    return page('projects.html', 'Urban Planning Projects in Egypt, Saudi Arabia and Beyond | PUD', body,
                'Explore %d PUD projects on an interactive map: urban plans, master plans, destinations and buildings in Egypt, Saudi Arabia and the wider region.' % len(PROJ), 'projects.html',
                schema=[crumbs([('Home', ''), ('Projects', 'projects.html')]), {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD Consultants projects', 'numberOfItems': len(PROJ), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/projects/' + PROJ[j]['slug'] + '.html', 'name': PROJ[j]['name']} for i, j in enumerate(order[:60])]}], data=data, ms=MILESTONES)

def partners_page():
    def sect(t, typ):
        L = [p for p in PART if p.get('type') == typ and has_logo(p)]
        items = ''.join(('<a href="%s" target="_blank" rel="noopener" aria-label="%s (opens in a new tab)"><img src="%s" alt="%s logo" loading="lazy"></a>' % (E(p.get('url') or '#'), E(p['name']), p['logo'], E(p['name']))) if p.get('url') else ('<div><img src="%s" alt="%s logo" loading="lazy"></div>' % (p['logo'], E(p['name']))) for p in sorted(L, key=lambda p: p['name']))
        names = sorted(p['name'] for p in PART if p.get('type') == typ and not has_logo(p) and not re.match(r'(Dr\.?|Eng\.?|Arch\.?|Prof\.?|Fawaz)\b', p['name']))
        more = ('<p class="note" style="color:var(--mute-d);margin-top:18px"><b>Also worked with:</b> %s.</p>' % E(', '.join(names))) if names else ''
        return '<h2 class="h-m" style="margin-top:50px">%s</h2><div class="pl">%s</div>%s' % (t, items, more)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Partners and clients</p><h1 class="h-xl" style="max-width:15ch">Trusted by clients. <em>Built with partners.</em></h1><p class="lede">National authorities, royal commissions, developers and universities commission our work. International firms such as WATG and AECOM plan alongside us.</p></div></section>'
            '<section class="sec paper" style="padding-top:60px"><div class="wrap">%s%s</div></section>') % (sect('Partners', 'partner'), sect('Clients', 'client')) + chapter(5)
    return page('partners.html', 'Clients and Partners: WATG, AECOM, NUCA, AlUla | PUD Consultants', body, 'WATG, AECOM, NUCA, the Royal Commission for AlUla, Saudi Aramco, universities and developers: the clients and partners PUD Consultants plans with.', 'partners.html',
                schema=[crumbs([('Home', ''), ('Partners', 'partners.html')])])

def contact_page():
    off = ''.join('<div><h2 class="h-m">%s</h2><p class="p-l" style="margin-top:10px">%s</p><p class="p-l"><a class="btn red call" href="tel:%s">Call %s</a></p></div>' % (E(a), E(b), re.sub(r'[^+0-9]', '', c), E(c)) for a, b, c in OFFICES)
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">Contact</p><h1 class="h-xl" style="max-width:14ch">Every great place starts <em>with a conversation.</em></h1><p class="lede">Call the office closest to your site. We plan and design from Cairo, Riyadh and Dubai.</p></div></section><section class="sec" style="padding-top:50px"><div class="wrap"><div class="offices">%s</div><div class="photo-strip"><img src="assets/stills/glowing-pins-across-the-middle-east.jpg" alt="Map of the Middle East with PUD project locations" loading="lazy"></div></div></section>' % off + chapter(6)
    return page('contact.html', 'Contact PUD Consultants | Offices in Cairo, Riyadh and Dubai', body, 'Talk to PUD about a plan, a destination or a design. Call Cairo +20 100 198 1111, Riyadh +966 540 39 8178 or Dubai +971 509 29 8178.', 'contact.html',
                schema=[crumbs([('Home', ''), ('Contact', 'contact.html')]), dict(ORG, **{'@context': 'https://schema.org'})])

RED_SEA = ['port-ghalib-master-plan', 'abo-dabbab-marine-field-station', 'green-star-hotels-initiative', 'yuwdda-sub-regional-plan', 'ain-el-sokhna-tourist-center', 'hurghada-apartments-hotel-and-shopping-mall', 'pyramisa-apartment-hotel-hurghada', 'castle-zaman-hotel-red-sea']
def red_sea_page():
    R = '../'; ps = [BYSLUG[s] for s in RED_SEA if s in BYSLUG]
    qa = [('Does PUD plan Red Sea destinations?', 'Yes. PUD has worked on Port Ghalib and the Abo Dabbab marine field station at Marsa Alam, Hurghada, Ain El Sokhna and the Red Sea sub-regional plan for Yanbu, Umluj, Al Wajh and Duba in Saudi Arabia, and on the Green Star Hotels initiative with GIZ.')]
    body = ('<section class="page-h"><div class="wrap"><p class="crumb"><a href="../services/sustainable-tourism-planning.html">Sustainable tourism planning</a></p><h1 class="h-xl" style="max-width:18ch">Planning Red Sea destinations.</h1><p class="lede" style="max-width:56ch">PUD Consultants has planned Red Sea destinations in Egypt and Saudi Arabia: Port Ghalib and Abo Dabbab at Marsa Alam, Hurghada, Ain El Sokhna, the Green Star Hotels initiative and the sub-regional plan for Yanbu, Umluj, Al Wajh and Duba.</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="pgrid">%s</div>%s</div></section>') % (''.join(card(p, R) for p in ps), faq_html(qa)) + cta(R)
    return page('destinations/red-sea.html', 'Sustainable Tourism Planning on the Red Sea | PUD Consultants', body, 'Red Sea destination planning by PUD Consultants: Port Ghalib, Abo Dabbab, Hurghada, Ain El Sokhna and the Yanbu to Duba sub-regional plan.', 'services.html',
                schema=[faq_ld(qa), crumbs([('Home', ''), ('Services', 'services.html'), ('Red Sea destinations', 'destinations/red-sea.html')])], og_img=hero_img(ps[0]['slug']) if ps else None)

def faq_page():
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">FAQ</p><h1 class="h-xl" style="max-width:16ch">Questions about <em>PUD.</em></h1></div></section><section class="sec" style="padding-top:20px"><div class="wrap">%s</div></section>' % faq_html(FAQ, 'Frequently asked questions') + cta('')
    return page('faq.html', 'PUD Consultants FAQ: Services, Offices and Projects', body, 'Who founded PUD, what it plans, where it works and how to reach its offices in Cairo, Riyadh and Dubai. Straight answers from PUD Consultants.', '', schema=[faq_ld(FAQ), crumbs([('Home', ''), ('FAQ', 'faq.html')])])

def insights_page():
    arts = ''.join('<a class="svc" href="insights/%s.html"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (a['slug'], E(a['h1']), E(clip(a['lead'], 120))) for a in ARTICLES)
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">Insights</p><h1 class="h-xl" style="max-width:15ch">Urban planning, <em>explained.</em></h1><p class="lede">Short guides from a practice that has planned cities for sixty years.</p></div></section><section class="sec" style="padding-top:20px"><div class="wrap"><div class="svcgrid">%s</div></div></section>' % arts + cta('')
    return page('insights.html', 'Urban Planning Explained: Plain Guides | PUD Consultants', body, 'Plain guides to urban planning, master planning and sustainable tourism, written by PUD Consultants, a practice that has planned cities since 1966.', 'insights.html', schema=[crumbs([('Home', ''), ('Insights', 'insights.html')])])

def article_page(a):
    R = '../'
    secs = ''.join('<h2 class="h-m" style="margin-top:42px">%s</h2><p class="p-l" style="margin-top:12px">%s</p>' % (E(h), E(t)) for h, t in a['sections'])
    rel = ''.join('<a class="svc" href="../services/%s.html"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (s['slug'], E(s['name']), E(SVC_CARD.get(s['slug']) or clip(s['lead'], 90))) for s in SERVICES if s['slug'] in a['related'])
    body = ('<article><section class="page-h"><div class="wrap narrow"><p class="crumb mono"><a href="../insights.html">Insights</a></p><h1 class="h-xl" style="max-width:20ch;font-size:clamp(38px,5.6vw,84px)">%s</h1><p class="lede" style="max-width:48ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap narrow">%s%s<h2 class="h-m" style="margin-top:50px">How PUD can help</h2><div class="svcgrid" style="margin-top:18px">%s</div></div></section></article>') % (E(a['h1']), E(a['lead']), secs, faq_html(a['faq'], 'Related question'), rel) + cta(R)
    art = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['h1'], 'description': a['desc'], 'datePublished': '2026-11-24', 'dateModified': TODAY, 'author': {'@id': BASE + '/#org'}, 'publisher': {'@id': BASE + '/#org'}, 'mainEntityOfPage': BASE + '/insights/' + a['slug'] + '.html', 'inLanguage': 'en'}
    return page('insights/%s.html' % a['slug'], a.get('title') or fit('%s | PUD Consultants' % a['h1'], '%s | PUD' % a['h1']), body, a['desc'], 'insights.html', schema=[art, faq_ld([(a['q'], a['lead'])] + a['faq']), crumbs([('Home', ''), ('Insights', 'insights.html'), (a['h1'], 'insights/%s.html' % a['slug'])])])

def services_page():
    gr = ''.join('<a class="svc" href="services/%s.html"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (s['slug'], E(s['name']), E(SVC_CARD.get(s['slug']) or clip(s['lead'], 110))) for s in SERVICES)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Services</p><h1 class="h-xl" style="max-width:16ch">From visionary master plans <em>to precise execution.</em></h1><p class="lede" style="max-width:46ch">Urban and regional planning, master planning, architecture, heritage, landscape and strategic advice for public and private clients.</p></div></section>'
            '<section class="sec" style="padding-top:20px"><div class="wrap"><div class="svcgrid">%s</div><h2 class="h-m" style="margin-top:70px">How we work</h2><p class="p-l" style="margin-top:12px">We start by listening: stakeholder engagement and a close reading of the place. Then we assemble the team each project needs from our network of planners, architects, designers, sustainability experts, economists and social scientists. Six principles guide every project: insight-driven planning, scenario-based thinking, collaborative co-creation, legacy-oriented design, agile project structuring and integrated sustainability.</p></div></section>') % gr + chapter(4)
    return page('services.html', 'Urban Planning and Master Planning Services | PUD Consultants', body, 'Nine services from PUD Consultants: urban and regional planning, master planning, tourism, heritage, landscape, architecture, sustainability and advisory.', 'services.html',
                schema=[crumbs([('Home', ''), ('Services', 'services.html')]), {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD services', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/services/' + s['slug'] + '.html', 'name': s['name']} for i, s in enumerate(SERVICES)]}])

def service_page(s):
    R = '../'
    sel = [p for p in PROJ if any(c in p.get('category', []) for c in s['cats'])]
    sel += [BYSLUG[x] for x in s['extra'] if x in BYSLUG]
    seen = set(); sel = [p for p in with_img_first(sel) if not (p['slug'] in seen or seen.add(p['slug']))]
    cds = {}
    for p in sel: cds[p['country']] = cds.get(p['country'], 0) + 1
    chips = ''.join('<a class="chip" href="../countries/%s.html">%s <small>%d</small></a>' % (cslug(c), E(c), n) for c, n in sorted(cds.items(), key=lambda kv: -kv[1]))
    pts = ''.join('<li>%s</li>' % E(x) for x in s['points'])
    body = ('<section class="page-h"><div class="wrap"><p class="crumb mono"><a href="../services.html">Services</a></p><h1 class="h-xl" style="max-width:18ch;font-size:clamp(38px,6vw,92px)">%s</h1><p class="lede" style="max-width:50ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="body"><div class="stack">%s</div><div><h2 class="h-m">What this covers</h2><ul class="ticks">%s</ul></div></div>'
            '<h2 class="h-m" style="margin-top:70px">Selected projects</h2><div class="pgrid">%s</div><p class="note" style="margin-top:14px">%d projects. Where we apply it:</p><div class="chiplist">%s</div>%s</div></section>') % (
        E(s['h1']), E(s['lead']), ''.join('<p class="p-l">%s</p>' % E(t) for t in s['body']), pts, ''.join(card(p, R) for p in sel[:12]), len(sel), chips, faq_html(s['faq'])) + cta(R)
    sv = {'@context': 'https://schema.org', '@type': 'Service', 'name': s['name'], 'serviceType': s['name'], 'description': s['lead'], 'provider': {'@id': BASE + '/#org'}, 'areaServed': ['Egypt', 'Saudi Arabia', 'Middle East']}
    return page('services/%s.html' % s['slug'], fit('%s | PUD Consultants' % s['h1'], '%s | PUD' % s['h1']), body, s['lead'], 'services.html', schema=[sv, faq_ld(s['faq']), crumbs([('Home', ''), ('Services', 'services.html'), (s['name'], 'services/%s.html' % s['slug'])])], og_img=(hero_img(sel[0]['slug']) if sel else None))

def place_intro(name, country, ps):
    y0, y1 = years(ps); cats = sorted({c for p in ps for c in p.get('category', [])})
    top = [p['name'] for p in with_img_first(ps)[:3]]
    n = len(ps); span = (' between %s and %s' % (y0, y1)) if y0 and y1 and y1 != y0 else ((' in %s' % y0) if y0 else '')
    t = 'PUD has %d project%s in %s, %s%s.' % (n, '' if n == 1 else 's', name, country, span)
    t += ' They include %s.' % ((', '.join(top[:-1]) + ' and ' + top[-1]) if len(top) > 1 else top[0])
    if cats: t += ' The work spans %s.' % (', '.join(c.lower() for c in cats[:-1]) + ' and ' + cats[-1].lower() if len(cats) > 1 else cats[0].lower())
    return t

NOINDEX_CITIES = set('km-47 city-view-compound west-arabella mansouria cairo-suez-road cairo-alexandria-desert-road 6th-of-october-city-and-ismailia empty-quarter al-salmiya al-khiran al-uqair jabal-al-lith shorouq-city kafr-el-zayat nag-hammadi katameya obour-city frankfurt aseer northern-borders red-sea-coast'.split())
def city_page(d):
    R = '../'; ps = with_img_first(d['projects']); name, country = d['name'], d['country']
    intro = place_intro(name, country, ps)
    fts = []
    for p in ps:
        for f in FACTS:
            if f.get('project') in (p['slug'], p['name']) and f.get('url') and f['fact'] not in [x[0] for x in fts]: fts.append((f['fact'], f['url']))
    facts = ''.join('<div class="fact">%s <a href="%s" target="_blank" rel="noopener">Source</a></div>' % (E(a), E(b)) for a, b in fts[:4])
    sib = sorted([x for x in PLACES.values() if x['country'] == country and x['slug'] != d['slug']], key=lambda x: -len(x['projects']))[:10]
    sibh = ''.join('<a class="chip" href="%s.html">%s <small>%d</small></a>' % (x['slug'], E(x['name']), len(x['projects'])) for x in sib)
    cts = {}
    for p in ps:
        for c in p.get('category', []): cts[c] = cts.get(c, 0) + 1
    sv = [s for s in SERVICES if any(c in s['cats'] for c in cts)][:3]
    svh = ''.join('<a class="chip" href="../services/%s.html">%s</a>' % (s['slug'], E(s['name'])) for s in sv)
    body = ('<section class="page-h"><div class="wrap"><p class="crumb mono"><a href="../projects.html">Projects</a> / <a href="../countries/%s.html">%s</a></p><h1 class="h-xl" style="max-width:20ch;font-size:clamp(38px,6vw,92px)">Urban planning and design in %s, <em>%s.</em></h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="pgrid">%s</div>%s<h2 class="h-m" style="margin-top:60px">Services used in %s</h2><div class="chiplist">%s</div>%s</div></section>') % (
        cslug(country), E(country), E(name), E(country), E(intro), ''.join(card(p, R) for p in ps), ('<h2 class="h-m" style="margin-top:60px">About %s</h2>%s' % (E(name), facts)) if facts else '', E(name), svh,
        ('<h2 class="h-m" style="margin-top:60px">Elsewhere in %s</h2><div class="chiplist">%s</div>' % (E(country), sibh)) if sibh else '') + cta(R)
    ll = {'@type': 'Place', 'name': name, 'address': {'@type': 'PostalAddress', 'addressCountry': country}}
    if d.get('lat') is not None: ll['geo'] = {'@type': 'GeoCoordinates', 'latitude': round(d['lat'], 2), 'longitude': round(d['lon'], 2)}
    il = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD projects in %s' % name, 'numberOfItems': len(ps), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/projects/' + p['slug'] + '.html', 'name': p['name']} for i, p in enumerate(ps)]}
    return page('cities/%s.html' % d['slug'], fit('Urban Planning in %s, %s | PUD Consultants' % (name, country), 'Urban Planning in %s | PUD Consultants' % name), body, intro, 'projects.html', schema=[dict(ll, **{'@context': 'https://schema.org'}), il, crumbs([('Home', ''), ('Projects', 'projects.html'), (country, 'countries/%s.html' % cslug(country)), (name, 'cities/%s.html' % d['slug'])])],
                og_img=hero_img(ps[0]['slug']), noindex=(d['slug'] in NOINDEX_CITIES and len(ps) < 2))

def country_page(c, ps):
    R = '../'; ps = with_img_first(ps); y0, y1 = years(ps)
    pls = sorted([d for d in PLACES.values() if d['country'] == c], key=lambda d: -len(d['projects']))
    chips = ''.join('<a class="chip" href="../cities/%s.html">%s <small>%d</small></a>' % (d['slug'], E(d['name']), len(d['projects'])) for d in pls)
    dec = {}
    for p in ps:
        if p.get('year_start'): dec.setdefault(p['year_start'] // 10 * 10, []).append(p)
    decs = ''.join('<div><b>%ds</b><span>%d project%s</span></div>' % (k, len(v), '' if len(v) == 1 else 's') for k, v in sorted(dec.items()))
    cats = {}
    for p in ps:
        for ct in p.get('category', []): cats[ct] = cats.get(ct, 0) + 1
    _t = ['%s (%d)' % (k.lower(), v) for k, v in sorted(cats.items(), key=lambda kv: -kv[1])[:4]]
    top = (', '.join(_t[:-1]) + ' and ' + _t[-1]) if len(_t) > 1 else (_t[0] if _t else 'planning and design')
    intro = 'PUD has %d documented project%s in %s%s. The largest groups are %s.' % (len(ps), '' if len(ps) == 1 else 's', c, (', from %s to %s' % (y0, y1)) if y0 else '', top)
    qa = [('What has PUD done in %s?' % c, intro), ('Which cities in %s has PUD worked in?' % c, 'PUD has worked in %s.' % (', '.join(d['name'] for d in pls[:12]) if pls else c))]
    body = ('<section class="page-h"><div class="wrap"><p class="crumb mono"><a href="../projects.html">Projects</a></p><h1 class="h-xl" style="max-width:20ch;font-size:clamp(38px,6vw,92px)">Urban planning and master planning in %s</h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap">%s<h2 class="h-m">Cities and regions</h2><div class="chiplist">%s</div><h2 class="h-m" style="margin-top:50px">All projects in %s</h2><div class="pgrid">%s</div>%s</div></section>') % (
        E(c), E(intro), ('<div class="cnrow decs">%s</div>' % decs) if decs else '', chips, E(c), ''.join(card(p, R) for p in ps), faq_html(qa)) + cta(R)
    il = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD projects in %s' % c, 'numberOfItems': len(ps), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/projects/' + p['slug'] + '.html', 'name': p['name']} for i, p in enumerate(ps[:100])]}
    return page('countries/%s.html' % cslug(c), fit('Urban Planning Consultants in %s | PUD Consultants' % c, 'Urban Planning in %s | PUD' % c), body, intro, 'projects.html', schema=[il, faq_ld(qa), crumbs([('Home', ''), ('Projects', 'projects.html'), (c, 'countries/%s.html' % cslug(c))])],
                og_img=hero_img(ps[0]['slug']))

def related_for(p):
    out = []; seen = {p['slug']}
    def add(L, n):
        for q in L:
            if q['slug'] not in seen and len(out) < 6 and n > 0: out.append(q); seen.add(q['slug']); n -= 1
    for sl in p.get('places', []): add(with_img_first(PLACES[sl]['projects']), 3)
    add(with_img_first([q for q in PROJ if q['country'] == p['country'] and p['cat1'] in q.get('category', [])]), 3)
    add(with_img_first([q for q in PROJ if abs((q.get('year_start') or 0) - (p.get('year_start') or 0)) <= 6 and q['country'] == p['country']]), 3)
    return out[:6]

def project_page(p):
    R = '../'; slug = p['slug']; himg = hero_img(slug); clp, clp_poster = clip_for(slug)
    imgs = imgsets.get(slug, [])
    place = ', '.join(x for x in [p.get('city'), p['country']] if x)
    typ = '%s in %s' % (p['noun'], place)
    bg = '<img src="%s%s" alt="%s: %s">' % (R, himg, E(p['name']), E(typ)) if himg else ''
    vid = ('<video autoplay muted loop playsinline preload="metadata" poster="%s%s" aria-hidden="true"><source src="%s%s" type="video/mp4"></video>' % (R, clp_poster, R, clp)) if clp else ''
    cats = ''.join('<span>%s</span>' % E(c) for c in p.get('category', []))
    plog = ''
    PNAME = {'pgesco': 'PGESCO', 'wep': 'WEP (Germany)', 'cupud': 'CUPUD, Ain Shams University', 'bect': 'BECT', 'getinsa': 'Getinsa', 'paymacotas': 'Paymacotas', 'atkinsrealis': 'AtkinsR\u00e9alis', 'ernst-young': 'Ernst & Young', 'khatib-alami': 'Khatib & Alami', 'horwath-htl': 'Horwath HTL', 'chemonix': 'Chemonics Egypt', 'ehaf': 'EHAF', 'frantz-slater-design-collective': 'Frantz Slater Design Collective'}
    for ps_ in [x for x in p.get('partners', []) if not re.match(r'(dr|eng|arch|prof)-', x)]:
        pp = pmap.get(ps_)
        if has_logo(pp): plog += '<a href="%s" target="_blank" rel="noopener"><img src="%s%s" alt="%s logo"></a>' % (E(pp.get('url') or '#'), R, pp['logo'], E(pp['name']))
        elif pp: plog += '<span>%s</span>' % E(pp['name'])
        elif ps_: plog += '<span>%s</span>' % E(PNAME.get(ps_) or ps_.replace('-', ' ').title())
    cl = ''.join('<span><img src="%s%s" alt="%s logo"></span>' % (R, c['logo'], E(c['name'])) for c in client_logos(p.get('client')))
    loc_html = (', '.join('<a href="%scities/%s.html">%s</a>' % (R, sl, E(PLACES[sl]['name'])) for sl in p.get('places', [])[:2]) + ', <a href="%scountries/%s.html">%s</a>' % (R, cslug(p['country']), E(p['country']))) if p.get('places') else '<a href="%scountries/%s.html">%s</a>' % (R, cslug(p['country']), E(place))
    meta = [m for m in [('Location', loc_html), ('Year', E(p['year']) if p.get('year') and p['year'] != 'None' else ''), ('Client', E(p['client']) if p.get('client') else ''), ('Role', E(p['role']) if p.get('role') else '')] if m[1]]
    meta_html = ''.join('<div><span class="k mono">%s</span><span class="v">%s</span></div>' % (k, v) for k, v in meta)
    gal = ''.join('<button data-full="%s%s"><img src="%s%s" alt="%s: %s" loading="lazy" width="%s" height="%s"></button>' % (R, im['src'], R, im.get('thumb') or im['src'], E(p['name']), E(im.get('note') or p['noun']), im.get('w', ''), im.get('h', '')) for im in imgs)
    st = still_for(slug)
    if st and imgs and st not in DROP: gal += '<button data-full="%s%s"><img src="%s%s" alt="%s visualisation" loading="lazy"><span class="lbl">Visualisation</span></button>' % (R, st, R, st, E(p['name']))
    facts = ''.join('<div class="fact">%s <a href="%s" target="_blank" rel="noopener">Source</a></div>' % (E(f['fact']), E(f['url'])) for f in FACTS if f.get('project') in (slug, p['name']) and f.get('url'))
    pl_ = PLINKS.get(slug); off = ('<p style="margin-top:22px"><a class="btn ghost" href="%s" target="_blank" rel="noopener">Official project site</a></p>' % E(pl_['official_url'])) if pl_ and pl_.get('official_url') else ''
    sv = [s for s in SERVICES if any(c in s['cats'] for c in p.get('category', []))][:2]
    svh = ''.join('<a class="chip" href="%sservices/%s.html">%s</a>' % (R, s['slug'], E(s['name'])) for s in sv)
    rel = related_for(p)
    relh = ('<h2 class="h-m" style="margin-top:70px">More from %s</h2><div class="pgrid">%s</div>' % (E(PLACES[p['places'][0]]['name'] if p.get('places') else p['country']), ''.join(card(q, R) for q in rel))) if rel else ''
    ordl = [x['slug'] for x in PROJ]; k = ordl.index(slug); pv = PROJ[(k - 1) % len(PROJ)]; nx = PROJ[(k + 1) % len(PROJ)]
    fav = '<span class="favtag">Founder\'s favourite</span>' if slug in FAV else ''
    role = ''
    sumtxt = p.get('summary') or ''
    body = ('<article><section class="ph-hero%s">%s%s<div class="wrap in"><nav class="crumb mono" aria-label="Breadcrumb"><a href="%sprojects.html">Projects</a> / <a href="%scountries/%s.html">%s</a> / %s</nav>%s<h1 class="h-xl%s" style="max-width:18ch;font-size:clamp(40px,6.4vw,100px)">%s</h1><p class="lede" style="margin-top:6px">%s · %s</p><div class="tags">%s</div></div></section>'
            '<section class="sec" style="padding-top:20px"><div class="wrap"><div class="meta">%s</div><div class="body" style="margin-top:50px"><div><p class="p-l" style="font-size:clamp(19px,1.8vw,24px);color:#f3f3f3">%s</p>%s%s<div class="chiplist" style="margin-top:22px">%s</div></div>'
            '<div><h2 class="mono" style="color:var(--mute);font-weight:400">Partners</h2><div class="prt">%s</div><h2 class="mono" style="color:var(--mute);font-weight:400;margin-top:30px">Client</h2><div class="prt">%s</div>%s</div></div>'
            '%s%s<div class="pn"><a href="%sprojects/%s.html" rel="prev"><span class="mono" style="color:var(--mute)">Previous project</span><b>%s</b></a><a href="%sprojects/%s.html" rel="next"><span class="mono" style="color:var(--mute)">Next project</span><b>%s</b></a></div><p style="margin-top:34px;text-align:center"><a class="btn ghost" href="%sprojects.html#atlas">Back to the map</a></p></div></section>' + cta(R) + '</article>'
            '<div class="lb" role="dialog" aria-modal="true" aria-label="Photo viewer"><button class="x" aria-label="Close">&times;</button><button class="p" aria-label="Previous">&lsaquo;</button><img alt=""><button class="n" aria-label="Next">&rsaquo;</button></div>') % (
        '' if (himg or clp) else ' none', (bg if himg else plan_svg(slug, p.get('category'), 800, 450)), vid, R, R, cslug(p['country']), E(p['country']), E(p['name']), fav, ' long' if len(p['name']) > 48 else '', E(p['name']), E(p['noun']), E(place), cats, meta_html, E(sumtxt), role, facts, svh,
        plog or '<span>PUD</span>', cl or ('<span>%s</span>' % E(p['client']) if p.get('client') else ''), off, ('<div class="gal">%s</div>' % gal) if gal else '', relh, R, pv['slug'], E(pv['name']), R, nx['slug'], E(nx['name']), R)
    desc = sclip(sumtxt if ' '.join(p['name'].split()[:2]) in sumtxt else '%s. %s' % (p['name'], sumtxt), 156) if sumtxt else '%s: %s, %s.' % (p['name'], typ, p['year'])
    loc = {'@type': 'Place', 'name': place, 'address': {'@type': 'PostalAddress', 'addressCountry': p['country']}}
    if p.get('lat') is not None: loc['geo'] = {'@type': 'GeoCoordinates', 'latitude': p['lat'], 'longitude': p['lon']}
    cw = {'@context': 'https://schema.org', '@type': 'CreativeWork', 'name': p['name'], 'description': clip(sumtxt or typ, 300), 'dateCreated': str(p.get('year_start') or p['year']), 'creator': {'@id': BASE + '/#org'}, 'about': p.get('category', []),
          'contentLocation': loc, 'url': BASE + '/projects/' + slug + '.html', 'inLanguage': 'en'}
    if himg: cw['image'] = BASE + '/' + himg
    return page('projects/%s.html' % slug, fit(('%s | %s in %s (%s) | PUD Consultants' % (p['name'], p['noun'], place, p['year'])) if p['year'] else '%s | %s in %s | PUD Consultants' % (p['name'], p['noun'], place), '%s | %s in %s | PUD Consultants' % (p['name'], p['noun'], p.get('city') or p['country']), '%s | %s | PUD Consultants' % (p['name'], p['noun']), '%s | PUD Consultants' % p['name']), body, desc, 'projects.html',
                schema=[cw, crumbs([('Home', ''), ('Projects', 'projects.html'), (p['country'], 'countries/%s.html' % cslug(p['country'])), (p['name'], 'projects/%s.html' % slug)])], og_img=himg)

def llms():
    sig = [p for p in PROJ if p.get('featured')][:10]
    L = ['# PUD Consultants', '',
         '> PUD Consultants (Planning & Urban Development Consultants) is an urban planning, master planning, architecture and sustainable tourism consultancy founded in Cairo in 1966 by Prof. Dr. Abdallah Attia and led today by Prof. Dr. Amr Attia. Offices: Cairo, Riyadh and Dubai. It is not related to planned unit developments or public utility districts, which share the acronym PUD.', '',
         '## Key facts',
         '- Founded: 1966, Cairo, Egypt',
         '- Founder: Prof. Dr. Abdallah Abdel Aziz Attia, architect and professor',
         '- Leader: Prof. Dr. Amr Attia, Professor of Urban Planning at Ain Shams University, Eisenhower Fellow (Egypt 2007), Board Chairman of SHARE Egypt',
         '- Offices: Cairo (Sheikh Zayed City and Heliopolis), Riyadh (Diplomatic Quarter and Al Nakheel), Dubai (Palm Jumeirah)',
         '- Work: %d documented projects in %d countries, mostly Egypt and Saudi Arabia' % (len(PROJ), len(COUNTRIES)),
         '- Partners include WATG, AECOM Arabia, Gillespies, Systematica, Dar Al-Handasah', '',
         '## Key pages', '- [Home](%s/)' % BASE, '- [60 years](%s/60-years.html)' % BASE, '- [Projects](%s/projects.html)' % BASE, '- [Services](%s/services.html)' % BASE, '- [People](%s/people.html)' % BASE, '- [Amr Attia](%s/amr-attia.html)' % BASE, '- [Partners](%s/partners.html)' % BASE, '- [FAQ](%s/faq.html)' % BASE, '- [Contact](%s/contact.html)' % BASE, '', '## Services']
    L += ['- [%s](%s/services/%s.html): %s' % (s['name'], BASE, s['slug'], s['lead']) for s in SERVICES]
    L += ['', '## Guides'] + ['- [%s](%s/insights/%s.html): %s' % (a['h1'], BASE, a['slug'], a['lead']) for a in ARTICLES]
    L += ['', '## Countries'] + ['- [%s](%s/countries/%s.html): %d projects' % (c, BASE, cslug(c), len(ps)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))]
    L += ['', '## Signature projects'] + ['- [%s](%s/projects/%s.html): %s' % (p['name'], BASE, p['slug'], clip(p.get('summary') or '', 150)) for p in sig]
    L += ['', '## Offices'] + ['- %s: %s, %s' % (a, b, c) for a, b, c in OFFICES]
    L += ['', '## Optional', '- [Full project list](%s/llms-full.txt)' % BASE]
    return '\n'.join(L) + '\n'
def llms_full():
    L = ['# PUD Consultants: project list', '']
    for p in sorted(PROJ, key=lambda p: -(p.get('year_start') or 0)):
        L.append('- [%s](%s/projects/%s.html), %s | %s%s | %s' % (p['name'], BASE, p['slug'], ', '.join(x for x in (p.get('city'), p['country']) if x), p['year'] + ' | ' if p['year'] else '', ('client: ' + p['client'] + ' | ') if p.get('client') else '', clip(p.get('summary') or '', 200)))
    return '\n'.join(L) + '\n'
def sitemap(paths):
    return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % ''.join('<url><loc>%s/%s</loc><lastmod>%s</lastmod></url>' % (BASE, '' if p == 'index.html' else p, TODAY) for p in paths)

def og_image():
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open('assets/founder/hero.jpg').convert('RGB').resize((1200, 675)).crop((0, 22, 1200, 652))
    ov = Image.new('RGBA', im.size, (10, 13, 18, 0)); d = ImageDraw.Draw(ov)
    for y in range(im.size[1]): d.line((0, y, im.size[0], y), fill=(10, 13, 18, int(30 + 190 * (y / im.size[1]) ** 1.5)))
    im = Image.alpha_composite(im.convert('RGBA'), ov); d = ImageDraw.Draw(im)
    try: f1 = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf', 66); f2 = ImageFont.truetype('/System/Library/Fonts/Avenir Next.ttc', 26, index=2)
    except Exception: f1 = f2 = ImageFont.load_default()
    d.text((60, 400), '60 years of helping people', font=f1, fill=(255, 255, 255)); d.text((60, 480), 'live a better life.', font=f1, fill=(239, 66, 35))
    d.text((60, 575), 'PUD CONSULTANTS  ·  URBAN PLANNING SINCE 1966', font=f2, fill=(220, 224, 230))
    lg = Image.open('assets/logo-mark.png').convert('RGBA'); lg.thumbnail((110, 180)); im.alpha_composite(lg, (1200 - 60 - lg.width, 40))
    im.convert('RGB').save('assets/og.jpg', quality=84)

def main():
    for sub in ('projects', 'css', 'js', 'data', 'services', 'insights', 'cities', 'countries'): os.makedirs(SITE + '/' + sub, exist_ok=True)
    if os.environ.get('OG'): og_image()  # needs macOS fonts; og.jpg is kept as committed
    css = open('src/fonts.css').read() if ex('src/fonts.css') else ''
    open(SITE + '/css/style.css', 'w').write(css + open('src/style.css').read())
    if os.path.exists(SITE + '/assets'): shutil.rmtree(SITE + '/assets')
    shutil.copytree('assets', SITE + '/assets', ignore=shutil.ignore_patterns('video'))
    shutil.copytree('fonts', SITE + '/fonts', dirs_exist_ok=True)
    shutil.copy('data/countries.geojson', SITE + '/data/countries.geojson')
    paths = []
    def W(n, c): open(SITE + '/' + n, 'w', encoding='utf-8').write(eco(n, c).replace(' &ndash; ', ', ').replace(' – ', ', ').replace(' — ', ', ').replace('—', ', ')); paths.append(n)
    W('index.html', home()); W('60-years.html', story()); W('people.html', people()); W('projects.html', projects_page()); W('partners.html', partners_page()); W('contact.html', contact_page())
    W('amr-attia.html', amr_page()); W('services.html', services_page()); W('insights.html', insights_page()); W('faq.html', faq_page()); os.makedirs(SITE + '/destinations', exist_ok=True); W('destinations/red-sea.html', red_sea_page())
    for s in SERVICES: W('services/%s.html' % s['slug'], service_page(s))
    for a in ARTICLES: W('insights/%s.html' % a['slug'], article_page(a))
    for p in PROJ: W('projects/%s.html' % p['slug'], project_page(p))
    for d in PLACES.values(): W('cities/%s.html' % d['slug'], city_page(d))
    for c, ps in COUNTRIES.items(): W('countries/%s.html' % cslug(c), country_page(c, ps))
    skip = {'cities/%s.html' % s for s in NOINDEX_CITIES if s in PLACES and len(PLACES[s]['projects']) < 2}
    open(SITE + '/sitemap.xml', 'w').write(sitemap([x for x in paths if x not in skip])); open(SITE + '/llms.txt', 'w').write(llms()); open(SITE + '/llms-full.txt', 'w').write(llms_full().replace(' – ', ', '))
    open(SITE + '/robots.txt', 'w').write(('User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE) if MODE == 'prod' else 'User-agent: *\nDisallow: /\n')
    print('MODE', MODE, 'pages', len(paths), 'projects', len(PROJ), 'places', len(PLACES), 'countries', len(COUNTRIES), 'logos', sum(1 for p in PART if has_logo(p)))
def postprocess():
    import glob
    # 1. root links to ./ instead of index.html
    for f in glob.glob(SITE + '/**/*.html', recursive=True):
        t = open(f, encoding='utf-8').read()
        depth = os.path.relpath(f, SITE).count('/')
        t2 = t.replace('href="index.html"', 'href="./"').replace('href="../index.html"', 'href="../"')
        if t2 != t: open(f, 'w', encoding='utf-8').write(t2)
    # 2. drop unreferenced assets and fonts
    text = ''
    for ext in ('html', 'js', 'css', 'json', 'txt', 'xml'):
        for f in glob.glob(SITE + '/**/*.' + ext, recursive=True):
            try: text += open(f, encoding='utf-8').read()
            except Exception: pass
    removed = 0
    for sub in ('assets', 'fonts'):
        for f in glob.glob(SITE + '/' + sub + '/**/*', recursive=True):
            if os.path.isfile(f) and os.path.relpath(f, SITE) not in text:
                os.remove(f); removed += 1
    print('removed unreferenced files:', removed)
    # 3. prod hosting files
    if MODE == 'prod':
        shutil.copy('data/qc/404.html', SITE + '/404.html'); shutil.copy('data/qc/_headers', SITE + '/_headers')
        red = open('data/qc/_redirects').read().rstrip() + '\n' + open('data/redirects-wix.txt').read()
        open(SITE + '/_redirects', 'w').write(red)

main()
postprocess()
