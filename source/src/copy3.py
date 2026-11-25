# -*- coding: utf-8 -*-
"""Six services, as in PUD's published service list. Slugs are kept so existing links still work;
the three retired services fold into the closest one and their old pages forward there."""
import seo, content

S = {s['slug']: s for s in seo.SERVICES}

# retired service -> where it now lives
RETIRED = {
 'sustainable-tourism-planning': 'master-planning-and-urban-design',
 'landscape-planning-and-design': 'master-planning-and-urban-design',
 'infrastructure-and-mobility-planning': 'urban-and-regional-planning',
}

def merge(into, src, para=True):
    a, b = S[into], S[src]
    if para: a['body'] = a['body'] + [b['body'][0]]
    a['points'] = a['points'] + [p for p in b['points'] if p not in a['points']][:3]
    a['cats'] = a['cats'] + [c for c in b['cats'] if c not in a['cats']]
    a['extra'] = a['extra'] + [x for x in b['extra'] if x not in a['extra']]
    a['faq'] = a['faq'] + b['faq'][:1]

merge('master-planning-and-urban-design', 'sustainable-tourism-planning')
merge('master-planning-and-urban-design', 'landscape-planning-and-design')
merge('urban-and-regional-planning', 'infrastructure-and-mobility-planning')

PROFILE = [
 ('urban-and-regional-planning', 'Urban & Regional Planning', 'Urban and regional planning',
  "We plan cities and regions: land use, mobility, infrastructure and growth, tied to national and local strategy. Examples: Egypt's North West Coast, Tanta, Mansoura and AlUla.",
  "We plan cities and regions: land use, mobility, infrastructure and growth, tied to national and local strategy. Examples: Egypt's North West Coast, Tanta, Mansoura and AlUla."),
 ('master-planning-and-urban-design', 'Urban Design & Master Planning', 'Urban design and master planning',
  'We turn a site, district or new city into a phased plan: land use, streets, public space and infrastructure. Examples: Marina El Alamein, Heliopark and New Najaf City.',
  'We turn a site, district or new city into a phased plan: land use, streets, public space and infrastructure. Examples: Marina El Alamein, Heliopark and New Najaf City.'),
 ('architecture-and-interior-design', 'Architecture & Interior Design', 'Architecture and interior design',
  'We design hotels, housing, offices and public buildings for their climate and place. Examples: Tut Amun, Hilton Dahab and the Madinah hotel complexes.',
  'We design hotels, housing, offices and public buildings for their climate and place. Examples: Tut Amun, Hilton Dahab and the Madinah hotel complexes.'),
 ('environment-and-sustainability', 'Environmentally Sustainable Development', 'Environmentally sustainable development',
  'We build water, energy, ecology and climate into a project from the first sketch. Examples: Abo Dabbab marine field station, the Green Star Hotels initiative with GIZ and Sharaan Nature Reserve.',
  'We build water, energy, ecology and climate into a project from the first sketch. Examples: Abo Dabbab marine field station, the Green Star Hotels initiative with GIZ and Sharaan Nature Reserve.'),
 ('cultural-heritage-planning', 'Cultural Heritage Planning', 'Cultural heritage planning',
  'We plan around heritage sites and historic districts so that new use does not erase what people come for. Examples: the Giza Pyramids plan with WATG, Khaybar and Historic Cairo.',
  'We plan around heritage sites and historic districts so that new use does not erase what people come for. Examples: the Giza Pyramids plan with WATG, Khaybar and Historic Cairo.'),
 ('development-consultancy-and-strategic-advisory', 'Development Consultancy & Strategic Advisory', 'Development consultancy and strategic advisory',
  'We advise governments and developers on feasibility, investment and delivery. Examples: Kidana in Makkah, the New Administrative Capital and the Riyadh Plan stakeholder engagement.',
  'We advise governments and developers on feasibility, investment and delivery. Examples: Kidana in Makkah, the New Administrative Capital and the Riyadh Plan stakeholder engagement.'),
]
LEAD_HTML = {}
new = []
for slug, name, h1, lead, html_ in PROFILE:
    s = S[slug]; s['name'] = name; s['h1'] = h1; s['lead'] = lead; LEAD_HTML[slug] = html_
    new.append(s)
seo.SERVICES[:] = new

# FAQ and article cross-links that named the retired services
for i, (q, a) in enumerate(seo.FAQ):
    if q == 'What does PUD do?':
        seo.FAQ[i] = (q, 'PUD offers six services: urban and regional planning; urban design and master planning; architecture and interior design; environmentally sustainable development; cultural heritage planning; and development consultancy and strategic advisory.')
for a in seo.ARTICLES:
    if 'related' in a:
        rel = []
        for r in a['related']:
            r = RETIRED.get(r, r)
            if r not in rel: rel.append(r)
        a['related'] = rel
