#!/bin/bash
# Bundles the JavaScript (three.js, gsap, atlas, paper scene) into site/js
cd "$(dirname "$0")/.."
[ -d node_modules ] || npm install --no-audit --no-fund
rm -rf site/js && ./node_modules/.bin/esbuild src/app.js --bundle --splitting --minify --format=esm --target=es2020 --outdir=site/js --chunk-names=c-[hash] --log-level=warning
