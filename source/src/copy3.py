# -*- coding: utf-8 -*-
"""Six services, as in the PUD company profile (2025). Slugs are kept so existing links still work;
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
 ('urban-and-regional-planning', 'Urban & Regional Planning & City Making', 'Urban and regional planning and city making',
  'We design resilient regions and vibrant cities through integrated frameworks that align land use, mobility, infrastructure and growth strategies with long-term national visions.',
  'We design <strong>resilient regions</strong> and <strong>vibrant cities</strong> through integrated frameworks that align land use, mobility, infrastructure and growth strategies with <strong>long-term national visions</strong>.'),
 ('master-planning-and-urban-design', 'Urban Design & Master Planning', 'Urban design and master planning',
  'We lead large-scale urban development, shaping mixed-use destinations and smart districts with strategic zoning, land optimisation and future-ready urban systems.',
  'We lead large-scale urban development, shaping <strong>mixed-use destinations</strong> and smart districts with <strong>strategic zoning</strong>, <strong>land optimisation</strong> and <strong>future-ready urban</strong> systems.'),
 ('architecture-and-interior-design', 'Architectural & Experiential Design', 'Architectural and experiential design',
  'We deliver context-driven, high-impact architecture across sectors, fusing aesthetics, functionality and user experience into signature landmarks and spaces.',
  'We deliver <strong>context-driven</strong>, <strong>high-impact</strong> architecture across sectors, fusing <strong>aesthetics</strong>, <strong>functionality</strong> and user <strong>experience</strong> into signature <strong>landmarks</strong> and spaces.'),
 ('environment-and-sustainability', 'Environmentally Sustainable Development', 'Environmentally sustainable development',
  'We embed sustainability into every layer: low-carbon strategies, green infrastructure and ecological systems that future-proof projects and meet global standards.',
  'We embed <strong>sustainability into every layer</strong>: low-carbon strategies, green infrastructure and ecological systems that <strong>future-proof projects and meet global standards</strong>.'),
 ('cultural-heritage-planning', 'Cultural Heritage & Identity Preservation', 'Cultural heritage and identity preservation',
  'We protect cultural identity by integrating heritage into urban and architectural design, ensuring continuity, relevance and authenticity.',
  'We protect <strong>cultural identity</strong> by integrating heritage into urban and architectural design, ensuring continuity, relevance and <strong>authenticity</strong>.'),
 ('development-consultancy-and-strategic-advisory', 'Strategic Advisory & Green Economy', 'Strategic advisory and green economy',
  'We provide end-to-end consulting and development economics, aligning vision with market feasibility, investment strategy and regenerative economic models.',
  'We provide <strong>end-to-end consulting</strong> and <strong>development economics</strong>, aligning vision with market feasibility, investment strategy and regenerative economic models.'),
]
LEAD_HTML = {}
new = []
for slug, name, h1, lead, html_ in PROFILE:
    s = S[slug]; s['name'] = name; s['h1'] = h1; s['lead'] = lead; LEAD_HTML[slug] = html_
    content.SVC_CARD[slug] = lead
    new.append(s)
seo.SERVICES[:] = new

# FAQ and article cross-links that named the retired services
for i, (q, a) in enumerate(seo.FAQ):
    if q == 'What does PUD do?':
        seo.FAQ[i] = (q, 'PUD offers six services: urban and regional planning and city making; urban design and master planning; architectural and experiential design; environmentally sustainable development; cultural heritage and identity preservation; and strategic advisory and green economy. Tourism destinations, landscape and infrastructure are planned within them.')
for a in seo.ARTICLES:
    if 'related' in a:
        rel = []
        for r in a['related']:
            r = RETIRED.get(r, r)
            if r not in rel: rel.append(r)
        a['related'] = rel
