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
    ends = [i for i in sentence_ends(t) if 60 < i < n] if 'sentence_ends' in globals() else []
    if ends: return t[:ends[-1] + 1]
    cut = t[:n]
    for sep in ('. ', '; ', ': ', ', '):
        i = cut.rfind(sep)
        if i > 80: return cut[:i].rstrip(',;:') + '.'
    return cut.rsplit(' ', 1)[0].rstrip(',;:') + '.'
def first_sentence(t):
    # CT-013: never cut a standfirst mid-sentence
    t = re.sub(r'\s+', ' ', t or '').strip(); m = re.match(r'(.+?[.!?])(\s|$)', t)
    return m.group(1) if m else t
def J(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':'))
ABBR = re.compile(r'(?:\b(?:Dr|Prof|Eng|Arch|St|Mr|Mrs|No|Co|Ltd|Inc|vs|e\.g|i\.e))$')
def sentence_ends(t):
    return [m.start() for m in re.finditer(r'\. (?=[A-Z0-9])', t) if not ABBR.search(t[:m.start()])]
def sclip(t, n=156):
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= n: return t
    ends = [i for i in sentence_ends(t) if i < n]
    return t[:ends[-1] + 1] if ends and ends[-1] > 60 else clip(t, n)

PROJ = load('data/projects.public.json', [])
CENSUS = load('data/projects.census.json', [])
have = {p['slug'] for p in PROJ}
for c in CENSUS:
    if c['slug'] not in have: PROJ.append(c); have.add(c['slug'])
# ---- live audit (Nov 2026): renamed, retired and merged entries ----
import copy5
PROJ = [p for p in PROJ if p['slug'] not in copy5.RETIRE]
_merged = [p for p in PROJ if p['slug'] in copy5.MERGE_FROM]
if _merged: PROJ = [p for p in PROJ if p['slug'] not in copy5.MERGE_FROM] + [dict(copy5.MERGED)]
for p in PROJ:
    if p['slug'] in copy5.RENAME: p['slug'] = copy5.RENAME[p['slug']]
have = {p['slug'] for p in PROJ}
PART = load('data/partners.json', [])
CLIPM = load('data/clip-map.json', {})
IMGS = load('data/images-A.json', []) + load('data/images-B.json', []) + load('data/images-C.json', [])
FACTS = load('data/online-facts.json', [])
PLINKS = {x['project_slug']: x for x in load('data/project-links.json', [])}
BYSLUG = {p['slug']: p for p in PROJ}
OVERRIDE.update(OVERRIDE2)
for _s, _o in list(OVERRIDE.items()) + list(copy5.OVERRIDE3.items()):
    _s = copy5.RENAME.get(_s, _s)
    if _s in BYSLUG: BYSLUG[_s].update(_o)
for _s, (_a, _b) in copy5.STRIP.items():
    if _s in BYSLUG: BYSLUG[_s]['summary'] = (BYSLUG[_s].get('summary') or '').replace(_a, _b)
for p in PROJ:  # CT-072: the official spelling is Somou
    for _k in ('name', 'summary'):
        if p.get(_k): p[_k] = p[_k].replace('Somou', 'Somou')
    if p.get('country') == p.get('city'): p['city'] = ''
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
 'port-said-tunnels':'suez-canal-tunnels-port-said','la-vista':'la-vista-town-new-cairo','private-waterfront-hurghada':'private-waterfront-property-hurghada','cairo-downtown':'downtown-cairo-regeneration',
 'jeddah-strategic-development-plan':'jeddah-spatial-framework-plan','saudi-railway-land-optimization':'saudi-railway-land-and-property-assets-strategy','taif-development-plan':'taif-development-plan',
 'al-khafji':'project-line-al-khafji-concept-master-plan','al-soudah':'al-soudah-master-plan-competition','alamein-riviera':'alamein-riviera-vision-master-plan','elysium':'elysium-mixed-use-development',
 'lusail':'simaisma-beach-and-lusail-islands','makkah-township':'makkah-township-vision-master-plan','najran-region':'najran-northern-border-design-guidelines','prime-dubai':'green-pearl-prime-dubai-competition',
 'ramla':'ramla-concept-master-plan','abu-qir':'abu-qir-city-and-port-extension','gargoub':'gargoub-new-port-city','khaybar':'khaybar-heritage-area-master-plan',
 'jadel-dhahran':'dhahran-investment-land-concept-master-plan','jadel-jeddah-hamdaniyah':'jeddah-hamdaniyah-investment-lands-concept-master-plan','hilton-dahab':'hilton-dahab-village-hotel',
}
IMG2PROJ.update(load('data/img2proj-extra.json', {}))
imgsets = {}
for s in IMGS:
    k = IMG2PROJ.get(s.get('slug_guess')) or s.get('slug_guess')
    k = copy5.RENAME.get(k, k)
    if k in copy5.MERGE_FROM: k = copy5.MERGE_INTO
    if k in BYSLUG:
        got = {i['src'] for i in imgsets.get(k, [])}
        imgsets.setdefault(k, []).extend([i for i in s.get('items', []) if ex(i['src']) and i['src'] not in got])
DROP = set(load('data/drop-images.json', []))
for k in imgsets: imgsets[k] = [i for i in imgsets[k] if i['src'] not in DROP][:12]
clipof = {}
for f, sl in load('data/clip-map.json', {}).items():
    stem = re.sub(r'[^a-z0-9]+', '-', os.path.basename(f).rsplit('.', 1)[0].lower()).strip('-'); stem = re.sub(r'-(egypt|ksa)$', '', stem)
    if isinstance(sl, dict): sl = sl.get('slug')
    sl = copy5.RENAME.get(sl, sl) if sl else sl
    if sl in copy5.MERGE_FROM: sl = copy5.MERGE_INTO
    if sl: clipof.setdefault(sl, {})['png' if f.lower().endswith('.png') else 'mov'] = stem
def still_for(slug):
    c = clipof.get(slug, {})
    for st in (c.get('png'), c.get('mov')):
        if not st: continue
        for cand in ('assets/stills/%s.jpg' % st, 'assets/stills/%s-egypt.jpg' % st, 'assets/stills/%s-ksa.jpg' % st, 'assets/stills/%s.jpg' % re.sub(r'-(egypt|ksa)$', '', st)):
            if ex(cand): return cand
NO_CLIP_HERO = set()
NO_STILL_IN_GALLERY = {'tut-amon-village-hotel-and-resort'}
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
def has_logo(p): return bool(p and p.get('logo') and ex(p['logo']) and p.get('slug') not in ('metropoli', 'tda'))
# LG-011 / LG-012 / LG-020: every name a client is written under, so the logo shows wherever the client is named
ALIASES = {
 'al-aqeelah': ['Al Aqeelah', 'Al-Aqeelah'], 'pif': ['PIF', 'Public Investment Fund'], 'madinah-development-authority': ['Madinah Central Area Development Authority', 'Madinah Development Authority'],
 'rcmc': ['RCMC', 'Royal Commission for Makkah'], 'gopp': ['GOPP', 'General Organization for Physical Planning'], 'tda': ['TDA', 'Tourism Development Authority'],
 'shoura-group': ['Shoura'], 'mckinsey': ['McKinsey'], 'strategy-and': ['Strategy&'], 'bcg': ['BCG', 'Boston Consulting Group'], 'ehcaan': ['EHCAAN'],
 'ministry-of-agriculture': ['Ministry of Agriculture'], 'saudi-railways': ['Saudi Railway Organization', 'SRO', 'Saudi Arabia Railways'], 'rcjy': ['Royal Commission for Jubail'],
 'paragon-developments': ['Paragon'], 'madaar': ['Madaar'], 'redcon': ['Redcon'], 'china-state-construction': ['China State Construction'], 'egypt-ministry-of-interior': ['Ministry of Interior'],
 'league-of-arab-states': ['League of Arab States', 'Arab League'], 'ministry-of-finance': ['Ministry of Finance'], 'nuca': ['NUCA', 'New Urban Communities Authority'],
 'rcu': ['Royal Commission for AlUla', 'RCU'], 'kidana': ['Kidana'], 'saudi-aramco': ['Saudi Aramco', 'Aramco'], 'palm-hills': ['Palm Hills'], 'kingdom-holding': ['Kingdom Holding'],
 'momrah': ['MOMRAH', 'Ministry of Municipal'], 'giza-governorate': ['Giza Governorate'], 'alexandria-governorate': ['Alexandria Governorate'], 'cairo-governorate': ['Cairo Governorate'],
 'ain-shams-university': ['Ain Shams University'], 'cairo-university': ['Cairo University'], 'world-bank': ['World Bank'], 'giz': ['GIZ'], 'sdc': ['Soudah Development'],
 'jeddah-municipality': ['Jeddah Municipality'], 'taif-municipality': ['Taif Municipality'], 'acud': ['ACUD'], 'state-of-cameroon': ['MAETUR'], 'cleopatra-group': ['Cleopatra'],
 'hassan-allam-properties': ['Hassan Allam'], 'marakez': ['Marakez'], 'nhmc': ['NHMC'], 'hepca': ['HEPCA'], 'kuwait-housing-authority': ['Kuwait Housing Authority'],
 'kuwait-real-estate-company': ['Kuwait Real Estate Company'], 'misr-hotels-company': ['Misr Hotels'], 'ministry-of-culture': ['Ministry of Culture'],
}
NO_LOGO = {'metropoli', 'tda', 'fawaz-alhokair'}  # LG-005 / LG-006: unreadable files stay off until PUD supplies proper ones; private client stays text
def client_logos(client, funders=False):
    """Logos for each named client, in the order the client line names them. Names after 'funded by' are funders."""
    c = client or ''; low = c.lower(); cut = low.find('funded by'); hits = []
    for p in PART:
        if p.get('type') != 'client' or not has_logo(p) or p['slug'] in NO_LOGO: continue
        names = ALIASES.get(p['slug'], []) + [re.sub(r'\s*\(.*\)$', '', p['name'])]
        pos = [m.start() for n in names for m in re.finditer(r'(?<![A-Za-z])' + re.escape(n) + r'(?![A-Za-z])', c)]
        if not pos: continue
        at = min(pos); is_f = cut >= 0 and at > cut
        if is_f == funders: hits.append((at, p))
    return [p for _, p in sorted(hits, key=lambda t: t[0])]

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
ORG = {'@type': ['Organization', 'ProfessionalService'], '@id': BASE + '/#org', 'name': 'PUD Consultants', 'alternateName': ['PUD', 'Planning & Urban Development Consultants'], 'url': BASE + '/', 'logo': BASE + '/assets/icon-512.png', 'image': BASE + '/assets/og.jpg', 'foundingDate': '1966',
       'description': 'PUD Consultants is an urban planning, master planning, architecture and sustainable tourism consultancy founded in Cairo in 1966, with offices in Cairo, Riyadh and Dubai.', 'legalName': 'Planning & Urban Development Consultants', 'disambiguatingDescription': 'Urban planning and architecture consultancy in Cairo. Not a planned unit development or public utility district, which share the acronym PUD.', 'foundingLocation': {'@type': 'Place', 'name': 'Cairo, Egypt'},
       'founder': {'@id': BASE + '/abdallah-attia.html#person'}, 'employee': {'@id': BASE + '/amr-attia.html#amr-attia'}, 'sameAs': ['https://www.linkedin.com/company/pud-consultants', 'https://share-architects.com/office/pud-consultants/'], 'slogan': '60 Years of Shaping Sustainable Cities', 'email': 'info@pudconsultants.com',
       'areaServed': ['Egypt', 'Saudi Arabia', 'United Arab Emirates', 'Kuwait', 'Iraq', 'Middle East and North Africa'],
       'knowsAbout': ['Urban planning', 'Regional planning', 'Master planning', 'Urban design', 'Sustainable tourism', 'Cultural heritage planning', 'Landscape design', 'Architecture', 'Sustainable development'],
       'location': [
                    {'@type': 'Place', 'name': 'PUD Cairo (Sheikh Zayed)', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Polygon Building 8, Office 208, SODIC, Beverly Hills', 'addressLocality': 'Sheikh Zayed City', 'postalCode': '12588', 'addressCountry': 'EG'}, 'telephone': '+20 100 198 1111'},
                    {'@type': 'Place', 'name': 'PUD Cairo (Heliopolis)', 'address': {'@type': 'PostalAddress', 'streetAddress': '115 El Thawra Street, 5th Floor, Heliopolis', 'addressLocality': 'Cairo', 'postalCode': '11757', 'addressCountry': 'EG'}, 'telephone': '+20 2 2414 7537'},
                    {'@type': 'Place', 'name': 'PUD Riyadh (Diplomatic Quarter)', 'address': {'@type': 'PostalAddress', 'streetAddress': '8620 Ibn Mousa Street, Diplomatic Quarter', 'addressLocality': 'Riyadh', 'postalCode': '2513', 'addressCountry': 'SA'}, 'telephone': '+966 540 39 8178'},
                    {'@type': 'Place', 'name': 'PUD Riyadh (Al Nakheel)', 'address': {'@type': 'PostalAddress', 'streetAddress': '7064 Salem bin Maaqil Street, Al Nakheel District', 'addressLocality': 'Riyadh', 'postalCode': '12393', 'addressCountry': 'SA'}, 'telephone': '800 111 0893'},
                    {'@type': 'Place', 'name': 'PUD Dubai (Palm Jumeirah)', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Shoreline 12, Al Anbara, PH 06, Palm Jumeirah', 'addressLocality': 'Dubai', 'addressCountry': 'AE'}, 'telephone': '+971 509 29 8178'}]}
WEB = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '/#site', 'url': BASE + '/', 'name': 'PUD Consultants', 'publisher': {'@id': BASE + '/#org'}, 'inLanguage': 'en'}

# CT-002: the home hero uses the counts the site can show (countries and documented projects)
AMR = load('data/amr.public.json', {})
NAV = [('about.html', 'About'), ('projects.html', 'Projects'), ('60-years.html', '60 years'), ('people.html', 'Leadership'), ('partners.html', 'Partners'), ('sustainability.html', 'Sustainability'), ('insights.html', 'Insights'), ('contact.html', 'Contact')]
CHAPTERS = [('index.html', 'Home', 'Back to the start'), ('60-years.html', 'The 60-year story', 'Six decades of work'), ('people.html', 'Leadership', 'The founder and the practice'), ('projects.html', 'The work', 'Every project on one map'),
            ('about.html', 'Who we are', 'About, expertise and values'), ('partners.html', 'Who we plan with', 'Clients and partners'), ('contact.html', 'Talk to us', 'Five offices')]

def fit(*c):
    for t in c:
        if len(t) <= 60: return t
    return c[-1].rsplit(' | ', 1)[0]

CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self'; font-src 'self'; "
       "connect-src 'self' https://formsubmit.co; object-src 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co")
def page(path, title, body, desc='', active='', schema=None, og_img=None, data=None, body_cls='', head_extra='', ms=None, noindex=False, og_type='website', og_alt=None):
    R = '../' * path.count('/')
    if path != '404.html': body = welcome_strip(R) + body
    d = sclip(desc or 'PUD Consultants: urban planning, master planning and sustainable development consultants since 1966, with offices in Cairo, Riyadh and Dubai.')
    lis = ''.join('<li><a href="%s%s"%s>%s</a></li>' % (R, h, ' aria-current="page"' if h == active else '', t) for h, t in NAV)
    url = BASE + '/' + ('' if path == 'index.html' else path)
    og = (BASE + '/' + og_img) if og_img else BASE + '/assets/og.jpg'
    robots = ('<meta name="robots" content="noindex,follow">' if noindex else '') if MODE == 'prod' else '<meta name="robots" content="noindex,nofollow,noarchive">'
    dat = ''
    if data is not None:  # SC-004: no inline script, so a strict Content-Security-Policy can apply
        open(SITE + '/data/projects-data.js', 'w', encoding='utf-8').write('window.__PROJECTS=%s;window.__MILESTONES=%s;\n' % (J(data), J(ms or [])))
        dat = '<script src="%sdata/projects-data.js?v=__V__"></script>' % R
    oimg = og_img or 'assets/og.jpg'
    ogx = '<meta property="og:image:width" content="%s"><meta property="og:image:height" content="%s">' % tuple(re.findall(r'\d+', wh(oimg)) or ('1200', '630'))
    ogx += '<meta property="og:image:alt" content="%s">' % E(og_alt or (title.split(' | ')[0] if og_img else 'PUD Consultants: urban planning and master planning since 1966'))
    sch = ld(*(schema or []))
    return ('<!doctype html><html lang="en" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="pud-build" content="__B__">'
            '<meta http-equiv="Content-Security-Policy" content="' + CSP + '"><meta name="referrer" content="strict-origin-when-cross-origin">'
            '<title>%s</title><meta name="description" content="%s">%s<link rel="canonical" href="%s">'
            '<meta name="theme-color" content="#000000"><meta property="og:type" content="' + og_type + '"><meta property="og:site_name" content="PUD Consultants"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s">' + ogx + '<meta property="og:locale" content="en_GB">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">'
            '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="192x192" href="/assets/icon-192.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="preload" href="%sfonts/antonio-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="%sfonts/roboto-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="%scss/style.css?v=__V__">%s%s</head>'
            '<body class="%s"><a class="skip" href="#main">Skip to content</a><header class="nav"><div class="wrap in"><a class="brand" href="%sindex.html" aria-label="PUD Consultants, home"><img src="%sassets/logo-mark.png" alt="PUD Consultants logo" width="25" height="40"><span><b>PUD Consultants</b><small>PLANNING &amp; URBAN DEVELOPMENT</small></span></a>'
            '<nav aria-label="Main"><ul>%s</ul></nav><a class="btn red film" href="%scontact.html">Talk to us</a><button class="burger" aria-label="Menu" aria-expanded="false"><i></i><i></i></button></div></header>'
            '<main id="main">%s</main>%s%s<script type="module" src="%sjs/app.js?v=__V__"></script></body></html>') % (
        E(title), E(d), robots, url, E(title), E(d), url, og, E(title), E(d), og, R, R, R, sch, head_extra, body_cls, R, R, lis, R, body, footer(R), dat, R)

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
            '<div><h2 class="f3-h">Work</h2><a href="%sprojects.html">Projects</a><a href="%sprojects.html#atlas">The 60-year map</a><a href="%sabout.html#expertise">Expertise</a><a href="%sinsights.html">Insights</a><a href="' + R + 'destinations/red-sea.html">Red Sea destinations</a></div>'
            '<div class="f3-sv"><h2 class="f3-h">Services</h2>%s</div>'
            '<div><h2 class="f3-h">Company</h2><a href="%sabout.html">About</a><a href="%ssustainability.html">Sustainability</a><a href="%s60-years.html">60 Years</a><a href="%sabdallah-attia.html">Founder: Prof. Dr. Abdallah Attia</a><a href="%samr-attia.html">Prof. Dr. Amr Attia</a><a href="%spartners.html">Partners</a><a href="' + R + 'clients.html">Clients</a><a href="' + R + 'awards.html">Awards</a><a href="' + R + 'news.html">News and events</a></div>'
            '<div><h2 class="f3-h">Connect</h2><a href="%scontact.html">Contact</a><a href="mailto:info@pudconsultants.com">info@pudconsultants.com</a><a href="%sfaq.html">FAQ</a><a href="' + R + 'privacy.html">Privacy</a><a href="' + R + 'accessibility.html">Accessibility</a><a href="tel:+201001981111">Cairo +20 100 198 1111</a><a href="tel:+966540398178">Riyadh +966 540 39 8178</a><a href="tel:+971509298178">Dubai +971 509 29 8178</a></div>'
            '</div><div class="fine"><span>&copy; 2026 PUD Consultants. All rights reserved.</span><span>60 Years of Shaping Sustainable Cities · 1966 to 2026</span></div></div></footer>') % (R, R, R, R, R, R, R, SV, R, R, R, R, R, R, R, R)

def alt_for(p):
    place = (p.get('city') or p['country']).split(',')[0].strip()
    return p['name'] if place.lower() in p['name'].lower() else '%s, %s' % (p['name'], place)
def card(p, R, i=None, tag=None, cls=''):
    t = thumb(p['slug']); url = '%sprojects/%s.html' % (R, p['slug'])
    di = ' data-i="%d"' % i if i is not None else ''
    meta = ' · '.join(x for x in (E(p.get('city') or p['country']), E(str(p['year']))) if x and x != 'None')
    tg = '<span class="tag">%s</span>' % E(tag) if tag else ''
    if t: return '<a class="pcard %s" href="%s"%s><img src="%s%s" alt="%s" loading="lazy"%s>%s<span class="t"><b>%s</b><span>%s</span></span></a>' % (cls, url, di, R, t, E(alt_for(p)), wh(t), tg, E(p['name']), meta)
    return '<a class="pcard ph %s" href="%s"%s>%s<span class="t"><b>%s</b><span>%s</span></span></a>' % (cls, url, di, tg, E(p['name']), meta)

def chapter(i, R=''):
    prv = CHAPTERS[i - 1] if i > 0 else None; nxt = CHAPTERS[i + 1] if i + 1 < len(CHAPTERS) else None
    a = '<a class="prev" href="%s%s"><span class="mono">Previous</span><b>%s</b></a>' % (R, prv[0], E(prv[1])) if prv else '<span></span>'
    b = '<a class="next" href="%s%s"><span class="mono">Next chapter · %s</span><b>%s</b><em>&rarr;</em></a>' % (R, nxt[0], E(nxt[2]), E(nxt[1])) if nxt else ''
    dots = ''.join('<i%s></i>' % (' class="on"' if k == i else '') for k in range(len(CHAPTERS)))
    return '<nav class="chapter" aria-label="Story chapters"><div class="wrap"><div class="dots" aria-hidden="true">%s</div><div class="row">%s%s</div></div></nav>' % (dots, a, b)

def welcome_strip(R=''):
    # CT-021 / G11: the announcement changes by date; the script keeps only the one that is current
    import datetime as _d
    today = _d.date.today().isoformat()
    if today <= '2026-11-25':
        return '<div class="welcome" data-until="2026-11-25">Prof. Dr. Amr Attia speaks at SHARE Kazakhstan in Almaty on 24 and 25 November. <a href="%samr-attia.html#on-stage">Read his profile</a></div><div class="welcome" data-from="2026-11-26" data-until="2026-12-14" hidden>Prof. Dr. Amr Attia is Board Chairman of SHARE Egypt 2026, at the Grand Egyptian Museum on 13 and 14 December. <a href="%snews.html">News and events</a></div>' % (R, R)
    if today <= '2026-12-14':
        return '<div class="welcome" data-until="2026-12-14">Prof. Dr. Amr Attia is Board Chairman of SHARE Egypt 2026, at the Grand Egyptian Museum on 13 and 14 December. <a href="%snews.html">News and events</a></div>' % R
    return ''

def cta(R='', text='Talk to us', head='Have a site, a district or a destination to plan?'):
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
 'master-planning-and-urban-design': ('assets/stills/sumoublvd-egypt.jpg', 'somou-boulevard-new-cairo', 'Somou Boulevard, New Cairo'),
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
    return ('<section class="svx" id="expertise"><div class="wrap svx-head"><div><p class="kicker mono" data-r>Our expertise</p><h2 class="h-l" data-r="0.1">Six services, <em>one practice.</em></h2></div>'
            '<div class="stack" data-r="0.2"><p class="p-l">PUD plans cities, regions and destinations, and designs the buildings and landscapes inside them. We have planned new towns, coastal resorts, university campuses, heritage areas and the holy sites of Makkah.</p></div></div>'
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
 ('Curate', 'Then we choose the team: planners, architects, economists and specialists from partner firms.', 'assets/people/giza-decision-framework.jpg'),
 ('Shape', 'We turn what we learn about the land and its history into a plan that keeps the character of the place.', 'assets/stills/azha-ras-al-hekma-egypt.jpg'),
 ('Deliver', 'From the master plan to site supervision, training the client\'s team along the way.', 'assets/stills/jorhum-ksa.jpg'),
]
def approach_section():
    return ('<section class="sec approach"><div class="wrap"><div class="ap-txt"><p class="kicker mono" data-r>Our approach</p>'
            '<p class="ap-lead" data-r="0.1">Every project starts with the site and the people who will use it. Then we choose the team: planners, architects, economists and specialists from partner firms. <a href="about.html#expertise">Explore our expertise</a></p></div>'
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
        rail += '<button type="button" data-i="%d"%s aria-label="Go to %s to %s"><span>%s</span></button>' % (i, ' aria-current="true"' if i == 0 else '', d['yr'], d['to'], d['yr'])
    return ('<section class="decades" id="story" style="--n:%d"><div class="dz-pin">%s<div class="dz-shade"></div>'
            '<div class="wrap dz-head"><p class="kicker mono">Sixty years</p><h2 class="h-l">Six decades, <em>two generations.</em></h2></div>'
            '<div class="dz-year" aria-hidden="true"><span>%s</span></div><div class="wrap dz-panels">%s</div>'
            '<nav class="dz-rail" aria-label="Decades">%s<i class="dz-fill"></i></nav>'
            '<a class="dz-more btn ghost" href="60-years.html">Read the full story</a></div></section>') % (
                len(DECADES), bgs, DECADES[0]['yr'], panels, rail)

FOUNDER_PROSE = [
 'Prof. Dr. Abdallah Attia founded PUD in Cairo in 1966. He trained as an architect in Alexandria and took his doctorate at ETH Zurich.',
 'He led Marina El Alamein from master plan to site supervision, designed Tut Amun on Lake Nasser and Hilton Dahab on the Gulf of Aqaba, and headed the Urban Planning Department at Ain Shams University. Marina El Alamein won the State Encouragement Prize in Architecture in 1990.',
]
AMR_PROSE = [
 'Prof. Dr. Amr Attia leads PUD, the practice his father founded. His master\'s thesis studied his father\'s Marina El Alamein, and his PhD examined tourism policy on Egypt\'s North West Coast. He spent nine years at AECOM Arabia, rising to Principal Director, and three at WATG as Vice President for the Middle East and Africa. In 2018 he co-founded PUD Saudi in Riyadh.',
 'Today PUD advises on the Pyramids Plateau, the holy sites of Makkah, AlUla and the next phases of Egypt\'s New Administrative Capital. He is Professor of Urban Planning at Ain Shams University, an Eisenhower Fellow (2007) and Board Chairman of SHARE Egypt 2026.',
]
def founder_section():
    paras = ''.join('<p class="prose" data-r="0.2">%s</p>' % E(p) for p in FOUNDER_PROSE)
    return ('<section class="sec founder" id="founder"><div class="wrap"><div class="grid2">%s'
            '<div><p class="kicker mono" data-r>The founder · 1966</p><h2 class="h-l" data-r="0.1">Prof. Dr. Abdallah <em>Attia</em></h2>%s'
            '<p class="note">The footage here is an illustrative recreation made for the 60-year celebration. It is not archive film.</p><p style="margin-top:22px"><a class="btn ghost" href="abdallah-attia.html">Read his story</a></p></div></div></div></section>') % (founder_block(), paras)

def leader_section():
    paras = ''.join('<p class="prose" data-r="0.2">%s</p>' % E(p) for p in AMR_PROSE)
    return ('<section class="sec amrcard"><div class="wrap"><div class="grid2 amrg"><div data-r data-px="-0.06">%s</div><div><p class="kicker" data-r>The new chapter</p><h2 class="h-l" data-r="0.1">Prof. Dr. Amr <em>Attia</em></h2>'
            '%s<p style="margin-top:26px" data-r="0.3"><a class="btn red" href="amr-attia.html">Read his profile</a></p></div></div></div></section>') % (amr_photo(), paras)

VALUES = [('Integrity', 'An ethical approach behind every relationship and every decision.'), ('Sustainability', 'Environmental, social and cultural harmony in every project.'),
          ('Innovation', 'Creativity and new tools for future-ready places.'), ('Excellence', 'The highest standards of quality and safety.')]
def culture_section():
    words = 'We don\'t just gather experts. We orchestrate brilliance.'.split(' ')
    q = ' '.join('<span>%s</span>' % E(w) for w in words)
    vals = ''.join('<li><b>%s</b><span>%s</span></li>' % (E(a), E(b)) for a, b in VALUES)
    return ('<section class="sec culture"><div class="wrap"><p class="kicker mono" data-r>Our culture</p><blockquote class="cq"><p>%s</p><footer class="mono">Prof. Dr. Amr Attia, CEO</footer></blockquote>'
            '<p style="margin-top:34px"><a class="btn ghost" href="people.html">Meet our leadership</a></p></div></section>') % q

SUSTAIN = [('People', 'Places designed around people: human-scale streets, shade, walkability and public space.'),
           ('Society', 'Inclusive, affordable and connected neighbourhoods that give every generation a place to belong.'),
           ('Culture', 'Heritage as a living foundation, so new development deepens a place\'s character.'),
           ('Environment', 'Working with nature, not against it: responsible land use and green building standards.'),
           ('Planet', 'Resilient regions for a changing climate, planned for compact, low-carbon growth.')]
def sustain_section():
    IC = {'People': '<circle cx="12" cy="7" r="3.2"/><path d="M5.5 20c.6-3.8 3.2-6 6.5-6s5.9 2.2 6.5 6"/>', 'Society': '<circle cx="7" cy="8.5" r="2.4"/><circle cx="17" cy="8.5" r="2.4"/><circle cx="12" cy="6.5" r="2.6"/><path d="M2.5 19c.4-2.8 2.2-4.4 4.5-4.4M21.5 19c-.4-2.8-2.2-4.4-4.5-4.4M7.2 20c.5-3.4 2.4-5.4 4.8-5.4s4.3 2 4.8 5.4"/>', 'Culture': '<path d="M3 9.5 12 4l9 5.5M4.5 9.5h15M6 9.5v8M10 9.5v8M14 9.5v8M18 9.5v8M3.5 20.5h17M4.5 17.5h15"/>', 'Environment': '<path d="M5 19c0-8 5.5-13.5 15-14-.3 9.5-6 15-14 15"/><path d="M5 19c3-4.5 6.5-7.5 10-9.5"/>', 'Planet': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.4 3.8 5.3 3.8 8.5s-1.2 6.1-3.8 8.5c-2.6-2.4-3.8-5.3-3.8-8.5S9.4 5.9 12 3.5z"/>'}
    items = ''.join('<li><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg><b>%s</b><span class="t">%s</span></li>' % (IC.get(a, ''), E(a), E(b)) for a, b in SUSTAIN)
    return ('<section class="sec sustain2"><div class="wrap"><div class="ap-txt"><p class="kicker mono" data-r><span>Sustainability and responsibility</span></p>'
            '<p class="ap-lead" data-r="0.1">Sustainability at PUD means responsible land use, inclusive neighbourhoods, respect for heritage and green building standards. <a href="sustainability.html">Our commitment</a></p></div>'
            '<a class="ap-img" href="projects/alamein-riviera-vision-master-plan.html" data-r="0.15"><span class="ap-par" data-px="0.08"><img src="assets/story/sustain-alamein-riviera.jpg" alt="Homes around a planted lagoon at dusk, Alamein Riviera" loading="lazy" style="object-position:50%% 65%%"></span><span class="ap-cap mono">Alamein Riviera · North Coast, Egypt</span></a>'
            '<ol class="five2" data-r="0.1">%s</ol></div></section>') % items

def legacy_section():
    return ('<section class="legacy"><div class="big" aria-hidden="true" data-px="0.25">60</div><div class="wrap">'
            '<p class="kicker mono" data-r>1966 to 2026</p><h2 class="h-xl" data-r="0.1">60 years of planning <em>cities and destinations.</em></h2>'
            '<p class="legacy-line" data-r="0.2">Two generations, one practice.</p>'
            '<p class="row" data-r="0.3"><a class="btn red" href="contact.html">Talk to us</a> <a class="btn ghost" href="60-years.html">Read the story</a></p></div></section>')


def home():
    strip = [p for p in PART if has_logo(p)]
    TOP = ['watg', 'aecom', 'rcu', 'pif', 'rcmc', 'nuca', 'saudi-aramco', 'kidana', 'dar-al-handasah', 'gillespies', 'momrah', 'hok']
    top = [pmap[s] for s in TOP if s in pmap and has_logo(pmap[s])][:10]
    tiles = ''.join('<span class="t"><img src="%s" alt="%s logo"%s loading="lazy" decoding="async"></span>' % (p['logo'], E(p['name']), wh(p['logo'])) for i, p in enumerate(top))
    hero_html = ('<section class="hero" id="top"><img class="poster" fetchpriority="high" src="assets/founder/hero.jpg" alt="Prof. Dr. Abdallah Attia drawing a plan, then Marina El Alamein and the Pyramids"><video muted loop playsinline preload="none" poster="assets/founder/hero.jpg" data-src="assets/founder/hero.mp4" data-src-m="assets/founder/hero-m.mp4" aria-hidden="true"></video>'
        '<div class="wrap in"><p class="kicker mono" data-r>1966 to 2026 · 60 years · Cairo · Riyadh · Dubai</p>'
        '<h1 class="h-xl hero-h" data-r="0.1">Planning cities and destinations <em>since 1966.</em></h1>'
        '<p class="lede" data-r="0.2">PUD Consultants plans cities, regions and tourism destinations, and designs the buildings and landscapes inside them. Prof. Dr. Abdallah Attia founded it in Cairo. Prof. Dr. Amr Attia leads it today, from Cairo, Riyadh and Dubai.</p>'
        '<div class="row" data-r="0.3"><a class="btn red" href="projects.html">Explore the work</a><a class="btn ghost" href="projects.html#atlas">Play the 60-year map</a></div>'
        '<div class="stats" data-r="0.4"><div class="stat"><b>1966</b><span class="mono">Founded in Cairo</span></div><div class="stat"><b>+12</b><span class="mono">Countries</span></div>'
        '<div class="stat"><b>+200</b><span class="mono">Global projects</span></div><div class="stat"><b>5</b><span class="mono">Offices in Cairo, Riyadh and Dubai</span></div></div></div>'
        '<p class="cap">Prof. Dr. Abdallah Attia, founder of PUD. Illustrative recreation, not archive footage.</p><i class="scrollcue"></i></section>')
    marq = '<div class="logos-strip" aria-label="Clients and partners"><div class="track" data-dup>%s</div></div>' % tiles if tiles else ''
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
    tl = ('<section class="tl-outer" id="story"><div class="tl-wrap"><div class="wrap tl-head"><p class="kicker mono">Sixty years</p><h2 class="h-l">Six decades, <em>two generations.</em></h2></div>'
          '<div class="tl-track">%s<article class="dec" style="width:min(80vw,380px)"><div class="yr">2026</div><h3>And the next sixty.</h3><p>PUD is still planning new cities, destinations and districts across the region.</p><p style="margin-top:22px"><a class="btn dark" href="60-years.html">Read the full story</a></p></article></div></div></section>') % decs
    facts = ''.join('<li><b>%s</b><span>%s</span></li>' % (a, E(b)) for a, b in sorted(FOUNDER_FACTS))
    founder = ('<section class="sec founder" id="founder"><div class="wrap"><div class="grid2">%s'
        '<div><p class="kicker mono" data-r>The founder · 1966</p><h2 class="h-l" data-r="0.1">Prof. Dr. Abdallah <em>Attia</em></h2><p class="p-l" style="margin-top:20px" data-r="0.2">%s</p>'
        '<ul class="facts" data-r="0.25">%s</ul><p class="note">The footage here is an illustrative recreation made for the 60-year celebration. It is not archive film.</p><p style="margin-top:22px"><a class="btn ghost" href="people.html">Read his story</a></p></div></div></div></section>') % (founder_block(), E(FOUNDER_LEAD), facts)
    feat = [p for p in PROJ if p.get('featured') and thumb(p['slug'])][:6]
    nac = BYSLUG.get('new-administrative-capital-phases-2-4')
    if nac and nac not in feat and thumb(nac['slug']): feat.insert(1, nac)  # Egypt's New Administrative Capital, always in Selected work
    tut = BYSLUG.get('tut-amon-village-hotel-and-resort')
    if tut and tut not in feat and thumb(tut['slug']): feat.insert(3, tut)  # featured in the founder's profile, always in Selected work
    bento = ''.join(card(p, '', tag=p['cat1'], cls='hs-card') for i, p in enumerate(feat))
    featsec = ('<section class="hsx" id="work" aria-label="Selected work"><div class="hsx-pin"><div class="wrap hsx-head"><div><p class="kicker mono">Selected work</p><h2 class="h-l sw-h">From regional visions<br>to city-making<br><em>to the Holy Sites.</em></h2></div>'
               '<div class="hsx-meta"><span class="hsx-n mono"><b>01</b> / %02d</span><a class="btn ghost" href="projects.html">All projects</a></div></div>'
               '<div class="hsx-track">%s</div><div class="wrap"><div class="hsx-bar" aria-hidden="true"><i></i></div></div></div></section>') % (len(feat), bento) if bento else ''
    cn_cards = ''.join('<a href="countries/%s.html"><b>%s</b></a>' % (cslug(c), E(c)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))[:6])
    PIN = '<svg viewBox="0 0 24 32" aria-hidden="true"><path d="M12 1C6 1 1.5 5.6 1.5 11.4 1.5 19 12 31 12 31s10.5-12 10.5-19.6C22.5 5.6 18 1 12 1z"/><circle cx="12" cy="11.5" r="4.2"/></svg>'
    def mpin(x, y, name, side=''):
        return '<span class="mpin2 %s" style="left:%s%%;top:%s%%">%s<b>%s</b></span>' % (side, x, y, PIN, name)
    pins = mpin(33, 6, 'Germany', 'r') + mpin(3, 63, 'The Gambia', 'r')
    teaser = ('<section class="sec mapteaser"><div class="wrap"><div class="grid2 mt-head"><div><p class="kicker mono" data-r>Where we work</p><h2 class="h-l" data-r="0.1">Working in <em>+12 countries.</em></h2></div>'
              '<div><p class="p-l" data-r="0.2">Egypt and Saudi Arabia hold most of our work. We have also worked in Kuwait, Iraq, Syria, the UAE, Qatar, Iran, Cameroon, The Gambia and Germany. Every pin opens a project page. <a href="destinations/red-sea.html">Sustainable tourism planning on the Red Sea</a>.</p><p style="margin-top:24px" data-r="0.3"><a class="btn red" href="projects.html#atlas">Open the map</a></p></div></div>'
              '<a class="mapimg big" href="projects.html#atlas" data-r="0.2"><img src="assets/stills/glowing-pins-across-the-middle-east.jpg" alt="Map of the Middle East with PUD project locations" loading="lazy">%s</a></div></section>') % pins
    def lrow(L): return ''.join('<span class="lg"><img src="%s" alt="%s"%s loading="lazy" decoding="async"></span>' % (p['logo'], E(p['name']), wh(p['logo'])) for p in L)
    cl = [p for p in strip if p.get('type') == 'client']; pt = [p for p in strip if p.get('type') != 'client']
    pl = ('<div class="lrow"><p class="mono lt">Our trusted clients</p><div class="lmq"><div class="ltr" data-dup>%s</div></div></div>'
          '<div class="lrow rev"><p class="mono lt">Partners &amp; collaborations</p><div class="lmq"><div class="ltr" data-dup>%s</div></div></div>') % (lrow(cl), lrow(pt))
    partners = ('<section class="sec partners-dk"><div class="wrap"><p class="kicker mono" data-r>Clients &amp; partners</p><h2 class="h-l" data-r="0.1">Trusted by clients. <em>Built with partners.</em></h2><p class="p-l" style="margin-top:18px;max-width:58ch" data-r="0.15">100+ clients and 90+ collaborations across six decades, from ministries and royal commissions to the world\'s leading design firms.</p><div class="logos2" data-r="0.2">%s</div><p style="margin-top:28px"><a class="btn ghost" href="partners.html">All clients and partners</a></p></div></section>') % pl if pl else ''
    fq = '<section class="sec"><div class="wrap">%s<p style="margin-top:24px"><a class="btn ghost" href="faq.html">More questions</a></p></div></section>' % faq_html(FAQ[:5])
    amr_card = ('<section class="sec amrcard"><div class="wrap"><div class="grid2 amrg"><div data-r>%s</div><div><p class="kicker" data-r>The new chapter</p><h2 class="h-l" data-r="0.1">Prof. Dr. Amr Attia</h2><p class="p-l" style="margin-top:18px" data-r="0.2">%s</p>%s'
        '<p style="margin-top:8px" data-r="0.3"><a class="btn red" href="amr-attia.html">Read his profile</a></p></div></div>'
        '<h3 class="h-m" style="margin-top:56px" data-r>Selected work</h3><div class="pgrid amrwork" data-r="0.1">%s</div></div></section>') % (amr_photo(), E(AMR_HEADLINE), stat_tiles(AMR_TILES), amr_work('', 3))
    film = ''
    body = hero_html + marq + featsec + services_immersive() + depth_story() + approach_section() + decades_section() + founder_section() + leader_section() + teaser + sustain_section() + partners + legacy_section()  + film
    return page('index.html', 'PUD Consultants | Urban Planning and Master Planning since 1966', body,
                'PUD Consultants plans cities, destinations and campuses. Founded in Cairo in 1966, with work across the region. Offices in Cairo, Riyadh and Dubai.', 'index.html',
                schema=[dict(ORG, **{'@context': 'https://schema.org'}), WEB], head_extra='<link rel="preload" as="image" href="assets/founder/hero.jpg" fetchpriority="high">')

def story():
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">1966 to 2026</p><h1 class="h-xl" style="max-width:16ch">Two generations, six decades, <em>one practice.</em></h1><p class="lede">PUD has planned from Cairo since 1966. <a href="abdallah-attia.html">Prof. Dr. Abdallah Attia</a> founded it; <a href="amr-attia.html">Prof. Dr. Amr Attia</a> leads it today.</p></div></section>'
    for d in DECADES:
        th = ''.join(card(p, '') for p in decade_projects(d, 4))
        beats = ''.join('<li><b>%s</b>%s</li>' % (a, E(b)) for a, b in d['beats'])
        body += ('<section class="sec paper" style="padding:80px 0"><div class="wrap"><div class="grid2" style="align-items:start"><div><div class="mono dec-range">%s to %s</div><h2 class="h-l" style="margin:10px 0 18px">%s</h2><p class="p-l">%s</p><div class="dec" style="width:auto;border:0;padding:0"><ul>%s</ul></div></div>'
                 '<div class="pgrid" style="grid-template-columns:1fr 1fr;margin-top:0">%s</div></div></div></section>') % (d['yr'], d['to'], E(d['title']), E(d['text']), beats, th)
    body += '<section class="sec"><div class="wrap" style="text-align:center"><p class="note" style="max-width:60ch;margin:0 auto">Dates come from PUD\'s project records and public sources. Where a project spans several years, the range is shown.</p></div></section>' + chapter(1)
    return page('60-years.html', 'PUD Consultants at 60: Urban Planning History, 1966 to 2026', body, 'Follow PUD from its first commissions in Cairo in 1966 and the North Coast of Egypt to AlUla, Makkah and the Pyramids Plateau today.', '60-years.html',
                schema=[crumbs([('Home', ''), ('60 years', '60-years.html')])])

def people():
    f = ''.join('<li><b>%s</b><span>%s</span></li>' % (a, E(b)) for a, b in sorted(FOUNDER_FACTS))
    loved = ''.join(card(BYSLUG[s], '', tag=lab.split(',')[0]) for s, lab in FOUNDER_LOVED if s in BYSLUG)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker">Leadership</p><h1 class="h-xl" style="max-width:16ch">Two generations <em>lead PUD.</em></h1><p class="lede"><a href="abdallah-attia.html">Prof. Dr. Abdallah Attia</a> founded the practice in 1966. <a href="amr-attia.html">Prof. Dr. Amr Attia</a> leads it today. <a href="partners.html#team">Meet the key staff</a></p></div></section>'
        '<section class="sec founder" id="abdallah-attia" style="padding-top:70px"><div class="wrap"><div class="grid2" style="align-items:start">%s'
        '<div><p class="kicker">The founder</p><h2 class="h-l">Prof. Dr. Abdallah Attia</h2><p class="p-l" style="margin-top:16px;color:#fff">%s</p><p class="p-l" style="margin-top:14px">%s</p><ul class="facts">%s</ul>'
        '<p class="note">Footage is an illustrative recreation made for the 60-year celebration, not archive film.</p><p style="margin-top:22px"><a class="btn ghost" href="abdallah-attia.html">Read his page</a></p></div></div>'
        '<h2 class="h-m" style="margin-top:70px">Three projects the practice singles out</h2><p class="p-l" style="margin-top:10px">%s</p><div class="loved">%s</div></div></section>'
        '<section class="sec paper" id="amr-attia"><div class="wrap grid2 amrg"><div>%s</div><div><p class="kicker">Leadership</p><h2 class="h-l">Prof. Dr. Amr Attia</h2><p class="p-l" style="margin-top:16px">%s</p>%s<p style="margin-top:6px"><a class="btn dark" href="amr-attia.html">Read his full profile</a></p></div></div></section>') % (
        founder_block(), E(FOUNDER_LEAD), E(FOUNDER_BIO), f, E(FOUNDER_LOVED_NOTE), loved, amr_photo('', 'light'), E(AMR_HEADLINE), stat_tiles(AMR_TILES)) + chapter(2)
    vals = '<section class="sec culture" style="padding-top:10px;padding-bottom:30px"><div class="wrap"><p class="trio mono" style="margin-top:0">Leadership · Harmony · Clarity</p><ul class="vals">%s</ul></div></section>' % ''.join('<li><b>%s</b><span>%s</span></li>' % (E(a_), E(b_)) for a_, b_ in VALUES)
    body = body.replace('</section>', '</section>' + vals, 1)
    pers = [{'@context': 'https://schema.org', '@type': 'ProfilePage', 'url': BASE + '/people.html', 'name': 'Leadership of PUD Consultants', 'hasPart': [{'@id': BASE + '/abdallah-attia.html#person'}, {'@id': BASE + '/amr-attia.html#amr-attia'}]}]
    return page('people.html', 'Leadership: Prof. Dr. Abdallah Attia and Prof. Dr. Amr Attia | PUD', body, 'Meet Prof. Dr. Abdallah Attia, who founded PUD in Cairo in 1966, and Prof. Dr. Amr Attia, his son, who leads the practice today.', 'people.html',
                schema=pers + [crumbs([('Home', ''), ('Leadership', 'people.html')])])



def founder_page():
    # SE-005: the founder gets his own page and the Person entity
    f = ''.join('<li><b>%s</b><span>%s</span></li>' % (a, E(b_)) for a, b_ in sorted(FOUNDER_FACTS))
    loved = ''.join(card(BYSLUG[s], '', tag=lab.split(',')[0]) for s, lab in FOUNDER_LOVED if s in BYSLUG)
    body = ('<section class="page-h"><div class="wrap"><p class="crumb"><a href="people.html">Leadership</a></p><p class="kicker">Founder, 1966</p><h1 class="h-xl">Prof. Dr. Abdallah Attia</h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '<section class="sec founder" style="padding-top:30px"><div class="wrap"><div class="grid2" style="align-items:start">%s<div><p class="p-l">%s</p>'
            '<details class="more" open><summary>Education and posts</summary><ul class="facts">%s</ul></details>'
            '<p class="note">The footage is an illustrative recreation made for the 60-year celebration. It is not archive film.</p></div></div>'
            '<h2 class="h-m" style="margin-top:70px">Featured in his profile</h2><p class="p-l" style="margin-top:10px">%s</p><div class="loved">%s</div>'
            '<p class="c-next"><a class="btn ghost" href="60-years.html">The 60-year story</a><a class="btn ghost" href="amr-attia.html">Prof. Dr. Amr Attia</a><a class="btn ghost" href="projects.html">All projects</a></p></div></section>') % (
        E(FOUNDER_LEAD), founder_block(), E(FOUNDER_BIO), f, E(FOUNDER_LOVED_NOTE), loved) + chapter(2)
    pers = {'@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/abdallah-attia.html#person', 'name': 'Abdallah Attia', 'honorificPrefix': 'Prof. Dr.',
            'alternateName': ['Abdallah Abdel Aziz Attia', 'Abdalla Abdel Aziz Attia', 'Abdalla Abdelaziz Attia'], 'url': BASE + '/abdallah-attia.html', 'image': BASE + '/assets/founder/draw.jpg',
            'description': 'Architect and professor who founded PUD Consultants in Cairo in 1966.', 'jobTitle': 'Professor of Architecture; founder of PUD Consultants',
            'alumniOf': [{'@type': 'CollegeOrUniversity', 'name': 'Alexandria University'}, {'@type': 'CollegeOrUniversity', 'name': 'ETH Zurich'}],
            'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Ain Shams University'}, 'founder': {'@id': BASE + '/#org'}, 'worksFor': {'@id': BASE + '/#org'},
            'award': 'State Encouragement Prize in Architecture (1990), for Marina El Alamein'}
    return page('abdallah-attia.html', 'Prof. Dr. Abdallah Attia | Founder of PUD Consultants', body,
                'Prof. Dr. Abdallah Attia, architect and professor, founded PUD Consultants in Cairo in 1966. Marina El Alamein, Tut Amun and Hilton Dahab are among his best-known work.', 'people.html',
                schema=[pers, crumbs([('Home', ''), ('Leadership', 'people.html'), ('Abdallah Attia', 'abdallah-attia.html')])], og_img='assets/founder/draw.jpg', og_type='profile', og_alt='Prof. Dr. Abdallah Attia at work, illustrative recreation')

def amr_photo(R='', cls=''):
    pri = ' fetchpriority="high"' if cls == 'lead' else ' loading="lazy"'  # PA-021: the portrait is the LCP image on his page
    return '<figure class="amrphoto %s"><img src="%sassets/people/amr-attia.jpg" alt="Prof. Dr. Amr Attia, CEO and Principal of PUD Consultants" width="800" height="800"%s><figcaption><b>Prof. Dr. Amr Attia</b><span>CEO and Principal, PUD Consultants</span></figcaption></figure>' % (cls, R, pri)
def amr_work(R='', n=4):
    ps = [BYSLUG[s] for s in AMR_WORK if s in BYSLUG][:n]
    return ''.join(card(p, R, tag=p['cat1']) for p in ps)
def stat_tiles(L):
    return '<div class="tiles">%s</div>' % ''.join('<div><b>%s</b><span>%s</span></div>' % (E(a), E(c)) for a, c in L)

def amr_page():
    A = AMR
    def src(s):
        m = re.search(r'https?://[^\s;,)\]]+', str(s or ''))
        if m and 'pudconsultants.com' in m.group(0): m = None
        if m and 'uia2023cph.org' in m.group(0): m = None  # UX-011: dead page
        if not m: return ''
        dom = re.sub(r'^www\.', '', re.match(r'https?://([^/]+)', m.group(0)).group(1))
        return ' <a class="srcl" href="%s" target="_blank" rel="noopener" aria-label="Source: %s (opens in a new tab)">%s</a>' % (E(m.group(0)), E(dom), E(dom))
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
    body = ('<section class="page-h" id="amr-attia"><div class="wrap grid2 amrg"><div><p class="crumb"><a href="people.html">Leadership</a></p><p class="kicker">Leadership</p><h1 class="h-xl" style="max-width:15ch">Prof. Dr. Amr Attia</h1><p class="lede" style="max-width:34ch">%s</p></div><div>%s</div></div></section>'
            '<section class="sec" style="padding-top:20px"><div class="wrap"><nav class="jump" aria-label="On this page"><a class="chip" href="#selected-work">Selected work</a><a class="chip" href="#on-stage">On stage</a><a class="chip" href="#recognition">Recognition</a><a class="chip" href="#research">Research and teaching</a></nav>%s<div class="narrow2">%s</div>'
            '<h2 class="h-m" id="selected-work" style="margin-top:70px">Selected work</h2><div class="pgrid">%s</div>'
            '<h2 class="h-m" id="roles" style="margin-top:70px">Roles and projects</h2><ul class="facts wide">%s</ul>'
            '<h2 class="h-m" id="on-stage" style="margin-top:70px">On stage</h2><div class="annc">%s</div><ul class="facts wide" style="margin-top:26px">%s</ul>'
            '<h2 class="h-m" id="recognition" style="margin-top:70px">Recognition</h2><ul class="facts wide">%s</ul>'
            '<h2 class="h-m" id="giza" style="margin-top:70px">The Giza Pyramids master plan</h2><div class="gfig">%s</div>'
            '<h2 class="h-m" id="research" style="margin-top:70px">Research and teaching</h2><ul class="facts wide">%s</ul>'
            '<details class="more"><summary>Full career and education</summary><ul class="facts wide">%s</ul></details>'
            '<details class="more"><summary>In the media</summary><ul class="facts wide">%s</ul></details>'
            '</div></section>') % (E(AMR_HEADLINE), amr_photo('', 'lead'), stat_tiles(AMR_TILES), paras, amr_work('', 6), leadrows, spot, stage, recog, giza, research, career, media) + cta('') + chapter(2)
    pers = {'@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/amr-attia.html#amr-attia', 'name': 'Amr Attia', 'honorificPrefix': 'Prof. Dr.', 'alternateName': 'Amr A. Attia', 'jobTitle': 'CEO and Principal, PUD Consultants; Professor of Urban Planning, Ain Shams University', 'worksFor': {'@id': BASE + '/#org'}, 'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Ain Shams University'}, 'url': BASE + '/amr-attia.html', 'image': BASE + '/assets/people/amr-attia.jpg',
            'alumniOf': {'@type': 'CollegeOrUniversity', 'name': 'University College London'}, 'sameAs': ['https://www.linkedin.com/in/amr-attia-9181898/', 'https://share-architects.com/speaker/amr-attia/', 'https://eng.asu.edu.eg/staff/Amr.Attia']}
    return page('amr-attia.html', 'Prof. Dr. Amr Attia | Urban Planner, PUD Consultants', body, 'Prof. Dr. Amr Attia leads PUD Consultants and teaches urban planning at Ain Shams University. Eisenhower Fellow. Board Chairman of SHARE Egypt 2026.', 'people.html', schema=[pers, crumbs([('Home', ''), ('Leadership', 'people.html'), ('Amr Attia', 'amr-attia.html')])], og_img='assets/people/amr-attia.jpg', og_type='profile', og_alt='Prof. Dr. Amr Attia')

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
                 featured=bool(p.get('featured')), thumb=thumb(p['slug']) or '', url='projects/%s.html' % p['slug'], svc=svc_of(p), approx=bool(p.get('coords_approx')) or sum(1 for q in PROJ if q.get('lat') == p.get('lat') and q.get('lon') == p.get('lon')) > 1) for p in PROJ]
    order = sorted(range(len(PROJ)), key=lambda i: (not PROJ[i].get('featured'), not thumb(PROJ[i]['slug']), -(PROJ[i].get('year_start') or 0)))
    grid = ''.join(card(PROJ[i], '', i=i) for i in order)
    ccs = ''.join('<a href="countries/%s.html"><b>%s</b><span>%d projects</span></a>' % (cslug(c), E(c), len(ps)) for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1])))
    cities = ''.join('<a class="chip" href="cities/%s.html">%s <small>%d</small></a>' % (d['slug'], E(d['name']), len(d['projects'])) for d in sorted(PLACES.values(), key=lambda d: d['name']))
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Projects</p><h1 class="h-xl" style="max-width:17ch">From regional visions <em>to the Holy Sites.</em></h1><p class="lede atlas-hint">Press play to watch the practice grow from Cairo across the region. Drag to turn the map and click a pin to open a project.</p></div></section>'
        '<section class="sec atlas" id="atlas" style="padding-top:30px"><div class="wrap"><a class="skip-map btn ghost" href="#expertise">Skip the map, go to the project list</a><p id="atlasDesc" hidden>Map of %d projects across Egypt, Saudi Arabia and the region. The full list of projects follows below the map.</p><div class="box" data-geo="data/countries.geojson"><canvas role="img" aria-label="Map of PUD projects" aria-describedby="atlasDesc"></canvas><div class="tip"></div><div class="story" aria-live="polite"><span class="mono"></span><b></b></div><div class="now"></div>'
        '<div class="side"><button class="chip" data-view="all">Region</button><button class="chip" data-view="egypt">Egypt</button><button class="chip" data-view="ksa">Saudi Arabia</button><button class="chip" data-view="makkah">Makkah</button><span style="display:flex;gap:6px"><button class="chip" data-view="in" aria-label="Zoom in">+</button><button class="chip" data-view="out" aria-label="Zoom out">&minus;</button></span></div>'
        '<div class="hud"><div class="yrbox"><div class="yr">2026</div><div class="n mono"></div></div><input type="range" min="1964" max="2026" value="2026" aria-label="Year"><button class="btn red play">Play the story</button><button class="chip speed">Speed 1x</button><button class="chip skip26" type="button">Skip to 2026</button><div class="legend"><span>1964</span><i></i><span>2026</span></div></div></div>'
        '<div class="cardsel"><img alt=""><div><h3 class="h-m"></h3><p class="note" style="font-size:14px"></p></div><a class="btn ghost">Open project</a></div>'
        + expertise_filters() +
        '<div class="pgrid">%s</div>'
        '</div></section>') % (len(PROJ), grid) + chapter(3)
    return page('projects.html', 'Urban Planning Projects in Egypt, Saudi Arabia and Beyond | PUD', body,
                'Explore %d PUD projects on an interactive map: urban plans, master plans, destinations and buildings in Egypt, Saudi Arabia and the wider region.' % len(PROJ), 'projects.html',
                schema=[crumbs([('Home', ''), ('Projects', 'projects.html')]), {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD Consultants projects', 'numberOfItems': len(PROJ), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/projects/' + PROJ[j]['slug'] + '.html', 'name': PROJ[j]['name']} for i, j in enumerate(order[:60])]}], data=data, ms=MILESTONES)

def partners_page():
    def sect(t, typ):
        L = [p for p in PART if p.get('type') == typ and has_logo(p)]
        nm = lambda p: re.sub(r'\s*\(.*\)$', '', p['name'])  # LG-021: a visible name under every logo
        items = ''.join(('<a href="%s" target="_blank" rel="noopener" aria-label="%s (opens in a new tab)"><img src="%s" alt="%s logo" loading="lazy"%s><span class="nm">%s</span></a>' % (E(p['url']), E(p['name']), p['logo'], E(p['name']), wh(p['logo']), E(nm(p)))) if p.get('url') else ('<div><img src="%s" alt="%s logo" loading="lazy"%s><span class="nm">%s</span></div>' % (p['logo'], E(p['name']), wh(p['logo']), E(nm(p)))) for p in sorted(L, key=lambda p: p['name']))
        names = sorted(p['name'] for p in PART if p.get('type') == typ and not has_logo(p) and not re.match(r'(Dr\.?|Eng\.?|Arch\.?|Prof\.?|Fawaz)\b', p['name']))
        more = ('<p class="note" style="color:var(--mute-d);margin-top:18px"><b>Also worked with:</b> %s.</p>' % E(', '.join(names))) if names else ''
        return '<h2 class="h-m" style="margin-top:50px">%s</h2><div class="pl">%s</div>%s' % (t, items, more)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Partners and clients</p><h1 class="h-xl" style="max-width:15ch">Trusted by clients. <em>Built with partners.</em></h1><p class="lede">National authorities, royal commissions, developers and universities commission our work. International firms such as WATG and AECOM plan alongside us, with strategic partners and specialists.</p></div></section>' + network_sections() +
            ('<section class="sec paper" id="clients" style="padding-top:60px"><div class="wrap"><p class="kicker mono">Clients and partner firms</p><h2 class="h-l">100+ clients. <em>90+ collaborations.</em></h2>%s%s</div></section>') % (sect('Partners', 'partner'), sect('Clients', 'client') + '<p class="lgcredit">Cairo University logo: Wikimedia Commons, CC BY 4.0. Dar Al-Handasah logo: Wikimedia Commons, CC BY-SA 4.0.</p>')) + chapter(5)
    return page('partners.html', 'Partners, Experts and Clients: WATG, AECOM, AlUla | PUD', body, 'PUD Consultants\' key staff, strategic partners and international expert network, and the clients and firms it plans with: WATG, AECOM, NUCA, the Royal Commission for AlUla and more.', 'partners.html',
                schema=[network_schema(), crumbs([('Home', ''), ('Partners', 'partners.html')])])

PUD_EMAIL = 'info@pudconsultants.com'
def map_block(R='', cap='Where we have worked'):
    # UX-006: the project map is captioned as such and opens the 60-year atlas (it is not an office map)
    return ('<a class="mapimg big" href="%sprojects.html#atlas" data-r="0.2"><img src="%sassets/stills/glowing-pins-across-the-middle-east.jpg" alt="Map of the Middle East with PUD project locations" loading="lazy"></a><p class="note" style="margin-top:12px">%s. <a href="%sprojects.html#atlas">Open the 60-year map</a></p>'
            % (R, R, E(cap), R))

def maps_url(addr): return 'https://www.google.com/maps/search/?api=1&query=' + re.sub(r'\s+', '+', re.sub(r'[^A-Za-z0-9 ,]', '', addr)).replace(',', '%2C')
def contact_page():
    off = ''.join('<div><h2 class="h-m">%s</h2><p class="p-l" style="margin-top:10px">%s</p><p class="p-l"><a class="btn red call" href="tel:%s">Call %s</a><a class="maps" href="%s" target="_blank" rel="noopener">Open in Maps</a></p></div>' % (E(a), E(b), re.sub(r'[^+0-9]', '', c), E(c), E(maps_url(b))) for a, b, c in OFFICES)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Contact</p><h1 class="h-xl">Talk to PUD about your site.</h1>'
            '<p class="lede">Write to us or call the office closest to your project. We usually reply within 48 hours.</p>'
            '<div class="c-mail"><a class="btn red" href="#" data-write>Write to us</a><a class="btn ghost" href="mailto:%s">%s</a></div></div></section>'
            '<section class="sec" style="padding-top:50px"><div class="wrap"><div class="offices">%s</div>'
            '<h2 class="h-m" style="margin-top:70px">Careers and CVs</h2><p class="p-l" style="margin-top:12px">Send your CV and a short note to <a href="mailto:%s?subject=Careers">%s</a>, or <a href="#" data-write data-topic="Careers">use the form</a> and choose Careers.</p>'
            '<h2 class="h-m" style="margin-top:50px">Press and speaking</h2><p class="p-l" style="margin-top:12px">For interviews and speaking requests, write to <a href="mailto:%s?subject=Media">%s</a>.</p>'
            '<div style="margin-top:clamp(50px,6vw,80px)">%s</div>'
            '<p class="c-next"><a class="btn ghost" href="projects.html">See our projects</a><a class="btn ghost" href="faq.html">Questions people ask</a><a class="btn ghost" href="./">Home</a></p></div></section>') % (
        PUD_EMAIL, PUD_EMAIL, off, PUD_EMAIL, PUD_EMAIL, PUD_EMAIL, PUD_EMAIL, map_block()) + chapter(6)
    return page('contact.html', 'Contact PUD Consultants | Offices in Cairo, Riyadh and Dubai', body, 'Write to PUD at %s or call Cairo +20 2 2414 7537, Riyadh +966 540 39 8178 or Dubai +971 509 29 8178.' % PUD_EMAIL, 'contact.html',
                schema=[crumbs([('Home', ''), ('Contact', 'contact.html')])] + office_nodes())

def office_nodes():
    # SE-013: each office as its own local entity, linked to the organisation (coordinates added once PUD confirms them)
    out = []
    for loc in ORG['location']:
        sl = slugify(loc['name'].replace('PUD ', ''))
        out.append({'@context': 'https://schema.org', '@type': 'ProfessionalService', '@id': BASE + '/contact.html#' + sl, 'name': loc['name'].replace('PUD ', 'PUD Consultants, '),
                    'parentOrganization': {'@id': BASE + '/#org'}, 'address': loc['address'], 'telephone': loc['telephone'], 'email': PUD_EMAIL, 'url': BASE + '/contact.html', 'image': BASE + '/assets/icon-512.png'})
    return out

RED_SEA = ['port-ghalib-master-plan', 'abo-dabbab-marine-field-station', 'green-star-hotels-initiative', 'yuwdda-sub-regional-plan', 'ain-el-sokhna-tourist-center', 'hurghada-apartments-hotel-and-shopping-mall', 'pyramisa-apartment-hotel-hurghada', 'castle-zaman-hotel-red-sea']
def red_sea_page():
    R = '../'; ps = [BYSLUG[s] for s in RED_SEA if s in BYSLUG]
    qa = [('Does PUD plan Red Sea destinations?', 'Yes. PUD has worked on Port Ghalib and the Abo Dabbab marine field station at Marsa Alam, Hurghada, Ain El Sokhna and the Red Sea sub-regional plan for Yanbu, Umluj, Al Wajh and Duba in Saudi Arabia, and on the Green Star Hotels initiative with GIZ.')]
    body = ('<section class="page-h"><div class="wrap"><p class="crumb"><a href="../services/master-planning-and-urban-design.html">Urban design and master planning</a></p><h1 class="h-xl" style="max-width:18ch">Planning Red Sea destinations.</h1><p class="lede" style="max-width:56ch">PUD Consultants has planned Red Sea destinations in Egypt and Saudi Arabia: Port Ghalib and Abo Dabbab at Marsa Alam, Hurghada, Ain El Sokhna, the Green Star Hotels initiative and the sub-regional plan for Yanbu, Umluj, Al Wajh and Duba.</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="pgrid">%s</div>%s</div></section>') % (''.join(card(p, R) for p in ps), faq_html(qa)) + cta(R)
    return page('destinations/red-sea.html', 'Sustainable Tourism Planning on the Red Sea | PUD Consultants', body, 'Red Sea destination planning by PUD Consultants: Port Ghalib, Abo Dabbab, Hurghada, Ain El Sokhna and the Yanbu to Duba sub-regional plan.', 'about.html',
                schema=[crumbs([('Home', ''), ('About', 'about.html'), ('Red Sea destinations', 'destinations/red-sea.html')])], og_img=hero_img(ps[0]['slug']) if ps else None)

def not_found_page():
    # UX-014 / UI-003 / PA-010: built from the same template as every other page
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Page not found</p><h1 class="h-xl">This page has moved or never existed.</h1>'
            '<p class="lede" style="max-width:46ch">Try one of these instead, or write to us at <a href="mailto:%s">%s</a>.</p>'
            '<p style="margin-top:28px;display:flex;gap:14px;flex-wrap:wrap"><a class="btn red" href="./">Home</a><a class="btn ghost" href="projects.html">Projects</a><a class="btn ghost" href="projects.html#atlas">The 60-year map</a><a class="btn ghost" href="about.html">About</a><a class="btn ghost" href="contact.html">Contact</a></p></div></section>') % (PUD_EMAIL, PUD_EMAIL)
    h = page('404.html', 'Page not found | PUD Consultants', body, 'This page could not be found. Go to the PUD Consultants home page, projects or contact page.', '', noindex=True)
    h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8"><base href="/">', 1)
    h = re.sub(r'<link rel="(canonical|alternate)"[^>]*>', '', h)
    if '<meta name="robots"' not in h: h = h.replace('<title>', '<meta name="robots" content="noindex,follow"><title>', 1)
    return h

def simple_page(path, kicker, h1, lede, inner, title, desc, schema_extra=None):
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">%s</p><h1 class="h-xl">%s</h1>%s</div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap narrow">%s</div></section>') % (E(kicker), h1, ('<p class="lede" style="max-width:56ch">%s</p>' % lede) if lede else '', inner)
    return page(path, title, body, desc, '', schema=[crumbs([('Home', ''), (kicker, path)])] + (schema_extra or []))

NEWS = [  # G11: dated items, each with its public source
 ('13 and 14 December 2026', 'SHARE Egypt 2026 at the Grand Egyptian Museum', 'Prof. Dr. Amr Attia is Board Chairman of SHARE Egypt, the first SHARE forum in Africa, held at the Grand Egyptian Museum in Giza.', 'https://shareegypt2026forum.sched.com', 'amr-attia.html#on-stage'),
 ('24 and 25 November 2026', 'SHARE Kazakhstan 2026, Almaty', 'Prof. Dr. Amr Attia was a panellist in the Master Debate on high-rise buildings in Almaty on 24 November and spoke on Day 2 on 25 November.', 'https://sharekazakshtan2026forum.sched.com/speaker/amr.attia', 'amr-attia.html#on-stage'),
 ('September 2026', 'SHARE Georgia 2026, Tbilisi', 'Prof. Dr. Amr Attia spoke at SHARE Georgia in Tbilisi.', None, 'amr-attia.html#on-stage'),
 ('2026', 'Sixty years of PUD', 'PUD Consultants marks sixty years since Prof. Dr. Abdallah Attia founded the practice in Cairo in 1966.', None, '60-years.html'),
 ('2025', 'Jabal Thabeer park recognised', 'The Jabal Thabeer hillside park at Mina, Makkah, was first runner-up in Future Landscapes (Unbuilt) at the Landscape Middle East Awards.', None, 'projects/jabal-thabeer-park.html'),
]
def news_page():
    items = ''.join('<li><b>%s</b><span><strong>%s</strong>. %s %s<a href="%s">Read more</a></span></li>' % (E(d), E(t), E(x), ('<a class="srcl" href="%s" target="_blank" rel="noopener">Programme</a> · ' % E(u)) if u else '', l) for d, t, x, u, l in NEWS)
    return simple_page('news.html', 'News and events', 'News and events.', 'Where PUD and its people are speaking, and what has changed in the practice.', '<ul class="facts wide">%s</ul>' % items,
                       'News and Events | PUD Consultants', 'News and events from PUD Consultants: SHARE Egypt 2026 at the Grand Egyptian Museum, SHARE Kazakhstan in Almaty, sixty years of the practice and recent recognition.')

AWARDS = [  # G05: only items the site can show; PUD to add years and issuers for the rest
 ('1990', 'State Encouragement Prize in Architecture', 'Marina El Alamein', 'marina-el-alamein'),
 ('2025', 'First runner-up, Future Landscapes (Unbuilt), Landscape Middle East Awards', 'Jabal Thabeer park, Mina, Makkah', 'jabal-thabeer-park'),
 ('', 'First prize, design competition (joint entry)', 'Nasser Memorial Civic Centre', 'nasser-memorial-civic-center'),
 ('', 'First prize, planning competition (joint entry)', 'Planning of Luxor City and its Region', 'luxor-city-and-region-planning'),
 ('', 'First prize, competition', 'Al-Ashish Urbanized Communities, Kuwait', 'al-ashish-urbanized-communities-kuwait'),
 ('', 'First prize, competition', 'Tut Amun Village Hotel, Aswan', 'tut-amon-village-hotel-and-resort'),
]
def awards_page():
    items = ''.join('<li><b>%s</b><span>%s: <a href="projects/%s.html">%s</a></span></li>' % (E(y or 'Prize'), E(a), s, E(n)) for y, a, n, s in AWARDS if s in BYSLUG)
    return simple_page('awards.html', 'Awards', 'Awards and recognition.', 'More than 20 first and second prizes in design and planning competitions in Egypt, Kuwait and Saudi Arabia. Selected prizes, each linked to its project.',
                       '<ul class="facts wide">%s</ul>' % items, 'Awards and Recognition | PUD Consultants', 'Awards won by PUD Consultants: the State Encouragement Prize in Architecture for Marina El Alamein, competition first prizes in Egypt and Kuwait, and the 2025 Landscape Middle East Awards.')

def clients_page():
    # G14: clients grouped by sector, each with the project pages that name it
    groups = [('Royal commissions', lambda n: 'Royal Commission' in n), ('Ministries and government authorities', lambda n: re.search(r'Ministry|Authority|Governorate|Municipality|NUCA|GOPP|ACUD|Organization|Forces|MOMRAH|MAETUR|Interior', n)),
              ('Universities', lambda n: 'University' in n), ('International organisations', lambda n: re.search(r'World Bank|GIZ|League', n)), ('Developers and companies', lambda n: True)]
    out, used = '', set()
    for g, test in groups:
        rows = ''
        for p in sorted([x for x in PART if x.get('type') == 'client' and x['slug'] not in used and x['slug'] != 'fawaz-alhokair'], key=lambda x: x['name']):
            if not test(p['name']): continue
            ps = [q for q in PROJ if p in client_logos(q.get('client')) or p in client_logos(q.get('client'), funders=True)] if has_logo(p) else [q for q in PROJ if re.sub(r'\s*\(.*\)$', '', p['name']).lower() in (q.get('client') or '').lower()]
            if not ps: continue
            used.add(p['slug'])
            rows += '<li><b>%s</b><span>%s</span></li>' % (E(re.sub(r'\s*\(.*\)$', '', p['name'])), ', '.join('<a href="projects/%s.html">%s</a>' % (q['slug'], E(q['name'])) for q in ps[:6]) + (' and %d more' % (len(ps) - 6) if len(ps) > 6 else ''))
        if rows: out += '<h2 class="h-m" style="margin-top:50px">%s</h2><ul class="facts wide">%s</ul>' % (E(g), rows)
    return simple_page('clients.html', 'Clients', 'Who we plan for.', 'National authorities, royal commissions, developers, universities and international organisations, with the projects we did for each.', out + '<p style="margin-top:40px"><a class="btn ghost" href="partners.html">Partners and experts</a></p>',
                       'Clients of PUD Consultants', 'The clients PUD Consultants plans and designs for: royal commissions, ministries, developers, universities and international organisations, with links to each project.')

def privacy_page():
    inner = ('<p class="p-l">This page explains what happens to the details you send PUD Consultants through this website.</p>'
             '<h2 class="h-m" style="margin-top:40px">What we collect</h2><p class="p-l" style="margin-top:12px">The enquiry form asks for your name, email address, an optional phone number, a topic and your message. Nothing else is collected. The site sets no cookies and uses no analytics or advertising trackers.</p>'
             '<h2 class="h-m" style="margin-top:40px">How it is sent</h2><p class="p-l" style="margin-top:12px">The form passes your message to the PUD team by email, through FormSubmit, an email relay service. You can also write to info@pudconsultants.com directly.</p>'
             '<h2 class="h-m" style="margin-top:40px">How we use it</h2><p class="p-l" style="margin-top:12px">We use your details only to reply to your enquiry and to follow up on it. We do not sell them, share them for marketing or add you to a mailing list.</p>'
             '<h2 class="h-m" style="margin-top:40px">Your choices</h2><p class="p-l" style="margin-top:12px">To see, correct or delete what you sent us, write to <a href="mailto:info@pudconsultants.com?subject=Privacy">info@pudconsultants.com</a>.</p>')
    return simple_page('privacy.html', 'Privacy', 'Privacy.', None, inner, 'Privacy | PUD Consultants', 'How PUD Consultants handles the details you send through its website: what the enquiry form collects, how it is sent and how it is used.')

def accessibility_page():
    inner = ('<p class="p-l">We want everyone to be able to use this website. We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA.</p>'
             '<h2 class="h-m" style="margin-top:40px">What we have done</h2><ul class="ticks"><li>Text and buttons meet colour contrast targets.</li><li>Every page can be used with a keyboard, with a skip link and visible focus.</li><li>Moving video and logo strips can be paused, and motion stops when your device asks for reduced motion.</li><li>Every project on the map is also in a plain list below it.</li></ul>'
             '<h2 class="h-m" style="margin-top:40px">Known limits</h2><p class="p-l" style="margin-top:12px">The interactive 60-year map is a 3D graphic. Use the project list under the map, which holds the same projects. Some older project images are scans of drawings with small text.</p>'
             '<h2 class="h-m" style="margin-top:40px">Tell us</h2><p class="p-l" style="margin-top:12px">If something on the site does not work for you, write to <a href="mailto:info@pudconsultants.com?subject=Accessibility">info@pudconsultants.com</a> and we will help and fix it.</p>')
    return simple_page('accessibility.html', 'Accessibility', 'Accessibility.', None, inner, 'Accessibility | PUD Consultants', 'Accessibility statement for the PUD Consultants website: the standard we aim for, what we have done, known limits and how to tell us about a problem.')

def faq_page():
    body = '<section class="page-h"><div class="wrap"><p class="kicker mono">FAQ</p><h1 class="h-xl" style="max-width:16ch">Questions about <em>PUD.</em></h1></div></section><section class="sec" style="padding-top:20px"><div class="wrap">%s</div></section>' % faq_html(FAQ, 'Frequently asked questions') + cta('')
    return page('faq.html', 'PUD Consultants FAQ: Services, Offices and Projects', body, 'Who founded PUD, what it plans, where it works and how to reach its offices in Cairo, Riyadh and Dubai. Straight answers from PUD Consultants.', '', schema=[faq_ld(FAQ), crumbs([('Home', ''), ('FAQ', 'faq.html')])])

ART_IMG = {'what-is-urban-planning': ('assets/p/new-capital/01.jpg', 'New Administrative Capital, Egypt'),
           'what-is-master-planning': ('assets/stills/sumoublvd-egypt.jpg', 'Somou Boulevard, New Cairo'),
           'what-is-sustainable-tourism-planning': ('assets/stills/marina-al-alamein-egypt.jpg', 'Marina El Alamein, North Coast'),
           'urban-planning-in-egypt': ('assets/stills/pyramids-plateau-egypt.jpg', 'Pyramids Plateau, Giza'),
           'urban-planning-in-saudi-arabia': ('assets/stills/al-mashaaer-al-mugaddassah-ksa.jpg', 'Al Mashaaer Al Mugaddassah, Makkah')}
ART_TAG = {'what-is-urban-planning': 'Guide', 'what-is-master-planning': 'Guide', 'what-is-sustainable-tourism-planning': 'Guide', 'urban-planning-in-egypt': 'Egypt', 'urban-planning-in-saudi-arabia': 'Saudi Arabia'}
def thumb_of(src):
    t = src[:-4] + '_t.jpg'
    return t if ex(t) else src
def read_min(a): return max(2, round(len(' '.join([a['lead']] + [t for h, t in a['sections']]).split()) / 200))
def insights_page():
    # richer hub: photo cards, the practice in numbers, an interactive decade chart, latest news
    cards = ''
    for a in ARTICLES:
        im, cap = ART_IMG.get(a['slug'], ('assets/og.jpg', ''))
        cards += ('<a class="icard" href="insights/%s.html"><span class="icard-im"><img src="%s" alt="%s" loading="lazy"%s></span><span class="icard-b"><span class="icard-t">%s · %d min read</span><b>%s</b><span>%s</span><i aria-hidden="true">&rarr;</i></span></a>'
                  % (a['slug'], thumb_of(im), E(cap), wh(thumb_of(im)), ART_TAG.get(a['slug'], 'Guide'), read_min(a), E(a['h1']), E(a.get('card') or first_sentence(a['lead']))))
    rs = hero_img('port-ghalib-master-plan') or 'assets/stills/marina-al-alamein-egypt.jpg'
    cards += ('<a class="icard" href="destinations/red-sea.html"><span class="icard-im"><img src="%s" alt="Red Sea destination planning" loading="lazy"%s></span><span class="icard-b"><span class="icard-t">Destination</span><b>Planning Red Sea destinations</b><span>Port Ghalib, Abo Dabbab, Hurghada, Ain El Sokhna and the Yanbu to Duba sub-regional plan.</span><i aria-hidden="true">&rarr;</i></span></a>' % (thumb_of(rs), wh(thumb_of(rs))))
    dec = {}
    for p in PROJ:
        if p.get('year_start'): dec[p['year_start'] // 10 * 10] = dec.get(p['year_start'] // 10 * 10, 0) + 1
    mx = max(dec.values())
    bars = ''.join('<button type="button" class="ibar" style="--h:%d%%" data-n="%d" data-d="%ds" aria-label="%ds: %d projects"><span class="ibar-v">%d</span><span class="ibar-f"></span><span class="ibar-l">%d</span></button>' % (round(100 * v / mx), v, k, k, v, v, k) for k, v in sorted(dec.items()))
    cn = sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))
    top = ''.join('<a class="irow" href="countries/%s.html"><span>%s</span><span class="irow-b" style="--w:%d%%"></span><b>%d</b></a>' % (cslug(c), E('UAE' if c == 'United Arab Emirates' else cname(c, True)), round(100 * len(ps) / len(cn[0][1])), len(ps)) for c, ps in cn[:6])
    news = ''.join('<li><b>%s</b><span><a href="%s">%s</a></span></li>' % (E(d), l, E(t)) for d, t, x, u, l in NEWS[:3])
    body = ('<section class="page-h ihero"><img class="ihero-im" src="assets/stills/pyramids-plateau-egypt.jpg" alt="" fetchpriority="high"><div class="wrap"><p class="kicker mono">Insights</p><h1 class="h-xl">Urban planning, <em>explained.</em></h1>'
            '<p class="lede">Short guides from a practice that has planned cities, coasts and holy sites since 1966.</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="igrid">%s</div></div></section>'
            '<section class="sec"><div class="wrap"><p class="kicker mono">Latest</p><h2 class="h-l">News and events.</h2><ul class="facts wide" style="margin-top:26px">%s</ul><p style="margin-top:24px"><a class="btn ghost" href="news.html">All news and events</a></p></div></section>'
            ) % (cards, news) + cta('')
    return page('insights.html', 'Urban Planning Explained: Plain Guides | PUD Consultants', body, 'Plain guides to urban planning, master planning and sustainable tourism from PUD Consultants, a practice that has planned cities, coasts and holy sites since 1966.', 'insights.html', schema=[crumbs([('Home', ''), ('Insights', 'insights.html')])], og_img='assets/stills/pyramids-plateau-egypt.jpg')

def article_page(a):
    R = '../'
    secs = ''.join('<h2 class="h-m" style="margin-top:42px">%s</h2><p class="p-l" style="margin-top:12px">%s</p>' % (E(h), E(t)) for h, t in a['sections'])
    rel = ''.join('<a class="svc" href="../services/%s.html"><b>%s</b><span>%s</span><i>&rarr;</i></a>' % (s['slug'], E(s['name']), E(SVC_CARD.get(s['slug']) or clip(s['lead'], 90))) for s in SERVICES if s['slug'] in a['related'])
    aim, acap = ART_IMG.get(a['slug'], (None, ''))
    fig = ('<figure class="ahero"><img src="../%s" alt="%s" fetchpriority="high"%s><figcaption class="mono">%s</figcaption></figure>' % (aim, E(acap), wh(aim), E(acap))) if aim else ''
    body = ('<article><section class="page-h"><div class="wrap narrow"><p class="crumb mono"><a href="../insights.html">Insights</a></p><h1 class="h-xl" style="max-width:20ch;font-size:clamp(38px,5.6vw,84px)">%s</h1><p class="lede" style="max-width:48ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap narrow">' + fig + '%s%s<h2 class="h-m" style="margin-top:50px">How PUD can help</h2><div class="svcgrid" style="margin-top:18px">%s</div></div></section></article>') % (E(a['h1']), E(a['lead']), secs, faq_html(a['faq'], 'Related question'), rel) + cta(R)
    art = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['h1'], 'description': a['desc'], 'datePublished': '2026-11-24', 'dateModified': (LASTMOD.get('insights/%s.html' % a['slug']) or [0, '2026-11-24'])[1], 'author': {'@id': BASE + '/#org'}, 'publisher': {'@id': BASE + '/#org'}, 'mainEntityOfPage': BASE + '/insights/' + a['slug'] + '.html', 'inLanguage': 'en', 'image': BASE + '/assets/og.jpg'}
    return page('insights/%s.html' % a['slug'], a.get('title') or fit('%s | PUD Consultants' % a['h1'], '%s | PUD' % a['h1']), body, a['desc'], 'insights.html', schema=[art, crumbs([('Home', ''), ('Insights', 'insights.html'), (a['h1'], 'insights/%s.html' % a['slug'])])], og_type='article', head_extra='<meta property="article:published_time" content="2026-11-24">')

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
            '%s<h2 class="h-m" style="margin-top:70px">Selected projects</h2><div class="pgrid">%s</div><p class="note" style="margin-top:14px">%d projects. Where we apply it:</p><div class="chiplist">%s</div>%s</div></section>') % (
        E(s['h1']), E(s['lead']), ''.join('<p class="p-l">%s</p>' % E(t) for t in s['body']) + ('<p class="p-l"><a href="../destinations/red-sea.html">Red Sea destinations we have planned</a></p>' if s['slug'] in ('sustainable-tourism-planning', 'master-planning-and-urban-design') else ''), pts, ''.join('<p class="p-l" style="margin-top:30px">Read the guide: <a href="../insights/%s.html">%s</a></p>' % (a['slug'], E(a['h1'])) for a in ARTICLES if s['slug'] in a.get('related', [])), ''.join(card(p, R) for p in sel[:12]), len(sel), chips, faq_html(s['faq'])) + cta(R)
    sv = {'@context': 'https://schema.org', '@type': 'Service', 'name': s['name'], 'serviceType': s['name'], 'description': s['lead'], 'provider': {'@id': BASE + '/#org'}, 'areaServed': ['Egypt', 'Saudi Arabia', 'Middle East']}
    return page('services/%s.html' % s['slug'], fit('%s | PUD Consultants' % s['h1'], '%s | PUD' % s['h1']), body, s['lead'], 'about.html', schema=[sv, crumbs([('Home', ''), ('About', 'about.html'), (s['name'], 'services/%s.html' % s['slug'])])], og_img=(hero_img(sel[0]['slug']) if sel else None))

THE = {'Gambia': 'The Gambia', 'United Arab Emirates': 'the United Arab Emirates'}
def cname(c, start=False):
    n = THE.get(c, c)
    return n[0].upper() + n[1:] if start else n
NUM = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
def num(n): return NUM[n] if n < len(NUM) else str(n)
def andlist(xs): return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
CAT_WORD = {'Masterplan': 'master plans', 'Regional planning': 'regional plans', 'Tourism': 'tourism projects', 'Hospitality': 'hotels', 'Housing': 'housing',
            'Mixed use': 'mixed-use developments', 'Heritage': 'heritage projects', 'Landscape': 'landscape projects', 'Education': 'campuses', 'Industrial': 'industrial buildings',
            'Advisory': 'advisory roles', 'Infrastructure': 'infrastructure plans', 'Urban design': 'urban design', 'Architecture': 'buildings', 'Healthcare': 'health buildings', 'Commercial': 'commercial buildings'}
def place_intro(name, country, ps):
    # CT-085 / CT-088: written sentences, not a template with counts in brackets
    y0, y1 = years(ps); n = len(ps); top = [p['name'] for p in with_img_first(ps)[:3]]
    where = name if name == cname(country) else '%s, %s' % (name, cname(country))
    if n == 1:
        p = ps[0]; yr = p['year'] if p.get('year') and p['year'] != 'None' else ''
        return 'PUD has one project in %s: %s%s.' % (where, p['name'], (' (%s)' % yr) if yr else '')
    span = (' between %s and %s' % (y0, y1)) if y0 and y1 and y1 != y0 else ((' in %s' % y0) if y0 else '')
    t = 'PUD has %s projects in %s%s, including %s.' % (num(n), where, span, andlist(top))
    cats = {}
    for p in ps:
        for c in p.get('category', []): cats[c] = cats.get(c, 0) + 1
    words = [CAT_WORD.get(k, k.lower()) for k, v in sorted(cats.items(), key=lambda kv: -kv[1])[:3]]
    if len(words) > 1: t += ' The work covers %s.' % andlist(words)
    return t

NOINDEX_CITIES = set('km-47 city-view-compound west-arabella mansouria cairo-suez-road cairo-alexandria-desert-road 6th-of-october-city-and-ismailia empty-quarter al-salmiya al-khiran al-uqair jabal-al-lith shorouq-city kafr-el-zayat nag-hammadi katameya obour-city frankfurt aseer northern-borders red-sea-coast'.split())
def city_page(d):
    R = '../'; ps = with_img_first(d['projects']); name, country = d['name'], d['country']
    intro = place_intro(name, country, ps)
    fts = []
    for p in ps:
        for f in FACTS:
            if f.get('project') in (p['slug'], p['name']) and f.get('url') and f['fact'] not in [x[0] for x in fts]: fts.append((f['fact'], f['url']))
    facts = ''  # sourced fact boxes removed from pages (Nov 2026)
    sib = sorted([x for x in PLACES.values() if x['country'] == country and x['slug'] != d['slug']], key=lambda x: -len(x['projects']))[:10]
    sibh = ''.join('<a class="chip" href="%s.html">%s <small>%d</small></a>' % (x['slug'], E(x['name']), len(x['projects'])) for x in sib)
    cts = {}
    for p in ps:
        for c in p.get('category', []): cts[c] = cts.get(c, 0) + 1
    sv = [s for s in SERVICES if any(c in s['cats'] for c in cts)][:3]
    svh = ''.join('<a class="chip" href="../services/%s.html">%s</a>' % (s['slug'], E(s['name'])) for s in sv)
    body = ('<section class="page-h"><div class="wrap"><p class="crumb mono"><a href="../projects.html">Projects</a> / <a href="../countries/%s.html">%s</a></p><h1 class="h-xl" style="max-width:20ch;font-size:clamp(38px,6vw,92px)">%s %s, <em>%s.</em></h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap"><div class="pgrid">%s</div>%s<h2 class="h-m" style="margin-top:60px">Services used in %s</h2><div class="chiplist">%s</div>%s</div></section>') % (
        cslug(country), E(cname(country, True)), 'Urban planning and design in' if any(c in ('Masterplan', 'Regional planning', 'Urban design', 'Tourism', 'Mixed use') for p in ps for c in p.get('category', [])) else 'PUD projects in', E(name), E(cname(country)), E(intro), ''.join(card(p, R) for p in ps), ('<h2 class="h-m" style="margin-top:60px">About %s</h2>%s' % (E(name), facts)) if facts else '', E(name), svh,
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
    intro = place_intro(cname(c, True), c, ps).replace(', %s,' % cname(c), ',')
    if len(ps) == 1:
        p = ps[0]; intro = 'PUD has one documented project in %s: %s%s. %s' % (cname(c), p['name'], (' (%s)' % p['year']) if p.get('year') and p['year'] != 'None' else '', sclip(p.get('summary') or '', 150))
    qa = [('Which cities in %s has PUD worked in?' % cname(c), ('PUD has worked in %s.' % andlist([d['name'] for d in pls[:12]])) if len(pls) > 1 else intro)]
    body = ('<section class="page-h"><div class="wrap"><p class="crumb mono"><a href="../projects.html">Projects</a></p><h1 class="h-xl" style="max-width:20ch;font-size:clamp(38px,6vw,92px)">Urban planning and master planning in %s</h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '<section class="sec" style="padding-top:30px"><div class="wrap">%s<h2 class="h-m">Cities and regions</h2><div class="chiplist">%s</div><h2 class="h-m" style="margin-top:50px">All projects in %s</h2><div class="pgrid">%s</div>%s</div></section>') % (
        E(cname(c)), E(intro) + ('</p><p class="lede" style="max-width:52ch"><a href="../destinations/red-sea.html">Red Sea destinations</a> · <a href="../insights/urban-planning-in-%s.html">Urban planning in %s, explained</a>' % (cslug(c), c) if c in ('Egypt', 'Saudi Arabia') else ''), ('<div class="cnrow decs">%s</div>' % decs) if decs else '', chips, E(cname(c)), ''.join(card(p, R) for p in ps), faq_html(qa)) + cta(R)
    il = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PUD projects in %s' % cname(c), 'numberOfItems': len(ps), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': BASE + '/projects/' + p['slug'] + '.html', 'name': p['name']} for i, p in enumerate(ps[:100])]}
    return page('countries/%s.html' % cslug(c), fit('Urban Planning Consultants in %s | PUD Consultants' % cname(c), 'Urban Planning in %s | PUD Consultants' % cname(c), 'Urban Planning in %s | PUD' % cname(c)), body, intro, 'projects.html', schema=[il, crumbs([('Home', ''), ('Projects', 'projects.html'), (c, 'countries/%s.html' % cslug(c))])],
                og_img=hero_img(ps[0]['slug']))

def project_title(p):
    nm = p['name']; short = re.split(r':\s| \(', nm)[0] if len(nm) > 44 else nm
    for t in ('%s | PUD Consultants' % nm, '%s | PUD Consultants' % short, '%s | PUD' % short):
        if len(t) <= 60: return t
    return (short[:52].rsplit(' ', 1)[0] + ' | PUD')

def og_card(p):
    # SE-010: projects without a photo get their own readable social card
    f = 'assets/og/%s.jpg' % p['slug']
    if os.environ.get('REGEN_OG') or not ex(f):
        try:
            import og; og.project_card(p, f)
        except Exception as e: print('og card skipped', p['slug'], e); return None
    return f

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
    if slug in NO_CLIP_HERO: clp, clp_poster = None, None  # newer, sharper photos replace the old clip
    imgs = imgsets.get(slug, [])
    place = ', '.join(x for x in [p.get('city'), p['country']] if x)
    typ = '%s in %s' % (p['noun'], place)
    bg = '<img src="%s%s" alt="%s: %s" fetchpriority="high"%s>' % (R, himg, E(p['name']), E(typ), wh(himg)) if himg else ''
    vid = ('<video autoplay muted loop playsinline preload="metadata" poster="%s%s" aria-hidden="true"><source src="%s%s" type="video/mp4"></video>' % (R, clp_poster, R, clp)) if clp else ''
    cats = ''.join('<span>%s</span>' % E(c) for c in p.get('category', []))
    plog = ''
    PNAME = {'pgesco': 'PGESCO', 'wep': 'WEP (Germany)', 'cupud': 'CUPUD, Ain Shams University', 'bect': 'BECT', 'getinsa': 'Getinsa', 'paymacotas': 'Paymacotas', 'atkinsrealis': 'AtkinsR\u00e9alis', 'ernst-young': 'Ernst & Young', 'khatib-alami': 'Khatib & Alami', 'horwath-htl': 'Horwath HTL', 'chemonix': 'Chemonics Egypt', 'ehaf': 'EHAF', 'frantz-slater-design-collective': 'Frantz Slater Design Collective'}
    for ps_ in [x for x in p.get('partners', []) if not re.match(r'(dr|eng|arch|prof)-', x)]:
        pp = pmap.get(ps_)
        if has_logo(pp) and pp.get('url'): plog += '<a href="%s" target="_blank" rel="noopener" aria-label="%s (opens in a new tab)"><img src="%s%s" alt="%s logo"></a>' % (E(pp['url']), E(pp['name']), R, pp['logo'], E(pp['name']))
        elif has_logo(pp): plog += '<span class="lgo"><img src="%s%s" alt="%s logo"></span>' % (R, pp['logo'], E(pp['name']))
        elif pp: plog += '<span>%s</span>' % E(pp['name'])
        elif ps_: plog += '<span>%s</span>' % E(PNAME.get(ps_) or ps_.replace('-', ' ').title())
    cl = ''.join('<span><img src="%s%s" alt="%s logo"></span>' % (R, c['logo'], E(c['name'])) for c in client_logos(p.get('client')))
    fund = ''.join('<span><img src="%s%s" alt="%s logo"></span>' % (R, c['logo'], E(c['name'])) for c in client_logos(p.get('client'), funders=True))
    ctext = re.split(r',?\s*/?\s*funded by', p.get('client') or '', flags=re.I)[0].strip(' ,/')
    loc_html = (', '.join('<a href="%scities/%s.html">%s</a>' % (R, sl, E(PLACES[sl]['name'])) for sl in p.get('places', [])[:2]) + ', <a href="%scountries/%s.html">%s</a>' % (R, cslug(p['country']), E(p['country']))) if p.get('places') else '<a href="%scountries/%s.html">%s</a>' % (R, cslug(p['country']), E(place))
    meta = [m for m in [('Location', loc_html), ('Year', E(p['year']) if p.get('year') and p['year'] != 'None' else ''), ('Client', E(p['client']) if p.get('client') else ''), ('Role', E(p['role']) if p.get('role') else '')] if m[1]]
    meta_html = ''.join('<div><span class="k mono">%s</span><span class="v">%s</span></div>' % (k, v) for k, v in meta)
    gal = ''.join('<button data-full="%s%s"><img src="%s%s" alt="%s: %s" loading="lazy" width="%s" height="%s"></button>' % (R, im['src'], R, im.get('thumb') or im['src'], E(p['name']), E(im.get('note') or p['noun']), im.get('w', ''), im.get('h', '')) for im in imgs)
    st = still_for(slug)
    if st and imgs and st not in DROP and slug not in NO_STILL_IN_GALLERY: gal += '<button data-full="%s%s"><img src="%s%s" alt="%s visualisation" loading="lazy"><span class="lbl">Visualisation</span></button>' % (R, st, R, st, E(p['name']))
    facts = ''  # sourced fact boxes removed from pages (Nov 2026)
    pl_ = PLINKS.get(slug); off = ('<p style="margin-top:22px"><a class="btn ghost" href="%s" target="_blank" rel="noopener">Official project site</a></p>' % E(pl_['official_url'])) if pl_ and pl_.get('official_url') else ''
    sv = [s for s in SERVICES if any(c in s['cats'] for c in p.get('category', []))][:2]
    svh = ''.join('<a class="chip" href="%sservices/%s.html">%s</a>' % (R, s['slug'], E(s['name'])) for s in sv)
    rel = related_for(p)
    relh = ('<h2 class="h-m" style="margin-top:70px">More from %s</h2><div class="pgrid">%s</div>' % (E(PLACES[p['places'][0]]['name'] if p.get('places') else p['country']), ''.join(card(q, R) for q in rel))) if rel else ''
    ordl = [x['slug'] for x in PROJ]; k = ordl.index(slug); pv = PROJ[(k - 1) % len(PROJ)]; nx = PROJ[(k + 1) % len(PROJ)]
    fav = '<span class="favtag">Featured in the founder\'s profile</span>' if slug in FAV else ''
    role = ''
    sumtxt = p.get('summary') or ''
    body = ('<article><section class="ph-hero%s">%s%s<div class="wrap in"><nav class="crumb mono" aria-label="Breadcrumb"><a href="%sprojects.html">Projects</a> / <a href="%scountries/%s.html">%s</a> / %s</nav>%s<h1 class="h-xl%s" style="max-width:18ch;font-size:clamp(40px,6.4vw,100px)">%s</h1><p class="lede" style="margin-top:6px">%s · %s</p><div class="tags">%s</div></div></section>'
            '<section class="sec" style="padding-top:20px"><div class="wrap"><div class="meta">%s</div><div class="body" style="margin-top:50px"><div><p class="p-l" style="font-size:clamp(19px,1.8vw,24px);color:#f3f3f3">%s</p>%s%s<div class="chiplist" style="margin-top:22px">%s</div></div>'
            '<div>%s%s%s%s</div></div>'
            '%s%s<div class="pn"><a href="%sprojects/%s.html" rel="prev"><span class="mono" style="color:var(--mute)">Previous project</span><b>%s</b></a><a href="%sprojects/%s.html" rel="next"><span class="mono" style="color:var(--mute)">Next project</span><b>%s</b></a></div><p style="margin-top:34px;text-align:center"><a class="btn ghost" href="%sprojects.html#atlas">Back to the map</a></p></div></section>' + cta(R, head='Planning a site like this?') + '</article>'
            '<div class="lb" role="dialog" aria-modal="true" aria-label="Photo viewer"><button class="x" aria-label="Close">&times;</button><button class="p" aria-label="Previous">&lsaquo;</button><img alt=""><button class="n" aria-label="Next">&rsaquo;</button></div>') % (
        '' if (himg or clp) else ' none', (bg if himg else ''), vid, R, R, cslug(p['country']), E(p['country']), E(p['name']), fav, ' long' if len(p['name']) > 48 else '', E(p['name']), E(p['noun']), E(place), cats, meta_html, E(sumtxt), role, facts, svh,
        ('<h2 class="mono" style="color:var(--mute);font-weight:400">Partners</h2><div class="prt">%s</div>' % plog) if plog else '', ('<h2 class="mono" style="color:var(--mute);font-weight:400;margin-top:30px">Client</h2><div class="prt">%s</div>%s' % (cl, ('<p class="ctext">%s</p>' % E(ctext)) if ctext else '')) if (cl or ctext) else '',
        ('<h2 class="mono" style="color:var(--mute);font-weight:400;margin-top:30px">Funded by</h2><div class="prt">%s</div>' % fund) if fund else '', off, ('<div class="gal">%s</div>' % gal) if gal else '', relh, R, pv['slug'], E(pv['name']), R, nx['slug'], E(nx['name']), R)
    yr = p['year'] if p.get('year') and p['year'] != 'None' else ''
    desc = sclip(sumtxt, 156) if sumtxt else '%s: %s%s.' % (p['name'], typ, (', ' + yr) if yr else '')
    if len(desc) < 100:
        extra = ' %s in %s%s, planned by PUD Consultants%s.' % (p['noun'], place, (' (%s)' % yr) if yr else '', (' for ' + p['client']) if p.get('client') and p['client'] not in desc else '')
        desc = sclip(desc + extra, 156)
    loc = {'@type': 'Place', 'name': place, 'address': {'@type': 'PostalAddress', 'addressCountry': p['country']}}
    if p.get('lat') is not None: loc['geo'] = {'@type': 'GeoCoordinates', 'latitude': p['lat'], 'longitude': p['lon']}
    cw = {'@context': 'https://schema.org', '@type': 'CreativeWork', 'name': p['name'], 'description': clip(sumtxt or typ, 300), 'dateCreated': str(p.get('year_start') or p['year']), 'creator': {'@id': BASE + '/#org'}, 'about': p.get('category', []),
          'contentLocation': loc, 'url': BASE + '/projects/' + slug + '.html', 'inLanguage': 'en'}
    ogc = himg or og_card(p)
    if ogc: cw['image'] = BASE + '/' + ogc
    if not cw['dateCreated'] or cw['dateCreated'] == 'None': del cw['dateCreated']  # SE-007
    return page('projects/%s.html' % slug, project_title(p), body, desc, 'projects.html',
                schema=[cw, crumbs([('Home', ''), ('Projects', 'projects.html'), (p['country'], 'countries/%s.html' % cslug(p['country'])), (p['name'], 'projects/%s.html' % slug)])], og_img=ogc, og_alt=p['name'])

def llms():
    sig = [p for p in PROJ if p.get('featured')][:10]
    L = ['# PUD Consultants', '',
         '> PUD Consultants (Planning & Urban Development Consultants) is an urban planning, master planning, architecture and sustainable tourism consultancy founded in Cairo in 1966 by Prof. Dr. Abdallah Attia and led today by Prof. Dr. Amr Attia. Offices: Cairo, Riyadh and Dubai. It is not related to planned unit developments or public utility districts, which share the acronym PUD.', '',
         '## Key facts',
         '- Founded: 1966, Cairo, Egypt',
         '- Founder: Prof. Dr. Abdallah Abdel Aziz Attia, architect and professor',
         '- Leader: Prof. Dr. Amr Attia, CEO and Principal; Professor of Urban Planning at Ain Shams University, Eisenhower Fellow (Egypt 2007), Board Chairman of SHARE Egypt 2026',
         '- Email: info@pudconsultants.com',
         '- Offices: Cairo (Sheikh Zayed City and Heliopolis), Riyadh (Diplomatic Quarter and Al Nakheel), Dubai (Palm Jumeirah)',
         '- Work: %d documented projects in %d countries, mostly Egypt and Saudi Arabia' % (len(PROJ), len(COUNTRIES)),
         '- Partners include WATG, AECOM Arabia, Gillespies, Systematica, Dar Al-Handasah', '',
         '## Key pages', '- [Home](%s/)' % BASE, '- [60 years](%s/60-years.html)' % BASE, '- [Projects](%s/projects.html)' % BASE, '- [About](%s/about.html)' % BASE, '- [Sustainability](%s/sustainability.html)' % BASE, '- [People](%s/people.html)' % BASE, '- [Abdallah Attia, founder](%s/abdallah-attia.html)' % BASE, '- [Amr Attia](%s/amr-attia.html)' % BASE, '- [Partners](%s/partners.html)' % BASE, '- [FAQ](%s/faq.html)' % BASE, '- [Contact](%s/contact.html)' % BASE, '', '## Services']
    L += ['- [%s](%s/services/%s.html): %s' % (s['name'], BASE, s['slug'], s['lead']) for s in SERVICES]
    L += ['', '## Guides'] + ['- [%s](%s/insights/%s.html): %s' % (a['h1'], BASE, a['slug'], a['lead']) for a in ARTICLES]
    L += ['', '## Countries'] + ['- [%s](%s/countries/%s.html): %d project%s' % (cname(c, True), BASE, cslug(c), len(ps), '' if len(ps) == 1 else 's') for c, ps in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[1]))]
    L += ['', '## Signature projects'] + ['- [%s](%s/projects/%s.html): %s' % (p['name'], BASE, p['slug'], clip(p.get('summary') or '', 150)) for p in sig]
    L += ['', '## Offices'] + ['- %s: %s, %s' % (a, b, c) for a, b, c in OFFICES]
    L += ['', '## Optional', '- [Full project list](%s/llms-full.txt)' % BASE]
    return '\n'.join(L) + '\n'
def llms_full():
    # SE-014: the full file carries the firm, services, people, FAQ and guides, then the project list
    L = llms().split('## Key pages')[0].rstrip().splitlines() + ['', '## About', ABOUT_LEAD] + ABOUT_WHO + ['', '## Services']
    for s in SERVICES: L += ['### ' + s['name'], s['lead']] + s['body'] + ['']
    L += ['## People', '### Prof. Dr. Abdallah Attia, founder', FOUNDER_LEAD, FOUNDER_BIO, '', '### Prof. Dr. Amr Attia, CEO and Principal'] + AMR_PROSE + ['']
    L += ['## Frequently asked questions'] + ['**%s** %s' % (q, a) for q, a in FAQ] + ['']
    L += ['## Guides'] + ['### %s\n%s\n%s' % (a['h1'], a['lead'], ' '.join(t for h, t in a['sections'])) for a in ARTICLES] + ['']
    L += ['## Offices'] + ['- %s: %s, %s' % (a, b_, c) for a, b_, c in OFFICES] + ['', '## Projects']
    for p in sorted(PROJ, key=lambda p: -(p.get('year_start') or 0)):
        place = ', '.join(x for x in (p.get('city'), cname(p['country'], True)) if x)
        yr = p['year'] if p.get('year') and p['year'] != 'None' else ''
        bits = ['%s%s' % (place, (', ' + yr) if yr else '')]
        if p.get('client'): bits.append('client: ' + p['client'])
        L.append('- [%s](%s/projects/%s.html) (%s): %s' % (p['name'], BASE, p['slug'], '; '.join(bits), clip(p.get('summary') or '', 220)))
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
SUS_IMG = {'abo-dabbab-marine-field-station': None, 'alula-strategic-framework-plan': 'assets/story/sus-alula-framework.jpg', 'khaybar-heritage-area-master-plan': 'assets/story/about-khaybar.jpg', 'kidana-al-khaif': 'assets/story/sus-kidana-al-khaif.jpg', 'sharaan-nature-reserve-master-plan': 'assets/story/sus-sharaan.jpg', 'north-coast-regional-vision-fuka-matrouh': 'assets/story/sus-nw-coast-regional-vision.jpg'}
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
    qa = [('What is PUD Consultants?', 'PUD (Planning & Urban Development) Consultants is an urban planning and architecture practice founded in Cairo in 1966 by Prof. Dr. Abdallah Abdel Aziz Attia. It plans cities, tourism destinations and heritage areas, and designs buildings and landscapes, in Egypt, Saudi Arabia, the UAE and beyond.'),
          ('Who leads PUD Consultants today?', 'PUD is led by Prof. Dr. Amr Attia, CEO and Principal. He is Professor of Urban Planning at Ain Shams University, an Eisenhower Fellow (2007), and was Principal Director at AECOM Arabia and Vice President at WATG.'),
          ('What services does PUD offer?', 'PUD offers %s, and assembles bespoke advisory groups of international experts for each project.' % (', '.join(s['name'].lower() for s in SERVICES[:-1]) + ' and ' + SERVICES[-1]['name'].lower())),
          ('Where does PUD work?', 'PUD\'s record documents %d projects in %d countries: %s. Its offices are in Cairo (Egypt), Riyadh (Saudi Arabia) and Dubai (UAE).' % (len(PROJ), len(countries), ', '.join(countries[:-1]) + ' and ' + countries[-1])),
          ('What are some of PUD\'s notable projects?', 'Highlights include the Pyramids Plateau destination master plan (with WATG), Al Mashaaer Al Mugaddassah in Makkah, Alamein Riviera, Somou Boulevard, Cairo Media City, strategic advisory for the New Administrative Capital, the Khaybar Heritage Area development brief and the AlUla Strategic Framework Plan, and Jazan Economic City.'),
          ('How does PUD approach sustainability?', 'Sustainability is part of how PUD plans, through environmental responsibility, social inclusion, cultural heritage preservation and green building standards. PUD\'s work contributes most directly to UN Sustainable Development Goals 7, 8, 9, 11, 12, 13, 15 and 17.'),
          ('Does PUD work with international firms?', 'Yes. PUD regularly collaborates with leading global firms including WATG, AECOM, SOM, BuroHappold, HOK, Hill International and Giugiaro, combining international expertise with deep local knowledge, alongside 100+ clients and 90+ collaborations over six decades.'),
          ('How can I contact PUD Consultants?', 'Write to info@pudconsultants.com or use the form on the contact page. Or call Cairo on +20 2 2414 7537 or +20 100 198 1111, Riyadh on +966 540 39 8178 or Dubai on +971 509 29 8178.')]
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">About PUD</p><h1 class="h-xl" style="max-width:16ch">Planning &amp; Urban Development <em>since 1966.</em></h1><p class="lede" style="max-width:50ch">%s</p></div></section>'
            '%s'
            '<section class="sec" style="padding-top:40px"><div class="wrap"><p class="kicker mono">Our purpose</p><p class="statement">%s</p>'
            '<h2 class="h-m" style="margin-top:80px">Who we are</h2><div class="cols2" style="margin-top:22px">%s</div>'
            '<div class="duo"><div><p class="kicker mono">Mission</p><p class="p-l">%s</p></div><div><p class="kicker mono">Vision</p><p class="p-l">%s</p></div></div>'
            '<h2 class="h-m" style="margin-top:80px">Core values</h2>%s</div></section>'
            '<section class="sec paper" id="expertise"><div class="wrap"><p class="kicker mono">Expertise</p><h2 class="h-l" style="max-width:18ch">From the regional plan <em>to the building.</em></h2><p class="p-l" style="margin-top:18px">Six services, plus a network of specialists we bring in for each project.</p><div class="svcgrid">%s</div></div></section>'
            '<section class="sec" id="approach"><div class="wrap"><p class="kicker mono">Approach</p><h2 class="h-l" style="max-width:20ch">How we work.</h2><p class="p-l" style="margin-top:18px">%s</p>%s</div></section>'
            '<section class="sec paper" id="sustainability"><div class="wrap grid2x"><div><p class="kicker mono">Sustainability</p><h2 class="h-l">Designing with purpose. <em>Building for tomorrow.</em></h2><p class="p-l" style="margin-top:18px">We test every plan against the same questions: does it use land, water and energy sensibly, does it include the people who live there, and does it keep what makes the place worth visiting? <a href="destinations/red-sea.html">Sustainable tourism planning on the Red Sea</a>.</p>%s<p style="margin-top:28px"><a class="btn dark" href="sustainability.html">Our sustainability commitments</a></p></div>'
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
                schema=[about, {'@context': 'https://schema.org', '@id': BASE + '/#org', '@type': ['Organization', 'ProfessionalService'], 'name': 'PUD Consultants', 'url': BASE + '/'}, il, crumbs([('Home', ''), ('About', 'about.html')])], og_img=hi)

def sustainability_page():
    R = ''; hi = 'assets/story/gp-4-people.jpg'
    five = ''
    for i, (th, h, t, slug, cap) in enumerate(SUS_FIVE):
        im = SUS_IMG.get(slug) or hero_img(slug)
        five += ('<article class="resp%s"><div class="resp-t"><p class="n mono">%02d · %s</p><h3 class="h-m">%s</h3><p class="p-l">%s</p></div>'
                 '<a class="figure" href="projects/%s.html"><img src="%s" alt="%s" loading="lazy"%s><span class="mono">%s &rarr;</span></a></article>') % (' flip' if i % 2 else '', i + 1, E(th), E(h), E(t), slug, im, E(cap.replace(' · ', ', ')), wh(im), E(cap))
    SDGC = {7: '#FCC30B', 8: '#A21942', 9: '#FD6925', 11: '#FD9D24', 12: '#BF8B2E', 13: '#3F7E44', 15: '#56C02B', 17: '#19486A'}
    sdg = ''.join('<li style="--sdg:%s"><span class="sdg-n">%d</span><b>%s</b><span class="un">%s</span><span class="pud"><em class="mono">PUD</em> %s</span><span class="sdg-p">%s</span></li>' % (
        SDGC.get(n, '#333'), n, E(g), E(u), E(p), ' '.join('<a href="projects/%s.html">%s &rarr;</a>' % (s_, E(BYSLUG[s_]['name'])) for s_ in sl if s_ in BYSLUG)) for n, g, u, p, sl in SDGS)
    lens = ''.join('<li>%s</li>' % E(x) for x in SUS_LENS)
    def scard(slug):
        p = BYSLUG[slug]; im = SUS_IMG.get(slug) or hero_img(slug)
        if not im: return card(p, R)
        return '<a class="pcard" href="projects/%s.html"><img src="%s" alt="%s, %s" decoding="async"%s><span class="t"><b>%s</b><span>%s</span></span></a>' % (slug, im, E(p['name']), E(p.get('city') or p['country']), wh(im), E(p['name']), E(' · '.join(x for x in (p.get('city') or p['country'], str(p['year'])) if x)))
    projs = ''.join(scard(s) for s in SUS_PROJECTS if s in BYSLUG)
    body = ('<section class="page-h"><div class="wrap"><p class="kicker mono">Sustainability</p><h1 class="h-xl" style="max-width:17ch">Sustainability <em>at PUD.</em></h1><p class="lede" style="max-width:52ch">%s</p></div></section>'
            '%s'
            '<section class="sec" style="padding-top:40px"><div class="wrap"><p class="kicker mono">Our commitment</p><p class="statement">Sustainability is part of how we plan.</p><div class="cols2" style="margin-top:26px">%s</div>'
            '<h2 class="h-l" style="margin-top:90px;max-width:18ch">Designing with purpose. <em>Building for tomorrow.</em></h2><p class="p-l" style="margin-top:14px">We are committed to:</p>%s</div></section>'
            '<section class="sec paper"><div class="wrap"><p class="kicker mono">Five responsibilities, one approach</p><h2 class="h-l" style="max-width:20ch">People, society, culture, environment <em>and planet.</em></h2>%s</div></section>'
            '<section class="sec interlude-s"><img src="assets/story/sustain-alamein-riviera.jpg" alt="Homes around a planted lagoon at dusk, Alamein Riviera" loading="lazy"%s><div class="wrap"><p class="h-l">Homes around a planted lagoon, Alamein Riviera.</p><a class="mono" href="projects/alamein-riviera-vision-master-plan.html">Alamein Riviera · North Coast, Egypt &rarr;</a></div></section>'
            '<section class="sec"><div class="wrap"><p class="kicker mono">Designing resilient futures</p><h2 class="h-l" style="max-width:18ch">Sustainability starts <em>with land use.</em></h2><p class="p-l" style="margin-top:18px">From new towns to heritage areas, we test each plan against land, water, movement, heritage and climate.</p><ul class="lens">%s</ul></div></section>'
            '<section class="sec paper" id="sdgs"><div class="wrap"><p class="kicker mono">Goals we support</p><h2 class="h-l">Leave no place behind.</h2><p class="p-l" style="margin-top:18px">Our work contributes most directly to eight of the seventeen UN Sustainable Development Goals. Each goal links to the projects behind it.</p><ol class="sdgs">%s</ol></div></section>'
            '<section class="sec"><div class="wrap"><p class="kicker mono">Sustainability in practice</p><h2 class="h-l">Selected projects</h2><div class="pgrid" style="margin-top:30px">%s</div>'
            '<p style="margin-top:24px"><a class="btn ghost" href="projects.html">All projects</a> <a class="btn ghost" href="services/environment-and-sustainability.html">Environmentally sustainable development</a></p>'
            '<div style="margin-top:80px">%s</div></div></section>'
            '<section class="sec ctaband"><div class="wrap duo"><div><p class="kicker mono">For clients</p><h2 class="h-m">Planning a project that has to meet sustainability targets?</h2><p style="margin-top:20px"><a class="btn red" href="contact.html">Talk to us</a></p></div>'
            '<div><p class="kicker mono">For partners</p><h2 class="h-m">Making progress together.</h2><p style="margin-top:20px"><a class="btn ghost" href="partners.html#network">Become one of our partners</a></p></div></div></section>') % (
        E(SUS_LEDE),
        ('<section class="wrap"><a class="figure wide" href="projects/green-pearl-prime-dubai-competition.html"><img src="%s" alt="Families walking and cycling along a green stream walk, Green Pearl, Dubai" fetchpriority="high"%s style="object-position:50%% 60%%"><span class="mono">Green Pearl · Dubai &rarr;</span></a></section>' % (hi, wh(hi))) if hi else '',
        ''.join('<p class="p-l">%s</p>' % E(t) for t in SUS_COMMIT), numbered(SUS_FOUR, 'nlist four'), five, wh('assets/story/sustain-alamein-riviera.jpg'), lens, sdg, projs, faq_html(SUS_FAQ))
    wp = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': BASE + '/sustainability.html', 'name': 'Sustainability commitments and SDGs', 'description': SUS_LEDE, 'about': [{'@id': BASE + '/#org'}, {'@type': 'Thing', 'name': 'Sustainable development'}] + [{'@type': 'Thing', 'name': 'SDG %d: %s' % (n, g)} for n, g, u, p, sl in SDGS], 'publisher': {'@id': BASE + '/#org'}, 'inLanguage': 'en'}
    return page('sustainability.html', 'Sustainability Commitments and UN SDGs | PUD Consultants', body,
                'How PUD Consultants plans for sustainability: four commitments, five responsibilities and the UN goals its projects support (SDGs 7, 8, 9, 11, 12, 13, 15 and 17).', 'sustainability.html',
                schema=[wp, crumbs([('Home', ''), ('Sustainability', 'sustainability.html')])], og_img=hi)

def network_sections():
    team = ''.join('<li><img src="%s" alt="%s" loading="lazy"%s><b>%s</b><span>%s</span><em class="mono">%s years of experience</em></li>' % (src, E(n), wh(src), E(n), E(r), y) for n, r, y, src in STAFF)
    def xp(name, role, creds): return '<li><span class="xp-i" aria-hidden="true">%s</span><b>%s</b><em class="mono">%s</em><ul>%s</ul></li>' % (E(initials(name)), E(name), E(role), ''.join('<li>%s</li>' % E(c) for c in creds))
    strat = ''.join(xp(n, 'Strategic partner', c) for n, c in STRATEGIC)
    spec = ''.join(xp(n, r, c) for n, r, c in SPECIALISTS)
    net = ''.join('<li><b>%s</b><span>%s</span></li>' % (E(n), E(r)) for n, r in NETWORK)
    tags = ''.join('<span class="chip">%s</span>' % E(t) for t in STRATEGY_TAGS)
    return ('<section class="sec" style="padding-top:30px"><div class="wrap grid2x"><div><p class="kicker mono">Partners and experts</p><h2 class="h-l">The team <em>and the specialists we work with.</em></h2><p class="p-l" style="margin-top:18px">%s</p><p class="p-l" style="margin-top:14px">%s</p></div>'
            '<figure class="figure"><img src="assets/people/team-gem.jpg" alt="The PUD team at the Grand Egyptian Museum, Giza" loading="lazy"%s><figcaption class="mono">The team at the Grand Egyptian Museum · Giza</figcaption></figure></div></section>'
            '<section class="sec paper" id="team"><div class="wrap"><p class="kicker mono">Key staff</p><h2 class="h-l">Key staff.</h2><p class="p-l" style="margin-top:18px">The people who run PUD\'s projects from brief to delivery.</p><ul class="team">%s</ul></div></section>'
            '<section class="sec" id="strategic-partners"><div class="wrap"><p class="kicker mono">Strategic partners</p><h2 class="h-l">Finance, engineering, law <em>and sustainability.</em></h2><ul class="xps">%s</ul>'
            '<p class="kicker mono" style="margin-top:90px">Our experts</p><h2 class="h-l">Specialists we call on</h2><ul class="xps">%s</ul></div></section>'
            '<section class="sec paper" id="network"><div class="wrap"><p class="kicker mono">The curated expert ensemble</p><h2 class="h-l" style="max-width:20ch">Specialists on PUD-led panels.</h2>%s'
            '<h3 class="h-m" style="margin-top:80px">Experts who have served on PUD-led panels</h3><ul class="netlist">%s</ul></div></section>'
            '<section class="sec"><div class="wrap"><h2 class="h-l">Work with us.</h2><p class="p-l" style="margin-top:18px">Specialists and firms who want to join a PUD team can write to <a href="mailto:info@pudconsultants.com?subject=Partnership">info@pudconsultants.com</a>.</p></div></section>') % (
        E(NET_INTRO), E(NET_QUOTE), wh('assets/people/team-gem.jpg'), team, strat, spec, numbered(ENSEMBLE, 'nlist three'), net)

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
    W('amr-attia.html', amr_page()); W('abdallah-attia.html', founder_page()); W('news.html', news_page()); W('awards.html', awards_page()); W('clients.html', clients_page()); W('privacy.html', privacy_page()); W('accessibility.html', accessibility_page()); W('about.html', about_page()); W('sustainability.html', sustainability_page()); W('services.html', stub_page(BASE + '/about.html#expertise')); W('insights.html', insights_page()); W('faq.html', faq_page()); os.makedirs(SITE + '/destinations', exist_ok=True); W('destinations/red-sea.html', red_sea_page())
    open(SITE + '/404.html', 'w', encoding='utf-8').write(not_found_page().replace('<img ', '<img decoding="async" '))
    for s in SERVICES: W('services/%s.html' % s['slug'], service_page(s))
    for old, new in RETIRED.items():
        W('services/%s.html' % old, stub_page(BASE + '/services/%s.html' % new))
    for a in ARTICLES: W('insights/%s.html' % a['slug'], article_page(a))
    for p in PROJ: W('projects/%s.html' % p['slug'], project_page(p))
    for d in PLACES.values(): W('cities/%s.html' % d['slug'], city_page(d))
    for c, ps in COUNTRIES.items(): W('countries/%s.html' % cslug(c), country_page(c, ps))
    skip = {'cities/%s.html' % s for s in NOINDEX_CITIES if s in PLACES and len(PLACES[s]['projects']) < 2}
    skip |= {'services/%s.html' % o for o in RETIRED} | {'services.html'}
    open(SITE + '/sitemap.xml', 'w').write(sitemap([x for x in paths if x not in skip])); open(SITE + '/llms.txt', 'w').write(llms()); open(SITE + '/llms-full.txt', 'w').write(llms_full().replace(' – ', ', '))
    # SE-015: one group for the AI crawlers; everything is allowed
    open(SITE + '/robots.txt', 'w').write(('User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nUser-agent: OAI-SearchBot\nUser-agent: ChatGPT-User\nUser-agent: ClaudeBot\nUser-agent: Claude-SearchBot\nUser-agent: Claude-User\nUser-agent: PerplexityBot\nUser-agent: Perplexity-User\nUser-agent: Google-Extended\nUser-agent: Applebot-Extended\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE) if MODE == 'prod' else 'User-agent: *\nDisallow: /\n')
    # SE-012: square icons at the root; SC-013: a disclosure contact
    for f in ('favicon.ico', 'apple-touch-icon.png'): shutil.copy('assets/' + f, SITE + '/' + f)
    open(SITE + '/site.webmanifest', 'w').write(J({'name': 'PUD Consultants', 'short_name': 'PUD', 'icons': [{'src': '/assets/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': '/assets/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}], 'theme_color': '#000000', 'background_color': '#000000', 'display': 'browser'}))
    os.makedirs(SITE + '/.well-known', exist_ok=True)
    open(SITE + '/.well-known/security.txt', 'w').write('Contact: mailto:info@pudconsultants.com\nExpires: 2027-11-24T00:00:00.000Z\nPreferred-Languages: en, ar\nCanonical: %s/.well-known/security.txt\n' % BASE)
    print('MODE', MODE, 'pages', len(paths), 'projects', len(PROJ), 'places', len(PLACES), 'countries', len(COUNTRIES), 'logos', sum(1 for p in PART if has_logo(p)))
def stub_page(url):
    # SE-001 / UX-009: old addresses forward to the new page. No noindex, so search engines pass the old URL on.
    u = E(url)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>This page has moved | PUD Consultants</title>'
            '<link rel="canonical" href="%s"><meta http-equiv="refresh" content="0; url=%s"><script>location.replace(%s)</script>'
            '<style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#000;color:#f3f3f3;font:18px/1.5 system-ui,-apple-system,Segoe UI,Arial,sans-serif}a{color:#fff}</style></head>'
            '<body><p>This page has moved. <a href="%s">Go to the new page</a>.</p></body></html>') % (E(url.split('#')[0]), u, json.dumps(url), u)

def postprocess():
    import glob
    import hashlib
    V = hashlib.md5((open('src/style.css').read() + open('src/app.js').read()).encode()).hexdigest()[:8]
    import time as _t
    B = hashlib.md5((V + open(SITE + '/index.html', encoding='utf-8').read()).encode()).hexdigest()[:10]
    if os.path.exists(SITE + '/build.txt'): os.remove(SITE + '/build.txt')  # SC-013: no longer published
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
    for ext in ('html', 'js', 'css', 'json', 'txt', 'xml', 'webmanifest'):
        for f in glob.glob(SITE + '/**/*.' + ext, recursive=True):
            try: text += open(f, encoding='utf-8').read()
            except Exception: pass
    removed = 0
    for sub in ('assets', 'fonts'):
        for f in glob.glob(SITE + '/' + sub + '/**/*', recursive=True):
            if os.path.isfile(f) and os.path.relpath(f, SITE) not in text:
                os.remove(f); removed += 1
    print('removed unreferenced files:', removed)
    # 2b. home page: below-the-fold images wait until they are near the screen (app.js loads them)
    hp = SITE + '/index.html'; t = open(hp, encoding='utf-8').read()
    def _defer(m):
        tag = m.group(0)
        if 'data-src=' in tag or 'fetchpriority="high"' in tag: return tag
        tag = re.sub(r'\ssrcset="', ' data-srcset="', tag)
        return re.sub(r'\ssrc="', ' data-src="', tag, count=1)
    t2 = re.sub(r'<img [^>]*loading="lazy"[^>]*>', _defer, t)
    open(hp, 'w', encoding='utf-8').write(t2)
    # 3. prod hosting files
    if MODE == 'prod':
        # GitHub Pages has no server redirects: old Wix addresses and short aliases get a small page that forwards
        from urllib.parse import unquote
        lines = open('data/redirects-wix.txt').read().splitlines() + ['/services  /about.html  301']
        lines += ['/projects/%s.html  /projects/%s.html  301' % (o, n) for o, n in copy5.RENAME.items()]
        lines += ['/projects/%s.html  /%s  301' % (o, n) for o, n in copy5.RETIRE.items()]
        lines += ['/projects/%s.html  /projects/%s.html  301' % (o, copy5.MERGE_INTO) for o in copy5.MERGE_FROM]
        for ln in lines:
            parts = ln.split()
            if len(parts) < 2 or ln.startswith('#'): continue
            src, dst = unquote(parts[0]).strip('/'), parts[1]
            target = os.path.join(SITE, src) if src.endswith('.html') else os.path.join(SITE, src, 'index.html')
            if not src or os.path.exists(target): continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            open(target, 'w', encoding='utf-8').write(stub_page(BASE + dst))
        open(SITE + '/CNAME', 'w').write('www.pudconsultants.com\n')
        open(SITE + '/.nojekyll', 'w').write('')
        shutil.copy('data/qc/_headers', SITE + '/_headers')
        red = open('data/qc/_redirects').read().rstrip() + '\n' + open('data/redirects-wix.txt').read()
        open(SITE + '/_redirects', 'w').write(red)

main()
postprocess()
