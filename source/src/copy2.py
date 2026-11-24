# -*- coding: utf-8 -*-
"""Final copy pass: short, direct, search-aware. Every claim comes from PUD material or a cited public source."""
import content, seo

# ---- decades (home timeline and 60-years page)
def _set(i, **kw): content.DECADES[i].update(kw)
_set(0, title='A professor opens a practice',
     text='Prof. Dr. Abdallah Attia founds PUD in Cairo in 1966. A university commission and a bus terminal come first, then governorate plans and, by 1973, a competition win in Kuwait.')
_set(1, title='The coast',
     text='PUD plans tourism development along Egypt\'s North West Coast and designs Tut Amun on Lake Nasser. Marina El Alamein breaks ground in 1985.')
_set(2, title='Marina El Alamein takes shape',
     text='Marina El Alamein grows through three phases and wins the State Encouragement Prize in Architecture in 1990. Amr Attia joins in 1991, the year Hilton Dahab is designed.')
_set(3, title='A second generation',
     text='Marina Matrouh, Latakia, Sheikh Zayed City and Historic Cairo. Amr Attia completes his PhD at UCL, serves on the technical committee of the Grand Egyptian Museum competition and becomes CEO in 2005.')
_set(4, title='Cities, campuses and green design',
     text='New cities and campuses in Iraq, Syria and Egypt, strategic plans for Tanta and Mansoura, then Jeddah and Taif with AECOM Arabia. A marine field station on the Red Sea and the Green Star Hotels programme with GIZ put sustainability into the portfolio.')
_set(5, title='Destinations at national scale',
     text='PUD Saudi opens in Riyadh in 2018. The work reaches AlUla, Khaybar, Makkah, the Pyramids Plateau and the next phases of Egypt\'s New Administrative Capital.')
# strip internal wording from beats
for d in content.DECADES:
    d['beats'] = [(y, t.replace(' (PUD record)', '')) for y, t in d['beats']]

content.FOUNDER_FACTS[:] = [
 ('1956', 'Graduates in architecture from Alexandria University and joins its faculty.'),
 ('1962', 'Doctorat d\'État in architecture and planning, ETH Zurich.'),
 ('1966', 'Founds PUD in Cairo.'),
 ('1975', 'Professor of Architecture.'),
 ('1987', 'Chairs the Urban Planning Department at Ain Shams University until 1992.'),
 ('1990', 'State Encouragement Prize in Architecture for Marina El Alamein.'),
]
FOUNDER_LEAD = 'He planned much of Egypt\'s North West Coast, taught a generation of planners and architects, and founded the practice that turns sixty in 2026.'
FOUNDER_BIO = ('Prof. Dr. Abdallah Attia trained in Alexandria and Zurich and founded PUD in Cairo in 1966 on one idea: planning and architecture should answer the place, not repeat a formula. '
               'He planned much of Egypt\'s North West Coast, led Marina El Alamein from master plan to site supervision, and designed Tut Amun on Lake Nasser and Hilton Dahab on the Gulf of Aqaba. '
               'Marina El Alamein won the State Encouragement Prize in Architecture in 1990. He taught as Professor of Architecture and chaired the Urban Planning Department at Ain Shams University.')

# ---- services: sharper leads
_LEADS = {
 'urban-and-regional-planning': 'We plan how cities and regions grow: land use, mobility, housing and infrastructure, aligned with national visions and tested with the people affected.',
 'master-planning-and-urban-design': 'From an empty site to a working district. We plan mixed-use destinations, communities and campuses with walkable streets, public space and phasing.',
 'sustainable-tourism-planning': 'Destinations that keep what visitors come for. We plan coasts, resorts and heritage sites that earn all year and protect their landscape and identity.',
 'cultural-heritage-planning': 'Heritage is not a backdrop. We build it into the plan, so new development continues the story of a place instead of replacing it.',
 'architecture-and-interior-design': 'Buildings that belong to their place. Hotels, campuses, offices and homes shaped by climate, setting and the people who use them.',
 'landscape-planning-and-design': 'Parks, waterfronts and open space are where a plan meets daily life. We design them to be used, easy to reach and at home in their landscape.',
 'environment-and-sustainability': 'Low-carbon, climate-resilient planning and green infrastructure, from a Red Sea marine field station to WATG\'s Sharaan Nature Reserve master plan.',
 'infrastructure-and-mobility-planning': 'Streets, tunnels, stormwater and rail planned together with the city, so networks serve neighbourhoods instead of cutting through them.',
 'development-consultancy-and-strategic-advisory': 'Plans that can be built and paid for. We link vision to feasibility, investment strategy and development economics on large programmes.',
}
for s in seo.SERVICES:
    if s['slug'] in _LEADS: s['lead'] = _LEADS[s['slug']]
_BODY0 = {
 'urban-and-regional-planning': 'Where people live, work, learn and move is decided in the plan. PUD has helped make those decisions since 1966: regional plans for Egypt\'s North West Coast, city strategies for Tanta and Mansoura, rural settlement plans across Egypt and sub-regional plans on Saudi Arabia\'s Red Sea coast.',
 'master-planning-and-urban-design': 'A master plan fixes how a place is organised: streets, public space, land uses, density, infrastructure, phasing and identity. Urban design gives it human scale, so the result is walkable, comfortable and easy to read.',
 'cultural-heritage-planning': 'Heritage sites are living places. We read the archaeology, the landscape and the community together, then give each its place in the plan.',
}
for s in seo.SERVICES:
    if s['slug'] in _BODY0: s['body'][0] = _BODY0[s['slug']]

# ---- FAQ openers
seo.FAQ[1] = ('Who is PUD Consultants?', 'PUD Consultants (Planning & Urban Development Consultants) plans cities, regions and destinations, and designs the buildings and landscapes inside them. Prof. Dr. Abdallah Attia founded the practice in Cairo in 1966, and Prof. Dr. Amr Attia leads it today from offices in Cairo, Riyadh and Dubai.')
seo.FAQ[4] = ('Who founded PUD and who leads it now?', 'Prof. Dr. Abdallah Abdel Aziz Attia founded PUD in 1966. His son, Prof. Dr. Amr Attia, joined in 1991, became CEO in 2005 and leads the practice today. He is also Professor of Urban Planning at Ain Shams University and an Eisenhower Fellow (2007).')

# ---- Amr Attia highlights and page copy
AMR_HEADLINE = 'He plans destinations from the Pyramids Plateau to Makkah, and teaches the planners who come next.'
AMR_PARAS = [
 'Prof. Dr. Amr Attia leads PUD Consultants. He joined the practice in 1991, became CEO in 2005 and co-founded PUD Saudi in Riyadh in 2018. His work includes planning frameworks for Jeddah, AlUla, the holy sites of Makkah and Egypt\'s New Administrative Capital, and the Giza Pyramids tourism master plan, where he guided the local Egyptology and heritage experts working with WATG.',
 'He is Professor of Urban Planning at Ain Shams University and holds a PhD from UCL on tourism policy on Egypt\'s North West Coast. He was selected as an Eisenhower Fellow in 2007, spent 2011 to 2020 at AECOM Arabia, rising to Principal Director, and was Vice President at WATG from 2020 to 2023.',
 'He spoke at SHARE Romania in Bucharest in 2025 and SHARE Georgia in Tbilisi in September 2026. He speaks at SHARE Kazakhstan in Almaty on 24 and 25 November 2026, and he is Board Chairman of SHARE Egypt, the first SHARE forum in Africa, at the Grand Egyptian Museum on 13 and 14 December 2026.',
]
AMR_TILES = [('2007', 'Eisenhower Fellow'), ('1991', 'Joined PUD'), ('2016', 'Professor of Urban Planning, Ain Shams University'), ('2026', 'Board Chairman, SHARE Egypt')]
AMR_PRIZES = ['Nasser Memorial Civic Centre, Egypt', 'Planning of Luxor City and its Region, Egypt', 'Al-Ashish Urbanized Communities, Kuwait', 'Tut Amun Village Hotel, Aswan, Egypt']
AMR_SPOTLIGHT = [
 dict(img='assets/people/share-egypt-committee.jpg', t='SHARE Egypt 2026 organising committee', d='Board Chairman of SHARE Egypt. The forum brings SHARE Architects to Africa for the first time.', url='https://share-architects.com/share-architects-expands-to-africa-share-egypt-2026-announced/'),
 dict(img='assets/people/share-egypt-forum.jpg', t='SHARE Egypt 2026, Grand Egyptian Museum', d='International Forum for Architecture and Urbanism, Cairo, 13 and 14 December 2026.', url='https://shareegypt2026forum.sched.com'),
 dict(img='assets/people/share-kazakhstan-speakers.jpg', t='SHARE Kazakhstan 2026, Almaty', d='Guest speaker. Master Debate on high-rise buildings in Almaty on 24 November, and the session Good Living and Working on 25 November.', url='https://sharekazakshtan2026forum.sched.com/speaker/amr.attia'),
 dict(img='assets/people/share-egypt-gem.jpg', t='SHARE Architects enters Africa', d='Announcement of the first SHARE forum on the continent, inside the Grand Egyptian Museum.', url='https://share-architects.com'),
]
AMR_GIZA = [
 dict(img='assets/people/giza-framework-1.jpg', t='Giza Pyramids tourism master plan framework', d='WATG led the plan; PUD was cultural-heritage specialist. WATG says the local Egyptologists and heritage architect worked under Prof. Dr. Amr Attia\'s guidance.'),
 dict(img='assets/people/giza-decision-framework.jpg', t='Decision framework', d='Heritage conservation, visitor experience, mobility, community benefit, economic value and resilience in one frame.'),
 dict(img='assets/people/giza-framework-2.jpg', t='The Pyramids Plateau', d='Final framework presented to the Ministry of Tourism in December 2025.'),
]
AMR_WORK = ['pyramids-plateau-destination-master-plan', 'new-administrative-capital-phases-2-4', 'somou-boulevard-new-cairo', 'jabal-thabeer-park', 'khaybar-heritage-area-master-plan', 'marina-el-alamein']

# project summaries sharpened with public SHARE sources
OVERRIDE2 = {
 'somou-boulevard-new-cairo': dict(summary='Sumou Boulevard is a mixed-use development at the gate of Mostakbal City in New Cairo, for Paragon-Adeer. It is built around a 2 km pedestrian boulevard with workspaces and leisure for young professionals. PUD supplied the subject-matter-expert group advising the steering committee that reviews the design, and supported consultant selection.'),
 'new-administrative-capital-phases-2-4': dict(summary='Egypt\'s New Administrative Capital is planned for 6.5 million residents across 220,000 feddan. PUD says it led the international Steering Committee advising ACUD on the strategic master plan for Phases 2 to 4, the 180,000 feddan beyond Phase 1, with Dar Al-Handasah as lead designer. The plan ties urban growth to ecological systems and revises the city\'s economic and development strategy.'),
}
