# -*- coding: utf-8 -*-
"""Live audit fixes (24 November 2026): project copy, private-owner pages, merged and retired entries.
Copy comes from PUD-approved public facts. Anything the audit marked as unsourced is removed, not reworded."""

# slug renames: old address -> new address (the old address keeps a forwarding page)
RENAME = {
 'prince-talal-hurghada-waterfront': 'private-waterfront-property-hurghada',          # CT-009
 'fawaz-alhokair-palace-extension-riyadh': 'fawaz-alhokair-residence-extension-riyadh', # CT-076
 'fawaz-alhokair-bvlgari-mansion-dubai': 'fawaz-alhokair-beachfront-residence-dubai',   # CT-077
}

# entries that leave the site: old address -> where it forwards
RETIRE = {
 'al-uqair-development': 'projects.html',  # CT-064: a file note, not a project (no client, scope or permission)
}

# CT-069: six private villa and garden pages become one entry
MERGE_INTO = 'private-villas-and-gardens-egypt'
MERGE_FROM = ['private-villa-city-view-compound', '47-compound-cairo-alexandria-desert-road', 'private-garden-mansouria',
              'private-residence-green-hills-compound', 'private-villa-cairo-suez-road', 'katameya-dunes-villas']
MERGED = dict(slug=MERGE_INTO, name='Private Villas and Gardens, Egypt', year='2005-2008', year_start=2005, country='Egypt', city='Cairo',
              lat=30.04, lon=31.24, category=['Housing', 'Landscape'], client=None, partners=[], role='Villa design, garden design and project management',
              summary='Private villas and gardens in Egypt (2005 to 2008): villa prototypes, a farm house and private gardens on the Cairo-Alexandria desert road, the Cairo-Suez road and in Katameya.',
              featured=False)

# private residences: the owner's company name stays, home details go (decision: Sawaf, 25 Nov 2026)
PRIVATE = {'fawaz-alhokair-estate-riyadh', 'fawaz-alhokair-residence-extension-riyadh', 'fawaz-alhokair-beachfront-residence-dubai', 'fawaz-alhokair-diriyah-farm-and-compound'}

OVERRIDE3 = {
 # CT-008 / CT-053
 'fawaz-alhokair-estate-riyadh': dict(city='Riyadh', featured=False, category=['Housing'],
     summary='Design management of a private estate in Riyadh: oversight across architecture, interiors and landscape, with WATG, Frantz Slater and NAGA.'),
 # CT-076
 'fawaz-alhokair-residence-extension-riyadh': dict(name='Fawaz Alhokair Residence Extension, Riyadh',
     summary='Design management of the extension of a private residence in Riyadh, with NAGA Signature Interior Design.'),
 # CT-077
 'fawaz-alhokair-beachfront-residence-dubai': dict(name='Fawaz Alhokair Beachfront Residence, Dubai', city='Dubai',
     summary='Design management of a private beachfront residence in Dubai, with NAGA Signature Interior Design.'),
 # CT-078
 'fawaz-alhokair-diriyah-farm-and-compound': dict(city='Riyadh',
     summary='Master plan for a private estate near Diriyah: a farm and a private compound. Ongoing.'),
 # CT-012
 'abo-dabbab-marine-field-station': dict(summary='Design of the Abo Dabbab marine field station at Marsa Alam on the Red Sea, for the Hurghada Environmental Protection and Conservation Association (HEPCA).'),
 # CT-054
 'alexandria-west-planning-maxx-to-km-34': dict(name='West Alexandria Regional Plan (Maxx to km 34)',
     summary='Regional plan for the area between the Maxx district (8th km) and the 34th km west of Alexandria, for NUCA, Ministry of Housing and New Communities.'),
 # CT-055
 'al-salam-oasis-master-plan': dict(summary='Master plan for an oasis along the Cairo-Alexandria desert road, for NUCA, Ministry of Housing and New Communities.'),
 # CT-056
 'marina-el-alamein-concept-master-plan': dict(summary='Concept master plan for the Marina El Alamein tourist centre on Egypt\'s North Coast, for NUCA, Ministry of Housing and New Communities.'),
 # CT-057
 'marina-el-alamein-venicia-phase-3': dict(summary='Phase 3 (Venicia) of the Marina El Alamein tourist centre, from km 104 to km 106 of the Alexandria-Matrouh coastal road, for NUCA, Ministry of Housing.'),
 # CT-058
 'north-west-coast-structure-plan': dict(summary='Structure plan for Egypt\'s North West Coast region, for NUCA, Ministry of Housing and New Communities.'),
 # CT-059
 'north-west-coast-tourism-development-planning': dict(summary='Tourism development plan for Egypt\'s North West Coast region, for the Ministry of Housing and New Communities. This 1978 plan is the start of PUD\'s tourism work.'),
 # CT-060 to CT-063
 'al-hashimi-hotel-concept-design': dict(summary='Concept design for the Al-Hashimi hotel, commercial and residential complex in Madinah, for the Al Madinah Central Area Development Authority (1995).'),
 'al-kattan-hotel-concept-design': dict(summary='Concept design for the Al Kattan hotel, commercial and residential complex in Madinah, for the Al Madinah Central Area Development Authority (1995).'),
 'al-zahem-hotel-concept-design': dict(summary='Concept design for the Al-Zahem hotel, commercial and residential complex in Madinah, for the Al Madinah Central Area Development Authority (1995).'),
 'basharia-hotel-concept-design': dict(summary='Concept design for the Basharia hotel, commercial and residential complex in Madinah, for the Al Madinah Central Area Development Authority (1994).'),
 'al-shirbini-complex-concept-design': dict(summary='Concept design for the Al Shirbini commercial and residential complex in Madinah, for the Al Madinah Central Area Development Authority.'),
 # CT-065
 'nasser-memorial-civic-center': dict(summary='Design for a memorial civic centre commemorating President Gamal Abdel Nasser, awarded first prize in a design competition (joint entry).'),
 'luxor-city-and-region-planning': dict(summary='Planning of Luxor City and its region, awarded first prize in a planning competition (joint entry).'),
 # CT-066
 'science-and-space-complex-riyadh': dict(summary='Competition design for a science and space complex in Riyadh.'),
 # CT-068
 'fragrance-factory-greiss': dict(summary='Design of a factory for fragrances and mixes in 6th of October City, for Greiss.'),
 'green-egypt-packhouse': dict(summary='Design of a packing house for agricultural produce in Giza, Egypt.'),
 'elegect-company-headquarters-cairo': dict(summary='Design of the headquarters of the Elegect Company in Cairo.'),
 'baker-atlas-plant-matrouh': dict(summary='Design of an industrial plant for Baker Atlas in Marsa Matrouh.'),
 'hostess-factory-extensions-10th-of-ramadan': dict(summary='Design of extensions to the Hostess factory in 10th of Ramadan City.'),
 # CT-070
 'khaybar-heritage-area-master-plan': dict(name='Khaybar Heritage Area: Development Brief for the Master Plan',
     summary='Development brief for the master plan of the Khaybar Heritage Area, for the Royal Commission for AlUla, with WATG. It links volcanic landscapes, archaeological sites and natural assets into one visitor route.'),
 # CT-074
 'cotton-ginning-factories-el-wadi-and-delta': dict(summary='Cotton ginning factories in Egypt for the Ministry of Agriculture, an early commission of the founder\'s practice (1964, before PUD was formally founded in 1966).'),
 # CT-067 / CT-086
 'kuwait-industrial-free-zone': dict(city=''),
 'al-ashish-urbanized-communities-kuwait': dict(city=''),
 'dream-beach-resort-gambia': dict(name='Dream Beach Resort, The Gambia', city='Atlantic coast'),
 # Tut Amun card copy (no more template line)
 'tut-amon-village-hotel-and-resort': dict(),
 # LG-016 / LG-017: logos only where the project is documented with that firm
 'organ-transplant-center-nasser-institute': dict(partners=[]),
 'ramla-concept-master-plan': dict(partners=[]),
 'makkah-township-vision-master-plan': dict(partners=[]),
 # LG-020: OBD is Osama Bukhamseen Design
 'al-aqeeq-marina-al-khiran': dict(partners=['hok', 'osama-bukhamseen-design']),
 'fayrouz-tower-kuwait': dict(city='Al Salmiya', partners=['osama-bukhamseen-design']),
}

# CT-071: drop the clause naming another firm
STRIP = {'marakia-tourist-village': (' PUD developed the initial design concept; implementation later passed to Noaman & Associates, who re-planned the site.', ' PUD developed the initial design concept (1981 to 1983).')}
