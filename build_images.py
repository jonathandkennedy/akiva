#!/usr/bin/env python3
"""Crop/resize client photography into optimized web assets (JPEG + WebP)."""
import os
from PIL import Image, ImageOps

BASE = "/Users/jonkennedy/retainer-reach/akiva-shapiro"
SRC = os.path.join(BASE, "photos")
OUT = os.path.join(BASE, "site", "img")
os.makedirs(OUT, exist_ok=True)

# name, source, target WxH, focus (fx, fy) as fraction of frame, optional zoom
JOBS = [
    # Hero — smiling, outside the office beside the LAW OFFICE sign
    ("akiva-hero",        "headshots/DSC_5905", (760, 1013),  (0.60, 0.42)),
    ("akiva-hero@2x",     "headshots/DSC_5905", (1520, 2026), (0.60, 0.42)),
    # Author box / byline — tight head-and-shoulders crop (reads at 96px)
    ("akiva-author",      "headshots/DSC_5943", (320, 320),   (0.475, 0.26), 0.48),
    ("akiva-author@2x",   "headshots/DSC_5943", (640, 640),   (0.475, 0.26), 0.48),
    # "Meet Akiva" — seated, hands clasped, thoughtful
    ("akiva-portrait",    "headshots/DSC_5682", (720, 900),   (0.52, 0.40)),
    ("akiva-portrait@2x", "headshots/DSC_5682", (1440, 1800), (0.52, 0.40)),
    # Attorney profile rail — confident standing portrait
    ("akiva-profile",     "headshots/DSC_5633", (620, 820),   (0.52, 0.42)),
    # Social share card — full sign + office, brand + local proof
    ("og-office",         "headshots/DSC_5860", (1200, 630),  (0.50, 0.52)),
    # Office interiors
    ("office-conference", "office/DSC_6011",    (1200, 800),  (0.50, 0.50)),
    ("office-reception",  "office/DSC_6004",    (1200, 800),  (0.50, 0.52)),
    ("office-desk",       "office/DSC_5996",    (1200, 800),  (0.48, 0.50)),
    # Detail accent — scales of justice
    ("office-justice",    "office/DSC_6008",    (800, 800),   (0.42, 0.45)),
]

def focal_crop(im, target, focus, zoom=1.0):
    """Crop to target aspect around a focal point. zoom<1 tightens the crop."""
    tw, th = target
    fx, fy = focus
    sw, sh = im.size
    tar = tw / th
    src = sw / sh
    if src > tar:                      # source wider -> crop sides
        nw, nh = int(sh * tar), sh
    else:                              # source taller -> crop top/bottom
        nw, nh = sw, int(sw / tar)
    nw, nh = int(nw * zoom), int(nh * zoom)
    cx, cy = fx * sw, fy * sh
    left = max(0, min(sw - nw, int(cx - nw / 2)))
    top = max(0, min(sh - nh, int(cy - nh / 2)))
    im = im.crop((left, top, left + nw, top + nh))
    return im.resize((tw, th), Image.LANCZOS)

for job in JOBS:
    name, rel, target, focus = job[:4]
    zoom = job[4] if len(job) > 4 else 1.0
    path = os.path.join(SRC, rel + ".jpg")
    if not os.path.exists(path):
        print("MISSING:", rel)
        continue
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = focal_crop(im, target, focus, zoom)
    jpg = os.path.join(OUT, name + ".jpg")
    webp = os.path.join(OUT, name + ".webp")
    im.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
    im.save(webp, "WEBP", quality=80, method=6)
    print(f"{name:20s} {target[0]}x{target[1]}  jpg {os.path.getsize(jpg)//1024}KB  webp {os.path.getsize(webp)//1024}KB")

# favicon from the firm logo mark if present
print("\nTotal img dir:", sum(os.path.getsize(os.path.join(OUT, f))
                             for f in os.listdir(OUT)) // 1024, "KB")
