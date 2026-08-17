#!/usr/bin/env python3
"""Crawl generated site/, verify internal links, images, orphans, nav, sitemap."""
import os
import re
from collections import defaultdict

BASE = "/Users/jonkennedy/retainer-reach/akiva-shapiro"
SITE = os.path.join(BASE, "site")

# --- map every URL path that actually exists to its file ---
existing = set()          # set of normalized url paths that resolve
file_for = {}
for root, _, files in os.walk(SITE):
    for fn in files:
        full = os.path.join(root, fn)
        rel = "/" + os.path.relpath(full, SITE)
        if fn == "index.html":
            url = rel[:-len("index.html")]      # "/foo/index.html" -> "/foo/"
            if url != "/":
                url = url.rstrip("/") + "/"
            existing.add(url)
            existing.add(url.rstrip("/"))       # allow no-trailing-slash
            file_for[url] = full
        else:
            existing.add(rel)                    # /404.html, /sitemap.xml, /css/style.css
            file_for[rel] = full
existing.add("/")

def resolve(href):
    """Return normalized path or None for skip."""
    h = href.strip()
    if h.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
        return None
    if h.startswith("#"):
        return None
    h = h.split("#")[0].split("?")[0]
    if not h:
        return None
    if not h.startswith("/"):
        return ("REL", h)
    return h

html_pages = {u: f for u, f in file_for.items() if f.endswith(".html")}

inbound = defaultdict(set)
broken = []          # (page, href)
broken_img = []
rel_links = []
link_count = 0

for url, path in html_pages.items():
    doc = open(path, encoding="utf-8").read()
    # internal <a href>
    for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', doc):
        r = resolve(href)
        if r is None:
            continue
        link_count += 1
        if isinstance(r, tuple):
            rel_links.append((url, href))
            continue
        norm = r if r.endswith("/") or "." in r.split("/")[-1] else r + "/"
        if norm in existing or r in existing or norm.rstrip("/") in existing:
            target = norm if norm in file_for else file_for.get(r, file_for.get(norm.rstrip("/")))
            inbound[norm.rstrip("/") + "/"].add(url)
        else:
            broken.append((url, href))
    # images / css / js
    for src in re.findall(r'<(?:img|script|link)[^>]*\b(?:src|href)="(/[^"]+\.(?:jpg|jpeg|png|webp|svg|css|js|ico))"', doc):
        if src not in existing and src not in file_for:
            broken_img.append((url, src))

# --- orphans: html pages with zero inbound internal links (excluding home, 404) ---
def norm_key(u):
    return (u.rstrip("/") + "/") if u != "/" else "/"
all_page_keys = {norm_key(u) for u in html_pages}
linked_keys = set(inbound.keys())
orphans = sorted(k for k in all_page_keys
                 if k not in linked_keys and k not in ("/", "/404.html/")
                 and "404" not in k)

# --- nav + footer link check (from homepage) ---
home = open(html_pages["/"], encoding="utf-8").read()
nav_block = re.search(r'<nav class="main".*?</nav>', home, re.S)
nav_hrefs = re.findall(r'href="([^"]+)"', nav_block.group(0)) if nav_block else []
nav_broken = [h for h in nav_hrefs if (resolve(h) and not isinstance(resolve(h), tuple)
              and (resolve(h).rstrip("/") + "/") not in existing and resolve(h) not in existing)]

# --- sitemap parity ---
sm = open(os.path.join(SITE, "sitemap.xml"), encoding="utf-8").read()
sm_urls = set(re.findall(r'<loc>https://www\.akivashapirolawpllc\.com(/[^<]*)</loc>', sm))
sm_missing_file = sorted(u for u in sm_urls if norm_key(u) not in all_page_keys and u not in existing)
indexable_pages = {k for k in all_page_keys if "404" not in k}
not_in_sitemap = sorted(k for k in indexable_pages if k not in {norm_key(u) for u in sm_urls} and k != "/404.html/")

# --- report ---
print(f"HTML pages crawled: {len(html_pages)}")
print(f"Internal <a> links checked: {link_count}")
print(f"\n== BROKEN INTERNAL LINKS: {len(broken)} ==")
for p, h in broken[:40]:
    print(f"  on {p}  ->  {h}")
print(f"\n== RELATIVE (non-root) links (should be none): {len(rel_links)} ==")
for p, h in rel_links[:20]:
    print(f"  on {p}  ->  {h}")
print(f"\n== BROKEN IMAGE/CSS/JS REFS: {len(broken_img)} ==")
for p, s in broken_img[:20]:
    print(f"  on {p}  ->  {s}")
print(f"\n== NAV LINKS BROKEN: {len(nav_broken)} ==")
for h in nav_broken:
    print("  ", h)
print(f"\n== ORPHAN PAGES (no inbound internal links): {len(orphans)} ==")
for o in orphans:
    print("  ", o)
print(f"\n== SITEMAP URLs with no file: {len(sm_missing_file)} ==")
for u in sm_missing_file:
    print("  ", u)
print(f"\n== Indexable pages NOT in sitemap: {len(not_in_sitemap)} ==")
for u in not_in_sitemap[:30]:
    print("  ", u)

# --- weakly linked (1 inbound) informational ---
weak = sorted((len(v), k) for k, v in inbound.items() if len(v) <= 1 and "404" not in k)
print(f"\n== Pages with only 1 inbound link: {len(weak)} ==")
for n, k in weak[:30]:
    print(f"  {n}  {k}")
