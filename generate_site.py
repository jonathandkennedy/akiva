#!/usr/bin/env python3
"""Static site generator for Akiva Shapiro Law, PLLC redesign.
Preserves every live URL path from the old WordPress site."""
import html as html_mod
import json
import os
import re
import shutil

BASE = "/Users/jonkennedy/retainer-reach/akiva-shapiro"
OUT = os.path.join(BASE, "site")
DOMAIN = "https://www.akivashapirolawpllc.com"
TODAY = "2026-08-17"

# --- launch config -------------------------------------------------------
# Paste the real GA4 Measurement ID (looks like "G-XXXXXXXXXX") to turn on
# analytics site-wide. Empty string = no analytics injected (clean output).
GA4_ID = ""
# Optional Google Tag Manager container ("GTM-XXXXXXX"). Empty = off.
GTM_ID = ""
# Contact-form backend: Formspree.
# PASTE AKIVA'S OWN Formspree endpoint here (formspree.io -> new form -> copy
# the /f/xxxxxxxx id). Do NOT reuse another client's endpoint — leads would be
# delivered to the wrong inbox. The build prints a loud warning while this is
# still the placeholder.
FORMSPREE_ENDPOINT = "https://formspree.io/f/REPLACE_ME"
FORM_NETLIFY = False

FIRM = "Akiva Shapiro Law, PLLC"
PHONE_DISPLAY = "(516) 806-0762"
PHONE_TEL = "+15168060762"
FAX = "(347) 710-2543"
EMAIL = "Akiva@AkivaShapiroLawPLLC.com"
ADDR = "1 West Park Drive"
CITY = "Old Bethpage"
STATE = "NY"
ZIP = "11804"
GEO = (40.7614078, -73.4641725)
MAPS_URL = "https://www.google.com/maps/place/1+W+Park+Dr,+Old+Bethpage,+NY+11804/@40.7614118,-73.4663612,17z"
BAR_URL = "https://iapps.courts.state.ny.us/attorneyservices/search?p=1"
YELP_REVIEW_URL = "https://www.yelp.com/writeareview/biz/cwEMzBl7tID_aZy1AP_MWg"
GOOGLE_REVIEW_URL = MAPS_URL  # profile link — has prominent "Write a review"; swap for a placeid deep link once confirmed
SAMEAS_PERSON = [
    "https://www.linkedin.com/in/akivashapiro/",
    "https://www.avvo.com/attorneys/11791-ny-akiva-shapiro-4676854.html",
    "https://profiles.superlawyers.com/new-york/old-bethpage/lawyer/akiva-shapiro/e6b6def9-8ccf-4b27-93d2-5b33afb48950.html",
    "https://lawyers.justia.com/lawyer/akiva-shapiro-1501200",
]
SAMEAS_FIRM = [
    "https://www.facebook.com/akivashapirolawpllc/",
    "https://www.yelp.com/biz/akiva-shapiro-law-old-bethpage-2",
    "https://profiles.superlawyers.com/new-york/old-bethpage/lawfirm/akiva-shapiro-law-pllc/52585fd5-68c2-40e2-a470-cf2d154cf4e3.html",
    "https://www.hg.org/attorney/akiva-shapiro-law-pllc/127605",
]

plan = json.load(open(os.path.join(BASE, "site-plan.json")))
pages = {p["slug"]: p for p in json.load(open(os.path.join(BASE, "pages.json")))}
CLUSTERS = plan["clusters"]
LOCAL = json.load(open(os.path.join(BASE, "local-data.json")))
G_RATING = LOCAL["google"]["rating"]
G_COUNT = LOCAL["google"]["review_count"]
G_REVIEWS = LOCAL["google"]["reviews"]
TOWNS = json.load(open(os.path.join(BASE, "towns.json")))

def town_slug(name):
    return "estate-planning-attorney-" + name.lower().replace(" ", "-") + "-ny"

# ---------------------------------------------------------------- helpers
def esc(s):
    return html_mod.escape(str(s), quote=True)

def read_article(slug):
    path = os.path.join(BASE, "articles", slug + ".json")
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path))
    except Exception as e:
        print("BAD JSON:", slug, e)
        return None

def title_for_article(h1):
    t = h1.rstrip("?").strip()
    full = f"{h1} | Akiva Shapiro Law"
    return full if len(full) <= 62 else h1

# ---------------------------------------------------------------- CSS
CSS = r"""
:root{--navy:#0E1E3A;--navy-deep:#0A1628;--navy-soft:#16305C;--gold:#C7A458;--gold-soft:#E4CB8E;
--paper:#F7F4EE;--ink:#1B2432;--muted:#5A6578;--line:#E6E1D6;--white:#fff;
--serif:"Fraunces",Georgia,serif;--sans:"Inter",-apple-system,"Segoe UI",sans-serif;
--maxw:1140px;--r:14px;--shadow:0 10px 30px rgba(10,22,40,.10)}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{font-family:var(--sans);color:var(--ink);background:var(--white);line-height:1.65;font-size:16.5px}
img{max-width:100%;display:block}
a{color:var(--navy-soft);text-decoration:none}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 22px}
h1,h2,h3,.serif{font-family:var(--serif);font-weight:600;line-height:1.18;color:var(--navy);letter-spacing:-.01em}
h1{font-size:clamp(1.9rem,4.2vw,3.1rem)}
h2{font-size:clamp(1.5rem,3vw,2.15rem)}
h3{font-size:1.22rem}
.kicker{font-family:var(--sans);font-size:.78rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-bottom:.7rem}
.lead{font-size:1.12rem;color:var(--muted);max-width:46em}
section{padding:72px 0}
.center{text-align:center}.center .lead{margin-inline:auto}
/* buttons */
.btn{display:inline-flex;align-items:center;gap:.55em;font-weight:600;font-size:1rem;padding:.9em 1.6em;border-radius:10px;transition:.18s;cursor:pointer;border:2px solid transparent}
.btn-gold{background:var(--gold);color:var(--navy-deep)}
.btn-gold:hover{background:var(--gold-soft);transform:translateY(-1px)}
.btn-outline{border-color:rgba(255,255,255,.55);color:#fff}
.btn-outline:hover{border-color:var(--gold);color:var(--gold-soft)}
.btn-navy{background:var(--navy);color:#fff}
.btn-navy:hover{background:var(--navy-soft)}
.btn-line{border-color:var(--navy);color:var(--navy)}
.btn-line:hover{background:var(--navy);color:#fff}
/* topbar */
.topbar{background:var(--navy-deep);color:#C8D2E4;font-size:.83rem;padding:.5em 0}
.topbar .wrap{display:flex;justify-content:space-between;gap:1em;align-items:center}
.topbar a{color:var(--gold-soft);font-weight:600}
.topbar .tb-hours{opacity:.85}
/* header */
header.site{position:sticky;top:0;z-index:60;background:#fff;border-bottom:1px solid var(--line);box-shadow:0 2px 14px rgba(10,22,40,.06)}
.nav-row{display:flex;align-items:center;justify-content:space-between;gap:1.2em;padding:.75em 0}
.logo{display:flex;flex-direction:column;line-height:1.12}
.logo .l1{font-family:var(--serif);font-weight:700;font-size:1.28rem;color:var(--navy);letter-spacing:.02em}
.logo .l2{font-size:.66rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--gold)}
nav.main{display:flex;align-items:center;gap:.2em}
nav.main>div{position:relative}
nav.main a.top{display:block;padding:.7em .8em;font-weight:600;font-size:.94rem;color:var(--ink);border-radius:8px}
nav.main a.top:hover{color:var(--navy-soft);background:var(--paper)}
.drop{position:absolute;top:100%;left:0;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);min-width:270px;padding:.5em;display:none;z-index:70}
nav.main>div:hover .drop,nav.main>div:focus-within .drop{display:block}
.drop a{display:block;padding:.5em .8em;border-radius:8px;font-size:.92rem;color:var(--ink)}
.drop a:hover{background:var(--paper);color:var(--navy-soft)}
.drop .d-label{font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);padding:.55em .8em .25em}
.nav-cta{white-space:nowrap;padding:.7em 1.2em;font-size:.94rem}
.burger{display:none;background:none;border:0;width:44px;height:44px;cursor:pointer;position:relative}
.burger span{display:block;height:2px;background:var(--navy);margin:5px 8px;transition:.2s}
/* hero */
.hero{background:radial-gradient(1100px 520px at 78% -10%,rgba(199,164,88,.16),transparent 60%),linear-gradient(160deg,var(--navy-deep),var(--navy) 55%,var(--navy-soft));color:#fff;padding:84px 0 92px}
.hero-grid{display:grid;grid-template-columns:1.25fr .75fr;gap:56px;align-items:center}
.hero h1{color:#fff;margin:.35em 0 .45em}
.hero h1 em{font-style:normal;color:var(--gold-soft)}
.hero .lead{color:#C8D2E4;font-size:1.16rem}
.hero-ctas{display:flex;gap:14px;flex-wrap:wrap;margin:1.7em 0 1.3em}
.chips{display:flex;flex-wrap:wrap;gap:.6em;padding:0;list-style:none;font-size:.86rem}
.chips li{border:1px solid rgba(228,203,142,.4);color:var(--gold-soft);padding:.35em .85em;border-radius:99px}
.hero-photo{position:relative}
.hero-photo img{border-radius:var(--r);box-shadow:0 24px 60px rgba(0,0,0,.42);border:1px solid rgba(228,203,142,.35)}
.hero-photo::after{content:"";position:absolute;inset:18px -18px -18px 18px;border:2px solid var(--gold);border-radius:var(--r);z-index:-1;opacity:.55}
.hero-badge{position:absolute;left:-14px;bottom:-16px;background:#fff;color:var(--navy);border-radius:12px;padding:.65em 1em;font-size:.8rem;font-weight:600;box-shadow:var(--shadow);display:flex;gap:.5em;align-items:center}
.hero-badge b{color:var(--gold);font-size:1rem}
/* pillars */
.pillars{background:var(--white)}
.pillar-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-top:44px}
.pillar{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:var(--r);padding:30px 28px;box-shadow:0 4px 18px rgba(10,22,40,.05);transition:.2s}
.pillar:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
.pillar h3{font-size:1.45rem;margin-bottom:.2em}
.pillar .tag{font-size:.8rem;color:var(--muted);margin-bottom:1em;display:block}
.pillar ul{list-style:none;margin:.9em 0 1.1em}
.pillar li{padding:.34em 0;border-bottom:1px dashed var(--line);font-size:.95rem}
.pillar li:last-child{border:0}
.pillar a.all{font-weight:600;color:var(--navy-soft);font-size:.95rem}
.pillar a.all::after{content:" →"}
/* alternating */
.band{background:var(--paper)}
.split{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.split .photo img{border-radius:var(--r);box-shadow:var(--shadow)}
blockquote.pull{font-family:var(--serif);font-size:1.35rem;line-height:1.45;color:var(--navy);border-left:4px solid var(--gold);padding-left:1.1em;margin:1.2em 0}
/* testimonials */
.t-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-top:44px}
.t-card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:28px;box-shadow:0 4px 18px rgba(10,22,40,.05);display:flex;flex-direction:column}
.t-card .stars{color:var(--gold);letter-spacing:.15em;font-size:.95rem;margin-bottom:.8em}
.t-card p{font-size:.97rem;flex:1}
.t-card footer{margin-top:1.2em;font-size:.86rem;color:var(--muted)}
.t-card footer b{color:var(--ink);display:block;font-size:.92rem}
/* faq teaser + article lists */
.q-list{margin-top:36px;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.q-item{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 22px;display:flex;justify-content:space-between;align-items:center;gap:1em;font-weight:600;color:var(--navy);transition:.15s}
.q-item:hover{border-color:var(--gold);box-shadow:0 4px 18px rgba(10,22,40,.07)}
.q-item span.arr{color:var(--gold);font-size:1.2rem}
/* local */
.local-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:start}
.nap{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:30px;box-shadow:0 4px 18px rgba(10,22,40,.05)}
.nap dt{font-size:.74rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--gold);margin-top:1.1em}
.nap dt:first-child{margin-top:0}
.nap dd{font-size:1rem}
.nap dd a{font-weight:600}
/* CTA band */
.cta-band{background:linear-gradient(135deg,var(--navy-deep),var(--navy-soft));color:#fff;text-align:center;padding:76px 0}
.cta-band h2{color:#fff}
.cta-band p{color:#C8D2E4;max-width:44em;margin:.8em auto 1.6em}
/* breadcrumbs & article */
.crumbs{font-size:.82rem;color:var(--muted);padding:18px 0 0}
.crumbs a{color:var(--muted)}
.crumbs a:hover{color:var(--navy-soft)}
.article-head{padding:26px 0 8px}
.article-head h1{max-width:20em}
.meta-row{display:flex;flex-wrap:wrap;align-items:center;gap:1em;margin:1.2em 0 0;font-size:.86rem;color:var(--muted)}
.meta-row .chip{background:var(--paper);border:1px solid var(--line);border-radius:99px;padding:.3em .9em;font-weight:600;color:var(--navy-soft)}
.byline{display:flex;align-items:center;gap:.6em}
.byline img{width:34px;height:34px;border-radius:50%;object-fit:cover}
.byline b{color:var(--ink)}
article.body{max-width:760px;padding:8px 0 40px}
article.body>section{padding:0}
article.body p,article.body ul,article.body ol{margin:0 0 1.15em;color:#2A3342}
article.body ul,article.body ol{padding-left:1.3em}
article.body li{margin-bottom:.45em}
article.body h2{margin:1.6em 0 .6em;font-size:1.5rem}
.direct{font-size:1.12rem;background:var(--paper);border-left:4px solid var(--gold);border-radius:0 12px 12px 0;padding:1.2em 1.4em;margin:1.4em 0 1.8em}
.direct p{margin:0;color:var(--ink)}
.takeaways{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:var(--r);padding:26px 30px;margin:2.2em 0;box-shadow:0 4px 18px rgba(10,22,40,.05)}
.takeaways h2{font-size:1.15rem;margin:0 0 .7em}
.takeaways ul{margin:0;padding-left:1.2em}
.takeaways li{margin:.4em 0}
/* video facade */
.video-facade{position:relative;aspect-ratio:16/9;background:linear-gradient(150deg,var(--navy-deep),var(--navy-soft));border-radius:var(--r);display:flex;align-items:center;justify-content:center;flex-direction:column;gap:.8em;cursor:pointer;margin:1.6em 0 2em;overflow:hidden;border:1px solid var(--line)}
.video-facade:hover .play{transform:scale(1.08)}
.video-facade .play{width:76px;height:76px;border-radius:50%;background:var(--gold);display:flex;align-items:center;justify-content:center;transition:.2s;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.video-facade .play::after{content:"";border-style:solid;border-width:14px 0 14px 24px;border-color:transparent transparent transparent var(--navy-deep);margin-left:6px}
.video-facade span{color:#C8D2E4;font-size:.9rem;font-weight:600;letter-spacing:.06em}
.video-facade iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
/* author box */
.author-box{display:grid;grid-template-columns:96px 1fr;gap:24px;background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:var(--r);padding:28px;margin:2.6em 0 1.4em}
.author-box img{width:96px;height:96px;border-radius:50%;object-fit:cover;border:3px solid #fff;box-shadow:0 4px 14px rgba(10,22,40,.15)}
.author-box .ab-kicker{font-size:.72rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);margin-bottom:.25em}
.author-box h3{margin:0 0 .35em;font-size:1.2rem}
.author-box p{font-size:.93rem;color:#2A3342;margin:0 0 .7em}
.author-box .ab-links{font-size:.87rem;font-weight:600;display:flex;flex-wrap:wrap;gap:.4em 1.2em}
.author-box .ab-links a{color:var(--navy-soft);border-bottom:1px solid var(--gold);padding-bottom:1px}
.disclaimer{font-size:.8rem;color:var(--muted);border-top:1px solid var(--line);padding-top:1.2em;margin-top:1em}
/* content tables */
article.body table,.content-main table{width:100%;border-collapse:collapse;margin:1.4em 0;font-size:.96rem;box-shadow:0 4px 18px rgba(10,22,40,.05);border-radius:12px;overflow:hidden}
article.body th,.content-main th{background:var(--navy);color:#fff;text-align:left;padding:.8em 1em;font-family:var(--sans);font-weight:600;font-size:.9rem}
article.body td,.content-main td{padding:.75em 1em;border-bottom:1px solid var(--line)}
article.body tbody tr:nth-child(even),.content-main tbody tr:nth-child(even){background:var(--paper)}
.table-scroll{overflow-x:auto}
/* FAQ accordion */
.faq-wrap{margin:2.2em 0}
.faq-item{border:1px solid var(--line);border-radius:12px;margin-bottom:12px;background:#fff;overflow:hidden;box-shadow:0 2px 10px rgba(10,22,40,.04)}
.faq-item summary{cursor:pointer;padding:1.05em 1.3em;font-family:var(--serif);font-weight:600;color:var(--navy);font-size:1.08rem;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1em}
.faq-item summary::-webkit-details-marker{display:none}
.faq-item summary::after{content:"+";color:var(--gold);font-size:1.5rem;font-weight:400;flex:none;transition:transform .2s}
.faq-item[open] summary::after{transform:rotate(45deg)}
.faq-item summary:hover{background:var(--paper)}
.faq-item .faq-a{padding:0 1.3em 1.15em;color:#2A3342}
.faq-item .faq-a p{margin:0}
/* related */
.related{background:var(--paper);padding:56px 0 72px}
.rel-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:26px}
/* practice pages */
.page-hero{background:linear-gradient(160deg,var(--navy-deep),var(--navy) 60%,var(--navy-soft));color:#fff;padding:64px 0}
.page-hero h1{color:#fff;max-width:18em}
.page-hero .lead{color:#C8D2E4}
.page-hero .hero-ctas{margin:1.6em 0 0}
.content-grid{display:grid;grid-template-columns:1fr 340px;gap:56px;padding:56px 0;align-items:start}
.content-main h2{margin:1.5em 0 .6em}
.content-main p,.content-main ul{margin-bottom:1.15em;color:#2A3342}
.content-main ul{padding-left:1.3em}
.rail{position:sticky;top:96px;display:flex;flex-direction:column;gap:22px}
.rail-card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:26px;box-shadow:0 4px 18px rgba(10,22,40,.05)}
.rail-card.gold{background:linear-gradient(150deg,var(--navy-deep),var(--navy-soft));color:#fff;border:0}
.rail-card.gold h3{color:#fff}
.rail-card.gold p{color:#C8D2E4;font-size:.92rem}
.rail-card h3{margin-bottom:.5em}
.rail-card ul{list-style:none;font-size:.92rem}
.rail-card li{padding:.4em 0;border-bottom:1px dashed var(--line)}
.rail-card li:last-child{border:0}
.rail-card .btn{width:100%;justify-content:center;margin-top:1em}
/* footer */
footer.site{background:var(--navy-deep);color:#AEB9CC;font-size:.92rem;padding:64px 0 0}
.f-grid{display:grid;grid-template-columns:1.3fr 1fr 1fr 1.2fr;gap:44px;padding-bottom:44px}
footer.site h4{color:#fff;font-family:var(--serif);font-size:1.05rem;margin-bottom:1em}
footer.site a{color:#AEB9CC;display:block;padding:.22em 0}
footer.site a:hover{color:var(--gold-soft)}
.f-brand .l1{font-family:var(--serif);color:#fff;font-size:1.25rem;font-weight:700}
.f-brand .l2{color:var(--gold);font-size:.68rem;letter-spacing:.18em;text-transform:uppercase;margin-bottom:1em}
.f-legal{border-top:1px solid rgba(255,255,255,.12);padding:1.4em 0;font-size:.78rem;color:#7E8BA3}
.f-legal .wrap{display:flex;flex-wrap:wrap;gap:.5em 2em;justify-content:space-between}
/* contact form */
.form-card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:32px;box-shadow:var(--shadow)}
.form-card h2{margin:0 0 .3em}
.contact-form{display:grid;gap:16px;margin-top:1.4em}
.contact-form .row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.field{display:flex;flex-direction:column;gap:.35em}
.field label{font-size:.82rem;font-weight:600;color:var(--navy)}
.field label .req{color:#B4472F}
.field input,.field select,.field textarea{font-family:var(--sans);font-size:1rem;padding:.7em .85em;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);width:100%}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgba(199,164,88,.18)}
.field textarea{min-height:130px;resize:vertical}
.consent{display:flex;gap:.6em;align-items:flex-start;font-size:.85rem;color:var(--muted)}
.consent input{margin-top:.25em;flex:none}
.form-hp{position:absolute;left:-9999px;opacity:0;height:0;overflow:hidden}
.form-note{font-size:.82rem;color:var(--muted);margin-top:.4em}
.contact-form button{width:100%;justify-content:center;font-size:1.05rem;padding:1em}
/* review buttons */
.review-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.btn-review-google{background:#fff;color:#3c4043;border:1px solid var(--line);box-shadow:0 3px 12px rgba(10,22,40,.08)}
.btn-review-google:hover{box-shadow:0 6px 18px rgba(10,22,40,.14);transform:translateY(-1px)}
.btn-review-google .g-mark{font-weight:700;font-family:var(--serif);background:conic-gradient(from -45deg,#EA4335 0 25%,#FBBC05 0 50%,#34A853 0 75%,#4285F4 0);-webkit-background-clip:text;background-clip:text;color:transparent;font-size:1.15rem;line-height:1}
.btn-review-yelp{background:#d32323;color:#fff}
.btn-review-yelp:hover{background:#af1e1e;transform:translateY(-1px)}
/* sticky mobile bar */
.mobile-bar{display:none;position:fixed;bottom:0;left:0;right:0;z-index:80;background:var(--navy-deep);box-shadow:0 -6px 22px rgba(0,0,0,.3);grid-template-columns:1fr 1fr}
.mobile-bar a{display:flex;align-items:center;justify-content:center;gap:.5em;padding:1em;font-weight:700;font-size:.95rem;color:#fff}
.mobile-bar a.call{background:var(--gold);color:var(--navy-deep)}
/* forms-ish contact */
.hours-table{width:100%;border-collapse:collapse;font-size:.95rem}
.hours-table td{padding:.5em 0;border-bottom:1px dashed var(--line)}
.hours-table td:last-child{text-align:right;font-weight:600;color:var(--navy)}
.map-frame{border:0;width:100%;height:340px;border-radius:var(--r);box-shadow:var(--shadow)}
/* responsive */
@media(max-width:1000px){
 .hero-grid,.split,.local-grid,.content-grid{grid-template-columns:1fr;gap:40px}
 .pillar-grid,.t-grid{grid-template-columns:1fr;gap:18px}
 .q-list,.rel-grid{grid-template-columns:1fr}
 .f-grid{grid-template-columns:1fr 1fr;gap:30px}
 .rail{position:static}
 .hero{padding:56px 0 64px}
 .hero-photo{max-width:420px}
 nav.main{display:none;position:fixed;inset:64px 0 0 0;background:#fff;flex-direction:column;align-items:stretch;padding:1em 1.4em;overflow:auto;gap:0;z-index:90}
 nav.main.open{display:flex}
 nav.main a.top{font-size:1.1rem;padding:.9em .4em;border-bottom:1px solid var(--line);border-radius:0}
 .drop{position:static;display:block;border:0;box-shadow:none;padding:0 0 .6em .8em;min-width:0}
 .drop a{font-size:.98rem;padding:.45em .4em}
 .nav-cta{display:none}
 .burger{display:block}
 .mobile-bar{display:grid}
 body{padding-bottom:56px}
 .topbar .tb-hours{display:none}
 section{padding:52px 0}
}
@media(max-width:560px){.f-grid{grid-template-columns:1fr}.author-box{grid-template-columns:1fr}.author-box img{width:80px;height:80px}}
"""

JS = r"""
document.addEventListener('DOMContentLoaded',function(){
  var b=document.querySelector('.burger'),n=document.querySelector('nav.main');
  if(b&&n){b.addEventListener('click',function(){n.classList.toggle('open');b.classList.toggle('x');});
    n.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){n.classList.remove('open');});});}
  document.querySelectorAll('.video-facade').forEach(function(v){
    v.addEventListener('click',function(){
      if(v.dataset.loaded)return;v.dataset.loaded='1';
      var f=document.createElement('iframe');
      f.src='https://player.vimeo.com/video/'+v.dataset.vid+'?autoplay=1';
      f.allow='autoplay; fullscreen; picture-in-picture';f.allowFullscreen=true;
      f.title=v.dataset.title||'Video';v.appendChild(f);
    });});
  // conversion tracking — no-ops if analytics isn't loaded
  function track(name,params){try{if(typeof gtag==='function'){gtag('event',name,params||{});}
    if(window.dataLayer){window.dataLayer.push(Object.assign({event:name},params||{}));}}catch(e){}}
  document.querySelectorAll('a[href^="tel:"]').forEach(function(a){
    a.addEventListener('click',function(){track('phone_call',{link_url:a.getAttribute('href')});});});
  document.querySelectorAll('a[href^="mailto:"]').forEach(function(a){
    a.addEventListener('click',function(){track('email_click',{});});});
  var cf=document.querySelector('.contact-form');
  if(cf){cf.addEventListener('submit',function(){track('generate_lead',{form:'contact'});});}
});
"""

# ---------------------------------------------------------------- schema
def firm_schema():
    return {
        "@type": ["LegalService", "Attorney"],
        "@id": DOMAIN + "/#firm",
        "name": FIRM,
        "url": DOMAIN + "/",
        "image": DOMAIN + "/img/akiva-shapiro-attorney.jpg",
        "telephone": PHONE_TEL,
        "faxNumber": FAX,
        "email": EMAIL,
        "priceRange": "Free phone consultation",
        "address": {"@type": "PostalAddress", "streetAddress": ADDR,
                    "addressLocality": CITY, "addressRegion": STATE,
                    "postalCode": ZIP, "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "hasMap": MAPS_URL,
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "09:30", "closes": "17:30"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "09:30", "closes": "16:00"},
        ],
        "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in
                       ["Nassau County, NY", "Suffolk County, NY", "Long Island, NY", "Queens, NY", "New York"]],
        "founder": {"@id": DOMAIN + "/#akiva"},
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(G_RATING), "reviewCount": str(G_COUNT),
            "bestRating": "5", "worstRating": "1",
        },
        "review": [
            {"@type": "Review",
             "author": {"@type": "Person", "name": r["author"]},
             "datePublished": r["date"],
             "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"},
             "reviewBody": r["text"]}
            for r in G_REVIEWS
        ],
        "sameAs": SAMEAS_FIRM,
    }

def person_schema():
    return {
        "@type": "Person",
        "@id": DOMAIN + "/#akiva",
        "name": "Akiva Shapiro, Esq.",
        "givenName": "Akiva", "familyName": "Shapiro",
        "honorificSuffix": "Esq.",
        "jobTitle": "Attorney and Counselor-at-Law",
        "image": DOMAIN + "/img/akiva-author.jpg",
        "worksFor": {"@id": DOMAIN + "/#firm"},
        "url": DOMAIN + "/attorney-profile/akiva-shapiro-esq/",
        "alumniOf": [
            {"@type": "CollegeOrUniversity", "name": "St. John's University School of Law"},
            {"@type": "CollegeOrUniversity", "name": "Duke University, Fuqua School of Business"},
            {"@type": "CollegeOrUniversity", "name": "Iona College"},
        ],
        "memberOf": [
            {"@type": "Organization", "name": "New York State Bar Association"},
            {"@type": "Organization", "name": "American Bar Association"},
            {"@type": "Organization", "name": "New York State Academy of Trial Lawyers"},
            {"@type": "Organization", "name": "WealthCounsel"},
        ],
        "knowsAbout": ["Estate Planning", "Wills and Trusts", "Probate", "Estate Litigation",
                       "Medicaid Planning", "Guardianship", "Asset Protection",
                       "Civil Litigation", "Commercial Litigation", "Appeals"],
        "sameAs": SAMEAS_PERSON,
    }

def website_schema():
    return {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/",
            "name": FIRM, "publisher": {"@id": DOMAIN + "/#firm"}}

def breadcrumbs_schema(crumbs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u}
        for i, (n, u) in enumerate(crumbs)]}

# ---------------------------------------------------------------- chrome
def nav_html():
    def drop_links(paths):
        out = []
        for p in paths:
            pg = pages.get(p.strip("/").replace("/", "__"))
            label = LABELS.get(p, (pg["h1"] if pg and pg["h1"] else p.strip("/").replace("-", " ").title()))
            out.append(f'<a href="{p}/">{esc(label)}</a>')
        return "".join(out)
    return f"""
<div class="topbar"><div class="wrap">
  <div>Free Phone Consultation: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
  <div class="tb-hours">By appointment · Mon–Thu 9:30–5:30 · Fri 9:30–4:00 · <a href="mailto:{EMAIL}">{EMAIL}</a></div>
</div></div>
<header class="site"><div class="wrap nav-row">
  <a href="/" class="logo" aria-label="{FIRM} home">
    <span class="l1">Akiva Shapiro Law</span>
    <span class="l2">A Personal Attorney · Life · Business · Legacy</span>
  </a>
  <nav class="main" aria-label="Main">
    <div><a class="top" href="/life/">Life ▾</a><div class="drop">
      <span class="d-label">Personal Legal Matters</span>
      {drop_links(["/lawsuits-civil-litigation","/trusts-asset-protection","/medicaid-trusts-and-applications","/medicaid-fair-hearings","/guardianships","/landlord-tenant","/divorce-and-family-law","/pre-post-nuptial-agreements","/property-tax-grievance","/ny-lemon-law-for-faulty-automobiles"])}
    </div></div>
    <div><a class="top" href="/business/">Business ▾</a><div class="drop">
      <span class="d-label">Business Counsel</span>
      {drop_links(["/commercial-litigation","/appellate-practice","/business-asset-protection","/mergers-acquisitions","/commercial-leasing","/lease-negotiation","/collection-of-unpaid-debts","/mechanics-liens","/off-shore-family-limited-liability-companies-partnerships"])}
    </div></div>
    <div><a class="top" href="/legacy/">Legacy ▾</a><div class="drop">
      <span class="d-label">Estate &amp; Elder Law</span>
      {drop_links(["/estate-planning","/wills","/trusts","/probate","/estate-litigation","/ny-deeds-for-out-of-state-trusts"])}
    </div></div>
    <div><a class="top" href="/faq/">Legal Answers</a></div>
    <div><a class="top" href="/attorney-profile/akiva-shapiro-esq/">About</a></div>
    <div><a class="top" href="/testimonials/">Testimonials</a></div>
    <div><a class="top" href="/contact-us/">Contact</a></div>
  </nav>
  <a class="btn btn-gold nav-cta" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
  <button class="burger" aria-label="Menu"><span></span><span></span><span></span></button>
</div></header>"""

def footer_html():
    return f"""
<footer class="site"><div class="wrap">
 <div class="f-grid">
  <div class="f-brand">
    <div class="l1">Akiva Shapiro Law, PLLC</div>
    <div class="l2">A Personal Attorney for Your Life, Business &amp; Legacy</div>
    <p>Estate planning, elder law, probate and litigation counsel for Long Island families and business owners — from one attorney who knows your whole picture.</p>
  </div>
  <div>
    <h4>Practice Areas</h4>
    <a href="/estate-planning/">Estate Planning</a>
    <a href="/trusts-asset-protection/">Trusts &amp; Asset Protection</a>
    <a href="/medicaid-trusts-and-applications/">Medicaid Planning</a>
    <a href="/guardianships/">Guardianships</a>
    <a href="/probate/">Probate</a>
    <a href="/estate-litigation/">Estate Litigation</a>
    <a href="/lawsuits-civil-litigation/">Civil Litigation</a>
    <a href="/commercial-litigation/">Commercial Litigation</a>
  </div>
  <div>
    <h4>Resources</h4>
    <a href="/faq/">Legal Answers Library</a>
    <a href="/attorney-profile/akiva-shapiro-esq/">Meet Akiva Shapiro, Esq.</a>
    <a href="/who-we-are/">Who We Are</a>
    <a href="/testimonials/">Client Testimonials</a>
    <a href="/attorney-profile/webinars/">Webinars</a>
    <a href="/areas-we-serve/">Areas We Serve</a>
    <a href="/review-attorney-akiva-shapiro/">Leave a Review</a>
    <a href="/privacy-policy/">Privacy Policy</a>
  </div>
  <div>
    <h4>Contact</h4>
    <p>{ADDR}<br>{CITY}, {STATE} {ZIP}<br>
    Tel: <a style="display:inline" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br>
    Fax: {FAX}<br>
    <a style="display:inline" href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p style="margin-top:.8em"><a style="display:inline" href="{MAPS_URL}" rel="noopener" target="_blank">Get directions →</a></p>
  </div>
 </div>
</div>
<div class="f-legal"><div class="wrap">
  <span>© 2026 {FIRM}. All rights reserved.</span>
  <span>Attorney Advertising. Prior results do not guarantee a similar outcome. This site provides general information, not legal advice.</span>
</div></div></footer>
<div class="mobile-bar">
  <a class="call" href="tel:{PHONE_TEL}">📞 Call Now</a>
  <a href="/contact-us/">Free Consultation</a>
</div>
<script src="/js/main.js" defer></script>"""

def head_html(title, desc, path, schema_extra=None, noindex=False, og_image=None):
    graph = [website_schema(), firm_schema(), person_schema()]
    if schema_extra:
        graph += schema_extra if isinstance(schema_extra, list) else [schema_extra]
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ""
    og = og_image or (DOMAIN + "/img/og-office.jpg")
    analytics = ""
    if GA4_ID:
        analytics += (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
            f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
            f"gtag('js',new Date());gtag('config','{GA4_ID}');</script>")
    if GTM_ID:
        analytics += (
            f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});"
            f"var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            f"j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})"
            f"(window,document,'script','dataLayer','{GTM_ID}');</script>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{DOMAIN}{path}">
{robots}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{FIRM}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{DOMAIN}{path}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
<script type="application/ld+json">{schema}</script>
{analytics}
</head>
<body>{('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM_ID + '" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>') if GTM_ID else ''}"""

def crumbs_html(crumbs):
    inner = ' <span aria-hidden="true">›</span> '.join(
        f'<a href="{u}">{esc(n)}</a>' if i < len(crumbs) - 1 else f"<span>{esc(n)}</span>"
        for i, (n, u) in enumerate(crumbs))
    return f'<div class="wrap crumbs" aria-label="Breadcrumb">{inner}</div>'

def author_box():
    return f"""
<aside class="author-box">
  <img src="/img/akiva-author.jpg" alt="Akiva Shapiro, Esq., Long Island attorney" width="96" height="96" loading="lazy">
  <div>
    <div class="ab-kicker">Written &amp; Reviewed By</div>
    <h3>Akiva Shapiro, Esq.</h3>
    <p>Akiva Shapiro is the founding attorney of {FIRM} in Old Bethpage, Long Island — a personal attorney for your life, business, and legacy. Admitted to the New York State Bar in 2014, he holds a J.D. from St. John's University School of Law, an Executive MBA from Duke University, and is the author of <em>Minimizing the Cost of E-Discovery Production in New York State Litigation</em>. He is a member of the New York State Bar Association, the American Bar Association, the NYS Academy of Trial Lawyers, and WealthCounsel.</p>
    <div class="ab-links">
      <a href="{BAR_URL}" rel="noopener" target="_blank">NY State Bar Attorney Directory</a>
      <a href="/attorney-profile/akiva-shapiro-esq/">Full Profile</a>
      <a href="{SAMEAS_PERSON[0]}" rel="noopener" target="_blank">LinkedIn</a>
      <a href="{SAMEAS_PERSON[1]}" rel="noopener" target="_blank">Avvo</a>
    </div>
  </div>
</aside>"""

YELP_BURST = ('<svg viewBox="0 0 32 32" width="20" height="20" aria-hidden="true" style="flex:none">'
              '<path fill="#fff" d="M15.6 4.2c1.2-.3 3.9.6 4.6 1.5.2.3.3.6.3 1 0 .2-.1 4.6-.2 6.6 0 .7-.2 1.2-.7 1.4-.5.2-1 0-1.4-.4-1.3-1.5-4-4.7-4.2-5-.2-.3-.3-.6-.3-1 0-.9 1-3.3 1.5-3.6zM12.9 15.9c-.4.4-1 .5-1.5.3-.3-.1-3.4-1.1-4.3-1.5-.4-.2-.7-.5-.8-.9-.2-1.2 1.2-3.7 2.1-4.2.3-.2.7-.2 1-.1.4.1 4 2.8 4.4 3.2.4.4.5 1 .3 1.5-.1.2-.3.5-1.2 1.7zm.2 3.3c.5.1.9.5 1 1 0 .3.1 3.5.1 4.4 0 .5-.2.9-.5 1.1-1 .7-3.9.7-4.9.1-.3-.2-.5-.6-.5-1 0-.4 1.4-3.9 1.6-4.3.2-.5.7-.8 1.2-.8.2 0 .5 0 1.9.5zm5.6-1.3c-.3-.4-.3-1-.1-1.5.1-.3 1.6-3.1 2.1-3.9.2-.4.6-.6 1-.6 1.2 0 3.4 1.9 3.7 2.9.1.3 0 .7-.2 1-.2.3-3.3 2.6-3.7 2.9-.4.3-1 .3-1.5 0-.2-.1-.4-.3-1.3-1.3zm.7 2.3c.4-.3 1-.4 1.5-.1.3.1 3.1 1.7 3.8 2.2.4.2.6.6.6 1 0 1.2-2 3.4-3 3.6-.3.1-.7 0-1-.2-.3-.2-2.4-3.4-2.6-3.8-.3-.5-.2-1 .1-1.5.1-.2.3-.4 1.6-1.2z"/></svg>')

def review_cta_module(heading="Share Your Experience", intro="If Akiva helped you, a two-minute review helps the next Long Island family find him — and helps AI assistants like Google and ChatGPT recommend him with confidence."):
    return f"""
<section class="band"><div class="wrap" style="max-width:820px;text-align:center">
  <div class="kicker">Leave a Review</div>
  <h2>{esc(heading)}</h2>
  <p class="lead" style="margin:.8em auto 1.8em">{esc(intro)}</p>
  <div class="review-btns">
    <a class="btn btn-review-google" href="{GOOGLE_REVIEW_URL}" rel="noopener" target="_blank">
      <span class="g-mark" aria-hidden="true">G</span> Review us on Google</a>
    <a class="btn btn-review-yelp" href="{YELP_REVIEW_URL}" rel="noopener" target="_blank">
      {YELP_BURST} Review us on Yelp</a>
  </div>
  <p style="font-size:.85rem;color:var(--muted);margin-top:1.3em">Reviews open in a new tab. Thank you for taking the time.</p>
</div></section>"""

def cta_band(h="Talk Through Your Situation With Akiva — Free", p="One phone call gets you a clear read on where you stand and what your options are. No pressure, no obligation — just straight answers from a Long Island attorney."):
    return f"""
<section class="cta-band"><div class="wrap">
  <h2>{esc(h)}</h2><p>{esc(p)}</p>
  <div class="hero-ctas" style="justify-content:center">
    <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    <a class="btn btn-outline" href="/contact-us/">Request a Consultation</a>
  </div>
</div></section>"""

LABELS = {
    "/lawsuits-civil-litigation": "Lawsuits & Civil Litigation",
    "/trusts-asset-protection": "Trusts & Asset Protection",
    "/medicaid-trusts-and-applications": "Medicaid Trusts & Applications",
    "/medicaid-fair-hearings": "Medicaid Fair Hearings",
    "/guardianships": "Guardianships",
    "/landlord-tenant": "Landlord / Tenant",
    "/divorce-and-family-law": "Divorce & Family Law",
    "/pre-post-nuptial-agreements": "Pre & Post-Nuptial Agreements",
    "/property-tax-grievance": "Property Tax Grievance",
    "/ny-lemon-law-for-faulty-automobiles": "NY Lemon Law",
    "/commercial-litigation": "Commercial Litigation",
    "/appellate-practice": "Appellate Practice",
    "/business-asset-protection": "Business Asset Protection",
    "/mergers-acquisitions": "Mergers & Acquisitions",
    "/commercial-leasing": "Commercial Leasing",
    "/lease-negotiation": "Lease Negotiation",
    "/collection-of-unpaid-debts": "Collection of Unpaid Debts",
    "/mechanics-liens": "Mechanics Liens",
    "/off-shore-family-limited-liability-companies-partnerships": "Offshore Family LLCs",
    "/estate-planning": "Estate Planning",
    "/wills": "Wills",
    "/trusts": "Trusts",
    "/probate": "Probate",
    "/estate-litigation": "Estate Litigation",
    "/ny-deeds-for-out-of-state-trusts": "NY Deeds for Out-of-State Trusts",
    "/business": "Business", "/life": "Life", "/legacy": "Legacy",
}

TESTIMONIALS = [
    ("Akiva Shapiro explained Elder Care law to my family and advised us on the best options for my parents. His concern and undivided attention to our legal issues was caring and forthright. The whole experience was stress free.", "Fiorinda De Angelis", "National MS Society"),
    ("I just wanted to say great job at Supreme Court. You did your homework and earned bragging rights by keeping the case going strong and getting me a great settlement.", "Kevin Mallory", "Client"),
    ("I have known and worked with Akiva many times through the years and he is a lawyer who is also a true professional. He always finds the right answer and practices with integrity. I highly recommend him to any client.", "Rachel R. Paras, Esq.", "The Law Offices of Rachel R. Paras, LLC"),
    ("When I referred some matters to him, Akiva has exceeded my expectations. If you are looking for an attorney who has the knowledge, skills, and tenacity to effectively represent you, I would recommend that you retain Akiva Shapiro.", "Monet Binder, Esq.", "Referring Attorney"),
    ("His unparalleled knowledge, expertise and professionalism are matched by his unwavering commitment to go above and beyond his strict call of duty, in order to bring about a satisfactory conclusion of the case for his client.", "Chasida Teichman", "Certified Life Coach"),
    ("Unbelievable. You accomplished what no one else could do. Thank you.", "Steve Rosner", "President & CEO, HeavenSent Legal Services"),
    ("Mr. Shapiro is very customer service driven, providing the best possible solutions through his out-of-the-box creative thinking, perseverance and due diligence.", "Monique Klein", "COO, Automation GT"),
    ("My dealings with Mr. Shapiro have demonstrated his high level of honesty and diligence, and he is to be commended.", "Stuart Parker", "CPA, Stuart L. Parker CPA PC"),
    ("Mr. Shapiro has been able to come up with creative solutions to complex problems involving uncooperative parties. I always admire his approach to resolving difficult situations.", "John Donatch", "Young Israel of New Hyde Park"),
    ("Mr. Shapiro has the broad knowledge and experience combined with creativity to design solutions that would not occur to others. He has a uniquely diverse background, which gives him insights into the problems facing his customers.", "Avi Deitcher", "President & CEO, Atomic, Inc."),
    ("Mr. Shapiro identifies hurdles or risks and navigates around them with agility. This instills confidence with the people around him. He possesses a very special ability to drive any complex project towards its target with efficiency and success.", "Gilles Brisson", "Principal Architect, Bombardier Aerospace"),
    ("Working with Mr. Shapiro is a delight. His business strategy of collaboration, hard work, and steadfastness, mixed with a touch of fun is a breath of fresh air.", "Rebecca Howard", "CEO, Dichotomy33Designs"),
]

def t_card(quote, name, role, source=None):
    src = f'<span style="color:var(--gold-soft);font-weight:600">✓ {esc(source)}</span>' if source else ""
    return f"""<div class="t-card"><div class="stars" aria-hidden="true">★★★★★</div>
<p>“{esc(quote)}”</p><footer><b>{esc(name)}</b>{esc(role)} {src}</footer></div>"""

GOOGLE_CARDS = [(r["text"], r["author"], "Google Review", "Verified on Google") for r in G_REVIEWS]

def rating_strip():
    return f"""
<div style="display:flex;align-items:center;justify-content:center;gap:1.4em;flex-wrap:wrap;margin-top:1.4em">
  <div style="font-family:var(--serif);font-size:2.4rem;color:var(--navy);font-weight:700;line-height:1">{G_RATING}</div>
  <div style="text-align:left">
    <div style="color:var(--gold);font-size:1.15rem;letter-spacing:.12em">★★★★★</div>
    <div style="font-size:.9rem;color:var(--muted)">Based on <b style="color:var(--ink)">{G_COUNT} verified Google reviews</b></div>
  </div>
</div>"""

# ---------------------------------------------------------------- article page
def article_page(meta, art):
    cl = CLUSTERS[meta["cluster"]]
    h1 = art.get("h1_clean") or meta["h1"]
    title = title_for_article(h1)
    path = meta["path"] + "/"
    crumbs = [("Home", "/"), ("Legal Answers", "/faq/"), (cl["label"], cl["practice"] + "/"), (h1, path)]
    video_html = ""
    schema_extra = [breadcrumbs_schema(crumbs[:-1] + [(h1, path)])]
    if meta["vimeo"]:
        vid = meta["vimeo"][0]
        video_html = f"""
<div class="video-facade" data-vid="{vid}" data-title="{esc(h1)}" role="button" tabindex="0" aria-label="Play video: {esc(h1)}">
  <div class="play" aria-hidden="true"></div><span>Watch Akiva answer this question</span>
</div>"""
        schema_extra.append({
            "@type": "VideoObject", "name": h1,
            "description": art["meta_desc"],
            "embedUrl": f"https://player.vimeo.com/video/{vid}",
            "uploadDate": meta["date"],
            "thumbnailUrl": DOMAIN + "/img/og-office.jpg",
            "publisher": {"@id": DOMAIN + "/#firm"},
        })
    extra_faqs = art.get("faqs") or []
    faq_entities = [{"@type": "Question", "name": h1,
                     "acceptedAnswer": {"@type": "Answer", "text": art["faq_short"]}}]
    faq_entities += [{"@type": "Question", "name": f["q"],
                      "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in extra_faqs]
    schema_extra.append({"@type": "FAQPage", "mainEntity": faq_entities})
    faq_accordion = ""
    if extra_faqs:
        items = "".join(
            f'<details class="faq-item"><summary>{esc(f["q"])}</summary><div class="faq-a"><p>{esc(f["a"])}</p></div></details>'
            for f in extra_faqs)
        faq_accordion = f'<h2 id="faq">Frequently Asked Questions</h2><div class="faq-wrap">{items}</div>'
    schema_extra.append({
        "@type": "Article", "headline": h1[:110],
        "description": art["meta_desc"],
        "author": {"@id": DOMAIN + "/#akiva"},
        "publisher": {"@id": DOMAIN + "/#firm"},
        "datePublished": meta["date"], "dateModified": TODAY,
        "mainEntityOfPage": DOMAIN + path,
        "image": DOMAIN + "/img/akiva-shapiro-attorney.jpg",
    })
    sections_html = "".join(
        f"<h2>{esc(s['h2'])}</h2>{s['html']}" for s in art["sections"])
    takeaways = "".join(f"<li>{esc(t)}</li>" for t in art["takeaways"])
    # rotating ring: every article links to the next 6 siblings in its cluster,
    # which (by symmetry) guarantees each article also RECEIVES ~6 inbound links.
    siblings = [q for q in plan["qa"] if q["cluster"] == meta["cluster"]]
    if len(siblings) > 1:
        idx = next((i for i, q in enumerate(siblings) if q["slug"] == meta["slug"]), 0)
        span = min(6, len(siblings) - 1)
        related = [siblings[(idx + 1 + j) % len(siblings)] for j in range(span)]
    else:
        related = []
    rel_html = "".join(
        f"""<a class="q-item" href="{r['path']}/"><span>{esc((read_article(r['slug']) or {}).get('h1_clean', r['h1']))}</span><span class="arr">→</span></a>"""
        for r in related)
    date_h = f"""<time datetime="{meta['date']}">Published {meta['date'][:4]}</time> · Last reviewed August 2026"""
    return head_html(title, art["meta_desc"], path, schema_extra) + nav_html() + f"""
{crumbs_html(crumbs)}
<div class="wrap article-head">
  <div class="kicker">{esc(cl['label'])} · Legal Answers</div>
  <h1>{esc(h1)}</h1>
  <div class="meta-row">
    <span class="byline"><img src="/img/akiva-author.jpg" alt="" width="34" height="34"> By <b>&nbsp;Akiva Shapiro, Esq.</b></span>
    <span class="chip">{date_h}</span>
  </div>
</div>
<div class="wrap"><article class="body">
  <div class="direct">{art['direct_answer']}</div>
  {video_html}
  {sections_html}
  <div class="takeaways"><h2>Key Takeaways</h2><ul>{takeaways}</ul></div>
  {faq_accordion}
  {author_box()}
  <p class="disclaimer">This article is attorney advertising and provides general information about New York law; it is not legal advice for your specific situation and does not create an attorney-client relationship. For advice about your circumstances, speak with a licensed New York attorney.</p>
</article></div>
{cta_band(h="Have This Exact Question? Get a Real Answer — Free",
          p="Every situation is different. Call for a free phone consultation and Akiva will tell you where you stand under New York law and what your next step should be.")}
<section class="related"><div class="wrap">
  <h2>Related {esc(cl['label'])} Questions</h2>
  <div class="rel-grid">{rel_html}</div>
  <p style="margin-top:1.6em"><a class="btn btn-line" href="/faq/">Browse the full Legal Answers library</a>
  <a class="btn btn-navy" style="margin-left:10px" href="{cl['practice']}/">Our {esc(cl['label'])} services</a></p>
</div></section>
""" + footer_html() + "</body></html>"

# ---------------------------------------------------------------- practice page
def render_blocks(blocks):
    out, in_ul = [], False
    for b in blocks:
        if b["tag"] == "li":
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{esc(b['text'])}</li>")
            continue
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if b["tag"] in ("h2", "h3", "h4"):
            out.append(f"<h2>{esc(b['text'])}</h2>")
        else:
            out.append(f"<p>{esc(b['text'])}</p>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)

def practice_page(pg):
    path = pg["path"] + "/"
    label = LABELS.get(pg["path"], pg["h1"] or pg["title"])
    h1 = pg["h1"] or label
    title = pg["title"] or f"{label} | {FIRM}"
    desc = pg["meta_desc"] or f"{label} counsel from {FIRM} in Old Bethpage — serving Nassau County, Suffolk County and all of Long Island. Free phone consultation: {PHONE_DISPLAY}."
    crumbs = [("Home", "/"), (label, path)]
    # cluster whose practice page is this path
    my_cluster = next((k for k, v in CLUSTERS.items() if v["practice"] == pg["path"]), None)
    qa_items = [q for q in plan["qa"] if q["cluster"] == my_cluster][:8] if my_cluster else []
    qa_html = ""
    if qa_items:
        links = "".join(
            f"""<a class="q-item" href="{q['path']}/"><span>{esc((read_article(q['slug']) or {}).get('h1_clean', q['h1']))}</span><span class="arr">→</span></a>"""
            for q in qa_items)
        qa_html = f"""<section class="band"><div class="wrap">
  <div class="kicker">Legal Answers</div>
  <h2>Questions Long Islanders Ask Us About {esc(label)}</h2>
  <div class="q-list">{links}</div>
  <p style="margin-top:1.6em"><a class="btn btn-line" href="/faq/">See all questions answered</a></p>
</div></section>"""
    schema_extra = [
        breadcrumbs_schema(crumbs),
        {"@type": "Service", "name": label, "serviceType": label,
         "provider": {"@id": DOMAIN + "/#firm"},
         "areaServed": [{"@type": "AdministrativeArea", "name": "Nassau County, NY"},
                        {"@type": "AdministrativeArea", "name": "Long Island, NY"}],
         "url": DOMAIN + path, "description": desc},
    ]
    content = render_blocks(pg["content"]) or f"<p>{FIRM} represents Long Island clients in {esc(label.lower())} matters.</p>"
    tcard = TESTIMONIALS[0]
    return head_html(title, desc, path, schema_extra) + nav_html() + f"""
<div class="page-hero"><div class="wrap">
  <div class="kicker">{FIRM}</div>
  <h1>{esc(h1)}</h1>
  <p class="lead">Straight answers and steady counsel for Nassau County, Suffolk County and all of Long Island. One attorney, personally on your side.</p>
  <div class="hero-ctas">
    <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    <a class="btn btn-outline" href="/contact-us/">Free Phone Consultation</a>
  </div>
</div></div>
{crumbs_html(crumbs)}
<div class="wrap content-grid">
  <div class="content-main">{content}</div>
  <aside class="rail">
    <div class="rail-card gold">
      <h3>Talk to Akiva First</h3>
      <p>Get a clear read on your situation before you make a move. Free phone consultation, no obligation.</p>
      <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    </div>
    <div class="rail-card">
      <h3>Why Clients Choose Akiva</h3>
      <ul>
        <li>One attorney for your whole legal life</li>
        <li>Admitted to the NY Bar since 2014</li>
        <li>Duke MBA — business-minded counsel</li>
        <li>Published author on NY litigation practice</li>
        <li>Old Bethpage office, mid-Long Island</li>
      </ul>
    </div>
    <div class="rail-card">
      <div class="stars" style="color:var(--gold);font-size:1.1rem">★★★★★ <span style="font-family:var(--serif);color:var(--navy)">{G_RATING}</span></div>
      <p style="font-size:.85rem;color:var(--muted);margin:.2em 0 .8em">{G_COUNT} verified Google reviews</p>
      <p style="font-size:.92rem">“{esc(G_REVIEWS[0]['text'][:140])}…”</p>
      <p style="font-size:.85rem;color:var(--muted);margin-top:.6em"><b>{esc(G_REVIEWS[0]['author'])}</b></p>
      <a href="/testimonials/" style="font-weight:600;font-size:.9rem">Read all testimonials →</a>
    </div>
  </aside>
</div>
{qa_html}
{cta_band()}
""" + footer_html() + "</body></html>"

# ---------------------------------------------------------------- custom rich pillar page
def custom_practice_page(pg, custom):
    path = pg["path"] + "/"
    label = custom.get("cluster_label", LABELS.get(pg["path"], pg["h1"]))
    h1 = custom["h1"]
    title = custom["title"]
    desc = custom["meta_desc"]
    crumbs = [("Home", "/"), (label, path)]
    my_cluster = next((k for k, v in CLUSTERS.items() if v["practice"] == pg["path"]), None)

    toc = "".join(
        f'<a href="#s{i}">{esc(s["h2"])}</a>'
        for i, s in enumerate(custom["sections"]))
    body_sections = "".join(
        f'<h2 id="s{i}">{esc(s["h2"])}</h2>' +
        (f'<div class="table-scroll">{s["html"]}</div>' if "<table" in s["html"] else s["html"])
        for i, s in enumerate(custom["sections"]))

    faq_html = "".join(
        f'<details class="faq-item"><summary>{esc(f["q"])}</summary>'
        f'<div class="faq-a"><p>{esc(f["a"])}</p></div></details>'
        for f in custom["faqs"])
    takeaways = "".join(f"<li>{esc(t)}</li>" for t in custom["takeaways"])

    schema_extra = [
        breadcrumbs_schema(crumbs),
        {"@type": "Service", "name": label, "serviceType": label,
         "provider": {"@id": DOMAIN + "/#firm"},
         "areaServed": [{"@type": "AdministrativeArea", "name": "New York"},
                        {"@type": "AdministrativeArea", "name": "Long Island, NY"}],
         "url": DOMAIN + path, "description": desc},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in custom["faqs"]]},
        {"@type": "Article", "headline": h1[:110], "description": desc,
         "author": {"@id": DOMAIN + "/#akiva"}, "publisher": {"@id": DOMAIN + "/#firm"},
         "datePublished": "2026-08-17", "dateModified": TODAY,
         "mainEntityOfPage": DOMAIN + path,
         "image": DOMAIN + "/img/akiva-shapiro-attorney.jpg"},
    ]
    qa_items = [q for q in plan["qa"] if q["cluster"] == my_cluster][:6] if my_cluster else []
    qa_html = ""
    if qa_items:
        links = "".join(
            f"""<a class="q-item" href="{q['path']}/"><span>{esc((read_article(q['slug']) or {}).get('h1_clean', q['h1']))}</span><span class="arr">→</span></a>"""
            for q in qa_items)
        qa_html = f"""<section class="related"><div class="wrap">
  <h2>Related Questions</h2><div class="rel-grid">{links}</div></div></section>"""

    return head_html(title, desc, path, schema_extra) + nav_html() + f"""
<div class="page-hero"><div class="wrap">
  <div class="kicker">{FIRM} · Serving All of New York</div>
  <h1>{esc(h1)}</h1>
  <p class="lead">Straight answers about your rights under New York law — and a free phone consultation to tell you exactly where you stand.</p>
  <div class="hero-ctas">
    <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    <a class="btn btn-outline" href="/contact-us/">Free Phone Consultation</a>
  </div>
</div></div>
{crumbs_html(crumbs)}
<div class="wrap content-grid">
  <div class="content-main">
    <div class="direct">{custom['intro_html']}</div>
    <nav class="toc" aria-label="On this page" style="background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:1.1em 1.4em;margin:0 0 1.8em">
      <div style="font-size:.72rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin-bottom:.5em">On This Page</div>
      <div class="toc-links" style="display:flex;flex-direction:column;gap:.3em;font-size:.95rem;font-weight:600">{toc}</div>
    </nav>
    {body_sections}
    <div class="takeaways"><h2 style="border:0;margin:0 0 .6em">Key Takeaways</h2><ul>{takeaways}</ul></div>
    <h2 id="faq">Frequently Asked Questions</h2>
    <div class="faq-wrap">{faq_html}</div>
    {author_box()}
    <p class="disclaimer">This article is attorney advertising and provides general information about New York law, current as of August 2026; it is not legal advice for your specific situation and does not create an attorney-client relationship. Statutes and thresholds can change — for advice about your circumstances, speak with a licensed New York attorney. Authoritative source: <a href="https://ag.ny.gov/resources/individuals/car-auto/lemon-law-program" rel="noopener" target="_blank">New York State Attorney General, Lemon Law Program</a>.</p>
  </div>
  <aside class="rail">
    <div class="rail-card gold">
      <h3>Think You Have a Lemon?</h3>
      <p>A two-minute call tells you whether you've crossed New York's legal thresholds — and what your claim may be worth.</p>
      <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    </div>
    <div class="rail-card">
      <h3>On This Page</h3>
      <ul style="list-style:none">{''.join(f'<li><a href="#s{i}">{esc(s["h2"])}</a></li>' for i,s in enumerate(custom["sections"]))}</ul>
    </div>
    <div class="rail-card">
      <div class="stars" style="color:var(--gold);font-size:1.1rem">★★★★★ <span style="font-family:var(--serif);color:var(--navy)">{G_RATING}</span></div>
      <p style="font-size:.85rem;color:var(--muted);margin:.2em 0 .8em">{G_COUNT} verified Google reviews</p>
      <p style="font-size:.92rem">“{esc(G_REVIEWS[0]['text'][:140])}…”</p>
      <a href="/testimonials/" style="font-weight:600;font-size:.9rem">Read all testimonials →</a>
    </div>
  </aside>
</div>
{qa_html}
{cta_band(h="Stuck With a Car That Can't Be Fixed?",
          p="You may be owed a refund or a replacement under New York's Lemon Law. Call for a free phone consultation and find out where you stand — the manufacturer often pays your attorney's fees.")}
""" + footer_html() + "</body></html>"

# ---------------------------------------------------------------- town / service-area pages
def town_page(town):
    name = town["name"]
    path = "/" + town_slug(name) + "/"
    court = TOWNS["court"]
    title = f"Estate Planning Attorney in {name}, NY | Akiva Shapiro Law"
    desc = (f"Estate planning, wills, trusts, probate & elder law attorney serving {name}, NY. "
            f"Akiva Shapiro Law — a personal attorney minutes from {name}. Free consultation: {PHONE_DISPLAY}.")
    crumbs = [("Home", "/"), ("Areas We Serve", "/areas-we-serve/"), (f"{name}, NY", path)]
    nearby_links = "".join(
        f'<a href="/{town_slug(n)}/">{esc(n)}</a>' if any(t["name"] == n for t in TOWNS["towns"])
        else f'<span>{esc(n)}</span>'
        for n in town["nearby"])
    faqs = [
        {"q": f"Where do {name} residents probate a will?",
         "a": f"A will for someone who lived in {name} is probated at the {court['name']}, located at {court['address']}, because {name} is in {court['county']}. Akiva Shapiro handles the entire Surrogate's Court process for {name} families."},
        {"q": f"Do you offer free consultations for {name} clients?",
         "a": f"Yes. Akiva offers a free phone consultation to {name} residents. Call {PHONE_DISPLAY} to talk through your situation and get a clear read on your options under New York law."},
        {"q": f"How can a {name} family avoid probate?",
         "a": f"The most common way {name} families avoid probate is a properly funded revocable living trust, which lets assets pass to heirs without Surrogate's Court. Akiva can advise whether a trust, beneficiary designations, or other tools fit your situation."},
    ]
    faq_html = "".join(
        f'<details class="faq-item"><summary>{esc(f["q"])}</summary><div class="faq-a"><p>{esc(f["a"])}</p></div></details>'
        for f in faqs)
    schema_extra = [
        breadcrumbs_schema(crumbs),
        {"@type": "Service", "name": f"Estate Planning Attorney in {name}, NY",
         "serviceType": "Estate Planning, Elder Law & Probate",
         "provider": {"@id": DOMAIN + "/#firm"},
         "areaServed": {"@type": "City", "name": f"{name}, NY"},
         "url": DOMAIN + path, "description": desc},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]},
    ]
    return head_html(title, desc, path, schema_extra) + nav_html() + f"""
<div class="page-hero"><div class="wrap">
  <div class="kicker">Serving {esc(name)}, New York · {esc(town['zip'])}</div>
  <h1>Estate Planning &amp; Elder Law Attorney in {esc(name)}, NY</h1>
  <p class="lead">{esc(town['proximity'])}</p>
  <div class="hero-ctas">
    <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    <a class="btn btn-outline" href="/contact-us/">Free Phone Consultation</a>
  </div>
  <ul class="chips"><li>★ {G_RATING} · {G_COUNT} Google reviews</li><li>Minutes from {esc(name)}</li><li>NY Bar since 2014 · Duke MBA</li></ul>
</div></div>
{crumbs_html(crumbs)}
<div class="wrap content-grid">
  <div class="content-main">
    <div class="direct"><p>{esc(town['intro'])}</p></div>
    <h2>{esc(town['angle_h2'])}</h2>
    {town['angle_html']}
    <h2>How Akiva Helps {esc(name)} Families</h2>
    <p>As your personal attorney for life, business, and legacy, Akiva Shapiro handles the full range of estate and elder law matters for {esc(name)} residents:</p>
    <ul>
      <li><a href="/estate-planning/">Estate planning</a> — wills, <a href="/trusts/">trusts</a>, health care proxies, and powers of attorney</li>
      <li><a href="/medicaid-trusts-and-applications/">Medicaid planning</a> and asset protection to guard your home from long-term-care costs</li>
      <li><a href="/probate/">Probate</a> and estate administration at the {esc(court['name'])}</li>
      <li><a href="/estate-litigation/">Estate litigation</a> — will contests and fiduciary disputes</li>
      <li><a href="/guardianships/">Guardianships</a> for aging parents or loved ones with special needs</li>
    </ul>
    <h2>Where {esc(name)} Residents Handle Probate</h2>
    <p>Because {esc(name)} is in {esc(court['county'])}, a {esc(name)} resident's estate is probated at the <strong>{esc(court['name'])}</strong>, {esc(court['address'])}. Surrogate's Court has its own rules, forms, and deadlines — and mistakes cause delay. Akiva handles the entire process for {esc(name)} families, from filing the petition to distributing the estate.</p>
    <div class="faq-wrap"><h2 id="faq" style="border:0">Common Questions From {esc(name)} Clients</h2>{faq_html}</div>
    {author_box()}
    <p class="disclaimer">Attorney advertising. This page provides general information about New York law, not legal advice, and does not create an attorney-client relationship. Akiva Shapiro Law is located in Old Bethpage, NY and serves clients throughout {esc(court['county'])} and Long Island.</p>
  </div>
  <aside class="rail">
    <div class="rail-card gold">
      <h3>Talk to a {esc(name)}-Area Attorney</h3>
      <p>Free phone consultation — get a clear read on your estate, elder law, or probate question.</p>
      <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    </div>
    <div class="rail-card">
      <div class="stars" style="color:var(--gold);font-size:1.1rem">★★★★★ <span style="font-family:var(--serif);color:var(--navy)">{G_RATING}</span></div>
      <p style="font-size:.85rem;color:var(--muted);margin:.2em 0 .8em">{G_COUNT} verified Google reviews</p>
      <p style="font-size:.92rem">“{esc(G_REVIEWS[2]['text'][:130])}…”</p>
      <p style="font-size:.85rem;color:var(--muted)"><b>{esc(G_REVIEWS[2]['author'])}</b></p>
    </div>
    <div class="rail-card">
      <h3>Nearby Communities We Serve</h3>
      <div class="toc-links" style="display:flex;flex-direction:column;gap:.3em;font-weight:600;font-size:.93rem">{nearby_links}</div>
    </div>
  </aside>
</div>
{cta_band(h=f"Serving {name} Families — Personally",
          p=f"You deserve one attorney who knows your whole picture. Call for a free phone consultation and see why {name}-area families and their neighbors trust Akiva Shapiro.")}
""" + footer_html() + "</body></html>"

def areas_hub_page():
    path = "/areas-we-serve/"
    title = "Areas We Serve — Long Island Estate Planning Attorney | Akiva Shapiro Law"
    desc = ("Akiva Shapiro Law serves estate planning, elder law, and probate clients across Nassau County "
            "and Long Island — Plainview, Hicksville, Bethpage, Syosset, Jericho, Woodbury, Massapequa & Farmingdale.")
    crumbs = [("Home", "/"), ("Areas We Serve", path)]
    cards = "".join(
        f"""<a class="q-item" href="/{town_slug(t['name'])}/"><span>Estate Planning Attorney in {esc(t['name'])}, NY</span><span class="arr">→</span></a>"""
        for t in TOWNS["towns"])
    return head_html(title, desc, path, [breadcrumbs_schema(crumbs)]) + nav_html() + f"""
{crumbs_html(crumbs)}
<section style="padding-top:44px"><div class="wrap">
  <div class="center">
    <div class="kicker">Nassau County &amp; Long Island</div>
    <h1>Areas We Serve</h1>
    <p class="lead">From our Old Bethpage office, Akiva Shapiro is the personal estate planning, elder law, and probate attorney for families across mid-Long Island. Find your community below.</p>
  </div>
  <div class="q-list" style="margin-top:2.4em">{cards}</div>
  <p class="center" style="margin-top:2em;color:var(--muted)">Don't see your town? Akiva serves all of {esc(TOWNS['court']['county'])} and Long Island — <a href="/contact-us/">get in touch</a>.</p>
</div></section>
{cta_band()}
""" + footer_html() + "</body></html>"

# ---------------------------------------------------------------- homepage
def home_page():
    path = "/"
    title = "Long Island Attorney for Life, Business & Legacy | Akiva Shapiro Law"
    desc = f"Estate planning, elder law, probate and litigation for Long Island families and business owners. Akiva Shapiro Law, PLLC — your personal attorney in Nassau County. Free phone consultation: {PHONE_DISPLAY}."
    featured_qs = [
        ("what-happens-if-i-die-without-a-will-in-new-york",),
        ("what-is-the-five-year-look-back-period",),
        ("what-actually-is-probate",),
        ("i-am-a-beneficiary-of-a-trust-what-are-my-rights",),
        ("do-i-need-an-attorney-to-get-a-divorce",),
        ("ive-been-sued-do-i-need-an-attorney",),
    ]
    q_html = ""
    for (slug,) in featured_qs:
        meta = next((q for q in plan["qa"] if q["slug"] == slug), None)
        if not meta:
            continue
        art = read_article(slug) or {}
        q_html += f"""<a class="q-item" href="{meta['path']}/"><span>{esc(art.get('h1_clean', meta['h1']))}</span><span class="arr">→</span></a>"""
    t_html = "".join(t_card(*t) for t in GOOGLE_CARDS)
    schema_extra = [breadcrumbs_schema([("Home", "/")])]
    return head_html(title, desc, path, schema_extra) + nav_html() + f"""
<div class="hero"><div class="wrap hero-grid">
  <div>
    <div class="kicker">Old Bethpage · Nassau County · Long Island</div>
    <h1>One Trusted Attorney for Your <em>Life</em>, Your <em>Business</em> &amp; Your <em>Legacy</em></h1>
    <p class="lead">Estate planning, elder law, and litigation — handled personally, not passed to an associate. Akiva Shapiro Law is the attorney Long Island families and business owners call first.</p>
    <div class="hero-ctas">
      <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-outline" href="/contact-us/">Request a Free Phone Consultation</a>
    </div>
    <ul class="chips">
      <li>★ {G_RATING} · {G_COUNT} Google reviews</li>
      <li>Admitted to the NY Bar since 2014</li>
      <li>Duke MBA · Business-Minded Counsel</li>
      <li>Published Author, NY Litigation</li>
    </ul>
  </div>
  <div class="hero-photo">
    <img src="/img/akiva-shapiro-attorney.jpg" alt="Akiva Shapiro, Esq., attorney in Old Bethpage, Long Island" width="468" height="625" fetchpriority="high">
    <div class="hero-badge"><b>★★★★★</b> <span>{G_RATING} on Google<br><small style="color:var(--muted);font-weight:500">{G_COUNT} verified reviews</small></span></div>
  </div>
</div></div>

<section class="pillars"><div class="wrap">
  <div class="center">
    <div class="kicker">How We Help</div>
    <h2>Every Legal Chapter of Your Life, One Attorney</h2>
    <p class="lead">Like a family physician for your legal health — Akiva knows your whole picture, so every solution fits the life you're actually living.</p>
  </div>
  <div class="pillar-grid">
    <div class="pillar">
      <h3>Life</h3><span class="tag">Protect what you're building</span>
      <ul>
        <li><a href="/lawsuits-civil-litigation/">Lawsuits &amp; Civil Litigation</a></li>
        <li><a href="/trusts-asset-protection/">Trusts &amp; Asset Protection</a></li>
        <li><a href="/medicaid-trusts-and-applications/">Medicaid Planning</a></li>
        <li><a href="/guardianships/">Guardianships</a></li>
        <li><a href="/landlord-tenant/">Landlord / Tenant</a></li>
      </ul>
      <a class="all" href="/life/">All Life services</a>
    </div>
    <div class="pillar">
      <h3>Business</h3><span class="tag">Counsel that speaks CEO</span>
      <ul>
        <li><a href="/commercial-litigation/">Commercial Litigation</a></li>
        <li><a href="/appellate-practice/">Appeals</a></li>
        <li><a href="/business-asset-protection/">Business Asset Protection</a></li>
        <li><a href="/lease-negotiation/">Lease Negotiation</a></li>
        <li><a href="/collection-of-unpaid-debts/">Debt &amp; Judgment Collection</a></li>
      </ul>
      <a class="all" href="/business/">All Business services</a>
    </div>
    <div class="pillar">
      <h3>Legacy</h3><span class="tag">Pass it on, protected</span>
      <ul>
        <li><a href="/estate-planning/">Estate Planning</a></li>
        <li><a href="/wills/">Wills</a></li>
        <li><a href="/trusts/">Trusts</a></li>
        <li><a href="/probate/">Probate</a></li>
        <li><a href="/estate-litigation/">Estate Litigation</a></li>
      </ul>
      <a class="all" href="/legacy/">All Legacy services</a>
    </div>
  </div>
</div></section>

<section class="band"><div class="wrap split">
  <div>
    <div class="kicker">A Different Kind of Practice</div>
    <h2>Your Personal Attorney — Like a Personal Physician for Your Legal Health</h2>
    <p>Most people only call a lawyer when something is on fire. But your legal life — your home, your family, your business, your estate — is connected. Decisions in one area ripple into the others.</p>
    <blockquote class="pull">Akiva looks at your legal life holistically, and crafts solutions that solve today's problem within the context of your whole picture.</blockquote>
    <p>That means the trust that protects your house also fits your Medicaid plan. The lease you sign doesn't undermine your asset protection. And the person advising you already knows your story — because he's the one who has handled it from the start.</p>
  </div>
  <div class="photo"><img src="/img/og-office.jpg" alt="Akiva Shapiro Law office in Old Bethpage, New York" loading="lazy" width="1200" height="630"></div>
</div></section>

<section><div class="wrap">
  <div class="center">
    <div class="kicker">Results People Talk About</div>
    <h2>Trusted by Clients — and by Other Attorneys</h2>
    {rating_strip()}
  </div>
  <div class="t-grid">{t_html}</div>
  <p class="center" style="margin-top:2em"><a class="btn btn-line" href="/testimonials/">Read all testimonials</a></p>
</div></section>

<section class="band"><div class="wrap split">
  <div class="photo"><img src="/img/akiva-shapiro-attorney.jpg" alt="Attorney Akiva Shapiro, Esq." loading="lazy" width="468" height="625" style="max-width:420px"></div>
  <div>
    <div class="kicker">Meet Your Attorney</div>
    <h2>Akiva Shapiro, Esq.</h2>
    <p>Before law, Akiva spent nearly three decades building and running business operations — so he reads contracts, balance sheets, and family dynamics with equal fluency. He holds a J.D. from St. John's University School of Law, an Executive MBA from Duke University, and wrote the book on minimizing e-discovery costs in New York litigation.</p>
    <p>He's a member of the New York State Bar Association, the American Bar Association, the NYS Academy of Trial Lawyers, and WealthCounsel — and he answers his own phone.</p>
    <div class="hero-ctas">
      <a class="btn btn-navy" href="/attorney-profile/akiva-shapiro-esq/">Get to Know Akiva</a>
      <a class="btn btn-line" href="{BAR_URL}" rel="noopener" target="_blank">Verify NY Bar Admission</a>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="center">
    <div class="kicker">Ask Akiva · Legal Answers Library</div>
    <h2>Your Question Has Probably Already Been Answered</h2>
    <p class="lead">100+ plain-English answers to the questions New Yorkers actually ask — many with Akiva on video.</p>
  </div>
  <div class="q-list">{q_html}</div>
  <p class="center" style="margin-top:2em"><a class="btn btn-navy" href="/faq/">Browse the full library</a></p>
</div></section>

<section class="band"><div class="wrap local-grid">
  <div>
    <div class="kicker">Mid-Island, Easy to Reach</div>
    <h2>Serving All of Long Island From Old Bethpage</h2>
    <p class="lead" style="margin-bottom:1em">Conveniently located mid-island, minutes off the Seaford–Oyster Bay Expressway — serving Nassau County, Suffolk County, Queens, and greater New York.</p>
    <p style="margin-bottom:1.2em"><a href="/areas-we-serve/" style="font-weight:600">See the Long Island communities we serve →</a></p>
    <iframe class="map-frame" title="Map to Akiva Shapiro Law, PLLC" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q=1+W+Park+Dr,+Old+Bethpage,+NY+11804&output=embed"></iframe>
  </div>
  <dl class="nap">
    <dt>Office</dt><dd>{ADDR}, {CITY}, {STATE} {ZIP}</dd>
    <dt>Phone</dt><dd><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></dd>
    <dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
    <dt>Hours</dt><dd>By appointment<br>Mon–Thu 9:30am–5:30pm<br>Fri 9:30am–4:00pm</dd>
    <dt>Consultation</dt><dd>Free by phone — <a href="/contact-us/">request yours</a></dd>
  </dl>
</div></section>
{cta_band()}
""" + footer_html() + "</body></html>"

# ---------------------------------------------------------------- hub pages
def faq_page():
    path = "/faq/"
    title = "Legal Answers Library: New York Law FAQ | Akiva Shapiro Law"
    desc = "100+ plain-English answers from a Long Island attorney: estate planning, trusts, Medicaid, guardianship, probate and litigation questions New Yorkers ask most."
    crumbs = [("Home", "/"), ("Legal Answers", path)]
    order = ["estate-planning", "trusts", "probate", "estate-litigation", "medicaid",
             "guardianship", "litigation", "appeals", "debt-collection",
             "divorce-family", "real-estate", "offshore"]
    groups_html = ""
    for key in order:
        items = [q for q in plan["qa"] if q["cluster"] == key]
        if not items:
            continue
        cl = CLUSTERS[key]
        links = "".join(
            f"""<a class="q-item" href="{q['path']}/"><span>{esc((read_article(q['slug']) or {}).get('h1_clean', q['h1']))}</span><span class="arr">→</span></a>"""
            for q in items)
        groups_html += f"""<section style="padding:34px 0 6px"><div class="wrap">
  <h2 id="{key}">{esc(cl['label'])} <span style="font-size:.9rem;color:var(--muted);font-family:var(--sans);font-weight:500">({len(items)} answers)</span></h2>
  <div class="q-list">{links}</div>
  <p style="margin-top:1em"><a href="{cl['practice']}/" style="font-weight:600">Our {esc(cl['label'])} services →</a></p>
</div></section>"""
    toc = " · ".join(f'<a href="#{k}" style="font-weight:600">{esc(CLUSTERS[k]["label"])}</a>'
                     for k in order if any(q["cluster"] == k for q in plan["qa"]))
    return head_html(title, desc, path, [breadcrumbs_schema(crumbs)]) + nav_html() + f"""
{crumbs_html(crumbs)}
<div class="wrap article-head">
  <div class="kicker">Ask Akiva</div>
  <h1>Legal Answers Library</h1>
  <p class="lead" style="margin-top:.8em">Plain-English answers to {len(plan['qa'])} real questions about New York law — written and reviewed by attorney Akiva Shapiro, many answered on video. Jump to a topic:</p>
  <p style="margin-top:1em;font-size:.95rem">{toc}</p>
</div>
{groups_html}
{cta_band(h="Can't Find Your Question?", p="Ask it directly. Call for a free phone consultation and get an answer specific to your situation.")}
""" + footer_html() + "</body></html>"

def testimonials_page():
    pg = pages.get("testimonials", {})
    path = "/testimonials/"
    title = pg.get("title") or "Client Testimonials | Akiva Shapiro Law, PLLC"
    desc = pg.get("meta_desc") or "What clients, business owners and fellow attorneys say about working with Long Island attorney Akiva Shapiro, Esq."
    crumbs = [("Home", "/"), ("Testimonials", path)]
    cards = "".join(t_card(*t) for t in (GOOGLE_CARDS + TESTIMONIALS))
    return head_html(title, desc, path, [breadcrumbs_schema(crumbs)]) + nav_html() + f"""
{crumbs_html(crumbs)}
<section><div class="wrap">
  <div class="center">
    <div class="kicker">In Their Words</div>
    <h1>Trusted by Clients — and by Other Attorneys</h1>
    <p class="lead">When other lawyers refer their own clients to you, that says something. Here's what clients and colleagues say about working with Akiva.</p>
    {rating_strip()}
  </div>
  <div class="t-grid">{cards}</div>
  <p class="center" style="margin-top:2.4em"><a class="btn btn-navy" href="/review-attorney-akiva-shapiro/">Worked with Akiva? Leave a review</a></p>
</div></section>
{cta_band()}
""" + footer_html() + "</body></html>"

def attorney_page():
    path = "/attorney-profile/akiva-shapiro-esq/"
    title = "Akiva Shapiro, Esq. — Long Island Attorney | Akiva Shapiro Law"
    desc = "Meet Akiva Shapiro, Esq.: Long Island attorney for life, business and legacy. J.D. St. John's Law, Duke MBA, published author, admitted to the NY Bar in 2014."
    crumbs = [("Home", "/"), ("About", path)]
    schema_extra = [breadcrumbs_schema(crumbs),
                    {"@type": "ProfilePage", "mainEntity": {"@id": DOMAIN + "/#akiva"}, "url": DOMAIN + path}]
    return head_html(title, desc, path, schema_extra) + nav_html() + f"""
{crumbs_html(crumbs)}
<div class="wrap content-grid" style="padding-top:34px">
  <div class="content-main">
    <div class="kicker">Attorney Profile</div>
    <h1>Akiva Shapiro, Esq.</h1>
    <p class="lead" style="margin:.8em 0 1.4em">A personal attorney for your life, business &amp; legacy — based in Old Bethpage, serving all of Long Island and greater New York.</p>
    <p>Conveniently located mid-Long Island, Akiva Shapiro wants to be your personal attorney. Your legal life is complex and connected — and Akiva is a different kind of attorney. He takes the time to know you, understands the issues you face, and looks at your legal life holistically, crafting solutions that solve individual problems within the context of the whole.</p>
    <p>Before practicing law, Akiva built nearly three decades of business operations and development experience — which is why business owners find counsel with him that speaks their language, and families get advice that accounts for the real-world dollars behind every decision.</p>
    <h2>Credentials &amp; Education</h2>
    <ul>
      <li><b>J.D.</b> — St. John's University School of Law</li>
      <li><b>International Executive MBA</b> — Duke University, Fuqua School of Business</li>
      <li><b>B.S. in Computer Science</b>, <i>summa cum laude</i> — Iona College</li>
      <li><b>Author</b> — <i>Minimizing the Cost of E-Discovery Production in New York State Litigation</i></li>
      <li>Certified Graduate of e-Discovery Team Training; Certified EDT eDiscovery Network Engineer</li>
    </ul>
    <h2>Bar Admission &amp; Memberships</h2>
    <ul>
      <li>Licensed to practice law in the State of New York as an Attorney and Counselor-at-Law — admitted 2014 (<a href="{BAR_URL}" rel="noopener" target="_blank">verify in the NY State Unified Court System attorney directory</a>)</li>
      <li>New York State Bar Association</li>
      <li>American Bar Association</li>
      <li>New York State Academy of Trial Lawyers</li>
      <li>WealthCounsel — national estate planning attorney network</li>
    </ul>
    <h2>How Akiva Practices</h2>
    <p>Having a personal attorney is much like having a personal physician: the goal is overall wellness, not just treating symptoms. Akiva helps clients handle personal and business litigation, protect assets from liability, taxes, and Medicaid spend-down, plan and litigate estates, negotiate leases and contracts, resolve landlord-tenant matters, and more — always within one coherent picture of your life.</p>
  </div>
  <aside class="rail">
    <div class="rail-card" style="text-align:center">
      <img src="/img/akiva-shapiro-attorney.jpg" alt="Akiva Shapiro, Esq." style="border-radius:12px;margin-bottom:1em" width="468" height="625">
      <a class="btn btn-gold" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-line" style="margin-top:.6em" href="/contact-us/">Free Phone Consultation</a>
    </div>
    <div class="rail-card">
      <h3>Verify &amp; Connect</h3>
      <ul>
        <li><a href="{BAR_URL}" rel="noopener" target="_blank">NY State Bar Attorney Directory</a></li>
        <li><a href="{SAMEAS_PERSON[0]}" rel="noopener" target="_blank">LinkedIn</a></li>
        <li><a href="{SAMEAS_PERSON[1]}" rel="noopener" target="_blank">Avvo Profile</a></li>
        <li><a href="{SAMEAS_PERSON[2]}" rel="noopener" target="_blank">Super Lawyers</a></li>
        <li><a href="/testimonials/">Client Testimonials</a></li>
      </ul>
    </div>
  </aside>
</div>
{cta_band()}
""" + footer_html() + "</body></html>"

MATTER_TYPES = ["Estate Planning", "Wills & Trusts", "Medicaid / Elder Law", "Probate",
                "Estate Litigation", "Guardianship", "Business / Commercial",
                "Real Estate", "Lemon Law", "Other"]

def contact_form_html(source="contact", idp="cf", submit_label="Request My Free Consultation"):
    """Reusable consultation form. `source` tags which page the lead came from."""
    if FORM_NETLIFY:
        form_attrs = (f'name="{source}" method="POST" action="/thank-you/" '
                      'data-netlify="true" netlify-honeypot="bot-field"')
        form_hidden = f'<input type="hidden" name="form-name" value="{source}">'
        honeypot_name = "bot-field"
    else:
        # Formspree: _next takes an absolute URL for the post-submit redirect,
        # _subject sets the notification email subject, _gotcha is its honeypot.
        subject = ("New consultation request — AkivaShapiroLawPLLC.com"
                   if source == "contact"
                   else f"New consultation request ({source}) — AkivaShapiroLawPLLC.com")
        form_attrs = f'method="POST" action="{FORMSPREE_ENDPOINT}"'
        form_hidden = (
            f'<input type="hidden" name="_next" value="{DOMAIN}/thank-you/">'
            f'<input type="hidden" name="_subject" value="{esc(subject)}">'
            f'<input type="hidden" name="source" value="{esc(source)}">')
        honeypot_name = "_gotcha"
    matter_options = "".join(f"<option>{esc(o)}</option>" for o in MATTER_TYPES)
    return f"""
    <form class="contact-form" {form_attrs}>
      {form_hidden}
      <p class="form-hp"><label>Don't fill this out if you're human: <input name="{honeypot_name}" tabindex="-1" autocomplete="off"></label></p>
      <div class="row">
        <div class="field"><label for="{idp}-name">Full Name <span class="req">*</span></label>
          <input id="{idp}-name" name="name" type="text" required autocomplete="name"></div>
        <div class="field"><label for="{idp}-phone">Phone</label>
          <input id="{idp}-phone" name="phone" type="tel" autocomplete="tel"></div>
      </div>
      <div class="field"><label for="{idp}-email">Email <span class="req">*</span></label>
        <input id="{idp}-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field"><label for="{idp}-matter">What can we help with?</label>
        <select id="{idp}-matter" name="matter">{matter_options}</select></div>
      <div class="field"><label for="{idp}-msg">Briefly, what's going on? <span class="req">*</span></label>
        <textarea id="{idp}-msg" name="message" required placeholder="A sentence or two is plenty — Akiva will follow up."></textarea></div>
      <label class="consent"><input type="checkbox" name="consent" required>
        <span>I understand that submitting this form does not create an attorney-client relationship, and that I should not send confidential or time-sensitive information through it.</span></label>
      <button class="btn btn-gold" type="submit">{esc(submit_label)}</button>
      <p class="form-note">Or call <a href="tel:{PHONE_TEL}" data-track="call">{PHONE_DISPLAY}</a> · email <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </form>"""

def contact_page():
    path = "/contact-us/"
    title = "Contact Long Island Attorney Akiva Shapiro | Free Phone Consultation"
    desc = f"Reach Akiva Shapiro Law, PLLC in Old Bethpage, NY. Free phone consultation for estate planning, elder law and litigation matters: {PHONE_DISPLAY}."
    crumbs = [("Home", "/"), ("Contact", path)]
    schema_extra = [breadcrumbs_schema(crumbs), {"@type": "ContactPage", "url": DOMAIN + path}]
    return head_html(title, desc, path, schema_extra) + nav_html() + f"""
{crumbs_html(crumbs)}
<section style="padding-top:36px 0 8px"><div class="wrap" style="max-width:820px;text-align:center">
  <div class="kicker">Talk to Akiva</div>
  <h1>Start With a Free Phone Consultation</h1>
  <p class="lead" style="margin:.8em auto 0">Tell Akiva what's going on. He'll tell you where you stand under New York law, what your options are, and what he'd do next — free, and without obligation. Prefer to call? <a href="tel:{PHONE_TEL}" data-track="call">{PHONE_DISPLAY}</a>.</p>
</div></section>
<section style="padding-top:24px"><div class="wrap local-grid">
  <div class="form-card">
    <h2>Request Your Consultation</h2>
    <p class="form-note">Akiva personally reviews every inquiry. Fields marked <span style="color:#B4472F">*</span> are required.</p>
    {contact_form_html(source="contact", idp="cf")}
  </div>
  <div>
    <dl class="nap">
      <dt>Office Address</dt><dd>{ADDR}<br>{CITY}, {STATE} {ZIP}</dd>
      <dt>Mailing Address</dt><dd>696 Old Bethpage Rd #540<br>{CITY}, {STATE} {ZIP}</dd>
      <dt>Phone</dt><dd><a href="tel:{PHONE_TEL}" data-track="call">{PHONE_DISPLAY}</a></dd>
      <dt>Fax</dt><dd>{FAX}</dd>
      <dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
      <dt>Hours</dt><dd>Mon–Thu 9:30am–5:30pm<br>Fri 9:30am–4:00pm<br>Evenings &amp; Sunday by appointment</dd>
    </dl>
    <iframe class="map-frame" style="margin-top:22px" title="Map to Akiva Shapiro Law, PLLC" loading="lazy" src="https://www.google.com/maps?q=1+W+Park+Dr,+Old+Bethpage,+NY+11804&output=embed"></iframe>
  </div>
</div></section>
""" + footer_html() + "</body></html>"

def webinars_page():
    path = "/attorney-profile/webinars/"
    title = "Estate Planning Webinars | Akiva Shapiro Law, PLLC"
    desc = "Free educational webinars from Long Island attorney Akiva Shapiro: protecting your inheritance from healthcare emergencies, estate planning basics, and more."
    crumbs = [("Home", "/"), ("Webinars", path)]
    return head_html(title, desc, path, [breadcrumbs_schema(crumbs)]) + nav_html() + f"""
{crumbs_html(crumbs)}
<section style="padding-top:40px"><div class="wrap" style="max-width:820px">
  <div class="kicker">Education</div>
  <h1>Webinars: Learn Before You Decide</h1>
  <p class="lead" style="margin:.8em 0 1.4em">Akiva regularly teaches free webinars for Long Island families — plain-English sessions on protecting what you've built.</p>
  <h2>Save Your Inheritance from Healthcare Emergencies</h2>
  <p>Without proper legal protection, an estate can be spent down in months when a medical emergency hits or long-term care is suddenly needed. This session covers:</p>
  <ul>
    <li>The estate planning questions families ask most</li>
    <li>The financial risks seniors face today</li>
    <li>The legal tools available — and which problems each one solves</li>
    <li>How an estate plan comes together, including fully remote signings</li>
    <li>Open Q&amp;A with Akiva</li>
  </ul>
  <p>To hear about the next session, request an invitation:</p>
  <div class="hero-ctas">
    <a class="btn btn-gold" href="mailto:{EMAIL}?subject=Webinar%20Invitation%20Request">Request an Invitation</a>
    <a class="btn btn-line" href="/faq/">Browse recorded legal answers instead</a>
  </div>
</div></section>
{cta_band()}
""" + footer_html() + "</body></html>"

def who_we_are_page():
    pg = pages.get("who-we-are", {})
    path = "/who-we-are/"
    title = pg.get("title") or "Who We Are | Akiva Shapiro Law, PLLC"
    desc = pg.get("meta_desc") or "Akiva Shapiro Law, PLLC is a Long Island practice built on one idea: every family and business deserves a personal attorney who knows their whole picture."
    crumbs = [("Home", "/"), ("Who We Are", path)]
    return head_html(title, desc, path, [breadcrumbs_schema(crumbs)]) + nav_html() + f"""
{crumbs_html(crumbs)}
<section style="padding-top:40px"><div class="wrap" style="max-width:820px">
  <div class="kicker">The Firm</div>
  <h1>Who We Are</h1>
  <p class="lead" style="margin:.8em 0 1.4em">A personal attorney for your life, business &amp; legacy.</p>
  <p>Akiva Shapiro Law, PLLC is built on a simple idea: your legal life is connected, so your counsel should be too. Instead of a different lawyer for every problem — and no one seeing the whole board — you get one attorney who knows your family, your business, and your goals.</p>
  <h2>Life</h2>
  <p>Legal life events surround us — marriage, divorce, guardianships, real estate, civil disputes, property tax grievances, asset protection, landlord-tenant matters. Having a personal attorney is like having a personal physician: the focus is your overall legal wellness, not just today's symptom.</p>
  <h2>Business</h2>
  <p>As a solution-focused lawyer with nearly three decades of business operations and development experience, Akiva brings CEO-level fluency to commercial litigation, leases, collections, asset protection, and deals.</p>
  <h2>Legacy</h2>
  <p>From wills and trusts to probate and estate litigation, Akiva helps you pass on what you've built — protected from taxes, creditors, healthcare spend-down, and conflict.</p>
  <div class="hero-ctas">
    <a class="btn btn-navy" href="/attorney-profile/akiva-shapiro-esq/">Meet Akiva Shapiro, Esq.</a>
    <a class="btn btn-line" href="/contact-us/">Talk to us</a>
  </div>
</div></section>
{cta_band()}
""" + footer_html() + "</body></html>"

def review_page():
    path = "/review-attorney-akiva-shapiro/"
    title = "Review Attorney Akiva Shapiro | Akiva Shapiro Law, PLLC"
    desc = "A current or former client of Akiva Shapiro Law? Share your experience — your review helps Long Island neighbors find trustworthy counsel."
    crumbs = [("Home", "/"), ("Leave a Review", path)]
    return head_html(title, desc, path, [breadcrumbs_schema(crumbs)]) + nav_html() + f"""
{crumbs_html(crumbs)}
<section style="padding-top:48px;padding-bottom:8px"><div class="wrap center" style="max-width:720px">
  <div class="kicker">Thank You</div>
  <h1>Review Attorney Akiva Shapiro</h1>
  <p class="lead" style="margin:1em auto 0">If you're a current or former client, your honest review helps other Long Island families and business owners find counsel they can trust — and it helps AI assistants like Google and ChatGPT recommend Akiva accurately. Pick whichever platform is easiest for you.</p>
</div></section>
{review_cta_module(heading="Choose Where to Leave Your Review", intro="Google and Yelp are the two that matter most for how people — and AI search — find a Long Island attorney. Either one takes about two minutes.")}
<section style="padding-top:8px"><div class="wrap center" style="max-width:640px">
  <p style="color:var(--muted);font-size:.95rem">Prefer another platform? You can also review Akiva on
    <a href="{SAMEAS_PERSON[1]}" rel="noopener" target="_blank">Avvo</a>.</p>
</div></section>
""" + footer_html() + "</body></html>"

def privacy_page():
    pg = pages.get("privacy-policy", {})
    path = "/privacy-policy/"
    content = render_blocks(pg.get("content", []))
    return head_html(pg.get("title") or "Privacy Policy | " + FIRM,
                     pg.get("meta_desc") or "Privacy policy for AkivaShapiroLawPLLC.com.",
                     path, noindex=False) + nav_html() + f"""
<section style="padding-top:40px"><div class="wrap" style="max-width:820px">
  <h1>Privacy Policy</h1>
  <div class="content-main" style="margin-top:1.4em">{content or '<p>This website collects only the information you choose to send us by phone or email. We do not sell or share personal information.</p>'}</div>
</div></section>
""" + footer_html() + "</body></html>"

def thank_you_page():
    path = "/thank-you/"
    return head_html("Thank You | " + FIRM, "Thank you — your message is on its way to Akiva.", path, noindex=True) + nav_html() + f"""
<section style="padding-top:60px"><div class="wrap center" style="max-width:640px">
  <div class="kicker">Message Received</div>
  <h1>Thank You</h1>
  <p class="lead" style="margin:1em auto">Your message is on its way. Akiva personally reviews every inquiry and will get back to you promptly. If it's urgent, call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
  <p style="margin-top:1.6em"><a class="btn btn-navy" href="/faq/">Browse legal answers while you wait</a></p>
</div></section>
""" + footer_html() + "</body></html>"

def not_found_page():
    popular = [
        ("/estate-planning/", "Estate Planning"),
        ("/trusts-asset-protection/", "Trusts &amp; Asset Protection"),
        ("/medicaid-trusts-and-applications/", "Medicaid Planning"),
        ("/probate/", "Probate"),
        ("/estate-litigation/", "Estate Litigation"),
        ("/guardianships/", "Guardianships"),
        ("/lawsuits-civil-litigation/", "Lawsuits &amp; Civil Litigation"),
        ("/ny-lemon-law-for-faulty-automobiles/", "NY Lemon Law"),
    ]
    pop_html = "".join(
        f'<a class="q-item" href="{u}"><span>{t}</span><span class="arr">→</span></a>'
        for u, t in popular)
    return head_html("Page Not Found | " + FIRM,
                     "That page couldn't be found. Browse our practice areas and legal answers, or send Akiva a message.",
                     "/404.html", noindex=True) + nav_html() + f"""
<section style="padding:56px 0 8px"><div class="wrap center" style="max-width:720px">
  <div class="kicker" style="font-size:.9rem">Error 404</div>
  <h1>We Couldn't Find That Page</h1>
  <p class="lead" style="margin:1em auto 1.6em">The page may have moved when we rebuilt the site, or the link may be out of date. Nothing is lost — here's how to get where you were going.</p>
  <div class="hero-ctas" style="justify-content:center">
    <a class="btn btn-gold" href="tel:{PHONE_TEL}" data-track="call">Call {PHONE_DISPLAY}</a>
    <a class="btn btn-line" href="/faq/">Browse Legal Answers</a>
    <a class="btn btn-navy" href="/">Go to Homepage</a>
  </div>
</div></section>

<section style="padding:40px 0 8px"><div class="wrap" style="max-width:900px">
  <h2 class="center" style="font-size:1.5rem">Popular Pages</h2>
  <div class="q-list" style="margin-top:1.4em">{pop_html}</div>
  <p class="center" style="margin-top:1.4em;font-size:.95rem">
    You can also see <a href="/areas-we-serve/">the communities we serve</a>,
    read <a href="/attorney-profile/akiva-shapiro-esq/">about Akiva</a>, or
    browse <a href="/testimonials/">client testimonials</a>.
  </p>
</div></section>

<section class="band"><div class="wrap" style="max-width:720px">
  <div class="form-card">
    <div class="center">
      <div class="kicker">Still Stuck?</div>
      <h2>Tell Akiva What You Were Looking For</h2>
      <p class="form-note" style="margin-top:.5em">Send a quick note and he'll point you to the right place — or just answer your question directly. Free, no obligation.</p>
    </div>
    {contact_form_html(source="404-page", idp="nf", submit_label="Send My Question")}
  </div>
</div></section>
""" + footer_html() + "</body></html>"

# ---------------------------------------------------------------- emit
def write(path, content):
    p = path.strip("/")
    base = os.path.basename(p)
    # literal file when it has an extension (.html/.xml/.txt), is a dotfile
    # (.htaccess), or is a known extensionless config file (_redirects);
    # otherwise emit a pretty-URL directory with index.html
    is_file = ("." in base) or base in ("_redirects",)
    full = os.path.join(OUT, p) if is_file else os.path.join(OUT, p, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def main():
    os.makedirs(os.path.join(OUT, "css"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "js"), exist_ok=True)
    open(os.path.join(OUT, "css", "style.css"), "w").write(CSS)
    open(os.path.join(OUT, "js", "main.js"), "w").write(JS)

    emitted = []

    write("/index.html", home_page())
    emitted.append("/")

    # practice pages (incl. pillar pages life/business/legacy)
    custom_dir = os.path.join(BASE, "custom")
    for slug, pg in pages.items():
        if pg["type"] == "practice":
            custom_path = os.path.join(custom_dir, slug + ".json")
            if os.path.exists(custom_path):
                custom = json.load(open(custom_path))
                write(pg["path"], custom_practice_page(pg, custom))
            else:
                write(pg["path"], practice_page(pg))
            emitted.append(pg["path"] + "/")

    # articles
    missing = []
    for meta in plan["qa"]:
        art = read_article(meta["slug"])
        if not art:
            missing.append(meta["slug"])
            continue
        write(meta["path"], article_page(meta, art))
        emitted.append(meta["path"] + "/")

    # hubs
    write("/faq", faq_page()); emitted.append("/faq/")
    write("/testimonials", testimonials_page()); emitted.append("/testimonials/")
    write("/attorney-profile/akiva-shapiro-esq", attorney_page()); emitted.append("/attorney-profile/akiva-shapiro-esq/")
    write("/attorney-profile/webinars", webinars_page()); emitted.append("/attorney-profile/webinars/")
    write("/contact-us", contact_page()); emitted.append("/contact-us/")
    write("/who-we-are", who_we_are_page()); emitted.append("/who-we-are/")
    write("/areas-we-serve", areas_hub_page()); emitted.append("/areas-we-serve/")
    for town in TOWNS["towns"]:
        p = "/" + town_slug(town["name"]) + "/"
        write(p.rstrip("/"), town_page(town)); emitted.append(p)
    write("/review-attorney-akiva-shapiro", review_page()); emitted.append("/review-attorney-akiva-shapiro/")
    write("/privacy-policy", privacy_page()); emitted.append("/privacy-policy/")
    write("/thank-you", thank_you_page())  # noindex — not in sitemap
    write("/404.html", not_found_page())

    # sitemap
    urls = "".join(
        f"<url><loc>{DOMAIN}{p}</loc><lastmod>{TODAY}</lastmod></url>"
        for p in sorted(set(emitted)))
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")

    # redirects (Netlify + Apache)
    lines_netlify = [f"{f}/ {t}/ 301" if not t.endswith("/") and t != "/" else f"{f}/ {t} 301"
                     for f, t in plan["redirects"].items()]
    lines_netlify = [f"{f} {t if t == '/' else t + '/'} 301!" for f, t in plan["redirects"].items()] + \
                    [f"{f}/ {t if t == '/' else t + '/'} 301!" for f, t in plan["redirects"].items()]
    write("/_redirects", "\n".join(lines_netlify) + "\n")
    ht = ["ErrorDocument 404 /404.html", "RewriteEngine On"]
    for f, t in plan["redirects"].items():
        target = t if t == "/" else t + "/"
        ht.append(f"RewriteRule ^{re.escape(f.strip('/'))}/?$ {target} [R=301,L]")
    write("/.htaccess", "\n".join(ht) + "\n")
    # Netlify 404 fallback
    with open(os.path.join(OUT, "_redirects"), "a") as f:
        f.write("/* /404.html 404\n")

    print(f"emitted {len(emitted)} pages; missing articles: {len(missing)}")
    if missing:
        print(" missing:", missing[:20])
    if not FORM_NETLIFY and "REPLACE_ME" in FORMSPREE_ENDPOINT:
        print("\n*** WARNING: contact form is NOT live ***")
        print("    FORMSPREE_ENDPOINT is still the placeholder — submissions will fail.")
        print("    Create a form at formspree.io for Akiva and paste its endpoint")
        print("    into FORMSPREE_ENDPOINT at the top of generate_site.py, then rebuild.")
    if not GA4_ID and not GTM_ID:
        print("\n    Note: no analytics ID set (GA4_ID / GTM_ID) — no tracking injected.")

if __name__ == "__main__":
    main()
