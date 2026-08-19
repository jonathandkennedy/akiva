#!/usr/bin/env python3
"""
Akiva Shapiro Law — high-intent landing page hub (results.* subdomain pattern).

Implements the client's Design System v1.0 PDF: Fraunces + Inter, ink navy /
brass / warm paper, sage & amber triage tags, one repeated CTA, calm motion.
Hub centerpiece (index.html) renders the fact-checked probate cornerstone copy
(landers/copy-source.json, verified against tax.ny.gov + nycourts.gov 8/15/26).

Outputs single-file HTML pages (inline CSS/JS; only external request = fonts).
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- config
PHONE_DISPLAY = "(516) 806-0762"
PHONE_TEL = "+15168060762"
EMAIL = "Akiva@AkivaShapiroLawPLLC.com"
FIRM = "Akiva Shapiro Law, PLLC"
ADDRESS = "1 West Park Drive, Old Bethpage, NY 11804"
# Same Formspree note as the main site: needs Akiva's own endpoint.
FORMSPREE_ENDPOINT = "https://formspree.io/f/REPLACE_ME"
GA4_ID = ""
# Real, verified Google Business Profile numbers (checked live 8/17/26).
G_RATING = "5.0"
G_COUNT = "34"
MAPS_URL = "https://www.google.com/maps/place/1+W+Park+Dr,+Old+Bethpage,+NY+11804/@40.7614118,-73.4663612,17z"
# Flat fee: leave empty until Akiva supplies a real number; a graceful
# no-number sentence renders instead. NEVER invent a figure here.
FLAT_FEE_LINE = ""
FLAT_FEE_FALLBACK = ("Most uncontested probate and estate administration matters at this firm "
                     "are quoted as a flat fee, set after the free 15-minute call once we know "
                     "how many distributees are involved and whether the will is self-proving.")
HUB_NOINDEX = False      # cornerstone is the organic play
LANDER_NOINDEX = True    # case-type pages are paid-traffic tools

REVIEWS = [
    {"author": "Lev Yakubov", "text": "Working with Akiva Shapiro was an outstanding experience from start to finish. He took the time to clearly explain every step of the process, making sure I fully understood my options and what to expect."},
    {"author": "J. Phinnaeus Morgan", "text": "Akiva Shapiro was recommended by a very capable estate planning attorney, to say the least — he did not disappoint."},
    {"author": "Estefany Canario", "text": "Finding a lawyer you can truly trust is rare — Akiva is one of them. He represented me for several years with honesty and dedication."},
]

GEOS = {
    "plainview": "Plainview", "hicksville": "Hicksville", "bethpage": "Bethpage",
    "syosset": "Syosset", "jericho": "Jericho", "woodbury": "Woodbury",
    "massapequa": "Massapequa", "farmingdale": "Farmingdale", "mineola": "Mineola",
    "garden-city": "Garden City", "huntington": "Huntington", "riverhead": "Riverhead",
    "levittown": "Levittown", "east-meadow": "East Meadow", "old-bethpage": "Old Bethpage",
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------------------------------------------------------------- css (design system v1.0)
CSS = """
:root{--navy:#16233A;--navy-deep:#0F1828;--brass:#A9824C;--brass-deep:#8E6C3C;
--paper:#F7F4EE;--paper-deep:#EFEAE0;--slate:#4B5566;--ink:#1C2536;--white:#fff;
--sage:#3F6E56;--sage-bg:#E7EFEA;--amber:#B4651D;--amber-bg:#F6EADF;
--line:#E3DCCE;--r:10px;--shadow:0 10px 30px rgba(16,26,44,.08);
--serif:'Fraunces',Georgia,'Times New Roman',serif;--sans:'Inter',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:120px}
body{font-family:var(--sans);font-size:16px;line-height:1.6;color:var(--slate);background:var(--paper)}
h1,h2,h3{font-family:var(--serif);font-weight:500;color:var(--navy);line-height:1.15}
h1{font-size:clamp(2.2rem,5vw,3.5rem)}
h2{font-size:clamp(1.6rem,3vw,2rem);line-height:1.2;margin:2.2em 0 .7em}
h3{font-size:1.375rem;margin:1.6em 0 .5em}
p{margin:.85em 0;max-width:68ch}
ul{margin:.85em 0 .85em 1.3em}
li{margin:.4em 0;max-width:65ch}
a{color:var(--brass-deep);text-decoration:underline;text-underline-offset:2px}
a:hover{color:var(--navy)}
img{max-width:100%;height:auto;display:block}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
.narrow{max-width:760px;margin:0 auto;padding:0 24px}
/* header */
header{background:var(--white);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50}
.hrow{display:flex;align-items:center;justify-content:space-between;gap:1em;padding:.9em 24px;max-width:1200px;margin:0 auto}
.brand{font-family:var(--serif);font-weight:600;font-size:1.15rem;color:var(--navy);text-decoration:none;white-space:nowrap}
.hlinks{display:flex;gap:1.6em;align-items:center;font-size:.92rem;font-weight:600}
.hlinks a{text-decoration:none;color:var(--ink)}
.hphone{white-space:nowrap;font-weight:700;color:var(--navy);text-decoration:none}
.btn{display:inline-block;background:var(--brass);color:#fff;font-weight:700;font-size:1rem;
padding:.9em 1.6em;border-radius:8px;text-decoration:none;border:0;cursor:pointer;
transition:background .18s ease,transform .18s ease;text-align:center}
.btn:hover{background:var(--brass-deep);color:#fff;transform:translateY(-1px)}
.btn-line{background:transparent;color:var(--navy);border:1.5px solid var(--navy)}
.btn-line:hover{background:var(--navy);color:#fff}
@media(max-width:840px){.hlinks{display:none}}
/* hero */
.hero{background:radial-gradient(900px 420px at 85% -20%,rgba(169,130,76,.22),transparent 60%),linear-gradient(160deg,var(--navy-deep),var(--navy) 70%);color:#fff;padding:clamp(60px,8vw,104px) 0}
.hero .eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--brass);margin-bottom:1.1em}
.hero h1{color:#fff;max-width:17em}
.hero .sub{color:#C9D2E0;font-size:clamp(1.05rem,1.6vw,1.22rem);max-width:38em;margin:1em 0 1.6em;line-height:1.65}
.cta-row{display:flex;gap:1.1em;align-items:center;flex-wrap:wrap}
.orcall{font-size:.85rem;color:#9FB0C8;text-transform:uppercase;letter-spacing:.1em;font-weight:700}
.orcall a{display:block;font-family:var(--serif);font-size:1.35rem;color:#fff;letter-spacing:.02em;text-decoration:none;text-transform:none}
.gbadge{display:inline-flex;align-items:center;gap:.6em;margin-top:1.6em;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);border-radius:99px;padding:.5em 1.1em;font-size:.9rem;color:#E8EDF5;text-decoration:none}
.gbadge b{color:#F4D06F;letter-spacing:.06em}
/* trust bar */
.trustbar{background:var(--white);border-bottom:1px solid var(--line)}
.trustbar .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:0;padding:0}
.tile{padding:1.15em 1em;text-align:center;border-left:1px solid var(--line);font-size:.88rem;font-weight:600;color:var(--ink)}
.tile:first-child{border-left:0}
.tile b{display:block;font-family:var(--serif);font-weight:600;font-size:1.15rem;color:var(--navy)}
@media(max-width:840px){.trustbar .wrap{grid-template-columns:repeat(2,1fr)}.tile:nth-child(3){border-left:0}}
/* jump nav */
.jump{position:sticky;top:57px;z-index:40;background:var(--paper);border-bottom:1px solid var(--line);overflow-x:auto;-webkit-overflow-scrolling:touch}
.jump .in{display:flex;gap:.4em;align-items:center;padding:.55em 24px;max-width:1200px;margin:0 auto;white-space:nowrap}
.jump span{font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--brass-deep);margin-right:.6em}
.jump a{font-size:.85rem;font-weight:600;text-decoration:none;color:var(--ink);padding:.35em .8em;border-radius:99px;border:1px solid transparent}
.jump a:hover{border-color:var(--line);background:var(--white)}
/* tags */
.tags{display:flex;gap:.6em;flex-wrap:wrap;margin:1.2em 0}
.tag{display:inline-flex;align-items:center;gap:.45em;font-size:.82rem;font-weight:700;padding:.4em .95em;border-radius:99px}
.tag::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
.tag.sage{background:var(--sage-bg);color:var(--sage)}
.tag.amber{background:var(--amber-bg);color:var(--amber)}
/* article */
article{background:var(--white)}
article .narrow{padding-top:56px;padding-bottom:56px}
article h2{padding-top:.5em;border-top:1px solid var(--line)}
article h2:first-of-type{border-top:0;margin-top:0;padding-top:0}
/* fee table */
table.fees{width:100%;border-collapse:collapse;margin:1.2em 0;font-size:.95rem;font-variant-numeric:tabular-nums}
table.fees th{background:var(--navy);color:#fff;text-align:left;padding:.7em 1em;font-weight:600;font-size:.85rem}
table.fees td{padding:.65em 1em;border-bottom:1px solid var(--line)}
table.fees tr:nth-child(even) td{background:var(--paper)}
/* steps */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:1.6em 0}
.step{background:var(--white);border:1px solid var(--line);border-top:3px solid var(--brass);border-radius:var(--r);padding:1.4em;box-shadow:var(--shadow)}
.step b{display:block;font-family:var(--serif);font-size:1.1rem;color:var(--navy);margin:.4em 0 .3em}
.step .n{font-family:var(--serif);color:var(--brass);font-size:1.6rem;font-weight:600}
@media(max-width:760px){.steps{grid-template-columns:1fr}}
/* reviews */
.reviews{background:var(--paper);padding:56px 0}
.rev-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:1.6em}
.rev{background:var(--white);border:1px solid var(--line);border-radius:var(--r);padding:1.5em;box-shadow:var(--shadow)}
.rev .stars{color:var(--brass);letter-spacing:.1em;margin-bottom:.5em}
.rev p{font-size:.94rem;font-style:italic;color:var(--ink)}
.rev footer{margin-top:.8em;font-size:.85rem;font-weight:700;color:var(--navy)}
.rev footer small{display:block;font-weight:500;color:var(--slate)}
@media(max-width:760px){.rev-grid{grid-template-columns:1fr}}
/* faq */
.faq{background:var(--white);padding:56px 0}
details{border:1px solid var(--line);border-radius:var(--r);background:var(--white);margin-bottom:10px;overflow:hidden}
summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:1em;align-items:center;
padding:1em 1.2em;font-family:var(--serif);font-size:1.06rem;color:var(--navy);font-weight:500}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";color:var(--brass);font-size:1.4rem;flex:none}
details[open] summary::after{content:"–"}
details .a{padding:0 1.2em 1.1em;font-size:.96rem}
/* form */
.formband{background:var(--navy);color:#fff;padding:64px 0}
.formband h2{color:#fff;border:0;margin-top:0}
.formband .lead{color:#C9D2E0;max-width:34em}
.fgrid{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:start}
@media(max-width:860px){.fgrid{grid-template-columns:1fr}}
.fcard{background:var(--white);border-radius:var(--r);padding:30px;box-shadow:0 18px 50px rgba(0,0,0,.25)}
.fcard label{display:block;font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--navy);margin:1em 0 .35em}
.fcard input,.fcard select,.fcard textarea{width:100%;font-family:var(--sans);font-size:1rem;padding:.7em .8em;border:1px solid var(--line);border-radius:8px;background:var(--paper);color:var(--ink)}
.fcard input:focus,.fcard select:focus,.fcard textarea:focus{outline:2px solid var(--brass);outline-offset:0;background:#fff}
.fcard textarea{min-height:96px;resize:vertical}
.fcard .btn{width:100%;margin-top:1.2em;font-size:1.05rem;padding:1em}
.micro{font-size:.78rem;color:var(--slate);margin-top:.9em;line-height:1.5}
.fside h3{color:#fff;margin-top:0}
.fside p{color:#C9D2E0;font-size:.95rem}
.fside .orcall a{font-size:1.7rem}
.hp{position:absolute;left:-9999px;opacity:0;height:0;overflow:hidden}
/* footer */
.foot{background:var(--navy-deep);color:#8FA0BA;font-size:.85rem;padding:34px 0}
.foot .wrap{display:flex;justify-content:space-between;gap:1.5em;flex-wrap:wrap}
.foot a{color:#C9D2E0;text-decoration:none}
.foot .case-links{display:flex;gap:1.2em;flex-wrap:wrap}
.disclaimer{font-size:.78rem;color:#6E7F9A;max-width:70ch;margin-top:1em}
/* motion: calm — one gentle load fade only */
@media(prefers-reduced-motion:no-preference){
.hero .eyebrow,.hero h1,.hero .sub,.hero .cta-row,.hero .gbadge{animation:rise .7s ease both}
.hero h1{animation-delay:.08s}.hero .sub{animation-delay:.18s}.hero .cta-row{animation-delay:.28s}.hero .gbadge{animation-delay:.38s}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">')

JS = """
document.addEventListener('DOMContentLoaded',function(){
  // geo swap: ?geo=plainview personalizes {GEO} tokens
  var GEOS=%GEOS%;
  try{var g=new URLSearchParams(location.search).get('geo');
    if(g&&GEOS[g.toLowerCase()]){var name=GEOS[g.toLowerCase()];
      document.querySelectorAll('[data-geo]').forEach(function(el){el.textContent=name;});}}catch(e){}
  function track(n,p){try{if(typeof gtag==='function')gtag('event',n,p||{});}catch(e){}}
  document.querySelectorAll('a[href^="tel:"]').forEach(function(a){a.addEventListener('click',function(){track('phone_call',{});});});
  var f=document.querySelector('form.lead');if(f){f.addEventListener('submit',function(){track('generate_lead',{});});}
});
"""

def head(title, desc, path, noindex, schema):
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ""
    ga = ""
    if GA4_ID:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
              f"gtag('js',new Date());gtag('config','{GA4_ID}');</script>")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">{robots}
{FONTS}
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(schema)}</script>{ga}
</head><body>"""

def header_html():
    return f"""<header><div class="hrow">
  <a class="brand" href="/">Akiva Shapiro Law</a>
  <nav class="hlinks">
    <a href="#how">How Probate Works</a><a href="#fees">Fees &amp; Timelines</a>
    <a href="#faq">FAQ</a><a class="hphone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
  </nav>
  <a class="btn" href="#contact">Free Consultation →</a>
</div></header>"""

def gbadge():
    return (f'<a class="gbadge" href="{MAPS_URL}" target="_blank" rel="noopener">'
            f'<b>★★★★★</b> {G_RATING} · {G_COUNT} Google reviews</a>')

def reviews_html(heading="Families Don't Feel Managed. Cases Just Move."):
    cards = "".join(
        f'<div class="rev"><div class="stars">★★★★★</div><p>“{esc(r["text"])}”</p>'
        f'<footer>{esc(r["author"])}<small>Verified Google review</small></footer></div>'
        for r in REVIEWS)
    return f"""<section class="reviews"><div class="wrap">
  <h2 style="border:0;margin-top:0">{esc(heading)}</h2>
  <p>Rated <b>{G_RATING}</b> across <a href="{MAPS_URL}" target="_blank" rel="noopener">{G_COUNT} Google reviews</a>.</p>
  <div class="rev-grid">{cards}</div></div></section>"""

def form_html(source, heading="Tell Us What You're Holding", sub=None):
    sub = sub or ("A name, a county, and one sentence about what's in front of you. "
                  "Akiva reviews every inquiry personally and the first call is free — "
                  "about fifteen minutes to tell you whether you're looking at a simple filing or something more.")
    return f"""<section class="formband" id="contact"><div class="wrap fgrid">
  <div class="fside">
    <h2>{esc(heading)}</h2>
    <p class="lead">{esc(sub)}</p>
    <div class="orcall" style="margin-top:1.6em">Prefer to talk now?
      <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
    <p style="margin-top:1.4em;font-size:.88rem">{esc(FIRM)} · {esc(ADDRESS)}</p>
    {gbadge()}
  </div>
  <form class="fcard lead" method="POST" action="{FORMSPREE_ENDPOINT}">
    <input type="hidden" name="_subject" value="New probate lead ({esc(source)}) — results hub">
    <input type="hidden" name="source" value="{esc(source)}">
    <input type="hidden" name="_next" value="https://www.akivashapirolawpllc.com/thank-you/">
    <p class="hp"><label>Leave blank: <input name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
    <label for="f-name">Your name</label><input id="f-name" name="name" required autocomplete="name">
    <label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel">
    <label for="f-email">Email</label><input id="f-email" name="email" type="email" required autocomplete="email">
    <label for="f-county">County</label>
    <select id="f-county" name="county"><option>Nassau</option><option>Suffolk</option><option>Not sure / other</option></select>
    <label for="f-msg">What are you holding right now?</label>
    <textarea id="f-msg" name="message" placeholder="A will, a death certificate, a question…" required></textarea>
    <button class="btn" type="submit">Request my free call</button>
    <p class="micro">Submitting this form doesn't create an attorney-client relationship — please don't include confidential or time-sensitive details. We respond the same business day whenever possible.</p>
  </form>
</div></section>"""

def footer_html(case_links=True):
    links = ""
    if case_links:
        links = '<div class="case-links">' + "".join(
            f'<a href="/{s}.html">{esc(l["short"])}</a>' for s, l in LANDERS.items()) + "</div>"
    return f"""<footer class="foot"><div class="wrap">
  <div><b style="color:#fff">{FIRM}</b><br>{ADDRESS}<br>
  <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></div>
  {links}
</div><div class="wrap"><p class="disclaimer">Attorney Advertising. Prior results do not guarantee a similar outcome. The information on this page is general information about New York law, not legal advice, and reading it does not create an attorney-client relationship. Main site: <a href="https://www.akivashapirolawpllc.com/">akivashapirolawpllc.com</a></p></div></footer>
<script>{JS.replace("%GEOS%", json.dumps(GEOS))}</script></body></html>"""

# ---------------------------------------------------------------- hub (cornerstone)
def fee_table(rows):
    tr = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in rows)
    return ('<table class="fees"><thead><tr><th>Estate value passing through court</th>'
            f'<th>Filing fee</th></tr></thead><tbody>{tr}</tbody></table>')

FEE_RE = re.compile(r"^(Less than \$[\d,]+|\$[\d,]+ to \$[\d,]+|\$[\d,]+ and above), the fee is (\$[\d,]+)$")

def hub_page():
    src = json.load(open(os.path.join(BASE, "copy-source.json")))
    body_blocks, faqs = src["body"], src["faqs"]

    # section ids for jump nav
    JUMPS = [("need", "Do I Need a Lawyer?"), ("weeks", "The First Two Weeks"),
             ("nowill", "No Will? What Happens"), ("courts", "Nassau & Suffolk Courts"),
             ("fees", "What It Costs"), ("faq", "FAQ"), ("contact", "Contact")]
    id_for_h2 = {
        "Why You Need a Probate Attorney in Long Island After a Family Member Dies": "need",
        "What Akiva Shapiro Law Handles for Nassau and Suffolk Families": "how",
        "How an Uncontested Probate Lawyer in Nassau County Gets a Will Admitted": "weeks",
        "What a Probate Administration Attorney Files When Someone Dies Without a Will": "nowill",
        "Where Long Island Probate Attorneys File in Nassau and Suffolk Surrogate’s Court": "courts",
        "What Probate Costs on Long Island and What Probate Attorneys Charge to Handle It": "fees",
    }

    html_parts, fee_rows, i = [], [], 0
    while i < len(body_blocks):
        b = body_blocks[i]
        t, k = b["t"], b["k"]
        m = FEE_RE.match(t)
        if m:
            fee_rows.append((m.group(1), m.group(2)))
            if i + 1 >= len(body_blocks) or not FEE_RE.match(body_blocks[i + 1]["t"]):
                html_parts.append(fee_table(fee_rows)); fee_rows = []
            i += 1; continue
        if k == "h2":
            sid = id_for_h2.get(t, "")
            idattr = f' id="{sid}"' if sid else ""
            html_parts.append(f"<h2{idattr}>{esc(t)}</h2>")
        elif k == "h3":
            html_parts.append(f"<h3>{esc(t)}</h3>")
        elif k == "li":
            html_parts.append(f"<ul><li>{esc(t)}</li></ul>")
        else:
            # inject flat-fee config right after the quoted-as-flat-fee sentence
            if t.startswith("Most uncontested probate and estate administration matters at this firm"):
                t = FLAT_FEE_LINE or FLAT_FEE_FALLBACK
            html_parts.append(f"<p>{esc(t)}</p>")
        i += 1
    body_html = "\n".join(html_parts).replace("<ul><li>", "<ul><li>", 1)
    body_html = re.sub(r"</ul>\s*<ul>", "", body_html)  # merge adjacent lists

    faq_html = "".join(
        f'<details><summary>{esc(f["q"])}</summary><div class="a"><p>{esc(f["a"])}</p></div></details>'
        for f in faqs)
    jump_html = "".join(f'<a href="#{jid}">{esc(lbl)}</a>' for jid, lbl in JUMPS)

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "LegalService", "name": FIRM, "telephone": PHONE_DISPLAY,
         "address": {"@type": "PostalAddress", "streetAddress": "1 West Park Drive",
                     "addressLocality": "Old Bethpage", "addressRegion": "NY", "postalCode": "11804"},
         "areaServed": ["Nassau County, NY", "Suffolk County, NY", "Long Island, NY"],
         "aggregateRating": {"@type": "AggregateRating", "ratingValue": G_RATING,
                             "reviewCount": G_COUNT, "bestRating": "5"},
         "url": "https://www.akivashapirolawpllc.com/"},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]},
    ]}

    return (head("Long Island Probate Attorney | Nassau & Suffolk County | Akiva Shapiro Law",
                 "Uncontested probate handled start to finish in Nassau & Suffolk Surrogate's Court. Free 15-minute call with attorney Akiva Shapiro: find out exactly what your case needs.",
                 "/", HUB_NOINDEX, schema)
        + header_html()
        + f"""<section class="hero"><div class="wrap">
  <div class="eyebrow">Probate &amp; Estate Administration Attorney — <span data-geo>Nassau &amp; Suffolk County</span>, NY</div>
  <h1>Long Island's Probate Attorney for Frozen Accounts and Fast Answers</h1>
  <p class="sub">If the will is real and the family agrees, your case is a paperwork problem with a deadline — not a legal fight. Free 15-minute call to find out exactly what yours needs.</p>
  <div class="cta-row">
    <a class="btn" href="#contact">Get My Free Case Review</a>
    <div class="orcall">or call now<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
  </div>
  {gbadge()}
</div></section>
<div class="trustbar"><div class="wrap">
  <div class="tile"><b>30+ Years</b>Business Experience Behind the Law Degree</div>
  <div class="tile"><b>St. John's J.D. · Duke MBA</b>Credentials, Stated Plainly</div>
  <div class="tile"><b>Free 15-Min</b>Case Review Call</div>
  <div class="tile"><b>Nassau &amp; Suffolk</b>Surrogate's Court Focus</div>
</div></div>
<div class="jump"><div class="in"><span>On this page</span>{jump_html}</div></div>
<article><div class="narrow">
<div class="tags"><span class="tag sage">Likely uncontested? Most are</span><span class="tag amber">Contested or missing heirs? We handle that too</span></div>
{body_html}
</div></article>
{reviews_html()}
<section class="faq" id="faq"><div class="narrow">
  <h2 style="border:0;margin-top:0">Frequently Asked Questions</h2>{faq_html}
</div></section>
{form_html("probate-hub", heading="Speak With a Probate Attorney Before You Sign Anything")}
""" + footer_html())

# ---------------------------------------------------------------- case-type landers
LANDERS = {
 "probate-attorney-nassau-county": {
  "short": "Probate · Nassau",
  "title": "Probate Attorney Nassau County NY | Free Case Review | Akiva Shapiro Law",
  "desc": "Nassau County probate handled start to finish at the Surrogate's Court in Mineola. Flat-fee friendly, free 15-minute case review: (516) 806-0762.",
  "eyebrow": "Probate Attorney — Nassau County, NY",
  "h1": "Nassau County Probate, Handled Start to Finish",
  "sub": "Your case will be filed at the Nassau County Surrogate's Court, 262 Old Country Road in Mineola. We prepare the petition, collect the signatures the court actually requires, and get letters testamentary issued — so the bank unfreezes the account.",
  "geo_default": "Nassau County",
  "tags": [("sage", "Uncontested probate"), ("sage", "Letters testamentary"), ("amber", "Missing-heir & citation cases")],
  "body": [
   ("Why Nassau probate stalls — and how it gets unstuck",
    "<p>The Surrogate's Court will not hand anyone authority over an estate until specific people sign specific things in a specific order. The distributees — the closest living relatives New York law recognizes — must be identified precisely, and each one either signs a waiver consenting to probate or gets formally served with a citation. One missed name resets the clock.</p><p>That is the real work of a Nassau County probate: building the family tree the court will accept, collecting waivers without drama, and filing a petition that gets through the clerk's checklist the first time. A genuinely uncontested estate typically moves in roughly two to four months; one unsigned waiver can stretch it to five to eight.</p>"),
   ("What it costs",
    "<p>Court filing fees are fixed by statute and run from $45 to $1,250 depending on the estate's value — the same in Mineola as anywhere in New York. Attorney fees are separate and negotiated; most uncontested matters at this firm are quoted as a flat fee after the free 15-minute call, once we know how many distributees are involved and whether the will is self-proving.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute review of what you're holding — will, death certificate, bank letter."),
            ("We build the file", "Petition, family tree, waivers or citations, original will to Mineola."),
            ("Letters issue", "You get certified letters testamentary — the document the bank actually wants.")],
  "faqs": [
   ("How long does probate take in Nassau County?", "A genuinely uncontested Nassau County estate typically takes roughly two to four months from filing to letters testamentary. Add an unsigned waiver, a missing distributee, or a will without a self-proving affidavit and it commonly runs five to eight months."),
   ("Where is the Nassau County Surrogate's Court?", "262 Old Country Road, 3rd Floor, Mineola, NY 11501 — phone 516-493-3800. Nassau probate filings are e-filed, and the original will must reach the court. We handle the filing logistics for you."),
   ("Do I need a lawyer to probate a will in Nassau County?", "Legally no, but the distributee list and waiver process trip up most self-filers, and one missed name resets the clock. An attorney earns their fee by getting the petition through the clerk's checklist the first time."),
   ("What does probate cost in Nassau County?", "The court's filing fee is set by statute — $45 to $1,250 based on estate value. Attorney fees are negotiated separately; most uncontested cases here are quoted flat after a free 15-minute call."),
  ]},
 "probate-attorney-suffolk-county": {
  "short": "Probate · Suffolk",
  "title": "Probate Attorney Suffolk County NY | Riverhead Surrogate's Court | Akiva Shapiro Law",
  "desc": "Suffolk County probate at the Surrogate's Court in Riverhead, handled start to finish. Free 15-minute case review with attorney Akiva Shapiro: (516) 806-0762.",
  "eyebrow": "Probate Attorney — Suffolk County, NY",
  "h1": "Suffolk County Probate Without the Runaround",
  "sub": "Your case belongs at the Suffolk County Surrogate's Court, 320 Center Drive in Riverhead. We prepare the petition, chase down the signatures, and get letters issued — while you handle everything else a death puts on a family.",
  "geo_default": "Suffolk County",
  "tags": [("sage", "Uncontested probate"), ("sage", "Estate administration"), ("amber", "Two-county & venue questions")],
  "body": [
   ("Filing in Riverhead, explained plainly",
    "<p>Suffolk probate runs through the Surrogate's Court in Riverhead. The court decides nothing until the paperwork is right: a petition that matches the death certificate and the will, a complete list of distributees, and a waiver or citation for each of them. Where the decedent owned homes in more than one county, venue follows domicile — the county that was truly home — and we sort that question before anything is filed.</p><p>A clean, uncontested Suffolk estate typically moves in roughly two to four months. The most common delays are an unsigned waiver and a will without a self-proving affidavit, both of which we plan around from day one.</p>"),
   ("What it costs",
    "<p>Filing fees are statutory — $45 to $1,250 by estate value — identical in Riverhead and Mineola. Attorney fees are negotiated; most uncontested matters are quoted as a flat fee after the free 15-minute call.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute review — we tell you if it's a simple filing or something more."),
            ("We build the file", "Petition, distributee list, waivers/citations, original will to Riverhead."),
            ("Letters issue", "Certified letters testamentary or of administration, ready for the bank.")],
  "faqs": [
   ("How long does probate take in Suffolk County?", "A genuinely uncontested Suffolk County estate typically runs roughly two to four months from filing to letters. Missing signatures, scattered witnesses, or venue questions between counties commonly push it to five to eight months."),
   ("Where is the Suffolk County Surrogate's Court?", "320 Center Drive, Riverhead, NY 11901. All Suffolk probate and administration filings go through this courthouse; we handle the filing and follow-up so you don't have to travel."),
   ("Which county do we file in if Dad owned homes in Nassau and Suffolk?", "Venue follows domicile — the county that was genuinely home: where he voted, banked, and spent most of the year. We resolve the domicile question before filing so the case isn't bounced between courts."),
   ("What does probate cost in Suffolk County?", "The court filing fee is fixed by statute at $45 to $1,250 depending on estate value. Attorney fees are separate; most uncontested cases are quoted flat after a free 15-minute call."),
  ]},
 "estate-administration-lawyer-long-island": {
  "short": "No Will / Administration",
  "title": "Estate Administration Lawyer Long Island | Died Without a Will | Akiva Shapiro Law",
  "desc": "When there's no will, New York supplies its own plan. Letters of administration for Nassau & Suffolk families — free 15-minute call: (516) 806-0762.",
  "eyebrow": "Estate Administration — No Will — Long Island, NY",
  "h1": "No Will? New York Has a Plan — We Make It Work for Your Family",
  "sub": "When someone dies without a will, the estate isn't lost and it doesn't go to the state. New York's intestacy statute decides who inherits, and the Surrogate's Court appoints an administrator — usually the closest relative willing to serve. We get you those letters of administration.",
  "geo_default": "Long Island",
  "tags": [("sage", "Letters of administration"), ("sage", "Intestate estates"), ("amber", "Kinship & missing-heir cases")],
  "body": [
   ("Who inherits and who can serve",
    "<p>New York's intestacy rules distribute the estate in a fixed order — spouse and children first, then parents, then siblings, and outward from there. The right to serve as administrator follows a statutory priority order, and every person with an equal or better right must either sign off or be formally cited. That is why an administration case usually draws more signatures than a probate case, and why building the family tree correctly is most of the battle.</p><p>Once letters of administration issue, the administrator has the same practical authority an executor would: collect the assets, pay the legitimate debts, and distribute what remains under the statute.</p>"),
   ("Small estates: the faster lane",
    "<p>If the personal property in the estate is worth under $50,000, a voluntary administration — the small-estate proceeding — may replace full administration. It is faster, cheaper, and mostly paperwork. We tell you in one call whether you qualify.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute review — we map who inherits and who can serve."),
            ("We build the file", "Administration petition, kinship proof, waivers or citations."),
            ("Letters issue", "Letters of administration — authority the bank and DMV respect.")],
  "faqs": [
   ("Who gets the estate when there's no will in New York?", "New York's intestacy statute sets the order: a surviving spouse and children share first; if there are none, parents, then siblings, then more distant relatives. The estate does not go to the state unless no eligible relative exists at all."),
   ("Who can be the administrator?", "New York gives priority in a fixed order, generally starting with the surviving spouse, then children, then other close relatives. Everyone with an equal or better right must consent or be formally cited before the court appoints an administrator."),
   ("What if the estate is small?", "If the personal property is under $50,000, a voluntary administration (small-estate proceeding) may replace full administration — faster, simpler, and inexpensive. One free call is usually enough to tell you whether you qualify."),
   ("How long does estate administration take?", "Uncontested administrations typically run on a similar clock to probate — a few months to letters — but they often need more signatures, so the timeline depends on how quickly the family's waivers come back."),
  ]},
 "small-estate-voluntary-administration-ny": {
  "short": "Small Estates",
  "title": "Small Estate Affidavit NY | Voluntary Administration Under $50,000 | Akiva Shapiro Law",
  "desc": "Under $50,000 in personal property? New York's voluntary administration is the fast, inexpensive path. We tell you in one free call if you qualify: (516) 806-0762.",
  "eyebrow": "Small Estates &amp; Voluntary Administration — New York",
  "h1": "Under $50,000? There's a Faster, Cheaper Way Through Surrogate's Court",
  "sub": "New York's voluntary administration — the small-estate proceeding — replaces full probate when the personal property is worth less than $50,000. It's mostly paperwork, the filing fee is one dollar, and it's built for exactly the situation you're probably in.",
  "geo_default": "Long Island",
  "tags": [("sage", "Small estate (under $50k)"), ("sage", "Voluntary administration"), ("amber", "Real property involved? Different path")],
  "body": [
   ("How the small-estate path works",
    "<p>The voluntary administrator — usually the closest relative — files a short affidavit with the Surrogate's Court listing the assets and the people entitled to inherit. The court issues a certificate for each asset, and that certificate is what the bank, the DMV, or the insurance company honors. No letters testamentary, no citations, no months of waiting.</p><p>The catch is the limit: only personal property counts toward the $50,000 line, and real estate owned solely by the person who died pushes the case out of the small-estate lane entirely. Getting that judgment call right at the start is exactly what the free call is for.</p>"),
   ("When small looks big (and big looks small)",
    "<p>Families are often surprised in both directions. A house owned jointly with a spouse passes outside the estate and doesn't count. Neither does a 401(k) with a named beneficiary or a payable-on-death account. A seven-figure family can qualify for voluntary administration because only one $9,000 checking account ever reached the court — and a modest family can need full probate because the house was in Dad's name alone.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute review — we tell you if you qualify for the small-estate lane."),
            ("We file the affidavit", "Short-form filing with the Surrogate's Court; $1 filing fee."),
            ("Certificates issue", "One certificate per asset — banks and the DMV honor them.")],
  "faqs": [
   ("What counts toward the $50,000 small-estate limit?", "Only personal property in the decedent's sole name — bank accounts, vehicles, uncashed checks. Jointly held assets, accounts with beneficiaries, and anything with a payable-on-death designation pass outside and don't count toward the limit."),
   ("Can I use voluntary administration if there's a house?", "Generally no — real property owned solely by the person who died takes the case out of the small-estate lane. But a house owned jointly with a surviving spouse passes automatically and doesn't disqualify the rest."),
   ("How fast is a small-estate proceeding?", "Usually weeks rather than months. It's an affidavit and certificates, not a full court proceeding with waivers and citations — which is why checking whether you qualify is always the first step."),
   ("Do I need a lawyer for a small estate?", "The form is simple; the judgment call about what counts, what passes outside the estate, and whether you actually qualify is where mistakes happen. A short flat-fee engagement typically covers the whole thing."),
  ]},
 "will-contest-lawyer-long-island": {
  "short": "Will Contests",
  "title": "Will Contest Lawyer Long Island | Estate Litigation Nassau & Suffolk | Akiva Shapiro Law",
  "desc": "Cut out of a will, or defending one? Will contests, undue influence, and fiduciary disputes in Nassau & Suffolk Surrogate's Court. Free consult: (516) 806-0762.",
  "eyebrow": "Will Contests &amp; Estate Litigation — Long Island, NY",
  "h1": "When the Will Doesn't Add Up — Or You're Defending the One That Does",
  "sub": "A sibling who suddenly inherited everything. A signature that doesn't look right. A caretaker in the will and the family out of it. Whether you're challenging a will or defending one, these cases are won on evidence and procedure in Surrogate's Court — not on volume.",
  "geo_default": "Long Island",
  "tags": [("amber", "Contested probate"), ("amber", "Undue influence & capacity"), ("sage", "Executor & trustee defense")],
  "body": [
   ("The four grounds that actually work",
    "<p>New York will contests come down to a short list: the will wasn't executed with the formalities the statute requires; the person lacked testamentary capacity; someone exerted undue influence; or the document is an outright forgery or fraud. Before objections are ever filed, the law gives you discovery — the attorney-drafter and the attesting witnesses can be examined under oath, which is often where a shaky will falls apart or a sound one proves itself.</p><p>Timing matters more than outrage. Rights narrow fast once waivers are signed, and a waiver signed early in grief is very hard to unwind. If something feels wrong, the time to talk to counsel is before you sign anything.</p>"),
   ("Executors and trustees: defense side",
    "<p>We also defend fiduciaries — executors and trustees accused of self-dealing or delay, and estates facing inflated claims. A clean accounting and a documented process end most of these disputes before trial.</p>"),
  ],
  "steps": [("Call or write", "Free, confidential read on whether you have grounds — or exposure."),
            ("Discovery first", "Examine the drafter and witnesses under oath before objections are due."),
            ("Resolve or try", "Most contests settle on the evidence; we prepare every one as if it won't.")],
  "faqs": [
   ("What are grounds to contest a will in New York?", "Improper execution, lack of testamentary capacity, undue influence, and fraud or forgery. Disliking the will's terms is not a ground — the challenge has to attack how the will was made, not what it says."),
   ("How long do I have to contest a will?", "Practically, until the will is admitted to probate — and your leverage is greatest before you sign a waiver. Once waivers are in and the will is admitted, unwinding it becomes dramatically harder. Talk to counsel before signing anything."),
   ("Who pays for a will contest?", "Each side generally bears its own fees, though in some circumstances the estate pays. Cost-benefit is case-specific — a candid first call covers whether the size of the dispute justifies the fight."),
   ("Do most will contests go to trial?", "No. Most resolve after the pre-objection examinations, when both sides can see the strength of the evidence. Preparation for trial is exactly what produces those settlements."),
  ]},
 "medicaid-planning-attorney-long-island": {
  "short": "Medicaid Planning",
  "title": "Medicaid Planning Attorney Long Island | Protect the House | Akiva Shapiro Law",
  "desc": "Nursing home costs don't have to take the house. Medicaid asset protection trusts and crisis planning for Nassau & Suffolk families. Free call: (516) 806-0762.",
  "eyebrow": "Medicaid &amp; Elder Law Planning — Long Island, NY",
  "h1": "Protect the House Before the Nursing Home Bill Arrives",
  "sub": "Long Island nursing homes can run past $150,000 a year. Medicaid pays — but only if the assets and the timing are right. Whether you're planning ahead or already in a crisis, there is almost always something worth protecting.",
  "geo_default": "Long Island",
  "tags": [("sage", "Planning ahead (5+ years out)"), ("amber", "Crisis: care needed now"), ("sage", "Home care planning window open")],
  "body": [
   ("Two clocks, two very different games",
    "<p>Nursing-home Medicaid in New York looks back five years at asset transfers, and gifts inside that window can trigger a penalty period. Home-care Medicaid is different: the 30-month lookback New York enacted in 2020 is still not being enforced as of 2026 — which means a planning window is open today for care at home that may not stay open. The right move depends entirely on which clock you're racing.</p><p>The cornerstone tool is the Medicaid Asset Protection Trust: your home goes in, you keep the right to live there for life, and after the applicable period the house is out of reach of the spend-down. Done early, it protects everything; done in a crisis, it can still protect a meaningful share.</p>"),
   ("Already in a crisis?",
    "<p>A parent entering a facility this month is not a lost cause. Spousal protections, exempt transfers, and promissory-note strategies exist precisely for late planning — but every week of delay costs options. This is the one situation where calling today genuinely matters.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute triage: planning ahead, or crisis — and which clock applies."),
            ("Plan & fund", "Trust drafted and funded correctly; applications timed to the rules."),
            ("Approval", "Medicaid coverage with the home and savings protected to the maximum the timing allows.")],
  "faqs": [
   ("Will Medicaid take my parents' house?", "Not if the planning is done right. A Medicaid Asset Protection Trust, funded early enough, removes the home from the spend-down entirely while your parents keep the right to live there. Even in a crisis, strategies exist to protect part of its value."),
   ("How does the 5-year lookback work?", "Nursing-home Medicaid reviews the 60 months before the application. Uncompensated transfers in that window create a penalty period — so transfers made more than five years out are fully protected, which is why starting early matters so much."),
   ("Is there a lookback for home care Medicaid?", "As of 2026, no — New York enacted a 30-month home-care lookback in 2020 but has repeatedly delayed enforcing it. That creates a real planning window for care at home today, though the rule could be switched on in the future."),
   ("Is it too late if Mom is already in the nursing home?", "No. Late-stage tools — spousal refusal, exempt transfers, promissory-note planning — can still protect a meaningful share of the estate. But options shrink by the week, so a crisis call should happen now, not after the first bill."),
  ]},
 "guardianship-attorney-long-island": {
  "short": "Guardianships",
  "title": "Guardianship Attorney Long Island | Article 81 | Akiva Shapiro Law",
  "desc": "When a parent can no longer manage and there's no power of attorney, Article 81 guardianship is the legal fix. Nassau & Suffolk filings. Free call: (516) 806-0762.",
  "eyebrow": "Article 81 Guardianship — Long Island, NY",
  "h1": "When a Parent Can't Manage and There's No Power of Attorney",
  "sub": "The bank won't talk to you. The doctors need a decision-maker. Dad never signed a power of attorney, and now he can't. Article 81 guardianship is New York's legal fix — and done right, it's protective, not punitive.",
  "geo_default": "Long Island",
  "tags": [("sage", "Article 81 guardianship"), ("amber", "Urgent: bills & care decisions stalled"), ("sage", "Contested guardianship defense")],
  "body": [
   ("How Article 81 actually works",
    "<p>Guardianship of an incapacitated adult in New York proceeds under Article 81 of the Mental Hygiene Law, in Supreme Court. The court appoints an evaluator to investigate and report, holds a hearing, and — where incapacity is proven — grants the guardian only the specific powers the situation requires. New York tailors guardianships narrowly on purpose: the goal is the least restrictive intervention that actually solves the problem.</p><p>A typical uncontested guardianship takes a few months from filing to appointment. Where a parent's decline is causing active harm — unpaid bills, an exploitative 'helper,' a stalled medical decision — the court can move faster on a temporary basis.</p>"),
   ("The better path, when it's still available",
    "<p>If your parent can still understand and sign documents, a durable power of attorney and health care proxy avoid guardianship entirely — cheaper, faster, private. Part of the first call is telling you honestly which side of that line your family is on.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute triage: guardianship, or a power of attorney while there's time."),
            ("Petition & hearing", "Article 81 filing, court evaluator, hearing — handled and explained."),
            ("Appointment", "Powers tailored to what your parent actually needs; you can act.")],
  "faqs": [
   ("What is Article 81 guardianship?", "New York's process for appointing a guardian for an adult who can no longer manage personal or financial affairs. It runs in Supreme Court under the Mental Hygiene Law, and the court grants only the powers the proven incapacity requires."),
   ("How long does guardianship take?", "A typical uncontested Article 81 case runs a few months from petition to appointment. Where there's active harm — financial exploitation, a stalled medical decision — courts can grant temporary powers faster."),
   ("Can we avoid guardianship?", "Yes, if your parent still has capacity to sign a durable power of attorney and health care proxy. That path is faster, cheaper, and private — and part of the first call is telling you honestly whether it's still available."),
   ("Who does the court appoint as guardian?", "Usually the family member who petitions, if suitable — but the court can appoint a neutral professional where the family is in conflict. A clean, well-documented petition is the best way to keep the appointment in the family."),
  ]},
 "estate-planning-attorney-long-island": {
  "short": "Estate Planning",
  "title": "Estate Planning Attorney Long Island | Wills, Trusts & Proxies | Akiva Shapiro Law",
  "desc": "A will, trust, power of attorney and health care proxy — built for Long Island families by a 5.0-rated attorney. Free 15-minute call: (516) 806-0762.",
  "eyebrow": "Estate Planning — Long Island, NY",
  "h1": "The Plan That Spares Your Family the Mess You're Cleaning Up",
  "sub": "Most people call an estate planner right after they've been an executor — because they've seen what no plan costs. A will, the right trust, a power of attorney, and a health care proxy: four documents that decide whether your family gets a plan or a project.",
  "geo_default": "Long Island",
  "tags": [("sage", "Wills & trusts"), ("sage", "Probate-avoidance planning"), ("amber", "Blended families & business owners")],
  "body": [
   ("What a real plan includes",
    "<p>A New York estate plan is four working parts: a will that says who gets what and who's in charge; often a revocable living trust that lets assets skip Surrogate's Court entirely; a durable power of attorney so someone can act if you can't; and a health care proxy with a living will so medical decisions never stall. For homeowners worried about long-term care, an irrevocable Medicaid asset protection trust adds a fifth part — the one that protects the house.</p><p>The difference between a $200 online will and a plan is not the paper. It's titling: a trust that was never funded, or a beneficiary form that contradicts the will, sends your family straight back into the court process you paid to avoid.</p>"),
   ("Built by someone who reads both sides",
    "<p>Akiva Shapiro spent 30 years in business operations before the law, and handles probate and estate litigation every week. The plans he drafts are shaped by watching exactly where other people's plans fail — in court, with real families, after it's too late to fix.</p>"),
  ],
  "steps": [("Call or write", "Free 15-minute conversation about your family, your house, your goals."),
            ("Plan & sign", "Documents drafted in plain English, signed with proper NY formalities."),
            ("Fund & maintain", "Trust funded, beneficiaries aligned, reviewed as life changes.")],
  "faqs": [
   ("What documents do I actually need?", "For most Long Island adults: a will, a durable power of attorney, and a health care proxy with a living will. Add a revocable trust to skip probate, and an irrevocable Medicaid trust if protecting the house from long-term-care costs is a goal."),
   ("Will vs. trust — which do I need?", "A will works through Surrogate's Court after you die; a funded revocable trust passes assets outside court, faster and privately. Many plans use both — the trust for the big assets, the will as the safety net."),
   ("How long does an estate plan take?", "Typically two to four weeks from the first conversation to signed documents — faster when there's urgency. The signing itself is one meeting with the witnesses and notary handled."),
   ("Does a trust protect my house from the nursing home?", "A revocable trust does not — you keep control, so Medicaid counts it. An irrevocable Medicaid asset protection trust does, once the applicable lookback period passes. Which one you need depends on your goals; that's the first call."),
  ]},
}

def lander_page(slug, L):
    tags = "".join(f'<span class="tag {c}">{esc(t)}</span>' for c, t in L["tags"])
    body = "".join(f'<h2>{esc(h)}</h2>{html}' for h, html in L["body"])
    steps = "".join(
        f'<div class="step"><span class="n">{i+1}</span><b>{esc(t)}</b><p style="font-size:.92rem;margin:0">{esc(d)}</p></div>'
        for i, (t, d) in enumerate(L["steps"]))
    faq_html = "".join(
        f'<details><summary>{esc(q)}</summary><div class="a"><p>{esc(a)}</p></div></details>'
        for q, a in L["faqs"])
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "LegalService", "name": FIRM, "telephone": PHONE_DISPLAY,
         "address": {"@type": "PostalAddress", "streetAddress": "1 West Park Drive",
                     "addressLocality": "Old Bethpage", "addressRegion": "NY", "postalCode": "11804"},
         "aggregateRating": {"@type": "AggregateRating", "ratingValue": G_RATING,
                             "reviewCount": G_COUNT, "bestRating": "5"}},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in L["faqs"]]},
    ]}
    return (head(L["title"], L["desc"], "/" + slug, LANDER_NOINDEX, schema)
        + header_html()
        + f"""<section class="hero"><div class="wrap">
  <div class="eyebrow">{L['eyebrow'].replace('Long Island', '<span data-geo>Long Island</span>').replace('Nassau County', '<span data-geo>Nassau County</span>').replace('Suffolk County', '<span data-geo>Suffolk County</span>')}</div>
  <h1>{esc(L['h1'])}</h1>
  <p class="sub">{esc(L['sub'])}</p>
  <div class="cta-row">
    <a class="btn" href="#contact">Get My Free Case Review</a>
    <div class="orcall">or call now<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
  </div>
  {gbadge()}
</div></section>
<div class="trustbar"><div class="wrap">
  <div class="tile"><b>30+ Years</b>Business Experience Behind the Law Degree</div>
  <div class="tile"><b>St. John's J.D. · Duke MBA</b>Credentials, Stated Plainly</div>
  <div class="tile"><b>Free 15-Min</b>Case Review Call</div>
  <div class="tile"><b>Nassau &amp; Suffolk</b>Surrogate's Court Focus</div>
</div></div>
<article><div class="narrow" style="padding-top:48px;padding-bottom:48px">
<div class="tags">{tags}</div>
{body}
<h2>How It Works</h2>
<div class="steps">{steps}</div>
</div></article>
{reviews_html()}
<section class="faq" id="faq"><div class="narrow">
  <h2 style="border:0;margin-top:0">Questions Families Ask First</h2>{faq_html}
</div></section>
{form_html(slug)}
""" + footer_html())

# ---------------------------------------------------------------- emit
def main():
    out = BASE
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(hub_page())
    for slug, L in LANDERS.items():
        open(os.path.join(out, slug + ".html"), "w", encoding="utf-8").write(lander_page(slug, L))
    print(f"emitted hub + {len(LANDERS)} landers")
    if "REPLACE_ME" in FORMSPREE_ENDPOINT:
        print("*** WARNING: forms not live — FORMSPREE_ENDPOINT is still the placeholder ***")
    if not GA4_ID:
        print("    note: GA4_ID empty — no analytics injected")

if __name__ == "__main__":
    main()
