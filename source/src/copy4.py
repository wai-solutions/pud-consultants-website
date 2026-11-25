"""Copy for the About, Sustainability and Partners (expert network) pages.
Copy comes from PUD-approved public facts."""

# ---------- About ----------
ABOUT_LEAD = 'PUD (Planning & Urban Development Consultants) is an urban planning and architecture practice. Prof. Dr. Abdallah Abdel Aziz Attia founded it in Cairo in 1966.'
ABOUT_PURPOSE = 'We plan cities, regions and destinations so that they work for the people who live in them, respect the land and keep what makes each place worth visiting.'
ABOUT_WHO = [
    'PUD plans cities, regions and destinations, designs buildings and landscapes, and advises on delivery. We work from Cairo, Riyadh and Dubai, and bring in specialists from partner firms for each project.',
    'Our work runs from Egypt\'s North West Coast and Marina El Alamein to the holy sites of Makkah, AlUla and the Pyramids Plateau, for ministries, royal commissions, developers and universities.',
    'Leadership, harmony and clarity describe how we work with clients. Integrity, sustainability, innovation and excellence are the standards we hold ourselves to.',
]
ABOUT_MISSION = 'To plan and design places that fit their context, from the regional plan to the building, and to train the planners who come next.'
ABOUT_VISION = 'To be the planning partner that governments and developers in Egypt, Saudi Arabia and the Gulf call first for cities, destinations and heritage areas.'
ABOUT_VALUES = [
    ('Integrity', 'Our ethical approach underpins all our relationships and decisions.'),
    ('Sustainability', 'Environmental, social and cultural harmony in all projects.'),
    ('Innovation', 'New tools and methods, tested on real projects.'),
    ('Excellence', 'The highest standards of quality and safety.'),
]
ABOUT_ORCHESTRATION = ('Specialists for each project', 'For each project we bring in specialists from partner firms and our expert network.')
ABOUT_APPROACH_LEAD = 'Each project starts with the site, its history and the people who will use it. Then we choose the team and the method that fit it.'
ABOUT_APPROACH = [
    ('Insight-driven planning', 'Stakeholder engagement and contextual analysis.'),
    ('Scenario-based thinking', 'Options tested against changes in demand, cost and climate.'),
    ('Collaborative co-creation', 'Clients, communities and experts shape the vision together.'),
    ('Context-led design', 'Design that keeps the character of the place.'),
    ('Agile project structuring', 'Project-specific teams and phasing.'),
    ('Sustainability from the start', 'Land, water, energy and heritage considered from the first sketch.'),
]
ABOUT_AWARDS = ('More than 20 first and second prizes.', 'More than 20 first and second prizes in design and planning competitions in Egypt, Kuwait and Saudi Arabia, and the State Encouragement Prize in Architecture (1990) for Marina El Alamein. First prizes won by PUD in competitions include the Nasser Memorial Civic Centre and the planning of Luxor City and its Region (both joint entries), Al-Ashish Urbanized Communities in Kuwait and Tut Amun Village Hotel.')

# ---------- Sustainability ----------
SUS_LEDE = 'Four commitments, applied to five responsibilities: people, society, culture, the environment and the planet.'
SUS_COMMIT = [
    'Sustainability is part of how PUD plans: four commitments applied across five responsibilities. We test every plan against the same questions: does it use land, water and energy sensibly, does it include the people who live there, and does it keep what makes the place worth visiting?',
    'Projects where sustainability is the main brief include the Abo Dabbab marine field station, the Green Star Hotels initiative with GIZ and the Sharaan Nature Reserve master plan, where PUD was sustainability expert to WATG.',
]
SUS_FOUR = [
    ('Environmental responsibility', 'Minimising our ecological impact through responsible land use, energy-efficient design and environmentally sound planning strategies.'),
    ('Social inclusion', 'Creating accessible, inclusive spaces that serve diverse communities and foster a sense of belonging for all.'),
    ('Cultural heritage preservation', 'Honouring the historical and cultural identity of each place in every project, ensuring continuity and authenticity.'),
    ('Green building standards', 'International good practice and construction methods that cut energy and water use over the life of a building.'),
]
# (theme, headline, text, project slug, caption)
SUS_FIVE = [
    ('People', 'Places designed around people.', 'Every plan starts with the people who will live, work, pray and visit there: human-scale streets, shade, walkability and public spaces where communities can gather.', 'kidana-al-khaif', 'Kidana Al Khaif · Mina, Makkah'),
    ('Society', 'Inclusive, affordable, connected.', 'We plan for social inclusion: affordable housing, access to services and mixed-use neighbourhoods for every generation.', 'somou-boulevard-new-cairo', 'Somou Boulevard · New Cairo'),
    ('Culture', 'Heritage as a living foundation.', 'We read each place\'s history before we draw a line, protecting cultural landscapes and carrying local identity forward, so that new development deepens a place\'s character rather than erasing it.', 'khaybar-heritage-area-master-plan', 'Khaybar Heritage Area · AlUla'),
    ('Environment', 'Working with nature, not against it.', 'Responsible land use, protected ecosystems, water-wise landscapes and green building standards, from nature reserves in AlUla to green communities in New Cairo.', 'sharaan-nature-reserve-master-plan', 'Sharaan Nature Reserve · AlUla'),
    ('Planet', 'Resilient regions for a changing climate.', 'At regional scale we plan for compact growth, public transport and coastlines and deserts managed for the long term.', 'north-coast-regional-vision-fuka-matrouh', 'North-West Coast Regional Vision · Egypt'),
]
SUS_LENS = ['Adaptive land use', 'Ecological corridors', 'Human-centred access', 'Cultural continuity', 'Context-sensitive design: respecting natural topography, climate and ecosystems', 'Green infrastructure systems']
# (SDG number, goal, UN target text, PUD contribution)
SDGS = [  # (SDG, goal, UN target, PUD contribution, supporting projects)
    (7, 'Affordable and clean energy', 'Ensure access to affordable, reliable, sustainable and modern energy for all.', 'Energy-efficient hotels and destinations through the Green Star Hotels initiative with GIZ.', ['green-star-hotels-initiative']),
    (8, 'Decent work and economic growth', 'Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all.', 'Destinations and economic cities that create jobs and local value.', ['jazan-economic-city', 'pyramids-plateau-destination-master-plan']),
    (9, 'Industry, innovation and infrastructure', 'Build resilient infrastructure, promote inclusive and sustainable industrialisation and foster innovation.', 'Infrastructure and land strategies, from the Saudi railway network to the Suez Canal tunnels.', ['saudi-railway-land-and-property-assets-strategy', 'suez-canal-tunnels-port-said']),
    (11, 'Sustainable cities and communities', 'Make cities and human settlements inclusive, safe, resilient and sustainable.', 'Our core purpose for sixty years: new cities, districts and destinations.', ['new-administrative-capital-phases-2-4', 'marina-el-alamein']),
    (12, 'Responsible consumption and production', 'Ensure sustainable consumption and production patterns.', 'Hotels and facilities planned to use less water, energy and materials.', ['green-star-hotels-initiative', 'abo-dabbab-marine-field-station']),
    (13, 'Climate action', 'Take urgent action to combat climate change and its impacts.', 'Flood resilience and long-term regional plans for coasts and cities.', ['jeddah-stormwater-drainage-program', 'north-coast-regional-vision-fuka-matrouh']),
    (15, 'Life on land', 'Protect, restore and promote sustainable use of terrestrial ecosystems and halt biodiversity loss.', 'Protected landscapes planned for people and nature.', ['sharaan-nature-reserve-master-plan']),
    (17, 'Partnerships for the goals', 'Strengthen the means of implementation and revitalise the Global Partnership for Sustainable Development.', 'A curated network of global partners, such as WATG, AECOM and GIZ, and local experts.', ['pyramids-plateau-destination-master-plan', 'green-star-hotels-initiative']),
]
SUS_PROJECTS = ['alula-strategic-framework-plan', 'khaybar-heritage-area-master-plan', 'north-coast-regional-vision-fuka-matrouh', 'sharaan-nature-reserve-master-plan']
SUS_FAQ = [
    ('How does PUD Consultants approach sustainability?', 'Sustainability is part of how PUD plans, through four commitments: environmental responsibility, social inclusion, cultural heritage preservation and green building standards. PUD applies them across five responsibilities: people, society, culture, the environment and the planet.'),
    ('Which UN Sustainable Development Goals does PUD\'s work support?', 'PUD\'s work contributes most directly to eight of the seventeen goals: SDG 7 (affordable and clean energy), 8 (decent work and economic growth), 9 (industry, innovation and infrastructure), 11 (sustainable cities and communities), 12 (responsible consumption and production), 13 (climate action), 15 (life on land) and 17 (partnerships for the goals). Each goal is linked to PUD projects.'),
    ('Which PUD projects show its sustainability work?', 'Examples include the AlUla Strategic Framework Plan, the Abo Dabbab marine field station, the Green Star Hotels initiative with GIZ and the Sharaan Nature Reserve master plan (as sustainability expert to WATG), and the North-West Coast regional vision in Egypt.'),
]

# ---------- Partners: the expert network ----------
NET_INTRO = 'A collaborative consultants\' network that brings finance, engineering, law and sustainability expertise to every engagement.'
NET_QUOTE = 'We bring the right specialists to each project, from finance and engineering to law and sustainability.'
# (name, role, years of experience, photo)
STAFF = [
    ('Prof. Dr. Amr Attia', 'CEO and Principal', '30+', 'assets/people/amr-attia.jpg'),
    ('Eng. Mostafa Fawzy', 'Construction Director, multinational project delivery', '37+', 'assets/people/staff/mostafa-fawzy.jpg'),
    ('Dr. Essam Saleh', 'Development Manager, business development', '30+', 'assets/people/staff/essam-saleh.jpg'),
    ('Arch. Ehab Kamal', 'Senior Master Planner, architecture & landscape', '37+', 'assets/people/staff/ehab-kamal.jpg'),
    ('Arch. Ahmed Naguib', 'Senior Urban Designer, research-led city planning', '10+', 'assets/people/staff/ahmed-naguib.jpg'),
]
STRATEGIC = [
    ('Dr. Amro Taibah', ['Landscape planning, conservation and restoration of desert and coastal ecosystems', 'PhD, Urban and Regional Science', 'MSc, Construction Management']),
    ('Waleed Shaalan', ['B.Arch', 'LEED Green Associate']),
    ('Joanna M. Esty', ['JD, University of Maryland School of Law', 'MBA, Pepperdine University', 'BSc Chemical Engineering, Georgia Tech']),
    ('Abdel Nasser Taha', ['BSc Architecture', 'MBA (IPE France): strategic planning, risk and change management']),
    ('Eng. Sherif Saleh', ['Strategic finance and green economy', 'MBA, Financial Risk Management', 'MSc Project Management', 'BSc Civil Engineering']),
]
SPECIALISTS = [
    ('Dr. Tamer Elshayal', 'Urbanism & landscape', ['PhD Urban Planning and MDes Urbanism, Landscape, Ecology, Harvard University', 'MLA with highest honours, Anhalt University']),
    ('Dr. Abdullah Ghazal', 'Horticulture & landscape', ['Hohenheim University, Stuttgart', 'MSc Horticulture, University of Aleppo']),
    ('Maha El Nahas', 'Environmental design', ['BSc Environmental Design, University of Oklahoma', 'BIA competition winner: passive-solar hotel design']),
    ('Ahmed Youssef', 'Energy & management', ['BEng, MBA', 'EUREM-certified energy manager']),
    ('Shady Fayed', 'Real estate & design', ['MSc Real Estate, NYU Schack Institute', 'MSt Interdisciplinary Design for the Built Environment, University of Cambridge', 'BSc Mechanical Engineering, AUC']),
]
ENSEMBLE = [
    ('Strategic project steering', 'Lead guides in major urban initiatives, setting direction and transformation paths.'),
    ('High-profile advisory boards', 'Decoding complex challenges and offering contextualised counsel to decision-makers.'),
    ('Competition juries', 'Cross-disciplinary evaluation, as in the Al Rabita Design Competition, Makkah.'),
]
NETWORK = [
    ('Anthony Mallows', 'Former CEO, WATG · Placemaking & real estate strategy'),
    ('Dan Ringelstein', 'Former Director, SOM · City planning & mixed-use master planning'),
    ('Charles Ledward', 'Former Global Head, AECOM · Economic planning & delivery'),
    ('Dr. Alfonso Vegara', 'Founder, Fundación Metropoli · Former ISOCARP President'),
    ('Marc Stringa', 'Founder, Territorio · City-scale strategic planning'),
    ('Dr. Saleh Al Hathloul', 'Architectural identity · Arab Muslim city · Urbanism'),
    ('Prof. Fekri Hassan', 'Emeritus Professor, UCL · Cultural heritage management'),
    ('Dr. Dalila El-Kerdany', 'Cairo University · Heritage preservation & conservation'),
    ('Keith Still', 'Crowd management & crowd security'),
    ('Bernardus Djonoputro', 'Regional development & infrastructure financing'),
    ('Mohamed El Baradei', 'CEO, VS Capital · Urban branding & PPP'),
    ('Del Hossain', 'RIBA architect · Leadership & design management'),
    ('Michael Jones', 'Heritage consultant · Archaeological conservation'),
    ('Dr. Basim Omar Kadi', 'Hajj & Umrah expert'),
]
STRATEGY = ''
STRATEGY_TAGS = []

# The UN target (from sdgs.un.org) each goal card points to, paraphrased short.
SDG_TARGET = {
    7: ('7.3', 'Double the global rate of improvement in energy efficiency.'),
    8: ('8.9', 'Promote sustainable tourism that creates jobs and promotes local culture and products.'),
    9: ('9.1', 'Develop quality, reliable, sustainable and resilient infrastructure.'),
    11: ('11.3', 'Inclusive, sustainable urbanisation and participatory, integrated planning.'),
    12: ('12.b', 'Monitor the sustainable development impacts of tourism.'),
    13: ('13.1', 'Strengthen resilience and adaptive capacity to climate hazards.'),
    15: ('15.1', 'Conserve, restore and sustainably use land ecosystems.'),
    17: ('17.17', 'Encourage effective public, public-private and civil society partnerships.'),
}
# Simple line icons drawn for PUD (not the official UN icons), 24x24, stroke = currentColor.
SDG_ICON = {
    7: '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    8: '<path d="M3 21h18M6 17v-4M11 17V9M16 17v-7"/><path d="M4 9l6-5 4 3 6-4M16 3h4v4"/>',
    9: '<rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="8.5" y="4" width="7" height="7"/>',
    11: '<path d="M3 21h18M5 21V9l5-3v15M10 21V4h6v17M16 21v-9h4v9M12.5 8h1M12.5 12h1M12.5 16h1M7 12h1M7 16h1"/>',
    12: '<path d="M6.5 8.5C3 8.5 3 15.5 6.5 15.5S11 12 12 12s2.5 3.5 5.5 3.5 3.5-7 0-7S13 12 12 12 9.5 8.5 6.5 8.5z"/>',
    13: '<circle cx="12" cy="12" r="9"/><path d="M3.5 9h17M3.5 15h17M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    15: '<path d="M12 21v-7M12 14l-4-3M12 16l4-3"/><path d="M12 3c4 0 7 3 7 7 0 3-3 5-7 5s-7-2-7-5c0-4 3-7 7-7z"/><path d="M8 21h8"/>',
    17: '<circle cx="8" cy="12" r="5"/><circle cx="16" cy="12" r="5"/>',
}
