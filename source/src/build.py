# -*- coding: utf-8 -*-
"""PUD 60-years site generator (v5, SEO/GEO edition). MODE=prod strips noindex. Usage: python3 src/build.py"""
import json, os, re, shutil, sys, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); os.chdir(ROOT); sys.path.insert(0, HERE)
from content import *
from seo import *
import copy2
from copy2 import *
import copy3
from copy3 import LEAD_HTML, RETIRED
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
       'founder': {'@id': BASE + '/people.html#abdallah-attia'}, 'employee': {'@id': BASE + '/amr-attia.html#amr-attia'}, 'sameAs': ['https://www.linkedin.com/company/pud-consultants', 'https://share-architects.com/office/pud-consultants/'], 'slogan': '60 Years of Shaping Sustainable Cities', 'award': 'International Star for Leadership in Quality, Paris 2010',
       'areaServed': ['Egypt', 'Saudi Arabia', 'United Arab Emirates', 'Kuwait', 'Iraq', 'Middle East and North Africa'],
       'knowsAbout': ['Urban planning', 'Regional planning', 'Master planning', 'Urban design', 'Sustainable tourism', 'Cultural heritage planning', 'Landscape design', 'Architecture', 'Sustainable development'],
       'location': [
                    {'@type': 'Place', 'name': 'PUD Cairo (Sheikh Zayed)', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Polygon Building 8, Office 208, SODIC, Beverly Hills', 'addressLocality': 'Sheikh Zayed City', 'postalCode': '12588', 'addressCountry': 'EG'}, 'telephone': '+20 100 198 1111'},
                    {'@type': 'Place', 'name': 'PUD Cairo (Heliopolis)', 'address': {'@type': 'PostalAddress', 'streetAddress': '115 El Thawra Street, 5th Floor, Heliopolis', 'addressLocality': 'Cairo', 'postalCode': '11757', 'addressCountry': 'EG'}, 'telephone': '+20 2 2414 7537'},
                    {'@type': 'Place', 'name': 'PUD Riyadh (Diplomatic Quarter)', 'address': {'@type': 'PostalAddress', 'streetAddress': '8620 Ibn Mousa Street, Diplomatic Quarter', 'addressLocality': 'Riyadh', 'postalCode': '2513', 'addressCountry': 'SA'}, 'telephone': '+966 540 39 8178'},
                    {'@type': 'Place', 'name': 'PUD Riyadh (Al Nakheel)', 'address': {'@type': 'PostalAddress', 'streetAddress': '7064 Salem bin Maaqil Street, Al Nakheel District', 'addressLocality': 'Riyadh', 'postalCode': '12393', 'addressCountry': 'SA'}, 'telephone': '800 111 0893'},
                    {'@type': 'Place', 'name': 'PUD Dubai (Palm Jumeirah)', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Shoreline 12, Al Anbara, PH 06, Palm Jumeirah', 'addressLocality': 'Dubai', 'addressCountry': 'AE'}, 'telephone': '+971 509 29 8178'}]}
WEB = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '/#site', 'url': BASE + '/', 'name': 'PUD Consultants', 'publisher': {'@id': BASE + '/#org'}, 'inLanguage': 'en'}

HERO_COUNTRIES, HERO_PROJECTS = 12, 200  # rounded figures shown in the home hero
AMR = load('data/amr.public.json', {})
NAV = [('about.html', 'About'), ('projects.html', 'Projects'), ('60-years.html', '60 years'), ('people.html', 'People'), ('partners.html', 'Partners'), ('sustainability.html', 'Sustainability'), ('insights.html', 'Insights'), ('contact.html', 'Contact')]
CHAPTERS = [('index.html', 'Home', 'Back to the start'), ('60-years.html', 'The 60-year story', 'Six decades of work'), ('people.html', 'The people', 'The founder and the practice'), ('projects.html', 'The work', 'Every project on one map'),
            ('about.html', 'Who we are', 'About, expertise and values'), ('partners.html', 'Who we plan with', 'Clients and partners'), ('contact.html', 'Talk to us', 'Five offices')]

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
    return ('<!doctype html><html lang="en" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="pud-build" content="__B__">'
            '<title>%s</title><meta name="description" content="%s">%s<link rel="canonical" href="%s"><link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="x-default" href="%s">'
            '<meta name="theme-color" content="#000000"><meta property="og:type" content="website"><meta property="og:site_name" content="PUD Consultants"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s"><meta property="og:locale" content="en_US">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">'
            '<link rel="icon" href="%sassets/logo-mark.png"><link rel="preload" href="%sfonts/antonio-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="%scss/style.css?v=__V__">%s%s</head>'
            '<body class="%s"><a class="skip" href="#main">Skip to content</a><header class="nav"><div class="wrap in"><a class="brand" href="%sindex.html" aria-label="PUD Consultants, home"><img src="%sassets/logo-mark.png" alt="PUD Consultants logo" width="25" height="40"><span><b>PUD Consultants</b><small>PLANNING &amp; URBAN DEVELOPMENT</small></span></a>'
            '<nav aria-label="Main"><ul>%s</ul></nav><a class="btn red film" href="%scontact.html">Talk to us</a><button class="burger" aria-label="Menu" aria-expanded="false"><i></i><i></i></button></div></header>'
            '<main id="main">%s</main>%s%s<script type="module" src="%sjs/app.js?v=__V__"></script></body></html>') % (
        E(title), E(d), robots, url, url, url, E(title), E(d), url, og, E(title), E(d), og, R, R, R, sch, head_extra, body_cls, R, R, lis, R, body, footer(R), dat, R)

# ---- v6: green #003737 touches for sustainability mentions and topics ----
ECO_SLUG = re.compile(r'(services|insights|destinations)/[^"]*(sustainab|environment|red-sea)|^(\.\./)?sustainability\.html')
ECO_WORDS = re.compile(r"\b(sustainab\w*|environmental|environment(?! and sustainability)|eco-?tourism|green infrastructure|low-carbon|climate[- ]resilien\w*|nature reserve)\b", re.I)
_SKIP = re.compile(r'(<head>.*?</head>|<script\b.*?</script>|<style\b.*?</style>|<svg\b.*?</svg>|<[^>]+>)', re.S)
def eco(path, html_):
    return html_  # sustainability green styling removed (Nov 2026)
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
    SV = ''.join('<a href="%sservices/%s.html">%s</a>' % (R, x['slug'], E(x['name'])) for x in SERVICES)
    return ('<footer class="f3"><div class="wrap"><div class="f3-g">'
            '<div class="f3-brand"><a class="brand" href="%sindex.html"><img src="%sassets/logo-mark.png" alt="PUD Consultants logo" width="25" height="40"><span><b>PUD Consultants</b><small>PLANNING &amp; URBAN DEVELOPMENT</small></span></a>'
            '<p>Leadership · Harmony · Clarity. Shaping sustainable cities since 1966.</p>'
            '<div class="f3-soc"><a href="https://www.linkedin.com/company/pud-consultants" target="_blank" rel="noopener" aria-label="PUD Consultants on LinkedIn"><svg viewBox="0 0 24 24"><path d="M4.98 3.5a2.5 2.5 0 11-.02 5 2.5 2.5 0 01.02-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.6 8.65 21 11.2 21 14.5V21h-4v-5.8c0-1.4-.03-3.2-1.95-3.2-1.95 0-2.25 1.52-2.25 3.1V21H9z"/></svg></a><a class="btn red" href="%scontact.html">Talk to us</a></div></div>'
            '<div><h5>Work</h5><a href="%sprojects.html">Projects</a><a href="%sprojects.html#atlas">The 60-year map</a><a href="%sabout.html#expertise">Expertise</a><a href="%sinsights.html">Insights</a></div>'
            '<div class="f3-sv"><h5>Services</h5>%s</div>'
            '<div><h5>Company</h5><a href="%sabout.html">About</a><a href="%ssustainability.html">Sustainability</a><a href="%s60-years.html">60 Years</a><a href="%speople.html">People</a><a href="%samr-attia.html">Prof. Dr. Amr Attia</a><a href="%spartners.html">Clients &amp; partners</a></div>'
            '<div><h5>Connect</h5><a href="%scontact.html">Contact</a><a href="%sfaq.html">FAQ</a><a href="tel:+201001981111">Cairo +20 100 198 1111</a><a href="tel:+966540398178">Riyadh +966 540 39 8178</a><a href="tel:+971509298178">Dubai +971 509 29 8178</a></div>'
            '</div><div class="fine"><span>&copy; 2026 PUD Consultants. All rights reserved.</span><span>60 Years of Shaping Sustainable Cities · 1966 to 2026</span></div></div></footer>') % (R, R, R, R, R, R, R, SV, R, R, R, R, R, R, R, R)

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
    return '<div class="reel" data-r><video muted loop playsinline preload="none" src="assets/founder/draw.mp4" poster="assets/founder/draw.jpg" aria-label="Illustrative recreation of Prof. Dr. Abdallah Attia at work"></video><div class="tabs">%s</div></div>' % tabs

# ---------- immersive home sections (v6) ----------
SVC_MEDIA = {
 'urban-and-regional-planning': ('assets/p/new-capital/01.jpg', 'new-administrative-capital-phases-2-4', 'New Administrative Capital, Phases 2 to 4'),
 'master-planning-and-urban-design': ('assets/stills/sumoublvd-egypt.jpg', 'somou-boulevard-new-cairo', 'Sumou Boulevard, New Cairo'),
 'sustainable-tourism-planning': ('assets/stills/marina-al-alamein-egypt.jpg', 'marina-el-alamein', 'Marina El Alamein, North Coast'),
 'cultural-heritage-planning': ('assets/stills/pyramids-plateau-egypt.jpg', 'pyramids-plateau-destination-master-plan', 'Pyramids Plateau Destination, Giza'),
 'architecture-and-interior-design': ('assets/stills/fawaz-al-hokair-estate-ksa.jpg', 'fawaz-alhokair-estate-riyadh', 'Fawaz Alhokair Estate, Riyadh'),
 'landscape-planning-and-design': ('assets/stills/jabal-thabeer-ksa.jpg', 'jabal-thabeer-park', 'Jabal Thabeer Park, Mina, Makkah'),
 'environment-and-sustainability': ('assets/stills/al-alamein-reveira-egypt.jpg', 'alamein-riviera-vision-master-plan', 'Alamein Riviera, North Coast'),
 'infrastructure-and-mobility-planning': ('assets/stills/al-ula-county-infrastructure.jpg', 'alula-county-infrastructure-master-plan', 'AlUla County Infrastructure Master Plan'),
 'development-consultancy-and-strategic-advisory': ('assets/stills/al-mashaaer-al-mugaddassah-ksa.jpg', 'al-mashaaer-al-mugaddassah-master-plan', 'Al Mashaaer Al Mugaddassah, Makkah'),
}

def services_immersive():
    media, rows = '', ''
    for i, s in enumerate(SERVICES):
        img, slug, cap = SVC_MEDIA.get(s['slug'], ('assets/stills/cairo-media-city-egypt.jpg', '', ''))
        media += '<figure data-i="%d"%s><img src="%s" alt="%s" loading="lazy"><figcaption class="mono">%s</figcaption></figure>' % (i, ' class="on"' if i == 0 else '', img, E(cap), E(cap))
        th = 'assets/thumbs/svx-%s.jpg' % s['slug'] if ex('assets/thumbs/svx-%s.jpg' % s['slug']) else img
        rows += ('<li data-i="%d"%s><a href="services/%s.html"><img class="mbg" src="%s" alt="" width="96" height="96"><span class="n mono">%02d</span><b>%s</b><span class="d">%s</span><i aria-hidden="true">&rarr;</i></a></li>'
                 % (i, ' class="on"' if i == 0 else '', s['slug'], th, i + 1, E(s['name']), LEAD_HTML.get(s['slug']) or E(s['lead'])))
    return ('<section class="svx" id="expertise"><div class="wrap svx-head"><div><p class="kicker mono" data-r>Our expertise</p><h2 class="h-l" data-r="0.1">Every place has <em>its own rhythm.</em></h2></div>'
            '<div class="stack" data-r="0.2"><p class="p-l">PUD (Planning &amp; Urban Development Consultants) is a multidisciplinary planning and design practice, founded in Cairo in 1966 by Prof. Dr. Abdallah Attia and led today by Prof. Dr. Amr Attia. We lead urban and tourism transformation, decoding land and cultural narratives to shape resilient communities, iconic destinations and sacred landscapes, from visionary master planning to precise execution.</p></div></div>'
            '<div class="wrap svx-body"><ol class="svx-list">%s</ol><div class="svx-media" aria-hidden="true"><div class="svx-frame">%s</div></div></div></section>') % (rows, media)

STORY = [('cmc-1-vision', 'Cairo Media City vision concept master plan at night, with the Pyramids of Giza on the horizon', 'cairo-media-city', 'Cairo Media City', 'Vision concept master plan · Giza'),
         ('gp-2-street', 'A tree-lined street opening onto a neighbourhood square, Green Pearl, Dubai', 'green-pearl-prime-dubai-competition', 'Green Pearl, Dubai', 'Concept master plan competition · Dubai, UAE'),
         ('gp-3-detail', 'Children and parents at a neighbourhood playground, Green Pearl, Dubai', 'green-pearl-prime-dubai-competition', 'Green Pearl, Dubai', 'Concept master plan competition · Dubai, UAE'),
         ('gp-4-people', 'Families walking and cycling along a green stream walk, Green Pearl, Dubai', 'green-pearl-prime-dubai-competition', 'Green Pearl, Dubai', 'Concept master plan competition · Dubai, UAE')]
def depth_story():
    shots = ''.join('<figure class="shot%s" data-i="%d" data-href="projects/%s.html" data-name="%s" data-sub="%s"><img src="assets/story/%s.jpg" srcset="assets/story/%s-m.jpg 1000w, assets/story/%s.jpg 1800w" sizes="100vw" alt="%s"%s></figure>'
                    % (' on' if i == 0 else '', i, slug, E(nm), E(sub), f, f, f, E(alt), ' loading="lazy" fetchpriority="low"') for i, (f, alt, slug, nm, sub) in enumerate(STORY))
    steps = ''.join('<div class="step"><span class="n mono">%s</span><h2>%s</h2><p>%s</p></div>' % (a, E(b), E(c)) for a, b, c in STEPS)
    f0 = STORY[0]
    return ('<section class="stage depth" aria-label="From vision to the people: four PUD projects"><div class="pin">'
            '<div class="cam">%s</div><div class="vig"></div><div class="steps">%s</div>'
            '<a class="projtag" href="projects/%s.html"><span class="mono">The project</span><b>%s</b><small>%s</small><i aria-hidden="true">&rarr;</i></a>'
            '<div class="bar" aria-hidden="true"><i></i></div><p class="hint mono">Scroll</p></div></section>') % (shots, steps, f0[2], E(f0[3]), E(f0[4]))

APPROACH = [
 ('Listen', 'Every project starts by listening: to the land, its history and the people who will live, work, pray and visit there.', 'assets/people/giza-framework-1.jpg'),
 ('Curate', 'Then we curate the best-fit minds (planners, architects, economists and global experts) around one shared mission.', 'assets/people/giza-decision-framework.jpg'),
 ('Shape', 'We decode land and cultural narratives into plans that tell a story, honour the place and stay ready for the future.', 'assets/stills/azha-ras-al-hekma-egypt.jpg'),
 ('Deliver', 'From visionary master planning to precise execution, transferring knowledge and building capabilities along the way.', 'assets/stills/jorhum-ksa.jpg'),
]
def approach_section():
    return ('<section class="sec approach"><div class="wrap"><div class="ap-txt"><p class="kicker mono" data-r>Our approach</p>'
            '<p class="ap-lead" data-r="0.1">We don\'t believe in one-size-fits-all. Every project starts by listening, then curates the best-fit minds (planners, architects, economists and global experts) around a shared mission. <a href="about.html#expertise">Explore our expertise</a></p></div>'
            '<a class="ap-img" href="projects/ramla-concept-master-plan.html" data-r="0.15"><span class="ap-par" data-px="0.08"><img src="assets/story/approach-ramla.jpg" alt="Beachfront town centre, Ramla, North Coast" loading="lazy"></span><span class="ap-cap mono">Ramla Beachfront Town Centre · North Coast, Egypt</span></a></div></section>')

DEC_BG = {'1966': ('assets/founder/draw.jpg', 'Prof. Dr. Abdallah Attia at work. Illustrative recreation.'),
          '1976': ('assets/stills/tut-amoun-village-2.jpg', 'Tut Amun Village, Lake Nasser, Aswan'),
          '1986': ('assets/stills/marina-al-alamein-egypt.jpg', 'Marina El Alamein, North Coast'),
          '1996': ('assets/p/al-madinah-hotels/01.jpg', 'Hotels and residential complexes, Al Madinah, 1998'),
          '2006': ('assets/p/maria-heights/01.jpg', 'Maria Heights Tourist Complex, Homs, 2008'),
          '2016': ('assets/stills/pyramids-plateau-egypt.jpg', 'Pyramids Plateau Destination, Giza')}
def decades_section():
    bgs, panels, rail = '', '', ''
    for i, d in enumerate(DECADES):
        img, cap = DEC_BG.get(d['yr'], ('assets/stills/cairo-media-city-egypt.jpg', ''))
        on = ' on' if i == 0 else ''
        bgs += '<figure class="dz-bg%s" data-i="%d"><img src="%s" alt="" loading="lazy"><figcaption class="mono">%s</figcaption></figure>' % (on, i, img, E(cap))
        th = ''.join('<a href="projects/%s.html"><img src="%s" alt="" loading="lazy"><span>%s</span></a>' % (p['slug'], thumb(p['slug']), E(p['name'])) for p in decade_projects(d))
        bl = ''.join('<li><b>%s</b>%s</li>' % (a, E(t)) for a, t in d['beats'][:3])
        panels += ('<article class="dz-p%s" data-i="%d"><p class="mono dz-range">%s to %s</p><h3>%s</h3><p class="dz-t">%s</p><ul>%s</ul><div class="th">%s</div></article>'
                   % (on, i, d['yr'], d['to'], E(d['title']), E(d['text']), bl, th))
        rail += '<button type="button" data-i="%d"%s><span>%s</span></button>' % (i, ' aria-current="true"' if i == 0 else '', d['yr'])
    return ('<section class="decades" id="story" style="--n:%d"><div class="dz-pin">%s<div class="dz-shade"></div>'
            '<div class="wrap dz-head"><p class="kicker mono">The journey</p><h2 class="h-l">Six decades. <em>One legacy.</em></h2></div>'
            '<div class="dz-year" aria-hidden="true"><span>%s</span></div><div class="wrap dz-panels">%s</div>'
            '<nav class="dz-rail" aria-label="Decades">%s<i class="dz-fill"></i></nav>'
            '<a class="dz-more btn ghost" href="60-years.html">Read the full story</a></div></section>') % (
                len(DECADES), bgs, DECADES[0]['yr'], panels, rail)

FOUNDER_PROSE = [
 'Prof. Dr. Abdallah Attia trained as an architect in Alexandria and completed his doctorate in architecture and planning at ETH Zurich, then founded PUD in Cairo in 1966 on a conviction that still guides the practice: planning and architecture should answer the place, never repeat a formula.',
 'His work gave shape to Egypt\'s North West Coast. He led Marina El Alamein from master plan to site supervision, recognised with the State Encouragement Prize in Architecture in 1990, and designed Tut Amun on Lake Nasser and Hilton Dahab on the Gulf of Aqaba. As Professor of Architecture and head of the Urban Planning Department at Ain Shams University, he shaped a generation of the region\'s planners and architects.',
]
AMR_PROSE = [
 'Prof. Dr. Amr Attia joined PUD in 1991 and has led it as CEO since 2005, carrying his father\'s vision into a new chapter of regional scale and international collaboration. In 2018 he co-founded PUD Saudi in Riyadh.',
 'His work spans planning frameworks for Jeddah, AlUla and the Holy Sites of Makkah, the next phases of Egypt\'s New Administrative Capital and the Giza Pyramids destination plan. Professor of Urban Planning at Ain Shams University, a UCL doctorate and an Eisenhower Fellow, he has held senior roles at AECOM Arabia and WATG, and chairs the board of SHARE Egypt 2026.',
]
def founder_section():
    paras = ''.join('<p class="prose" data-r="0.2">%s</p>' % E(p) for p in FOUNDER_PROSE)
    return ('<section class="sec founder" id="founder"><div class="wrap"><div class="grid2">%s'
            '<div><p class="kicker mono" data-r>The founder · 1966</p><h2 class="h-l" data-r="0.1">Prof. Dr. Abdallah <em>Attia</em></h2><p class="pull" data-r="0.15">Every legacy begins with a vision.</p>%s'
            '<p class="note">The footage here is an illustrative recreation made for the 60-year celebration. It is not archive film.</p><p style="margin-top:22px"><a class="btn ghost" href="people.html">Read his story</a></p></div></div></div></section>') % (founder_block(), paras)

def leader_section():
    paras = ''.join('<p class="prose" data-r="0.2">%s</p>' % E(p) for p in AMR_PROSE)
    return ('<section class="sec amrcard"><div class="wrap"><div class="grid2 amrg"><div data-r data-px="-0.06">%s</div><div><p class="kicker" data-r>The new chapter</p><h2 class="h-l" data-r="0.1">Prof. Dr. Amr <em>Attia</em></h2>'
            '<p class="pull" data-r="0.15">A great leader builds beyond today.</p>%s<p style="margin-top:26px" data-r="0.3"><a class="btn red" href="amr-attia.html">Read his profile</a></p></div></div></div></section>') % (amr_photo(), paras)

VALUES = [('Integrity', 'An ethical approach behind every relationship and every decision.'), ('Sustainability', 'Environmental, social and cultural harmony in every project.'),
          ('Innovation', 'Creativity and new tools for future-ready places.'), ('Excellence', 'The highest standards of quality and safety.')]
def culture_section():
    words = 'We don\'t just gather experts. We orchestrate brilliance.'.split(' ')
    q = ' '.join('<span>%s</span>' % E(w) for w in words)
    vals = ''.join('<li><b>%s</b><span>%s</span></li>' % (E(a), E(b)) for a, b in VALUES)
    return ('<section class="sec culture"><div class="wrap"><p class="kicker mono" data-r>Our culture</p><blockquote class="cq"><p>%s</p><footer class="mono">Prof. Dr. Amr Attia, CEO</footer></blockquote>'
            '<p style="margin-top:34px"><a class="btn ghost" href="people.html">Meet our people</a></p></div></section>') % q

SUSTAIN = [('People', 'Places designed around people: human-scale streets, shade, walkability and public space.'),
           ('Society', 'Inclusive, affordable and connected neighbourhoods that give every generation a place to belong.'),
           ('Culture', 'Heritage as a living foundation, so new development deepens a place\'s character.'),
           ('Environment', 'Working with nature, not against it: responsible land use and green building standards.'),
           ('Planet', 'Resilient regions for a changing climate, planned for compact, low-carbon growth.')]
def sustain_section():
    IC = {'People': '<circle cx="12" cy="7" r="3.2"/><path d="M5.5 20c.6-3.8 3.2-6 6.5-6s5.9 2.2 6.5 6"/>', 'Society': '<circle cx="7" cy="8.5" r="2.4"/><circle cx="17" cy="8.5" r="2.4"/><circle cx="12" cy="6.5" r="2.6"/><path d="M2.5 19c.4-2.8 2.2-4.4 4.5-4.4M21.5 19c-.4-2.8-2.2-4.4-4.5-4.4M7.2 20c.5-3.4 2.4-5.4 4.8-5.4s4.3 2 4.8 5.4"/>', 'Culture': '<path d="M3 9.5 12 4l9 5.5M4.5 9.5h15M6 9.5v8M10 9.5v8M14 9.5v8M18 9.5v8M3.5 20.5h17M4.5 17.5h15"/>', 'Environment': '<path d="M5 19c0-8 5.5-13.5 15-14-.3 9.5-6 15-14 15"/><path d="M5 19c3-4.5 6.5-7.5 10-9.5"/>', 'Planet': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.4 3.8 5.3 3.8 8.5s-1.2 6.1-3.8 8.5c-2.6-2.4-3.8-5.3-3.8-8.5S9.4 5.9 12 3.5z"/>'}
    items = ''.join('<li><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg><b>%s</b><span class="t">%s</span></li>' % (IC.get(a, ''), E(a), E(b)) for a, b in SUSTAIN)
    return ('<section class="sec sustain2"><div class="wrap"><div class="ap-txt"><p class="kicker mono" data-r><span>Sustainability and responsibility</span></p>'
            '<p class="ap-lead" data-r="0.1">From mega cities to sacred landscapes, sustainability is a lens of transformation: responsible land use, social inclusion, cultural continuity and green building standards. <a href="sustainability.html">Our commitment</a></p></div>'
            '<a class="ap-img" href="projects/alamein-riviera-vision-master-plan.html" data-r="0.15"><span class="ap-par" data-px="0.08"><img src="assets/story/sustain-alamein-riviera.jpg" alt="Homes around a planted lagoon at dusk, Alamein Riviera" loading="lazy" style="object-position:50%% 65%%"></span><span class="ap-cap mono">Alamein Riviera · North Coast, Egypt</span></a>'
            '<ol class="five2" data-r="0.1">%s</ol></div></section>') % items

def legacy_section():
    return ('<section class="legacy"><div class="big" aria-hidden="true" data-px="0.25">60</div><div class="wrap">'
            '<p class="kicker mono" data-r>1966 to 2026</p><h2 class="h-xl" data-r="0.1">60 years of shaping <em>sustainable cities.</em></h2>'
            '<p class="legacy-line" data-r="0.2">The legacy continues.</p>'
            '<p class="row" data-r="0.3"><a class="btn red" href="contact.html">Talk to us</a> <a class="btn ghost" href="60-years.html">Read the story</a></p></div></section>')


def home():
    strip = [p for p in PART if has_logo(p)]
    tiles = ''.join('<span class="t"><img src="%s" alt="%s logo" height="40" fetchpriority="low"></span>' % (p['logo'], E(p['name'])) for p in strip)
    hero_html = ('<section class="hero" id="top"><img class="poster" fetchpriority="high" src="assets/founder/hero.jpg" alt="Prof. Dr. Abdallah Attia drawing a plan, then Marina El Alamein and the Pyramids"><video autoplay muted loop playsinline preload="auto" poster="assets/founder/hero.jpg" aria-hidden="true"><source src="assets/founder/hero-m.mp4" type="video/mp4" media="(max-width:700px)"><source src="assets/founder/hero.mp4" type="video/mp4"></video>'
        '<div class="wrap in"><p class="kicker mono" data-r>1966 to 2026 · 60 years · Cairo · Riyadh · Dubai</p>'
        '<h1 class="h-xl hero-h" data-r="0.1">60 years of shaping <em>sustainable cities.</em></h1>'
        '<p class="lede" data-r="0.2">A multidisciplinary planning and design practice, shaping cities, destinations and sacred landscapes. The legacy continues; the future begins.</p>'
        '<div class="row" data-r="0.3"><a class="btn red" href="projects.html">Explore the work</a><a class="btn ghost" href="projects.html#atlas">Play the 60-year map</a></div>'
        '<div class="stats" data-r="0.4"><div class="stat"><b>1966</b><span class="mono">Founded in Cairo</span></div><div class="stat"><b>+%d</b><span class="mono">Countries</span></div>'
        '<div class="stat"><b>+%d</b><span class="mono">Projects</span></div><div class="stat"><b>5</b><span class="mono">Offices: Cairo, Riyadh, Dubai</span></div></div></div>'
        '<p class="cap">Prof. Dr. Abdallah Attia, founder of PUD. Illustrative recreation, not archive footage.</p><i class="scrollcue"></i></section>') % (HERO_COUNTRIES, HERO_PROJECTS)
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
    bento = ''.join(card(p, '', tag=p['cat1'], cls='hs-card') for i, p in enumerate(feat))
    featsec = ('<section class="hsx" id="work" aria-label="Selected work"><div class="hsx-pin"><div class="wrap hsx-head"><div><p class="kicker mono">Selected work</p><h2 class="h-l sw-h">From regional visions<br>to city-making<br><em>to the Holy Sites.</em></h2></div>'
               '<div class="hsx-meta"><span class="hsx-n mono"><b>01</b> / %02d</span><a class="btn ghost" href="projects.html">All projects</a></div></div>'
               '<div class="hsx-track">%s</div><div class="wrap"><div class="hsx-bar" aria-hidden="true"><i></i></div></div></div></section>') % (len(feat), bento) if bento else ''
    cn_cards = ''.join('<a href="countries/%s.html"><b>%s</b></a>' % (cslug(c), E(c)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))[:6])
    PIN = '<svg viewBox="0 0 24 32" aria-hidden="true"><path d="M12 1C6 1 1.5 5.6 1.5 11.4 1.5 19 12 31 12 31s10.5-12 10.5-19.6C22.5 5.6 18 1 12 1z"/><circle cx="12" cy="11.5" r="4.2"/></svg>'
    def mpin(x, y, name, side=''):
        return '<span class="mpin2 %s" style="left:%s%%;top:%s%%">%s<b>%s</b></span>' % (side, x, y, PIN, name)
    pins = mpin(44.8, 33.5, 'Palestine') + mpin(33, 6, 'Germany', 'r') + mpin(3, 63, 'Gambia', 'r')
    teaser = ('<section class="sec mapteaser"><div class="wrap"><div class="grid2 mt-head"><div><p class="kicker mono" data-r>Where we work</p><h2 class="h-l" data-r="0.1">From Egypt <em>to global destinations.</em></h2></div>'
              '<div><p class="p-l" data-r="0.2">From Alex to Aswan along the Mediterranean, the Red Sea and the Nile, across the Red Sea to Jeddah, AlUla and the Holy Sites, and on to Kuwait, Iraq, Syria, Palestine, the UAE, Cameroon, Gambia and Germany. Every pin opens a project with its client, partners and facts.</p><p style="margin-top:24px" data-r="0.3"><a class="btn red" href="projects.html">Open the map</a></p></div></div>'
              '<a class="mapimg big" href="projects.html" data-r="0.2"><img src="assets/stills/glowing-pins-across-the-middle-east.jpg" alt="Glowing map of the Middle East with PUD project locations" loading="lazy">%s</a></div></section>') % pins
    def lrow(L): return ''.join('<span class="lg"><img src="%s" alt="%s" loading="lazy"></span>' % (p['logo'], E(p['name'])) for p in L)
    cl = [p for p in strip if p.get('type') == 'client']; pt = [p for p in strip if p.get('type') != 'client']
    pl = ('<div class="lrow"><p class="mono lt">Our trusted clients</p><div class="lmq"><div class="ltr">%s%s</div></div></div>'
          '<div class="lrow rev"><p class="mono lt">Partners &amp; collaborations</p><div class="lmq"><div class="ltr">%s%s</div></div></div>') % (lrow(cl), lrow(cl), lrow(pt), lrow(pt))
    partners = ('<section class="sec partners-dk"><div class="wrap"><p class="kicker mono" data-r>Clients &amp; partners</p><h2 class="h-l" data-r="0.1">Trusted by clients. <em>Built with partners.</em></h2><p class="p-l" style="margin-top:18px;max-width:58ch" data-r="0.15">100+ clients and 90+ collaborations across six decades, from ministries and royal commissions to the world\'s leading design firms.</p><div class="logos2" data-r="0.2">%s</div><p style="margin-top:28px"><a class="btn ghost" href="partners.html">All clients and partners</a></p></div></section>') % pl if pl else ''
    fq = '<section class="sec"><div class="wrap">%s<p style="margin-top:24px"><a class="btn ghost" href="faq.html">More questions</a></p></div></section>' % faq_html(FAQ[:5])
    amr_card = ('<section class="sec amrcard"><div class="wrap"><div class="grid2 amrg"><div data-r>%s</div><div><p class="kicker" data-r>The new chapter</p><h2 class="h-l" data-r="0.1">Prof. Dr. Amr Attia</h2><p class="p-l" style="margin-top:18px" data-r="0.2">%s</p>%s'
        '<p style="margin-top:8px" data-r="0.3"><a class="btn red" href="amr-attia.html">Read his profile</a></p></div></div>'
        '<h3 class="h-m" style="margin-top:56px" data-r>Selected work</h3><div class="pgrid amrwork" data-r="0.1">%s</div></div></section>') % (amr_photo(), E(AMR_HEADLINE), stat_tiles(AMR_TILES), amr_work('', 3))
    film = ''
    body = welcome_strip() + hero_html + marq + featsec + services_immersive() + depth_story() + approach_section() + decades_section() + founder_section() + leader_section() + culture_section() + teaser + sustain_section() + partners + legacy_section()  + film
    return page('index.html', 'PUD Consultants | Urban Planning & Master Planning since 1966', body,
                'PUD Consultants plans cities, destinations and campuses. Founded in Cairo in 1966, with work across the region. Offices in Cairo, Riyadh and Dubai.', 'index.html',
                schema=[dict(ORG, **{'@context': 'https://schema.org'}), WEB])

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
    vals = '<section class="sec culture" style="padding-top:10px;padding-bottom:30px"><div class="wrap"><p class="trio mono" style="margin-top:0">Leadership · Harmony · Clarity</p><ul class="vals">%s</ul></div></section>' % ''.join('<li><b>%s</b><span>%s</span></li>' % (E(a_), E(b_)) for a_, b_ in VALUES)
    body = body.replace('</section>', '</section>' + vals, 1)
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

def expertise_filters():
    n = {x['slug']: sum(1 for p in PROJ if x['slug'] in svc_of(p)) for x in SERVICES}
    big = '<button type="button" class="ex-i" data-filter="svc:All" aria-pressed="true">All projects<sup>%d</sup></button>' % len(PROJ) + ''.join(
        '<button type="button" class="ex-i" data-filter="svc:%s" aria-pressed="false">%s<sup>%d</sup></button>' % (x['slug'], E(x['name']), n[x['slug']]) for x in SERVICES)
    pill = lambda k, v, lab, on=False: '<button type="button" class="fp" data-filter="%s:%s" aria-pressed="%s">%s</button>' % (k, E(v), 'true' if on else 'false', E(lab))
    region = pill('region', 'All', 'All regions', True) + pill('region', 'Egypt', 'Egypt') + pill('region', 'Saudi Arabia', 'Saudi Arabia') + pill('region', 'Intl', 'International')
    types = pill('svc', 'All', 'All types', True) + ''.join(pill('svc', x['slug'], x['name']) for x in SERVICES)
    era = pill('era', 'All', 'All years', True) + pill('era', '2020', '2020s') + pill('era', '2010', '2010s') + pill('era', '2000', '2000s') + pill('era', 'pre', 'Before 2000')
    return ('</div></section><section class="sec exf" id="expertise"><div class="wrap"><div class="ex-head"><p class="kicker mono">Expertise</p><div>'
            '<h2 class="h-l">Every place has its own rhythm. <em>Every challenge its own context.</em></h2>'
            '<p class="p-l" style="margin-top:18px">Our work crosses planning, design and heritage, and each project brings together the best-fit minds from PUD\'s network of planners, architects, economists and specialists.</p>'
            '<div class="ex-list" role="group" aria-label="Expertise">%s</div></div></div></div>'
            '<div class="fbar"><div class="wrap fbar-top"><button type="button" class="fb-t" aria-expanded="false" aria-controls="fbarG"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M7 12h10M10 17h4"/></svg>Filter by<i class="fb-c" aria-hidden="true"></i></button>'
            '<input class="search" type="search" placeholder="Search projects, cities, clients" aria-label="Search projects"><span class="count" data-total="%d"><b>%d</b> projects</span></div>'
            '<div class="wrap fbar-g" id="fbarG" hidden><div role="group" aria-label="Region"><h4>Region</h4>%s</div><div role="group" aria-label="Project type"><h4>Project type</h4>%s</div><div role="group" aria-label="Era"><h4>Era</h4>%s</div></div></div>'
            '<div class="wrap" style="padding-top:34px">') % (big, len(PROJ), len(PROJ), region, types, era)

def svc_of(p):
    return [x['slug'] for x in SERVICES if any(c in x['cats'] for c in p.get('category', [])) or p['slug'] in x['extra']]

def projects_page():
    cs = sorted({p['country'] for p in PROJ}); cats = sorted({c for p in PROJ for c in p.get('category', [])})
    ch = lambda k, vals: ''.join('<button class="chip" data-filter="%s:%s" aria-pressed="%s">%s</button>' % (k, E(v), 'true' if v == 'All' else 'false', E(v)) for v in ['All'] + vals)
    data = [dict(slug=p['slug'], name=p['name'], city=p.get('city', ''), country=p['country'], year=str(p['year']), year_start=p.get('year_start') or 2000, client=p.get('client', ''), category=p.get('category', []), lat=p.get('lat'), lon=p.get('lon'),
                 featured=bool(p.get('featured')), thumb=thumb(p['slug']) or '', url='projects/%s.html' % p['slug'], svc=svc_of(p)) for p in PROJ]
    order = sorted(range(len(PROJ)), key=lambda i: (not PROJ[i].get('featured'), not thumb(PROJ[i]['slug']), -(PROJ[i].get('year_start') or 0)))
    grid = ''.join(card(PROJ[i], '', i=i) for i in order)
    ccs = ''.join('<a href="countries/%s.html"><b>%s</b><span>%d projects</span></a>' % (cslug(c), E(c), len(ps)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1])))
    cities = ''.join('<a class="chip" href="cities/%s.html">%s <small>%d</small></a>' % (d['slug'], E(d['name']), len(d['projects'])) for d in sorted(PLACES.values(), key=lambda d: d['name']))
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Projects</p><h1 class="h-xl" style="max-width:17ch">From regional visions <em>to the Holy Sites.</em></h1><p class="lede">Press play to watch the practice grow from Cairo across the region. Drag to turn the map and click a pin to open a project.</p></div></section>'
        '<section class="sec atlas" id="atlas" style="padding-top:30px"><div class="wrap"><div class="box" data-geo="data/countries.geojson"><canvas aria-label="Map of PUD projects"></canvas><div class="tip"></div><div class="story" aria-live="polite"><span class="mono"></span><b></b></div><div class="now"></div>'
        '<div class="side"><button class="chip" data-view="all">Region</button><button class="chip" data-view="egypt">Egypt</button><button class="chip" data-view="ksa">Saudi Arabia</button><button class="chip" data-view="makkah">Makkah</button><span style="display:flex;gap:6px"><button class="chip" data-view="in" aria-label="Zoom in">+</button><button class="chip" data-view="out" aria-label="Zoom out">&minus;</button></span></div>'
        '<div class="hud"><div class="yrbox"><div class="yr">2026</div><div class="n mono"></div></div><input type="range" min="1964" max="2026" value="2026" aria-label="Year"><button class="btn red play">Play the story</button><button class="chip speed">Speed 1x</button><div class="legend"><span>1964</span><i></i><span>2026</span></div></div></div>'
        '<div class="cardsel"><img alt=""><div><h3 class="h-m"></h3><p class="note" style="font-size:14px"></p></div><a class="btn ghost" href="#">Open project</a></div>'
        + expertise_filters() +
        '<div class="pgrid">%s</div>'
        '</div></section>') % grid + chapter(3)
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
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Partners and clients</p><h1 class="h-xl" style="max-width:15ch">Trusted by clients. <em>Built with partners.</em></h1><p class="lede">National authorities, royal commissions, developers and universities commission our work. International firms such as WATG and AECOM plan alongside us, with a curated network of strategic partners and specialists.</p></div></section>' + network_sections() +
            ('<section class="sec paper" id="clients" style="padding-top:60px"><div class="wrap"><p class="kicker mono">Clients and partner firms</p><h2 class="h-l">100+ clients. <em>90+ collaborations.</em></h2>%s%s</div></section>') % (sect('Partners', 'partner'), sect('Clients', 'client'))) + chapter(5)
    return page('partners.html', 'Partners, Experts and Clients: WATG, AECOM, AlUla | PUD', body, 'PUD Consultants\' key staff, strategic partners and international expert network, and the clients and firms it plans with: WATG, AECOM, NUCA, the Royal Commission for AlUla and more.', 'partners.html',
                schema=[network_schema(), crumbs([('Home', ''), ('Partners', 'partners.html')])])

def map_block(R=''):
    pin = '<svg viewBox="0 0 24 32" aria-hidden="true"><path d="M12 1C6 1 1.5 5.6 1.5 11.4 1.5 19 12 31 12 31s10.5-12 10.5-19.6C22.5 5.6 18 1 12 1z"/><circle cx="12" cy="11.5" r="4.2"/></svg>'
    mp = lambda x, y, name, side='': '<span class="mpin2 %s" style="left:%s%%;top:%s%%">%s<b>%s</b></span>' % (side, x, y, pin, name)
    return ('<a class="mapimg big" href="%sprojects.html" data-r="0.2"><img src="%sassets/stills/glowing-pins-across-the-middle-east.jpg" alt="Glowing map of the Middle East with PUD project locations" loading="lazy">%s</a>'
            % (R, R, mp(44.8, 33.5, 'Palestine') + mp(33, 6, 'Germany', 'r') + mp(3, 63, 'Gambia', 'r')))

def contact_page():
    off = ''.join('<div><h2 class="h-m">%s</h2><p class="p-l" style="margin-top:10px">%s</p><p class="p-l"><a class="btn red call" href="tel:%s">Call %s</a></p></div>' % (E(a), E(b), re.sub(r'[^+0-9]', '', c), E(c)) for a, b, c in OFFICES)
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">Contact</p><h1 class="h-xl" style="max-width:14ch">Every great place starts <em>with a conversation.</em></h1><p class="lede">Call the office closest to your site. We plan and design from Cairo, Riyadh and Dubai.</p></div></section><section class="sec" style="padding-top:50px"><div class="wrap"><div class="offices">%s</div><div style="margin-top:clamp(50px,6vw,80px)">%s</div></div></section>' % (off, map_block()) + chapter(6)
    return page('contact.html', 'Contact PUD Consultants | Offices in Cairo, Riyadh and Dubai', body, 'Talk to PUD about a plan, a destination or a design. Call Cairo +20 100 198 1111, Riyadh +966 540 39 8178 or Dubai +971 509 29 8178.', 'contact.html',
                schema=[crumbs([('Home', ''), ('Contact', 'contact.html')]), dict(ORG, **{'@context': 'https://schema.org'})])

RED_SEA = ['port-ghalib-master-plan', 'abo-dabbab-marine-field-station', 'green-star-hotels-initiative', 'yuwdda-sub-regional-plan', 'ain-el-sokhna-tourist-center', 'hurghada-apartments-hotel-and-shopping-mall', 'pyramisa-apartment-hotel-hurghada', 'castle-zaman-hotel-red-sea']
def red_sea_page():
    R = '../'; ps = [BYSLUG[s] for s in RED_SEA if s in BYSLUG]
    qa = [('Does PUD plan Red Sea destinations?', 'Yes. PUD has worked on Port Ghalib and the Abo Dabbab marine field station at Marsa Alam, Hurghada, Ain El Sokhna and the Red Sea sub-regional plan for Yanbu, Umluj, Al Wajh and Duba in Saudi Arabia, and on the Green Star Hotels initiative with GIZ.')]
    body = ('<section class="page-h"><div class="wrap"><p class="crumb"><a href="../services/master-planning-and-urban-design.html">Urban design and master planning</a></p><h1 class="h-xl" style="max-width:18ch">Planning Red Sea destinations.</h1><p class="lede" style="max-width:56ch">PUD Consultants has planned Red Sea destinations in Egypt and Saudi Arabia: Port Ghalib and Abo Dabbab at Marsa Alam, Hurghada, Ain El Sokhna, the Green Star Hotels initiative and the sub-regional plan for Yanbu, Umluj, Al Wajh and Duba.</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="pgrid">%s</div>%s</div></section>') % (''.join(card(p, R) for p in ps), faq_html(qa)) + cta(R)
    return page('destinations/red-sea.html', 'Sustainable Tourism Planning on the Red Sea | PUD Consultants', body, 'Red Sea destination planning by PUD Consultants: Port Ghalib, Abo Dabbab, Hurghada, Ain El Sokhna and the Yanbu to Duba sub-regional plan.', 'about.html',
                schema=[faq_ld(qa), crumbs([('Home', ''), ('About', 'about.html'), ('Red Sea destinations', 'destinations/red-sea.html')])], og_img=hero_img(ps[0]['slug']) if ps else None)

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
    art = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['h1'], 'description': a['desc'], 'datePublished': '2026-11-24', 'dateModified': (LASTMOD.get('insights/%s.html' % a['slug']) or [0, '2026-11-24'])[1], 'author': {'@id': BASE + '/#org'}, 'publisher': {'@id': BASE + '/#org'}, 'mainEntityOfPage': BASE + '/insights/' + a['slug'] + '.html', 'inLanguage': 'en'}
    return page('insights/%s.html' % a['slug'], a.get('title') or fit('%s | PUD Consultants' % a['h1'], '%s | PUD' % a['h1']), body, a['desc'], 'insights.html', schema=[art, faq_ld([(a['q'], a['lead'])] + a['faq']), crumbs([('Home', ''), ('Insights', 'insights.html'), (a['h1'], 'insights/%s.html' % a['slug'])])])

def service_page(s):
    R = '../'
    sel = [p for p in PROJ if any(c in p.get('category', []) for c in s['cats'])]
    sel += [BYSLUG[x] for x in s['extra'] if x in BYSLUG]
    seen = set(); sel = [p for p in with_img_first(sel) if not (p['slug'] in seen or seen.add(p['slug']))]
    cds = {}
    for p in sel: cds[p['country']] = cds.get(p['country'], 0) + 1
    chips = ''.join('<a class="chip" href="../countries/%s.html">%s <small>%d</small></a>' % (cslug(c), E(c), n) for c, n in sorted(cds.items(), key=lambda kv: -kv[1]))
    pts = ''.join('<li>%s</li>' % E(x) for x in s['points'])
    body = ('<section class="page-h"><div class="wrap"><p class="crumb mono"><a href="../about.html#expertise">Expertise</a></p><h1 class="h-xl" style="max-width:18ch;font-size:clamp(38px,6vw,92px)">%s</h1><p class="lede" style="max-width:50ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="body"><div class="stack">%s</div><div><h2 class="h-m">What this covers</h2><ul class="ticks">%s</ul></div></div>'
            '<h2 class="h-m" style="margin-top:70px">Selected projects</h2><div class="pgrid">%s</div><p class="note" style="margin-top:14px">%d projects. Where we apply it:</p><div class="chiplist">%s</div>%s</div></section>') % (
        E(s['h1']), E(s['lead']), ''.join('<p class="p-l">%s</p>' % E(t) for t in s['body']), pts, ''.join(card(p, R) for p in sel[:12]), len(sel), chips, faq_html(s['faq'])) + cta(R)
    sv = {'@context': 'https://schema.org', '@type': 'Service', 'name': s['name'], 'serviceType': s['name'], 'description': s['lead'], 'provider': {'@id': BASE + '/#org'}, 'areaServed': ['Egypt', 'Saudi Arabia', 'Middle East']}
    return page('services/%s.html' % s['slug'], fit('%s | PUD Consultants' % s['h1'], '%s | PUD' % s['h1']), body, s['lead'], 'about.html', schema=[sv, faq_ld(s['faq']), crumbs([('Home', ''), ('About', 'about.html'), (s['name'], 'services/%s.html' % s['slug'])])], og_img=(hero_img(sel[0]['slug']) if sel else None))

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
         '## Key pages', '- [Home](%s/)' % BASE, '- [60 years](%s/60-years.html)' % BASE, '- [Projects](%s/projects.html)' % BASE, '- [About](%s/about.html)' % BASE, '- [Sustainability](%s/sustainability.html)' % BASE, '- [People](%s/people.html)' % BASE, '- [Amr Attia](%s/amr-attia.html)' % BASE, '- [Partners](%s/partners.html)' % BASE, '- [FAQ](%s/faq.html)' % BASE, '- [Contact](%s/contact.html)' % BASE, '', '## Services']
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
LASTMOD_FILE = os.path.join(ROOT, 'data', 'lastmod.json')
LASTMOD = load('data/lastmod.json', {})
def page_dates(paths):
    """lastmod per page: the date its content last changed (build tokens ignored), kept in data/lastmod.json"""
    import hashlib
    changed = False
    for p in paths:
        try: t = open(SITE + '/' + p, encoding='utf-8').read()
        except Exception: continue
        t = re.sub(r'__[BV]__|\?v=[0-9a-f]{8}', '', t)
        h = hashlib.md5(t.encode()).hexdigest()[:12]
        old = LASTMOD.get(p)
        if not old or old[0] != h:
            LASTMOD[p] = [h, TODAY]; changed = True
    if changed and MODE == 'prod': open(LASTMOD_FILE, 'w').write(json.dumps(LASTMOD, indent=0, sort_keys=True))
def sitemap(paths):
    page_dates(paths)
    return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % ''.join('<url><loc>%s/%s</loc><lastmod>%s</lastmod></url>' % (BASE, '' if p == 'index.html' else p, (LASTMOD.get(p) or [0, TODAY])[1]) for p in paths)

# ---------- v7: About, Sustainability and the expert network ----------
from copy4 import *
SUS_IMG = {'alula-strategic-framework-plan': 'assets/story/sus-alula-framework.jpg', 'khaybar-heritage-area-master-plan': 'assets/story/about-khaybar.jpg', 'kidana-al-khaif': 'assets/story/sus-kidana-al-khaif.jpg', 'sharaan-nature-reserve-master-plan': 'assets/story/sus-sharaan.jpg', 'north-coast-regional-vision-fuka-matrouh': 'assets/story/sus-nw-coast-regional-vision.jpg'}
_WH = {}
def wh(src):
    """width/height attributes for a local image, so the browser reserves space (no layout shift)."""
    if src not in _WH:
        try:
            from PIL import Image
            with Image.open(os.path.join(ROOT, src)) as im: _WH[src] = ' width="%d" height="%d"' % im.size
        except Exception: _WH[src] = ''
    return _WH[src]
def initials(n): return ''.join(w[0] for w in re.sub(r'^(Prof\.|Dr\.|Eng\.|Arch\.)\s*', '', re.sub(r'^(Prof\.|Dr\.|Eng\.|Arch\.)\s*', '', n)).split()[:2])
def numbered(items, cls='nlist'):
    return '<ol class="%s">%s</ol>' % (cls, ''.join('<li><span class="n mono">%02d</span><b>%s</b><span>%s</span></li>' % (i + 1, E(a), E(b)) for i, (a, b) in enumerate(items)))

def about_page():
    hero = 'khaybar-heritage-area-master-plan'; hi = 'assets/story/about-khaybar.jpg'
    gr = ''.join('<a class="svc" href="services/%s.html"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (s['slug'], E(s['name']), E(SVC_CARD.get(s['slug']) or clip(s['lead'], 110))) for s in SERVICES)
    gr += '<a class="svc" href="partners.html#network"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (E(ABOUT_ORCHESTRATION[0]), E(ABOUT_ORCHESTRATION[1]))
    countries = [c for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))]
    qa = [('What is PUD Consultants?', 'PUD (Planning & Urban Development) Consultants is a multidisciplinary planning and design consultancy founded in Cairo in 1966 by Prof. Abdallah Abdel Aziz Attia. It shapes sustainable cities, tourism destinations, heritage areas and sacred landscapes across Egypt, Saudi Arabia, the UAE and beyond.'),
          ('Who leads PUD Consultants today?', 'PUD is led by Prof. Dr. Amr A. Attia, CEO and Principal, Professor of Architecture and Urban Planning at Ain Shams University, an Eisenhower Fellow (2007) and former Vice President of Strategic Development at WATG and Principal Director at AECOM.'),
          ('What services does PUD offer?', 'PUD offers %s, and assembles bespoke advisory groups of international experts for each project.' % (', '.join(s['name'].lower() for s in SERVICES[:-1]) + ' and ' + SERVICES[-1]['name'].lower())),
          ('Where does PUD work?', 'PUD\'s record documents %d projects in %d countries: %s. Its offices are in Cairo (Egypt), Riyadh (Saudi Arabia) and Dubai (UAE).' % (len(PROJ), len(countries), ', '.join(countries[:-1]) + ' and ' + countries[-1])),
          ('What are some of PUD\'s notable projects?', 'Highlights include the Pyramids Plateau destination master plan (with WATG), Al Mashaaer Al Mugaddassah in Makkah, Alamein Riviera, Sumou Boulevard, Cairo Media City, strategic advisory for the New Administrative Capital, the Khaybar Heritage Area and AlUla framework plans, and Jazan Economic City.'),
          ('How does PUD approach sustainability?', 'Sustainability is at the core of every PUD project, through environmental responsibility, social inclusion, cultural heritage preservation and green building standards. PUD\'s work aligns with UN Sustainable Development Goals 7, 8, 9, 11, 12, 13 and 17.'),
          ('Does PUD work with international firms?', 'Yes. PUD regularly collaborates with leading global firms including WATG, AECOM, SOM, BuroHappold, HOK, Hill International and Giugiaro, combining international expertise with deep local knowledge, alongside 100+ clients and 90+ collaborations over six decades.'),
          ('How can I contact PUD Consultants?', 'Call Cairo on +20 2 2414 7537 or +20 100 198 1111, Riyadh on +966 540 39 8178 or Dubai on +971 509 29 8178, or use the enquiry form on the contact page.')]
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">About PUD</p><h1 class="h-xl" style="max-width:16ch">Planning &amp; Urban Development <em>since 1966.</em></h1><p class="lede" style="max-width:50ch">%s</p></div></section>'
            '%s'
            '<section class="sec" style="padding-top:40px"><div class="wrap"><p class="kicker mono">Our purpose</p><p class="statement">%s</p>'
            '<h2 class="h-m" style="margin-top:80px">Who we are</h2><div class="cols2" style="margin-top:22px">%s</div>'
            '<div class="duo"><div><p class="kicker mono">Mission</p><p class="p-l">%s</p></div><div><p class="kicker mono">Vision</p><p class="p-l">%s</p></div></div>'
            '<h2 class="h-m" style="margin-top:80px">Core values</h2>%s</div></section>'
            '<section class="sec paper" id="expertise"><div class="wrap"><p class="kicker mono">Expertise</p><h2 class="h-l" style="max-width:18ch">From visionary master plans <em>to precise execution.</em></h2><p class="p-l" style="margin-top:18px">Six services, one integrated practice, and a global network of experts orchestrated around each project.</p><div class="svcgrid">%s</div></div></section>'
            '<section class="sec" id="approach"><div class="wrap"><p class="kicker mono">Approach</p><h2 class="h-l" style="max-width:20ch">Tailored thinking. Integrated delivery. <em>Lasting impact.</em></h2><p class="p-l" style="margin-top:18px">%s</p>%s</div></section>'
            '<section class="sec paper" id="sustainability"><div class="wrap grid2x"><div><p class="kicker mono">Sustainability</p><h2 class="h-l">Designing with purpose. <em>Building for tomorrow.</em></h2><p class="p-l" style="margin-top:18px">Sustainability is not just a guideline, it is a lens of transformation. From mega cities to sacred landscapes, our goal is simple: to leave a positive legacy.</p>%s<p style="margin-top:28px"><a class="btn dark" href="sustainability.html">Our sustainability commitments</a></p></div>'
            '<a class="figure" href="projects/sharaan-nature-reserve-master-plan.html"><img src="%s" alt="Sharaan Nature Reserve master plan, AlUla" loading="lazy"%s><span class="mono">Sharaan Nature Reserve · AlUla</span></a></div></section>'
            '<section class="sec" id="awards"><div class="wrap"><p class="kicker mono">Awards</p><h2 class="h-l" style="max-width:20ch">%s</h2><p class="p-l" style="margin-top:18px">%s</p>'
            '<div style="margin-top:80px">%s</div></div></section>') % (
        E(ABOUT_LEAD),
        ('<section class="wrap"><a class="figure wide" href="projects/%s.html"><img src="%s" alt="Khaybar Heritage Area master plan, AlUla" fetchpriority="high"%s><span class="mono">Khaybar Heritage Area master plan · AlUla &rarr;</span></a></section>' % (hero, hi, wh(hi))) if hi else '',
        E(ABOUT_PURPOSE), ''.join('<p class="p-l">%s</p>' % E(t) for t in ABOUT_WHO), E(ABOUT_MISSION), E(ABOUT_VISION), numbered(ABOUT_VALUES, 'nlist four'),
        gr, E(ABOUT_APPROACH_LEAD), numbered(ABOUT_APPROACH, 'nlist three'),
        numbered([(a, b) for a, b in SUS_FOUR], 'nlist two'), SUS_IMG['sharaan-nature-reserve-master-plan'], wh(SUS_IMG['sharaan-nature-reserve-master-plan']),
        E(ABOUT_AWARDS[0]), E(ABOUT_AWARDS[1]), faq_html(qa, 'Frequently asked questions')) + chapter(4)
    about = {'@context': 'https://schema.org', '@type': 'AboutPage', 'url': BASE + '/about.html', 'name': 'About PUD Consultants', 'description': ABOUT_LEAD, 'mainEntity': {'@id': BASE + '/#org'}, 'inLanguage': 'en'}
    il = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD services', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/services/' + s['slug'] + '.html', 'name': s['name']} for i, s in enumerate(SERVICES)]}
    return page('about.html', 'About PUD Consultants: Urban Planning since 1966 | PUD', body,
                'PUD Consultants, founded in Cairo in 1966: our purpose, mission, values, six services, approach, sustainability and awards. Offices in Cairo, Riyadh and Dubai.', 'about.html',
                schema=[about, dict(ORG, **{'@context': 'https://schema.org'}), il, faq_ld(qa), crumbs([('Home', ''), ('About', 'about.html')])], og_img=hi)

def sustainability_page():
    R = ''; hi = 'assets/story/gp-4-people.jpg'
    five = ''
    for i, (th, h, t, slug, cap) in enumerate(SUS_FIVE):
        im = SUS_IMG.get(slug) or hero_img(slug)
        five += ('<article class="resp%s"><div class="resp-t"><p class="n mono">%02d · %s</p><h3 class="h-m">%s</h3><p class="p-l">%s</p></div>'
                 '<a class="figure" href="projects/%s.html"><img src="%s" alt="%s" loading="lazy"%s><span class="mono">%s &rarr;</span></a></article>') % (' flip' if i % 2 else '', i + 1, E(th), E(h), E(t), slug, im, E(cap.replace(' · ', ', ')), wh(im), E(cap))
    sdg = ''.join('<li><span class="sdg-n">%d</span><b>%s</b><span class="un">%s</span><span class="pud"><em class="mono">PUD</em> %s</span></li>' % (n, E(g), E(u), E(p)) for n, g, u, p in SDGS)
    lens = ''.join('<li>%s</li>' % E(x) for x in SUS_LENS)
    def scard(slug):
        p = BYSLUG[slug]; im = SUS_IMG.get(slug) or hero_img(slug)
        if not im: return card(p, R)
        return '<a class="pcard" href="projects/%s.html"><img src="%s" alt="%s, %s" loading="lazy"%s><span class="t"><b>%s</b><span>%s</span></span></a>' % (slug, im, E(p['name']), E(p.get('city') or p['country']), wh(im), E(p['name']), E(' · '.join(x for x in (p.get('city') or p['country'], str(p['year'])) if x)))
    projs = ''.join(scard(s) for s in SUS_PROJECTS if s in BYSLUG)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Sustainability</p><h1 class="h-xl" style="max-width:17ch">Sustainable commitments for a <em>vibrant urban future.</em></h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '%s'
            '<section class="sec" style="padding-top:40px"><div class="wrap"><p class="kicker mono">Our commitment</p><p class="statement">Sustainability is at the core of everything we do.</p><div class="cols2" style="margin-top:26px">%s</div>'
            '<h2 class="h-l" style="margin-top:90px;max-width:18ch">Designing with purpose. <em>Building for tomorrow.</em></h2><p class="p-l" style="margin-top:14px">We are committed to:</p>%s</div></section>'
            '<section class="sec paper"><div class="wrap"><p class="kicker mono">Five responsibilities, one approach</p><h2 class="h-l" style="max-width:20ch">People, society, culture, environment <em>and planet.</em></h2>%s</div></section>'
            '<section class="sec interlude-s"><img src="assets/story/sustain-alamein-riviera.jpg" alt="Homes around a planted lagoon at dusk, Alamein Riviera" loading="lazy"%s><div class="wrap"><p class="h-l">Where sustainability shapes place, purpose and people.</p><a class="mono" href="projects/alamein-riviera-vision-master-plan.html">Alamein Riviera · North Coast, Egypt &rarr;</a></div></section>'
            '<section class="sec"><div class="wrap"><p class="kicker mono">Designing resilient futures</p><h2 class="h-l" style="max-width:18ch">Not just a guideline: <em>a lens of transformation.</em></h2><p class="p-l" style="margin-top:18px">From mega cities to sacred landscapes, we weave resilience into every layer of planning.</p><ul class="lens">%s</ul><p class="p-l" style="margin-top:26px">Every decision we make is designed to serve the future. That is how we build legacy, rooted in sustainability.</p></div></section>'
            '<section class="sec paper" id="sdgs"><div class="wrap"><p class="kicker mono">Goals we support</p><h2 class="h-l">Leave no place behind.</h2><p class="p-l" style="margin-top:18px">Our work is aligned with the UN Sustainable Development Goals, contributing most directly to seven of the seventeen.</p><ol class="sdgs">%s</ol></div></section>'
            '<section class="sec"><div class="wrap"><p class="kicker mono">Sustainability in practice</p><h2 class="h-l">Selected projects</h2><div class="pgrid" style="margin-top:30px">%s</div>'
            '<p style="margin-top:24px"><a class="btn ghost" href="projects.html">All projects</a> <a class="btn ghost" href="services/environment-and-sustainability.html">Environmentally sustainable development</a></p>'
            '<div style="margin-top:80px">%s</div></div></section>'
            '<section class="sec ctaband"><div class="wrap duo"><div><p class="kicker mono">For clients</p><h2 class="h-m">Need help developing your SDGs strategy?</h2><p style="margin-top:20px"><a class="btn red" href="contact.html">Contact one of our experts</a></p></div>'
            '<div><p class="kicker mono">For partners</p><h2 class="h-m">Making progress together.</h2><p style="margin-top:20px"><a class="btn ghost" href="partners.html#network">Become one of our partners</a></p></div></div></section>') % (
        E(SUS_LEDE),
        ('<section class="wrap"><a class="figure wide" href="projects/green-pearl-prime-dubai-competition.html"><img src="%s" alt="Families walking and cycling along a green stream walk, Green Pearl, Dubai" fetchpriority="high"%s style="object-position:50%% 60%%"><span class="mono">Green Pearl · Dubai &rarr;</span></a></section>' % (hi, wh(hi))) if hi else '',
        ''.join('<p class="p-l">%s</p>' % E(t) for t in SUS_COMMIT), numbered(SUS_FOUR, 'nlist four'), five, wh('assets/story/sustain-alamein-riviera.jpg'), lens, sdg, projs, faq_html(SUS_FAQ))
    wp = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': BASE + '/sustainability.html', 'name': 'Sustainability commitments and SDGs', 'description': SUS_LEDE, 'about': [{'@id': BASE + '/#org'}, {'@type': 'Thing', 'name': 'Sustainable development'}] + [{'@type': 'Thing', 'name': 'SDG %d: %s' % (n, g)} for n, g, u, p in SDGS], 'publisher': {'@id': BASE + '/#org'}, 'inLanguage': 'en'}
    return page('sustainability.html', 'Sustainability Commitments and UN SDGs | PUD Consultants', body,
                'PUD Consultants\' sustainability commitments: people, society, culture, environment and planet, aligned with UN SDGs 7, 8, 9, 11, 12, 13 and 17.', 'sustainability.html',
                schema=[wp, faq_ld(SUS_FAQ), crumbs([('Home', ''), ('Sustainability', 'sustainability.html')])], og_img=hi)

def network_sections():
    team = ''.join('<li><img src="%s" alt="%s" loading="lazy"%s><b>%s</b><span>%s</span><em class="mono">%s years of experience</em></li>' % (src, E(n), wh(src), E(n), E(r), y) for n, r, y, src in STAFF)
    def xp(name, role, creds): return '<li><span class="xp-i" aria-hidden="true">%s</span><b>%s</b><em class="mono">%s</em><ul>%s</ul></li>' % (E(initials(name)), E(name), E(role), ''.join('<li>%s</li>' % E(c) for c in creds))
    strat = ''.join(xp(n, 'Strategic partner', c) for n, c in STRATEGIC)
    spec = ''.join(xp(n, r, c) for n, r, c in SPECIALISTS)
    net = ''.join('<li><b>%s</b><span>%s</span></li>' % (E(n), E(r)) for n, r in NETWORK)
    tags = ''.join('<span class="chip">%s</span>' % E(t) for t in STRATEGY_TAGS)
    return ('<section class="sec" style="padding-top:30px"><div class="wrap grid2x"><div><p class="kicker mono">Stronger together</p><h2 class="h-l">An ecosystem of <em>partners and experts.</em></h2><p class="p-l" style="margin-top:18px">%s</p><blockquote class="pull">&ldquo;%s&rdquo;</blockquote></div>'
            '<figure class="figure"><img src="assets/people/team-gem.jpg" alt="The PUD team at the Grand Egyptian Museum, Giza" loading="lazy"%s><figcaption class="mono">The team at the Grand Egyptian Museum · Giza</figcaption></figure></div></section>'
            '<section class="sec paper" id="team"><div class="wrap"><p class="kicker mono">Key staff</p><h2 class="h-l">The permanent core.</h2><p class="p-l" style="margin-top:18px">The team driving PUD\'s long-term vision, ensuring continuity, strategic leadership and quality from advisory orchestration to delivery.</p><ul class="team">%s</ul></div></section>'
            '<section class="sec" id="strategic-partners"><div class="wrap"><p class="kicker mono">Strategic partners</p><h2 class="h-l">Finance, engineering, law <em>and sustainability.</em></h2><ul class="xps">%s</ul>'
            '<p class="kicker mono" style="margin-top:90px">Our experts</p><h2 class="h-l">Specialists we call on</h2><ul class="xps">%s</ul></div></section>'
            '<section class="sec paper" id="network"><div class="wrap"><p class="kicker mono">The curated expert ensemble</p><h2 class="h-l" style="max-width:20ch">Matching minds to missions, <em>and context to calibre.</em></h2>%s'
            '<h3 class="h-m" style="margin-top:80px">Experts who have served on PUD-led panels</h3><ul class="netlist">%s</ul></div></section>'
            '<section class="sec"><div class="wrap"><p class="kicker mono"><span>Our strategy for a sustainable future</span></p><h2 class="h-l">People-driven. <em>Extraordinary results.</em></h2><p class="p-l" style="margin-top:18px">%s</p><div class="chiplist" style="margin-top:22px">%s</div><p style="margin-top:28px"><a class="btn red" href="contact.html">Join our community</a></p></div></section>') % (
        E(NET_INTRO), E(NET_QUOTE), wh('assets/people/team-gem.jpg'), team, strat, spec, numbered(ENSEMBLE, 'nlist three'), net, E(STRATEGY), tags)

def network_schema():
    org = {'@id': BASE + '/#org'}
    people = [{'@type': 'Person', 'name': n, 'jobTitle': r, 'worksFor': org, 'image': BASE + '/' + src} for n, r, y, src in STAFF]
    people += [{'@type': 'Person', 'name': n, 'jobTitle': 'Strategic partner, PUD Consultants', 'description': '; '.join(c)} for n, c in STRATEGIC if n not in [s[0].split('. ', 1)[-1] for s in STAFF] and n not in [s[0] for s in STAFF]]
    people += [{'@type': 'Person', 'name': n, 'jobTitle': r, 'description': '; '.join(c)} for n, r, c in SPECIALISTS]
    return {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD Consultants: key staff, strategic partners and specialists', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': p} for i, p in enumerate(people)]}

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
    def W(n, c): c = c.replace('<img ', '<img decoding="async" '); open(SITE + '/' + n, 'w', encoding='utf-8').write(eco(n, c).replace(' &ndash; ', ', ').replace(' – ', ', ').replace(' — ', ', ').replace('—', ', ')); paths.append(n)
    W('index.html', home()); W('60-years.html', story()); W('people.html', people()); W('projects.html', projects_page()); W('partners.html', partners_page()); W('contact.html', contact_page())
    W('amr-attia.html', amr_page()); W('about.html', about_page()); W('sustainability.html', sustainability_page()); W('services.html', '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="%s/about.html"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=about.html#expertise"></head><body><a href="about.html#expertise">Our services are now on the About page.</a></body></html>' % BASE); W('insights.html', insights_page()); W('faq.html', faq_page()); os.makedirs(SITE + '/destinations', exist_ok=True); W('destinations/red-sea.html', red_sea_page())
    for s in SERVICES: W('services/%s.html' % s['slug'], service_page(s))
    for old, new in RETIRED.items():
        W('services/%s.html' % old, '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="%s/services/%s.html"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=%s.html"></head><body><a href="%s.html">This service is now part of another page.</a></body></html>' % (BASE, new, new, new))
    for a in ARTICLES: W('insights/%s.html' % a['slug'], article_page(a))
    for p in PROJ: W('projects/%s.html' % p['slug'], project_page(p))
    for d in PLACES.values(): W('cities/%s.html' % d['slug'], city_page(d))
    for c, ps in COUNTRIES.items(): W('countries/%s.html' % cslug(c), country_page(c, ps))
    skip = {'cities/%s.html' % s for s in NOINDEX_CITIES if s in PLACES and len(PLACES[s]['projects']) < 2}
    skip |= {'services/%s.html' % o for o in RETIRED} | {'services.html'}
    open(SITE + '/sitemap.xml', 'w').write(sitemap([x for x in paths if x not in skip])); open(SITE + '/llms.txt', 'w').write(llms()); open(SITE + '/llms-full.txt', 'w').write(llms_full().replace(' – ', ', '))
    open(SITE + '/robots.txt', 'w').write(('User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE) if MODE == 'prod' else 'User-agent: *\nDisallow: /\n')
    print('MODE', MODE, 'pages', len(paths), 'projects', len(PROJ), 'places', len(PLACES), 'countries', len(COUNTRIES), 'logos', sum(1 for p in PART if has_logo(p)))
def postprocess():
    import glob
    import hashlib
    V = hashlib.md5((open('src/style.css').read() + open('src/app.js').read()).encode()).hexdigest()[:8]
    import time as _t
    B = hashlib.md5((V + open(SITE + '/index.html', encoding='utf-8').read()).encode()).hexdigest()[:10]
    open(SITE + '/build.txt', 'w').write(B)
    for f in glob.glob(SITE + '/**/*.html', recursive=True):
        t = open(f, encoding='utf-8').read()
        if '__B__' in t: open(f, 'w', encoding='utf-8').write(t.replace('__B__', B))
    for f in glob.glob(SITE + '/**/*.html', recursive=True):
        t = open(f, encoding='utf-8').read()
        if '__V__' in t: open(f, 'w', encoding='utf-8').write(t.replace('__V__', V))
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
        # GitHub Pages has no server redirects: old Wix addresses and short aliases get a small page that forwards
        from urllib.parse import unquote
        lines = open('data/redirects-wix.txt').read().splitlines() + ['/services  /about.html  301']
        for ln in lines:
            parts = ln.split()
            if len(parts) < 2 or ln.startswith('#'): continue
            src, dst = unquote(parts[0]).strip('/'), parts[1]
            if not src or os.path.exists(os.path.join(SITE, src, 'index.html')): continue
            d = os.path.join(SITE, src); os.makedirs(d, exist_ok=True)
            open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved | PUD Consultants</title><link rel="canonical" href="%s%s"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=%s"><script>location.replace(%s)</script></head><body><a href="%s">This page has moved.</a></body></html>' % (BASE, dst, dst, json.dumps(dst), dst))
        open(SITE + '/CNAME', 'w').write('www.pudconsultants.com\n')
        open(SITE + '/.nojekyll', 'w').write('')
        shutil.copy('data/qc/404.html', SITE + '/404.html'); shutil.copy('data/qc/_headers', SITE + '/_headers')
        red = open('data/qc/_redirects').read().rstrip() + '\n' + open('data/redirects-wix.txt').read()
        open(SITE + '/_redirects', 'w').write(red)

main()
postprocess()
