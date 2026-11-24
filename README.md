# PUD Consultants website

Source of the website at pudconsultants.com (served for now at https://pud.vwch4.com).
PUD Consultants: urban planning, master planning and architecture, Cairo, since 1966.

## What is here

- `site/`: the finished static website, exactly as deployed. Upload this folder to any web host and it works.
- `source/`: the generator that produces the site.
  - `src/build.py` builds every page (home, 60 years, projects, countries, cities, services, guides, FAQ, people, Amr Attia, contact), plus the sitemap, robots.txt, llms.txt and structured data.
  - `src/app.js`, `atlas.js`, `paper.js`: the 3D scenes, the 60-year map and page motion (three.js and gsap).
  - `src/style.css`, `src/fonts.css`: the design.
  - `data/`: project records, partners, facts, redirects from the old Wix addresses.
  - `assets/`, `fonts/`: project images, logos, founder footage, people photos.

## Build it again

Needs Python 3 with Pillow, and Node 18+.

```
cd source
./src/bundle.sh                              # bundles the JavaScript into site/js
python3 src/build.py                         # preview build (noindex) into site/
MODE=prod SITE_DIR=$PWD/site-prod python3 src/build.py   # launch build, indexable, canonical to www.pudconsultants.com
cp -R site/js site-prod/
```

The launch build in `site-prod/` is the same as the `site/` folder in this repository (the host adds the old-address redirects in its own config; the list is in `source/data/redirects-wix.txt`).

## Rights

All text, images, logos, footage and project material belong to PUD Consultants and its named partners. All rights reserved. The code in `source/src` is shared so PUD's team and developers can maintain the site.
