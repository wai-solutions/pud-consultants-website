# -*- coding: utf-8 -*-
"""Social cards (LG-001, SE-010): 1200x630 images with the site's own fonts, large enough to read in a link preview.
Run from source/:  python3 src/og.py   (needs Pillow and fonttools with brotli)"""
import os, io, json, sys, re
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); os.chdir(ROOT)
RED = (217, 58, 28)

def ttf(name):
    t = TTFont('fonts/%s.woff2' % name); t.flavor = None; b = io.BytesIO(); t.save(b); b.seek(0); return b
def antonio(size):
    f = ImageFont.truetype(ttf('antonio-latin-wght-normal'), size)
    try: f.set_variation_by_axes([700])
    except Exception: pass
    return f
def roboto(size, w='400'): return ImageFont.truetype(ttf('roboto-latin-%s-normal' % w), size)

def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def logo(h):
    lg = Image.open('assets/logo-mark.png').convert('RGBA'); lg.thumbnail((h, h)); return lg

def home_card():
    im = Image.open('assets/founder/hero.jpg').convert('RGB')
    w, h = im.size; s = max(1200 / w, 630 / h); im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    im = im.crop(((im.width - 1200) // 2, (im.height - 630) // 2, (im.width - 1200) // 2 + 1200, (im.height - 630) // 2 + 630)).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for x in range(1200): d.line((x, 0, x, 630), fill=(0, 0, 0, int(225 * max(0, 1 - x / 1000) ** 0.8)))
    im = Image.alpha_composite(im, ov); d = ImageDraw.Draw(im)
    f1 = antonio(96); y = 150
    for ln in ['URBAN PLANNING AND', 'MASTER PLANNING', 'SINCE 1966']:
        d.text((64, y), ln, font=f1, fill=(255, 255, 255) if ln != 'SINCE 1966' else (239, 66, 35)); y += 104
    d.text((66, 500), 'PUD Consultants · Cairo, Riyadh and Dubai', font=roboto(34, '700'), fill=(235, 235, 235))
    lg = logo(150); im.alpha_composite(lg, (1200 - 60 - lg.width, 50))
    im.convert('RGB').save('assets/og.jpg', quality=85, optimize=True, progressive=True)

def project_card(p, out):
    im = Image.new('RGBA', (1200, 630), (12, 12, 12, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 18, 630), fill=RED)
    f = antonio(84); lines = wrap(d, p["name"].upper(), f, 940)
    if len(lines) > 3: f = antonio(64); lines = wrap(d, p["name"].upper(), f, 940)[:4]
    y = 120
    for ln in lines: d.text((70, y), ln, font=f, fill=(255, 255, 255)); y += int(f.size * 1.08)
    place = ', '.join(x for x in (p.get('city'), p['country']) if x)
    sub = ' · '.join(x for x in (place, str(p.get('year') or '')) if x and x != 'None')
    d.text((72, y + 24), sub, font=roboto(36), fill=(210, 210, 210))
    d.text((72, 548), 'PUD Consultants · Urban planning since 1966', font=roboto(30, '700'), fill=(239, 66, 35))
    lg = logo(120); im.alpha_composite(lg, (1200 - 56 - lg.width, 48))
    im.convert('RGB').save(out, quality=82, optimize=True)

if __name__ == '__main__':
    home_card()
    if len(sys.argv) > 1:
        for p in json.load(open(sys.argv[1])): project_card(p, 'assets/og/%s.jpg' % p['slug'])
