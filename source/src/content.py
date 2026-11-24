# -*- coding: utf-8 -*-
"""Copy and sourced beats for the PUD 60-years site. Every beat comes from deliverables/pud-story/STORY-BIBLE-FINAL.md (public-YES rows)."""

TAGLINE = "Creating spaces that interact with people."
H1 = "60 years of helping people live a better life."

DECADES = [
 dict(id='1966', yr='1966', to='1975', title='The professor opens a practice',
      text='In Cairo, Prof. Abdallah Attia founds PUD in 1966. The first commissions are institutions and city fabric: university halls, bus terminals, regional plans.',
      beats=[('1966','PUD is founded in Cairo by Prof. Abdallah Abdel Aziz Attia.'),
             ('1969','Lecture halls and research institute for Ain Shams University.'),
             ('1972','Al-Tahrir bus terminals in Cairo, and the regional and urban plan for Assiut governorate.'),
             ('1973','International competition success for urban communities in Kuwait (PUD record).'),
             ('1975','Kuwait programme continues: Al-Ashish communities and low-income housing.')],
      slugs=['al-tahrir-bus-terminals','assiut-regional-and-urban-planning','al-ashish-urbanized-communities-kuwait','al-jahraa-housing-project-kuwait']),
 dict(id='1976', yr='1976', to='1985', title='The coast',
      text='The practice turns to Egypt\'s North West Coast and plans the beginnings of a tourism coastline, then designs Tut Amun on Lake Nasser.',
      beats=[('1978','Tourism development planning for the North West Coast region of Egypt.'),
             ('1979','Military Officers Club in Abu Dhabi, the first work in the UAE.'),
             ('1981','Tut Amun village hotel and resort on Lake Nasser, Aswan: designed in 1981, completed in 1984.'),
             ('1982','Structure plan for the North West Coast of Egypt.'),
             ('1985','Marina El Alamein, Phase 1: site works begin in late 1985, on a 2,000 hectare site.')],
      slugs=['tut-amon-village-hotel-and-resort','north-west-coast-tourism-development-planning','north-west-coast-structure-plan','marina-el-alamein']),
 dict(id='1986', yr='1986', to='1995', title='Marina rises, the son arrives',
      text='Marina El Alamein grows through three phases. In 1991 Amr Attia joins the practice and Hilton Dahab is designed.',
      beats=[('1989','Marina El Alamein Phase 2. A 2020 Springer paper calls the resort the first large-scale Egyptian recreation centre on the north-western coastline.'),
             ('1990','State Encouragement Prize in Architecture for Marina El Alamein (PUD record).'),
             ('1991','Amr Attia joins PUD. Hilton Dahab Village is designed the same year.'),
             ('1992','Marina El Alamein Phase 3, "Venicia", shown at the Rome Biennale.'),
             ('1994','Amr Attia\'s London master\'s thesis studies the Marina El Alamein project.')],
      slugs=['hilton-dahab-village-hotel','marina-el-alamein-venicia-phase-3','marina-matrouh']),
 dict(id='1996', yr='1996', to='2005', title='The second generation',
      text='Marina Matrouh, Sinai, Syria and Cairo. Amr Attia completes his PhD in 1999, works on the Grand Egyptian Museum competition and becomes CEO of PUD in 2005.',
      beats=[('1997','Marina Matrouh programme begins; later phases follow to 2004.'),
             ('1999','Amr Attia awarded his PhD, University of London (UCL).'),
             ('2002','Grand Egyptian Museum international competition: Amr Attia serves on the technical committee.'),
             ('2005','Amr Attia becomes CEO of PUD.')],
      slugs=['marina-latakia-master-plan-and-detailed-design','royal-oasis-sheikh-zayed','magra-el-oyoun-urban-renewal']),
 dict(id='2006', yr='2006', to='2015', title='The wider region',
      text='New cities and campuses in Iraq, Syria, Egypt and the Gulf, and a growing track record in sustainable tourism.',
      beats=[('2007','Strategic plans for Tanta and Mansoura; Amr Attia is an Eisenhower Fellow.'),
             ('2008','Master plans for Maria Heights (Homs), New Najaf City, City of Knowledge and Om El Baneen Oasis.'),
             ('2009','Abo Dabbab marine field station, and the Green Star Hotels initiative with GIZ.'),
             ('2011','Jeddah stormwater and spatial plans with AECOM Arabia.')],
      slugs=['maria-heights-tourist-complex-homs','new-najaf-city','green-star-hotels-initiative','abo-dabbab-marine-field-station']),
 dict(id='2016', yr='2016', to='2026', title='The return and the region',
      text='PUD Saudi opens in Riyadh in 2018. Work reaches AlUla, Khaybar, Makkah, the Pyramids and the next phases of a new capital.',
      beats=[('2018','PUD Saudi is co-founded in Riyadh.'),
             ('2020','Development brief for the Khaybar Heritage Area, scoping its master plan for the Royal Commission for AlUla, with WATG.'),
             ('2022','AlUla Strategic Framework Plan; Alamein Riviera vision master plan.'),
             ('2024','Giza Pyramids destination master plan: PUD is part of the WATG team as cultural-heritage specialist.'),
             ('2025','Jabal Thabeer hillside park in Makkah is first runner-up in Future Landscapes (Unbuilt) at the Landscape Middle East Awards.'),
             ('2026','Sixty years of PUD. Dr Amr Attia is Board Chairman of SHARE Egypt, the first SHARE forum in Africa, at the Grand Egyptian Museum in December.')],
      slugs=['khaybar-heritage-area-master-plan','sharaan-nature-reserve-master-plan','alamein-riviera-vision-master-plan','pyramids-plateau-destination-master-plan','jabal-thabeer-park','somou-boulevard-new-cairo']),
]

FOUNDER_FACTS = [
 ('1956','Graduates in architecture from Alexandria University and joins the faculty as a teaching assistant.'),
 ('1962','Doctorat d\'État in architecture and planning, ETH Zurich.'),
 ('1966','Founds PUD in Cairo.'),
 ('1975','Becomes Professor of Architecture.'),
 ('1990','State Encouragement Prize in Architecture, for Marina El Alamein (PUD record).'),
 ('1987','Chairs the Urban Planning Department at Ain Shams University until 1992.'),
]
FOUNDER_LOVED = [('tut-amon-village-hotel-and-resort','Tut Amun, Lake Nasser'),('hilton-dahab-village-hotel','Hilton Dahab, Gulf of Aqaba'),('marina-el-alamein','Marina El Alamein, North Coast')]
FOUNDER_LOVED_NOTE = 'Three places with strong natural conditions, a lake, a gulf and a coast, each answered with an architecture of its own.'

AMR_FACTS = [
 ('1991','Joins PUD as a planner and urban designer.'),
 ('1994','MSc, University of London (UCL): thesis on the Marina El Alamein project.'),
 ('1999','PhD, University of London (UCL), on sustainable tourism policy on Egypt\'s North West Coast.'),
 ('2005','CEO of PUD until 2011.'),
 ('2011','AECOM Arabia: Jeddah, Taif, Jazan and Makkah programmes.'),
 ('2020','WATG, Vice President for the Middle East and Africa until 2023.'),
 ('2018','Co-founds PUD Saudi in Riyadh.'),
 ('2016','Professor of Urban Planning, Ain Shams University.'),
]

OFFICES = [('Cairo, Sheikh Zayed','Polygon Building 8, Office 208, SODIC, Beverly Hills, Sheikh Zayed City 12588, Egypt','+20 100 198 1111'),
           ('Cairo, Heliopolis','115 El Thawra Street, 5th Floor, Heliopolis, Cairo 11757, Egypt','+20 2 2414 7537'),
           ('Riyadh, Diplomatic Quarter','8620 Ibn Mousa Street, 3372 Diplomatic Quarter, Riyadh 2513, Saudi Arabia','+966 540 39 8178'),
           ('Riyadh, Al Nakheel','7064 Salem bin Maaqil Street, Al Nakheel District, 4092 Riyadh 12393, Saudi Arabia','800 111 0893'),
           ('Dubai, Palm Jumeirah','Shoreline 12, Al Anbara, PH 06, Palm Jumeirah, Dubai, UAE','+971 509 29 8178'),
           ('Dubai, Jabal Ali','Office G03, Jabal Ali Industrial First, Dubai, UAE','+971 52 2510 777')]

STEPS = [
 ('01','It starts as a line on paper.','Every city we have planned began as a drawing, years before anyone moved in.'),
 ('02','The line becomes a street.','Then a block, a square, a neighbourhood. Scale changes, the care does not.'),
 ('03','Every detail changes a life on the ground.','A school within walking distance. A shaded street. A park where children play.'),
 ('04','So we plan for people first.','Spaces that interact with the people who use them. For sixty years.'),
]

FAV = {'tut-amon-village-hotel-and-resort','hilton-dahab-village-hotel','marina-el-alamein'}
OVERRIDE = {
 'tut-amon-village-hotel-and-resort': dict(summary="Tut Amun is a village hotel and resort on Lake Nasser in Aswan, designed in 1981 and completed in 1984. Its architecture follows the local Nubian tradition, in a search for a form that is both authentic and contemporary. It later received a certificate as best architectural and urban tourism project (mid-1990s)."),
 'hilton-dahab-village-hotel': dict(summary="Hilton Dahab is a village hotel on the Gulf of Aqaba in Sinai, designed in 1991 for Misr Hotels Company and built in the mid-1990s. Its rooms sit around linked lagoons below the mountains, in forms drawn from Bedouin building."),
 'marina-el-alamein': dict(summary="Master planning, detailed design and site supervision for the 2,000 hectare Marina El Alamein tourist centre on Egypt's North Coast, for NUCA, Ministry of Housing. Built in phases from 1985, it won the State Encouragement Prize in Architecture in 1990 and became the subject of Dr Amr Attia's 1994 London master's thesis."),
}

SVC_CARD = {
 'urban-and-regional-planning': 'Regional plans and city strategies that guide growth.',
 'master-planning-and-urban-design': 'Districts, destinations and new cities, planned from the street up.',
 'sustainable-tourism-planning': 'Coasts, resorts and heritage destinations that keep what visitors come for.',
 'cultural-heritage-planning': 'New development that continues the story of a place.',
 'architecture-and-interior-design': 'Hotels, campuses, offices and homes shaped by their setting.',
 'landscape-planning-and-design': 'Parks, waterfronts and open spaces that people use.',
 'environment-and-sustainability': 'Low-carbon, climate-resilient planning and green infrastructure.',
 'infrastructure-and-mobility-planning': 'Streets, tunnels, drainage and rail planned with the city.',
 'development-consultancy-and-strategic-advisory': 'Feasibility, steering committees and economics for large programmes.',
}
MILESTONES = [
 dict(y=1966, t='PUD is founded in Cairo by Prof. Abdallah Attia.', view='egypt', hold=4200),
 dict(y=1973, t='International competition success in Kuwait.', view='all', hold=3400),
 dict(y=1978, t='Tourism planning for Egypt\'s North West Coast begins.', view='coast', hold=4200),
 dict(y=1985, t='Marina El Alamein breaks ground on Egypt\'s North Coast.', view='coast', hold=3800),
 dict(y=1991, t='Amr Attia joins the practice. Hilton Dahab is designed.', view='egypt', hold=3800),
 dict(y=2005, t='Amr Attia becomes CEO of PUD.', view='all', hold=3400),
 dict(y=2008, t='New cities and campuses in Iraq and Syria.', view='iraq', hold=4200),
 dict(y=2011, t='Jeddah stormwater and spatial plans with AECOM Arabia.', view='ksa', hold=3800),
 dict(y=2018, t='PUD Saudi opens in Riyadh.', view='riyadh', hold=3800),
 dict(y=2020, t='Khaybar heritage area development brief, with WATG.', view='alula', hold=3800),
 dict(y=2024, t='PUD joins WATG\'s team on the Pyramids Plateau destination plan, as cultural-heritage specialist.', view='giza', hold=3800),
 dict(y=2025, t='Jabal Thabeer park at Mina, Makkah, is first runner-up at the Landscape Middle East Awards.', view='makkah', hold=3800),
]
