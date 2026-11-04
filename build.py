#!/usr/bin/env python3
"""Animal Cafe static site builder.

python3 build.py prod     -> public/     (clean URLs for Cloudflare, /acai-bowls/ etc.)
python3 build.py preview  -> preview/   (flat .html files, everything inline)
"""
import json, os, sys, shutil, html as H

MODE = sys.argv[1] if len(sys.argv) > 1 else "prod"
OUT = "public" if MODE == "prod" else "preview"
SITE = "https://animalcafe.net"

# ---------------------------------------------------------------- links
PHONE = "856-839-4536"
TEL = "tel:+18568394536"
EMAIL = "info@animalparadisegyms.com"
ADDR1 = "3849 S Delsea Dr, Suite E000"
ADDR2 = "Vineland, NJ 08360"
CLOVER = "https://animal-cafe.cloveronline.com/menu/all"
CLV = "https://animal-cafe.cloveronline.com/menu/"
UBER = "https://www.ubereats.com/store/animal-cafe/uxlY_r_lUMOmbjL9ZRG-vQ"
DOOR = "https://www.doordash.com/store/animal-cafe-vineland-32609433/105593151/"
GRUB = "https://www.grubhub.com/restaurant/animal-cafe-3849-s-delsea-dr-vineland/10498544"
MAPS = "https://www.google.com/maps?cid=17550021963729498866"
MAP_EMBED = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3081.724536129197!2d-75.03585360000001!3d39.4303531!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c733d4d5824537%3A0xf38e33fdf46672f2!2sAnimal%20Cafe!5e0!3m2!1sen!2sus!4v1792395826220!5m2!1sen!2sus"
IG = "https://www.instagram.com/animalcafenj/"
FB = "https://www.facebook.com/profile.php?id=61560036899811"
APG = "https://animalparadisegyms.com/"
APG_MEM = "https://animalparadisegyms.com/memberships/"
SUPPS = "https://animalsupps.co/"
CLOVER_IOS = "https://apps.apple.com/us/app/clover/id428620381"
CLOVER_AND = "https://play.google.com/store/apps/details?id=com.getperka.android"
META_PIXEL = "1973725770154277"  # from the Hostinger draft; confirm before launch

# ---------------------------------------------------------------- images
# All images live in /img inside the site (no hotlinks), so nothing breaks when DNS moves.
P = "/img/" if MODE == "prod" else "img/"
IMG = {k: P + v for k, v in {
    "logo": "logo.webp", "logo_png": "logo.png", "logo_full": "logo-full.webp", "logo_full_png": "logo-full.png", "og": "og.jpg",
    "video": "cafe.mp4", "poster": "cafe-poster.webp",
    "counter": "counter.webp", "cafe_sign": "cafe-sign.webp", "lounge": "lounge.webp",
    "cafe_floor": "cafe-floor.webp", "posing": "posing-room.webp",
    "bowl_signature": "bowl-animal-paradise.webp", "bowl_dragon": "bowl-dragon-breeze.webp",
    "bowl_oasis": "bowl-oasis.webp", "bowl_paradise": "bowl-paradise-split.webp",
    "bowl_sunrise": "bowl-sunrise.webp", "bowl_bliss": "bowl-banana-berry.webp",
    "bowl_twist": "bowl-tropical-twist.webp",
    "sm_jungle": "smoothie-jungle-berry.webp", "sm_island": "smoothie-island-heat.webp",
    "sh_gorilla": "shake-gorilla-gainz.webp", "sh_berry": "shake-berry-blast.webp", "sh_tropical": "shake-tropical-paradise.webp",
    "lineup_bowls": "lineup-bowls.webp", "lineup_smoothies": "lineup-smoothies.webp",
}.items()}
ABS = lambda k: SITE + "/img/" + IMG[k].split("/img/")[-1].split("img/")[-1]

# base / ingredient swatch colours used for card art
SW = {
    "acai": "#4B1D66", "pitaya": "#E0337E", "mango": "#FFB01F", "passion": "#F28C28",
    "coconut": "#EFE6D8", "banana": "#F4D96B", "berry": "#B3264A", "citrus": "#FF9F1C",
    "green": "#79B64A", "beet": "#8E1F4F", "choc": "#5A3524", "pb": "#C68B4E",
    "kiwi": "#8DBF3F", "pine": "#F7C948", "straw": "#E2453C", "blue": "#3B4A9E",
    "berrymix": "#9B2D5C", "gold": "#E9A23B", "pink": "#F06C9B",
}

# ---------------------------------------------------------------- menu data
def item(name, price, desc, cat, sw, img=None, base=None, badge=None, clover=None,
         pickup=True, delivery=True, note=None):
    return dict(name=name, price=price, desc=desc, cat=cat, sw=sw, img=img, base=base,
                badge=badge, clover=clover, pickup=pickup, delivery=delivery, note=note)

SINGLE = [
    item("The Animal Paradise Bowl", "11.99", ["Banana", "Strawberries", "Almond halves", "Nutella drizzle"],
         "bowls", ["acai", "banana", "straw"], "bowl_signature", "Açaí", "Signature",
         "the-animal-paradise-bowl-SD1KJYQEDMTVE"),
    item("The Oasis Bowl", "11.99", ["Pineapple", "Mango", "Coconut flakes", "Honey drizzle"],
         "bowls", ["pitaya", "pine", "mango"], "bowl_oasis", "Pitaya (dragon fruit)"),
    item("The Vineland Bowl", "11.99", ["Blueberries", "Strawberries", "Chia seeds", "Strawberry drizzle"],
         "bowls", ["coconut", "blue", "straw"], None, "Coconut", None,
         "the-vineland-bowl-YMGJGXAJG5856"),
    item("Banana Berry Bliss Bowl", "11.99", ["Strawberries", "Blueberries", "Cocoa nibs", "Peanut butter drizzle"],
         "bowls", ["banana", "straw", "pb"], "bowl_bliss", "Banana", "New",
         "banana-berry-bliss-bowl-60WMD4WGBSXS4"),
]
SPLIT = [
    item("The Sunrise Bowl", "12.99", ["Pineapple", "Kiwi", "Coconut flakes", "Honey drizzle"],
         "bowls", ["acai", "mango", "kiwi"], "bowl_sunrise", "Açaí + mango", None,
         "the-sunrise-bowl-63JSYWRKG3M78"),
    item("The Dragon Breeze Bowl", "12.99", ["Blueberries", "Raspberries", "Toasted coconut", "Chia seeds", "Nutella drizzle"],
         "bowls", ["pitaya", "passion", "blue"], "bowl_dragon", "Dragon fruit + passion fruit", None,
         "the-dragon-breeze-bowl-FEARD4RN86FWJ"),
    item("The Tropical Twist Bowl", "12.99", ["Banana", "Mango", "Almond halves", "Caramel drizzle"],
         "bowls", ["acai", "coconut", "mango"], "bowl_twist", "Açaí + coconut", None,
         "the-tropical-twist-M7Q1YRYAHT79M"),
    item("Paradise Split Bowl", "12.99", ["Kiwi", "Pineapple", "Cocoa nibs", "Nutella drizzle"],
         "bowls", ["banana", "coconut", "kiwi"], "bowl_paradise", "Banana + coconut", "New",
         "paradise-split-bowl-AH55P9PFSW96G"),
]
WEEKEND = [
    ("Animal Bowl", "Açaí base", "Granola, strawberry, blueberry, Nutella drizzle", ["acai", "straw"], "animal-bowl-special-336V1CQSMXJMR"),
    ("Dragon Bowl", "Dragon fruit base", "Granola, blackberry, banana, strawberry drizzle", ["pitaya", "banana"], "dragon-bowl-special-JFR8Y9G2YQE4R"),
    ("Island Bowl", "Mango base", "Granola, strawberry, pineapple, honey drizzle", ["mango", "pine"], "island-bowl-special-MB4BKEXYPAGS8"),
    ("Playa Bowl", "Coconut base", "Granola, kiwi, strawberries, toasted coconut", ["coconut", "kiwi"], "playa-bowl-special-Q253PCSK0FVK6"),
]
SMOOTHIES = [
    item("Jungle Berry", "9.99", ["Strawberry", "Blueberry", "Raspberry", "Blackberry", "Coconut water"],
         "smoothies", ["berry", "blue", "straw"], "sm_jungle", pickup=False, delivery=False),
    item("Island Heat", "9.99", ["Pineapple", "Mango", "Banana", "Kiwi", "Coconut water"],
         "smoothies", ["pine", "mango", "kiwi"], "sm_island", pickup=False, delivery=False),
    item("Paradise Citrus", "9.99", ["Orange", "Mango", "Pineapple", "Coconut water"],
         "smoothies", ["citrus", "mango", "pine"], None, pickup=False, delivery=False),
    item("Tiki Chill", "9.99", ["Banana", "Strawberry", "Blueberry", "Coconut water"],
         "smoothies", ["banana", "straw", "blue"], None, pickup=False, delivery=False),
    item("Build Your Own Smoothie", "9.99", ["Any base", "Any 3 fruits"],
         "smoothies", ["straw", "mango", "kiwi"], "lineup_smoothies", None, "Popular", pickup=False, delivery=False),
]
SHAKES_HIGH = [
    item("Gorilla Gainz", "10.99", ["Isolate vanilla whey", "Banana", "Almond milk", "Natural peanut butter"],
         "protein", ["banana", "pb", "coconut"], "sh_gorilla", None, "Best seller", pickup=False, delivery=False),
    item("Lean Machine", "9.99", ["Isolate vanilla whey", "Mixed berries", "Coconut water"],
         "protein", ["berrymix", "blue", "coconut"], None, pickup=False, delivery=False),
    item("Muscle Monkey Madness", "10.99", ["Isolate chocolate whey", "Banana", "Almond milk", "Natural peanut butter"],
         "protein", ["choc", "banana", "pb"], None, pickup=False, delivery=False),
]
SHAKES_SPEC = [
    item("Tropical Paradise", "10.99", ["Isolate whey", "Pineapple", "Mango", "Coconut water", "Greek yogurt"],
         "protein", ["pine", "mango", "coconut"], "sh_tropical", pickup=False, delivery=False),
    item("Berry Blast", "10.49", ["Isolate whey", "Mixed berries", "Greek yogurt"],
         "protein", ["berrymix", "straw", "coconut"], "sh_berry", pickup=False, delivery=False),
    item("Citrus Sunrise", "10.99", ["Isolate whey", "Orange", "Pineapple", "Coconut water", "Greek yogurt"],
         "protein", ["citrus", "pine", "coconut"], None, pickup=False, delivery=False),
]
ALL = SINGLE + SPLIT + SMOOTHIES + SHAKES_HIGH + SHAKES_SPEC

BASES = [("Açaí", "acai", "Deep berry with a cocoa finish. The classic."),
         ("Pitaya", "pitaya", "Dragon fruit. Bright magenta, lightly sweet."),
         ("Mango", "mango", "Thick, sunny and sweet."),
         ("Passion fruit", "passion", "Tart and tropical. Great in a split."),
         ("Banana", "banana", "Thick, creamy and naturally sweet. Great with peanut butter."),
         ("Coconut", "coconut", "Creamy and mellow. Lets the toppings lead.")]
FRUITS = ["Strawberry", "Blueberry", "Raspberry", "Blackberry", "Pineapple", "Mango", "Kiwi", "Banana", "Orange"]
CRUNCH = ["Toasted coconut flakes", "Cocoa nibs", "Almond halves", "Pumpkin seeds"]
DRIZZLE = ["Honey", "Nutella", "Caramel", "Strawberry"]
EXTRA = ["Chia seeds", "Coconut flakes"]

# ---------------------------------------------------------------- pages
PAGES = [
    ("home", "Home"), ("acai-bowls", "Açaí Bowls"), ("smoothies", "Smoothies"),
    ("protein-shakes", "Protein Shakes"),
    ("menu", "Full Menu"), ("order", "Order"), ("about-us", "About"),
    ("contact", "Contact"), ("faq", "FAQ"),
]
NAV = [("acai-bowls", "Bowls"), ("smoothies", "Smoothies"), ("protein-shakes", "Protein"),
       ("menu", "Menu"), ("about-us", "About"), ("contact", "Visit")]

def href(slug):
    if MODE == "prod":
        return "/" if slug == "home" else f"/{slug}/"
    return "index.html" if slug == "home" else f"{slug}.html"

def canon(slug):
    return SITE + ("/" if slug == "home" else f"/{slug}/")

e = H.escape

def ext(url, label, cls="", extra=""):
    if url == CLOVER:
        return f'<a class="{cls}" href="#order" data-order aria-haspopup="dialog"{extra}>{label}</a>'
    return f'<a class="{cls}" href="{url}" target="_blank" rel="noopener"{extra}>{label}</a>'

def money(p):
    return f"${p}"

# ---------------------------------------------------------------- components
def art(sw, img=None, alt="", eager=False):
    cols = [SW[s] for s in sw] + [SW[sw[0]]] * (3 - len(sw))
    style = f"--a:{cols[0]};--b:{cols[1]};--c:{cols[2]}"
    im = ""
    if img:
        lz = "eager" if eager else "lazy"
        im = f'<img src="{IMG[img]}" alt="{e(alt)}" loading="{lz}" decoding="async" onerror="this.remove()">'
    return f'<div class="art" style="{style}" aria-hidden="{ "false" if img else "true"}"><span class="blob b1"></span><span class="blob b2"></span><span class="blob b3"></span>{im}</div>'

def order_links(it):
    # Same actions on every product card: pickup on Clover, then the 3 delivery apps.
    url = CLV + it["clover"] if it["clover"] else CLOVER
    pickup = f'<a class="btn btn-sm btn-mango" href="{url}" target="_blank" rel="noopener">Order pickup</a>'
    deliv = f'<span class="deliv">Delivery: {ext(UBER,"Uber Eats")} {ext(DOOR,"DoorDash")} {ext(GRUB,"Grubhub")}</span>'
    return '<div class="card-actions">' + pickup + deliv + "</div>"

def card(it, eager=False):
    badge = f'<span class="badge">{e(it["badge"])}</span>' if it["badge"] else ""
    base = f'<p class="base">Suggested base: <strong>{e(it["base"])}</strong></p>' if it["base"] and it["cat"] == "bowls" else ""
    size = ""
    chips = "".join(f"<li>{e(x)}</li>" for x in it["desc"])
    return f'''<article class="card" data-cat="{it["cat"]}">
  <div class="card-art">{art(it["sw"], it["img"], it["name"], eager)}{badge}</div>
  <div class="card-body">
    <div class="card-head"><h3>{e(it["name"])}</h3><span class="price">{money(it["price"])}</span></div>
    {base}{size}
    <ul class="chips">{chips}</ul>
    {order_links(it)}
  </div>
</article>'''

def grid(items, eager=False):
    return '<div class="grid">' + "".join(card(i, eager) for i in items) + "</div>"

def page_head(eyebrow, h1, lead, crumbs):
    cr = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{href("home")}">Home</a><span>/</span><span>{e(crumbs)}</span></nav>'
    return f'''<header class="phead"><div class="wrap">{cr}
  <p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p></div></header>'''

def counter_band(title, text):
    return f'''<section class="band band-acai"><div class="wrap band-in">
  <div><h2>{title}</h2><p>{text}</p></div>
  <div class="band-btns"><a class="btn btn-mango" href="{TEL}">Call {PHONE}</a><a class="btn btn-line" href="{href("acai-bowls")}">Order a bowl online</a></div>
</div></section>'''

def order_band(title="Order ahead, skip the line.", text="Pickup orders go straight to the counter inside Animal Paradise Gyms. Delivery runs through the apps you already use."):
    return f'''<section class="band band-acai"><div class="wrap band-in">
  <div><h2>{title}</h2><p>{text}</p></div>
  <div class="band-btns">{ext(CLOVER,"Order for pickup","btn btn-mango")}
    {ext(UBER,"Uber Eats","btn btn-line")}{ext(DOOR,"DoorDash","btn btn-line")}{ext(GRUB,"Grubhub","btn btn-line")}</div>
</div></section>'''

def faq_block(qs, schema_list=None):
    out = '<div class="faq">'
    for q, a in qs:
        out += f'<details><summary>{e(q)}</summary><p>{a}</p></details>'
        if schema_list is not None:
            import re
            schema_list.append({"@type": "Question", "name": q,
                                "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}})
    return out + "</div>"

def menu_schema(name, sections):
    return {"@context": "https://schema.org", "@type": "Menu", "name": name,
            "hasMenuSection": [{"@type": "MenuSection", "name": sn, "hasMenuItem": [
                {"@type": "MenuItem", "name": i["name"], "description": ", ".join(i["desc"]),
                 "offers": {"@type": "Offer", "price": i["price"], "priceCurrency": "USD"}} for i in its]}
                for sn, its in sections]}

BUSINESS = {
    "@context": "https://schema.org", "@type": "Restaurant", "@id": SITE + "/#cafe",
    "name": "Animal Cafe", "url": SITE + "/", "telephone": "+1-856-839-4536", "email": EMAIL,
    "image": ABS("og"), "logo": ABS("logo_full_png"), "priceRange": "$",
    "servesCuisine": ["Açaí bowls", "Smoothies", "Protein shakes"],
    "address": {"@type": "PostalAddress", "streetAddress": "3849 S Delsea Dr, Suite E000",
                "addressLocality": "Vineland", "addressRegion": "NJ", "postalCode": "08360", "addressCountry": "US"},
    "geo": {"@type": "GeoCoordinates", "latitude": 39.4303531, "longitude": -75.0358536}, "hasMap": MAPS,
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "04:00", "closes": "23:59"}],
    "hasMenu": SITE + "/menu/", "acceptsReservations": False,
    "potentialAction": {"@type": "OrderAction", "target": CLOVER},
    "containedInPlace": {"@type": "ExerciseGym", "name": "Animal Paradise Gyms", "url": APG},
    "sameAs": [IG, FB],
}

# ---------------------------------------------------------------- page bodies
def home():
    picks = [SINGLE[0], SPLIT[1], SHAKES_HIGH[0], SMOOTHIES[0], SPLIT[0], SHAKES_SPEC[0]]
    cats = [
        ("acai-bowls", "Açaí bowls", "from $10.49", "Single base, split base or build your own. Granola in every bowl.", ["acai", "pitaya", "mango"], "lineup_bowls"),
        ("smoothies", "Smoothies", "$9.99", "Real fruit and coconut water, blended when you order.", ["berry", "mango", "kiwi"], "sm_jungle"),
        ("protein-shakes", "Protein shakes", "from $9.99", "Isolate whey, real fruit and natural peanut butter.", ["choc", "pb", "banana"], "sh_gorilla"),
    ]
    catcards = "".join(f'''<a class="cat" href="{href(s)}">{art(sw, im, t)}
      <div class="cat-body"><div class="card-head"><h3>{t}</h3><span class="price">{p}</span></div><p>{d}</p><span class="more">See the {t.lower()}</span></div></a>''' for s, t, p, d, sw, im in cats)
    gallery = "".join(f'<figure>{art(sw, k, cap)}<figcaption>{cap}</figcaption></figure>' for k, cap, sw in [
        ("counter", "The counter inside the gym", ["acai", "mango"]),
        ("bowl_signature", "Animal Paradise Bowl", ["pitaya", "straw"]),
        ("cafe_sign", "Animal Cafe, Vineland", ["acai", "pitaya"]),
        ("bowl_dragon", "Dragon Breeze", ["pitaya", "blue"]),
        ("bowl_oasis", "Oasis Bowl", ["mango", "acai"]),
        ("lounge", "The lounge by the counter", ["mango", "acai"]),
    ])
    faqs = [
        ("Do I need a gym membership to order?", "No. Animal Cafe is open to everyone. Walk in through Animal Paradise Gyms, order at the counter, and you are good to go."),
        ("What are your hours?", "Every day from 4AM to midnight, the same hours as the gym."),
        ("Can I order ahead for pickup?", f'Yes. Bowls can be ordered ahead on our {ext(CLOVER,"online pickup menu")}. Smoothies and protein shakes are made at the counter.'),
        ("Do gym members get a discount?", f'Animal Paradise Gold members save 5% and Premium members save 10% at the cafe. {ext(APG_MEM,"See gym memberships")}.'),
    ]
    marquee = " · ".join(["Açaí", "Pitaya", "Mango", "Passion fruit", "Coconut", "Granola", "Nutella drizzle", "Isolate whey", "Natural peanut butter", "Kiwi", "Coconut water", "Chia seeds", "Almond milk", "Greek yogurt"])
    return f'''
<section class="hero"><div class="wrap hero-in">
  <div class="hero-copy">
    <p class="eyebrow">Inside Animal Paradise Gyms · Vineland, NJ</p>
    <h1>Fresh bowls.<br>Real fruit.<br><em>Serious protein.</em></h1>
    <p class="lead">Açaí bowls, smoothies and protein shakes blended to order, right inside the gym. Open every day from 4AM to midnight, so breakfast, post workout and late night are all covered.</p>
    <div class="hero-btns">{ext(CLOVER,"Order for pickup","btn btn-mango btn-lg")}<a class="btn btn-ink btn-lg" href="{href("menu")}">See the full menu</a></div>
    <ul class="hero-facts"><li><strong>4AM to 12AM</strong><span>Every day</span></li><li><strong>$9.99</strong><span>Smoothies</span></li><li><strong>3 apps</strong><span>For delivery</span></li></ul>
  </div>
  <div class="hero-bowl">
    <div class="bowl">
      <div class="art" style="--a:{SW['acai']};--b:{SW['pitaya']};--c:{SW['mango']}"><span class="blob b1"></span><span class="blob b2"></span><span class="blob b3"></span>
        <video autoplay muted loop playsinline preload="metadata" poster="{IMG['poster']}" aria-label="Açaí bowls being made at Animal Cafe"><source src="{IMG['video']}" type="video/mp4"></video></div>
    </div>
    <div class="sticker s1"><span>Signature</span><strong>Animal Paradise Bowl</strong><em>$11.99</em></div>
    <div class="sticker s2"><span>Best seller</span><strong>Gorilla Gainz</strong><em>$10.99</em></div>
  </div>
</div></section>
<div class="ticker" aria-hidden="true"><div class="ticker-track"><span>{marquee} · </span><span>{marquee} · </span></div></div>

<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">What we make</p><h2>Three ways to fuel up</h2><p>Everything starts the moment you order. Nothing sits on a shelf waiting for you.</p></div>
  <div class="cats">{catcards}</div>
</div></section>

<section class="sec sec-tint"><div class="wrap">
  <div class="sec-head row"><div><p class="eyebrow">Counter favorites</p><h2>What Vineland keeps ordering</h2></div><a class="link-arrow" href="{href("menu")}">Full menu with prices</a></div>
  {grid(picks)}
</div></section>

<section class="sec"><div class="wrap split">
  <div class="split-media">{art(["acai","mango"], "bowl_sunrise", "A fresh fruit açaí bowl at Animal Cafe")}</div>
  <div class="split-copy"><p class="eyebrow">Build your own</p><h2>Your bowl, priced as you build it</h2>
    <p>Pick one base or split two, add your fruit, crunch and drizzle, and watch the total update before you order. Single base bowls start at $10.49 with granola, two fruits and a drizzle included.</p>
    <ul class="ticks"><li>6 bases: açaí, pitaya, mango, passion fruit, coconut, banana</li><li>9 fruits, 4 crunch toppings, 4 drizzles</li><li>Split base for $11.99</li></ul>
    <a class="btn btn-ink" href="{href("acai-bowls")}">Open the bowl builder</a></div>
</div></section>

<section class="sec sec-acai"><div class="wrap">
  <div class="sec-head"><p class="eyebrow light">How to order</p><h2>Counter, pickup or delivery</h2></div>
  <div class="ways">
    <div class="way"><h3>Order ahead for pickup</h3><p>Bowls and weekend specials on our online menu. Pay ahead and grab it at the counter on your way in or out.</p>{ext(CLOVER,"Open pickup menu","btn btn-mango btn-sm")}</div>
    <div class="way"><h3>Get it delivered</h3><p>Every signature and build your own bowl, delivered across the Vineland area.</p><div class="way-links">{ext(UBER,"Uber Eats","btn btn-line btn-sm")}{ext(DOOR,"DoorDash","btn btn-line btn-sm")}{ext(GRUB,"Grubhub","btn btn-line btn-sm")}</div></div>
    <div class="way"><h3>Walk up to the counter</h3><p>Inside Animal Paradise Gyms at Cumberland Mall. No membership needed to order.</p>{ext(MAPS,"Get directions","btn btn-line btn-sm")}</div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head row"><div><p class="eyebrow">@animalcafenj</p><h2>Fresh off the counter</h2></div>{ext(IG,"Follow on Instagram","link-arrow")}</div>
  <div class="gallery">{gallery}</div>
</div></section>

<section class="sec sec-tint"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Google reviews</p><h2>What customers say</h2></div>
  <div class="quotes">
    <blockquote><p class="stars" aria-label="5 out of 5 stars">★★★★★</p><p>Everything tasted amazing. The fruit was fresh and very sweet, the mango base is great as well as the açaí base and my bowl was filled. Definitely recommend!</p><footer>Keyona</footer></blockquote>
    <blockquote><p class="stars" aria-label="5 out of 5 stars">★★★★★</p><p>Honestly the best smoothie I've ever had.</p><footer>Zuhayr</footer></blockquote>
    <div class="member"><p class="eyebrow">Train here too?</p><h3>Members save up to 10%</h3><p>Animal Paradise Gold members save 5% at the cafe. Premium members save 10%.</p>{ext(APG_MEM,"See gym memberships","btn btn-ink btn-sm")}</div>
  </div>
</div></section>

<section class="sec"><div class="wrap split">
  <div class="split-copy"><p class="eyebrow">Good to know</p><h2>Quick answers</h2>{faq_block(faqs)}<a class="link-arrow" href="{href("faq")}">All questions</a></div>
  {visit_card()}
</div></section>
{order_band()}'''

def map_block():
    frame = (f'<iframe src="{MAP_EMBED}" title="Map to Animal Cafe inside Animal Paradise Gyms, Vineland NJ" loading="lazy" '
             f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>') if MODE == "prod" else ""
    return f'''<div class="map-wrap"><div class="map">
  <a class="map-fallback" href="{MAPS}" target="_blank" rel="noopener"><span class="pin" aria-hidden="true"></span><strong>Animal Cafe</strong><span>3849 S Delsea Dr, Vineland NJ</span><em>Open in Google Maps</em></a>{frame}</div>
  <div class="map-card"><p class="eyebrow">Inside Animal Paradise Gyms</p><h3>Cumberland Mall, Vineland</h3>
    <p class="open-now" data-open>Open every day, 4AM to 12AM</p>
    <p class="muted">{ADDR1}<br>{ADDR2}</p>
    <div class="visit-btns">{ext(MAPS,"Get directions","btn btn-mango btn-sm")}<a class="btn btn-line-ink btn-sm" href="{TEL}">{PHONE}</a></div></div>
</div>'''

def visit_card():
    return f'''<aside class="visit">
  <p class="eyebrow">Find us</p><h3>Animal Cafe</h3>
  <p class="open-now" data-open>Open every day, 4AM to 12AM</p>
  <dl><dt>Address</dt><dd>{ADDR1}<br>Cumberland Mall, {ADDR2}<br><span class="muted">Inside Animal Paradise Gyms. Free parking.</span></dd>
  <dt>Hours</dt><dd>Monday to Sunday<br>4:00AM to 12:00AM</dd>
  <dt>Phone</dt><dd><a href="{TEL}">{PHONE}</a></dd></dl>
  <div class="visit-btns">{ext(MAPS,"Get directions","btn btn-mango btn-sm")}<a class="btn btn-line-ink btn-sm" href="{TEL}">Call the cafe</a></div>
</aside>'''

def builder():
    base_btns = "".join(f'<button type="button" class="pick base-pick" data-base="{n}" style="--sw:{SW[k]}" aria-pressed="false"><i></i>{n}</button>' for n, k, _ in BASES)
    def checks(group, opts, price):
        return "".join(f'<label class="opt"><input type="checkbox" name="{group}" value="{e(o)}" id="{group}-{i}"><span>{e(o)}</span></label>' for i, o in enumerate(opts))
    return f'''<div class="builder" id="builder">
  <div class="b-main">
    <div class="b-step"><h3>1. Size up</h3><div class="seg" role="radiogroup" aria-label="Bowl type">
      <button type="button" class="seg-btn on" data-type="single" aria-pressed="true">Single base <b>$10.49</b></button>
      <button type="button" class="seg-btn" data-type="split" aria-pressed="false">Split base <b>$11.99</b></button></div></div>
    <div class="b-step"><h3>2. Pick your base <span class="hint" id="baseHint">Choose 1</span></h3><div class="picks">{base_btns}</div></div>
    <div class="b-step"><h3>3. Fruit <span class="hint">2 included, extras $1.25</span></h3><div class="opts">{checks("fruit", FRUITS, 1.25)}</div></div>
    <div class="b-step"><h3>4. Crunch <span class="hint">$0.75 each</span></h3><div class="opts">{checks("crunch", CRUNCH, .75)}</div></div>
    <div class="b-step"><h3>5. Drizzle <span class="hint">1 included, extras $0.50</span></h3><div class="opts">{checks("drizzle", DRIZZLE, .5)}</div></div>
    <div class="b-step"><h3>6. Extras <span class="hint">$0.75 each</span></h3><div class="opts">{checks("extra", EXTRA, .75)}</div></div>
  </div>
  <aside class="b-sum" aria-live="polite">
    <div class="b-bowl" id="bowlViz"><span></span><span></span></div>
    <p class="eyebrow">Your bowl</p>
    <ul class="b-lines" id="bLines"></ul>
    <p class="b-total"><span>Estimated total</span><strong id="bTotal">$10.49</strong></p>
    <a class="btn btn-mango" id="bOrder" href="{CLV}build-your-own-bowl-EFH18GTNEDRMT" target="_blank" rel="noopener">Order this bowl for pickup</a>
    <p class="fine">Granola comes in every bowl. You will pick these same options on the pickup menu. Final price shows at checkout.</p>
  </aside>
</div>'''

def acai():
    weekend = "".join(f'''<article class="wk">{art(sw)}<div><h3>{n}</h3><p class="base">{b}</p><p>{t}</p>{ext(CLV+c,"Check today","link-arrow sm")}</div></article>''' for n, b, t, sw, c in WEEKEND)
    bases = "".join(f'<li><i style="--sw:{SW[k]}"></i><strong>{n}</strong><span>{d}</span></li>' for n, k, d in BASES)
    faqs = [
        ("What comes in every açaí bowl?", "Every bowl comes with your base of choice and granola. Signature bowls come fully topped. Build your own bowls include two fruit toppings and one drizzle."),
        ("Can I swap the base on a signature bowl?", "Yes. Each signature bowl has a suggested base, but you can pick any base you like."),
        ("What is a split base bowl?", "Two bases side by side in one bowl, like açaí with mango or dragon fruit with passion fruit. Split base signature bowls are $12.99 and build your own split bowls are $11.99."),
        ("Are the bowls made to order?", "Yes. Every bowl is built when you order it, with fresh fruit cut for the day."),
    ]
    sl = []
    return f'''{page_head("Açaí bowls · Vineland, NJ", "Açaí bowls, built by hand", "Thick, cold bases topped with fresh fruit, crunch and a drizzle. Every bowl comes with granola. Order at the counter inside Animal Paradise Gyms or ahead for pickup.", "Açaí Bowls")}
<section class="sec"><div class="wrap">
  <div class="sec-head row"><div><p class="eyebrow">$11.99 · Granola included</p><h2>Single base bowls</h2></div></div>
  {grid(SINGLE, True)}
  <p class="fine">Prices shown are in store and pickup prices. Bowls on Uber Eats, DoorDash and Grubhub cost a little more.</p>
</div></section>
<section class="sec sec-tint"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">$12.99 · Two bases, one bowl</p><h2>Split base bowls</h2></div>
  {grid(SPLIT)}
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">From $10.49</p><h2>Build your own bowl</h2><p>Tap through the options and the total updates as you go. Then order it for pickup.</p></div>
  {builder()}
</div></section>
<section class="sec sec-tint"><div class="wrap two">
  <div><p class="eyebrow">Base guide</p><h2>Which base is yours?</h2><ul class="bases">{bases}</ul></div>
  <div><p class="eyebrow">Saturday and Sunday</p><h2>Weekend specials</h2><p class="muted">Rotating weekend bowls. Check the pickup menu to see what is on today.</p><div class="wks">{weekend}</div></div>
</div></section>
<section class="sec"><div class="wrap narrow"><div class="sec-head"><p class="eyebrow">Açaí bowl questions</p><h2>Before you order</h2></div>{faq_block(faqs, sl)}</div></section>
{order_band("Ready for a bowl?")}''', [menu_schema("Açaí bowls", [("Single base bowls", SINGLE), ("Split base bowls", SPLIT)]),
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": sl}]

def smoothies():
    return f'''{page_head("Smoothies · Vineland, NJ", "Fruit smoothies, $9.99", "Real fruit and coconut water, blended the second you order. Pick a house favorite or build your own with any three fruits.", "Smoothies")}
<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">House smoothies</p><h2>Blended with coconut water</h2></div>
  {grid(SMOOTHIES, True)}
</div></section>
<section class="sec sec-tint"><div class="wrap two">
  <div><p class="eyebrow">Build your own · $9.99</p><h2>Any base, any three fruits</h2>
    <h3 class="mini">Bases</h3><ul class="pills"><li>Almond milk</li><li>Coconut water</li></ul>
    <h3 class="mini">Fruits</h3><ul class="pills">{"".join(f"<li>{f}</li>" for f in ["Banana","Strawberry","Blueberry","Raspberry","Kiwi","Mango","Pineapple","Orange"])}</ul></div>
  <div class="callout"><p class="eyebrow">Need more protein?</p><h3>Make it a shake</h3><p>Our protein shakes use isolate whey with real fruit, almond milk or Greek yogurt. Most land between $9.99 and $10.99.</p><a class="btn btn-ink btn-sm" href="{href("protein-shakes")}">See protein shakes</a></div>
</div></section>
{counter_band("Smoothie on the way?", "Smoothies are blended at the counter inside Animal Paradise Gyms. Call ahead and we will have it ready.")}''', [menu_schema("Smoothies", [("Fruit smoothies", SMOOTHIES)])]

def protein():
    return f'''{page_head("Protein shakes · Vineland, NJ", "Protein shakes built for the gym floor", "Isolate whey blended with real fruit, almond milk, natural peanut butter or Greek yogurt. Grab one on the way out of your session.", "Protein Shakes")}
<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">High protein</p><h2>The core three</h2></div>
  {grid(SHAKES_HIGH, True)}
</div></section>
<section class="sec sec-tint"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Specialty</p><h2>Specialty shakes</h2><p>Greek yogurt and tropical fruit for a thicker, creamier shake.</p></div>
  {grid(SHAKES_SPEC)}
</div></section>
<section class="sec"><div class="wrap two">
  <div class="callout"><p class="eyebrow">Same building</p><h3>Restock at Animal Supps</h3><p>Protein, creatine, pre-workout and recovery are stocked at Animal Supps inside the gym.</p>{ext(SUPPS,"Shop Animal Supps","btn btn-ink btn-sm")}</div>
  <div class="callout"><p class="eyebrow">Train at Animal Paradise</p><h3>The gym behind the counter</h3><p>A full-service gym open 4AM to midnight with recovery, a women's-only Lioness Den and an 80 ft turf.</p>{ext(APG,"Visit Animal Paradise Gyms","btn btn-ink btn-sm")}</div>
</div></section>
{counter_band("Shake after your set?", "Shakes are made at the counter inside Animal Paradise Gyms. Call ahead and grab it on your way out.")}''', [menu_schema("Protein shakes", [("High protein shakes", SHAKES_HIGH), ("Specialty shakes", SHAKES_SPEC)])]

def full_menu():
    sections = [("bowls", "Single base bowls", SINGLE, "acai-bowls"), ("bowls", "Split base bowls", SPLIT, "acai-bowls"),
                ("smoothies", "Smoothies", SMOOTHIES, "smoothies"), ("protein", "High protein shakes", SHAKES_HIGH, "protein-shakes"),
                ("protein", "Specialty shakes", SHAKES_SPEC, "protein-shakes")]
    blocks = ""
    for cat, title, its, slug in sections:
        rows = "".join(f'<li><div class="mb-row"><span class="mb-name">{e(i["name"])}</span><span class="mb-dots"></span><span class="mb-price">{money(i["price"])}</span></div><p>{e(", ".join(i["desc"]))}</p></li>' for i in its)
        blocks += f'<section class="mb" data-cat="{cat}"><div class="mb-head"><h2>{title}</h2><a class="link-arrow sm" href="{href(slug)}">Photos and details</a></div><ul>{rows}</ul></section>'
    byo = f'''<section class="mb" data-cat="bowls"><div class="mb-head"><h2>Build your own bowl</h2><a class="link-arrow sm" href="{href("acai-bowls")}">Open the builder</a></div><ul>
<li><div class="mb-row"><span class="mb-name">Single base</span><span class="mb-dots"></span><span class="mb-price">$10.49</span></div><p>Granola, 2 fruit toppings and a drizzle included</p></li>
<li><div class="mb-row"><span class="mb-name">Split base</span><span class="mb-dots"></span><span class="mb-price">$11.99</span></div><p>Granola, 2 fruit toppings and a drizzle included</p></li>
<li><div class="mb-row"><span class="mb-name">Extra fruit</span><span class="mb-dots"></span><span class="mb-price">$1.25</span></div><p>{", ".join(FRUITS)}</p></li>
<li><div class="mb-row"><span class="mb-name">Crunch</span><span class="mb-dots"></span><span class="mb-price">$0.75</span></div><p>{", ".join(CRUNCH)}</p></li>
<li><div class="mb-row"><span class="mb-name">Extra drizzle</span><span class="mb-dots"></span><span class="mb-price">$0.50</span></div><p>{", ".join(DRIZZLE)}</p></li>
<li><div class="mb-row"><span class="mb-name">Additional toppings</span><span class="mb-dots"></span><span class="mb-price">$0.75</span></div><p>{", ".join(EXTRA)}</p></li></ul>
<p class="fine">Bases: açaí, mango, passion fruit, pitaya (dragon fruit), coconut, banana.</p></section>'''
    tabs = "".join(f'<button type="button" class="tab{" on" if k=="all" else ""}" data-filter="{k}" aria-pressed="{"true" if k=="all" else "false"}">{t}</button>' for k, t in [("all","Everything"),("bowls","Bowls"),("smoothies","Smoothies"),("protein","Protein")])
    return f'''{page_head("Animal Cafe menu · Vineland, NJ", "The full menu", "Every bowl, smoothie and protein shake with current prices. Tap a category to narrow it down.", "Full Menu")}
<section class="sec"><div class="wrap">
  <div class="tabs" role="toolbar" aria-label="Filter the menu">{tabs}</div>
  <div class="board">{blocks.replace('<section class="mb" data-cat="smoothies">', byo + '<section class="mb" data-cat="smoothies">', 1)}</div>
  <p class="fine center">Prices match our current in-store menu. Delivery app prices may be higher.</p>
</div></section>
{order_band()}''', [menu_schema("Animal Cafe menu", [("Single base bowls", SINGLE), ("Split base bowls", SPLIT), ("Smoothies", SMOOTHIES),
            ("High protein shakes", SHAKES_HIGH), ("Specialty shakes", SHAKES_SPEC)])]

def order():
    apps = [("Uber Eats", UBER, "Bowls, delivered"), ("DoorDash", DOOR, "Bowls, delivered"), ("Grubhub", GRUB, "Bowls, delivered")]
    appcards = "".join(f'<a class="app" href="{u}" target="_blank" rel="noopener"><strong>{n}</strong><span>{d}</span><em>Open {n}</em></a>' for n, u, d in apps)
    return f'''{page_head("Order online", "Order Animal Cafe", "Pick it up at the counter or have it delivered. Here is every way to order, in one place.", "Order")}
<section class="sec"><div class="wrap two">
  <div class="callout big"><p class="eyebrow">Fastest</p><h2>Order ahead for pickup</h2><p>Bowls and weekend specials are on our online pickup menu. Pay ahead, then grab your order at the counter inside Animal Paradise Gyms.</p>
    {ext(CLOVER,"Open the pickup menu","btn btn-mango btn-lg")}
    <p class="fine">Earn rewards when you order through the Clover app: {ext(CLOVER_IOS,"App Store")} · {ext(CLOVER_AND,"Google Play")}</p></div>
  <div><p class="eyebrow">Delivery</p><h2>Get it delivered</h2><p class="muted">All signature bowls and build your own bowls are on all three apps. Smoothies and protein shakes are made at the counter.</p><div class="apps">{appcards}</div>
    <p class="fine">Prefer to call it in? <a href="{TEL}">{PHONE}</a></p></div>
</div></section>
<section class="sec sec-tint"><div class="wrap split">
  <div class="split-copy"><p class="eyebrow">Picking up?</p><h2>How pickup works</h2><p>Animal Cafe is inside Animal Paradise Gyms at Cumberland Mall. You do not need a membership to pick up.</p>
    <a class="link-arrow" href="{href("contact")}">Map and directions</a></div>
  <ol class="pickup">
    <li><strong>Order on the pickup menu</strong><span>Pick your bowl, pay ahead, and note the pickup time.</span></li>
    <li><strong>Walk into Animal Paradise Gyms</strong><span>{ADDR1}, Cumberland Mall. Free parking out front.</span></li>
    <li><strong>Grab it at the cafe counter</strong><span>Give your name at the counter. Open every day 4AM to 12AM.</span></li>
  </ol>
</div></section>''', []

def about():
    return f'''{page_head("About Animal Cafe", "Fueling Vineland, one bowl at a time", "A locally owned cafe inside Animal Paradise Gyms, making fresh food for people who train and people who just want something good.", "About")}
<section class="sec"><div class="wrap split">
  <div class="split-media tall">{art(["acai","mango"], "counter", "The Animal Cafe counter inside Animal Paradise Gyms")}</div>
  <div class="split-copy"><p class="eyebrow">Our story</p><h2>More than a quick bite</h2>
    <p>Animal Cafe started with a simple idea: the people training at Animal Paradise Gyms deserved food as serious as their workouts. So we put a cafe inside the gym and stocked it with real fruit, quality protein and nothing that sits around waiting.</p>
    <p>Today we are the go-to spot in Vineland for gym-goers, early commuters, students and anyone who wants a fresh açaí bowl or smoothie without the drive. We open at 4AM for the first sessions of the day and stay open until midnight for the last.</p>
    <a class="btn btn-ink" href="{href("menu")}">See the menu</a></div>
</div></section>
<section class="sec sec-tint"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">What we stand for</p><h2>Three things we do not compromise on</h2></div>
  <div class="values">
    <div><h3>Fresh, wholesome ingredients</h3><p>Real fruit, real nut butter and simple bases. Everything is blended or built after you order.</p></div>
    <div><h3>Fitness focused</h3><p>Isolate whey shakes, high protein options and portions that actually fuel a training day.</p></div>
    <div><h3>Part of your routine</h3><p>Open 20 hours a day so the cafe fits around your schedule, not the other way around.</p></div>
  </div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Under one roof</p><h2>The Animal family</h2></div>
  <div class="family">
    <a class="fam" href="{APG}" target="_blank" rel="noopener">{art(["acai","gold"], "posing", "Inside Animal Paradise Gyms")}<div><h3>Animal Paradise Gyms</h3><p>The full-service gym the cafe lives in. Open 4AM to midnight.</p><span class="more">Visit the gym</span></div></a>
    <a class="fam" href="{SUPPS}" target="_blank" rel="noopener">{art(["pitaya","mango"], "cafe_floor", "Animal Cafe counter and lounge")}<div><h3>Animal Supps</h3><p>Supplements, health food and meal prep, stocked inside the gym.</p><span class="more">Shop supps</span></div></a>
  </div>
</div></section>
{order_band()}''', []

def contact():
    return f'''{page_head("Visit and contact", "Come see us", "Animal Cafe is inside Animal Paradise Gyms at Cumberland Mall in Vineland. Walk in, call ahead or send us a message.", "Contact")}
<section class="sec"><div class="wrap">
  <div class="contact-grid four">
    <div class="cbox"><p class="eyebrow">Call</p><a class="cbig" href="{TEL}">{PHONE}</a><p>Questions, large orders or calling an order in.</p></div>
    <div class="cbox"><p class="eyebrow">Email</p><a class="cbig sm" href="mailto:{EMAIL}">{EMAIL}</a><p>Shared with the Animal Paradise front desk.</p></div>
    <div class="cbox"><p class="eyebrow">Instagram</p>{ext(IG,"@animalcafenj","cbig sm")}<p>New bowls, weekend specials and DMs.</p></div>
    <div class="cbox"><p class="eyebrow">Hours</p><p class="cbig sm">4AM to 12AM</p><p>Every day, including weekends. Same hours as the gym.</p></div>
  </div>
</div></section>
<section class="sec sec-tint"><div class="wrap">{map_block()}</div></section>
<section class="sec"><div class="wrap narrow"><div class="sec-head"><p class="eyebrow">Getting here</p><h2>Finding the counter</h2></div>
  <ol class="steps"><li><strong>Park at Cumberland Mall.</strong> Parking is free.</li><li><strong>Head into Animal Paradise Gyms</strong> at 3849 S Delsea Dr, Suite E000.</li><li><strong>Order at the cafe counter.</strong> No gym membership needed.</li></ol>
  <div class="center">{ext(MAPS,"Open in Google Maps","btn btn-mango")}</div></div></section>''', []

def faq():
    qs = [
        ("Where is Animal Cafe?", f"We are at {ADDR1}, {ADDR2}, inside Animal Paradise Gyms at Cumberland Mall."),
        ("What are Animal Cafe's hours?", "Every day from 4AM to 12AM (midnight), including weekends and holidays the gym is open."),
        ("Do I need a gym membership to order?", "No. Anyone can walk in and order at the cafe counter."),
        ("Can I order ahead for pickup?", f'Yes. Bowls and weekend specials are on our {ext(CLOVER,"online pickup menu")}. Pay ahead and grab it at the counter.'),
        ("Do you deliver?", f'Yes, through {ext(UBER,"Uber Eats")}, {ext(DOOR,"DoorDash")} and {ext(GRUB,"Grubhub")}. Delivery prices are set by the apps and may be higher than in store.'),
        ("How much is an açaí bowl?", "Signature single base bowls are $11.99, split base bowls are $12.99, and build your own bowls start at $10.49."),
        ("How much are smoothies and protein shakes?", "Smoothies are $9.99. Protein shakes run from $9.99 to $10.99."),
        ("What protein do you use in the shakes?", "Isolate whey protein in vanilla or chocolate, depending on the shake."),
        ("Can I customize my order?", "Always. Swap the base on any bowl, build your own bowl from six bases, or pick any base and three fruits for a $9.99 smoothie."),
        ("Do Animal Paradise members get a discount?", f'Yes. Gold members save 5% and Premium members save 10% at the cafe. {ext(APG_MEM,"Compare gym memberships")}.'),
        ("Is there parking?", "Yes, free parking at Cumberland Mall right outside the gym."),
    ]
    sl = []
    body = f'''{page_head("Animal Cafe FAQ", "Frequently asked questions", "Hours, ordering, prices and everything else people ask at the counter.", "FAQ")}
<section class="sec"><div class="wrap narrow">{faq_block(qs, sl)}</div></section>
{order_band()}'''
    return body, [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": sl}]

def notfound():
    return f'''<section class="sec nf"><div class="wrap narrow center"><p class="eyebrow">404</p><h1>This page got blended.</h1><p class="lead">The page you are looking for moved or never existed. The menu is right where we left it.</p>
<div class="hero-btns center">{ext(CLOVER,"Order for pickup","btn btn-mango")}<a class="btn btn-ink" href="{href("menu")}">See the menu</a></div></div></section>''', []

META = {
    "home": ("Animal Cafe | Açaí Bowls, Smoothies & Protein Shakes in Vineland, NJ",
             "Açaí bowls, smoothies and protein shakes inside Animal Paradise Gyms in Vineland, NJ. Open daily 4AM to midnight. Order pickup or delivery.", home),
    "acai-bowls": ("Açaí Bowls in Vineland, NJ | Animal Cafe",
                   "Signature and split base açaí bowls from $11.99, or build your own from $10.49. Granola in every bowl. Inside Animal Paradise Gyms, Vineland NJ.", acai),
    "smoothies": ("Fruit Smoothies in Vineland, NJ | $9.99 | Animal Cafe",
                  "Real fruit smoothies blended with coconut water for $9.99. Jungle Berry, Island Heat, Paradise Citrus, Tiki Chill or build your own. Vineland, NJ.", smoothies),
    "protein-shakes": ("Protein Shakes in Vineland, NJ | Animal Cafe",
                       "Isolate whey protein shakes with real fruit and natural peanut butter, from $9.99. Gorilla Gainz, Muscle Monkey Madness and more. Inside Animal Paradise Gyms.", protein),
    "menu": ("Menu & Prices | Animal Cafe Vineland, NJ",
             "The full Animal Cafe menu with prices: açaí bowls, smoothies and protein shakes. Vineland, NJ.", full_menu),
    "order": ("Order Online for Pickup or Delivery | Animal Cafe",
              "Order Animal Cafe for pickup inside Animal Paradise Gyms, or get delivery on Uber Eats, DoorDash and Grubhub. Vineland, NJ.", order),
    "about-us": ("About Animal Cafe | Vineland, NJ",
                 "A locally owned cafe inside Animal Paradise Gyms serving fresh açaí bowls, smoothies and protein shakes to Vineland since day one.", about),
    "contact": ("Contact & Directions | Animal Cafe Vineland, NJ",
                "Animal Cafe, 3849 S Delsea Dr Suite E000, Vineland NJ 08360, inside Animal Paradise Gyms. Call 856-839-4536. Open daily 4AM to 12AM.", contact),
    "faq": ("FAQ | Animal Cafe Vineland, NJ",
            "Hours, ordering, delivery, prices and member discounts at Animal Cafe inside Animal Paradise Gyms in Vineland, NJ.", faq),
    "404": ("Page not found | Animal Cafe", "This page could not be found.", notfound),
}

# ---------------------------------------------------------------- shell
CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.css")).read()
JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.js")).read()
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;800;900&family=Michroma&family=Figtree:wght@400;500;600;700&display=swap">'

def header(slug):
    cur = ' aria-current="page"'
    links = "".join(f'<li><a href="{href(s)}"{cur if s==slug else ""}>{t}</a></li>' for s, t in NAV)
    return f'''<div class="topbar"><div class="wrap topbar-in"><span class="open-now" data-open>Open every day 4AM to 12AM</span><span class="tb-addr">Inside Animal Paradise Gyms · 3849 S Delsea Dr, Vineland NJ</span><a href="{TEL}">{PHONE}</a></div></div>
<header class="site-head"><div class="wrap head-in">
  <a class="brand" href="{href("home")}"><img src="{IMG["logo_full"]}" alt="Animal Cafe" width="61" height="72"></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" id="menuBtn">Menu</button>
  <nav id="nav" aria-label="Main"><ul>{links}</ul>{ext(CLOVER,"Order now","btn btn-mango btn-sm nav-cta")}</nav>
</div></header>'''

def order_modal():
    picks = [("Build your own bowl", "10.49", "#1 most liked", "Granola, 2 fruits and a drizzle", "bowl_bliss", "build-your-own-bowl-EFH18GTNEDRMT"),
             ("Build your split base bowl", "11.99", "#2 most liked", "Two bases, granola, 2 fruits, a drizzle", "bowl_dragon", "build-your-split-base-bowl-CQRF8J3VPT8GC"),
             ("The Animal Paradise Bowl", "11.99", "#3 most liked", "Açaí, banana, strawberry, Nutella", "bowl_signature", "the-animal-paradise-bowl-SD1KJYQEDMTVE")]
    rows = "".join(f'''<a class="om-item" href="{CLV}{c}" target="_blank" rel="noopener"><img src="{IMG[i]}" alt="" width="64" height="64" loading="lazy">
      <span class="om-txt"><em>{r}</em><strong>{n}</strong><span>{d}</span></span><span class="om-price">${p}</span></a>''' for n, p, r, d, i, c in picks)
    return f'''<div class="om" id="orderModal" role="dialog" aria-modal="true" aria-labelledby="omTitle" hidden>
  <div class="om-backdrop" data-close></div>
  <div class="om-panel" tabindex="-1">
    <button class="om-x" type="button" data-close aria-label="Close">&times;</button>
    <div class="om-head"><img src="{IMG["logo_full"]}" alt="" width="52" height="61">
      <div><p class="eyebrow">Order for pickup</p><h2 id="omTitle">What are you craving?</h2><p class="open-now" data-open>Open every day, 4AM to 12AM</p></div></div>
    <div class="om-list">{rows}</div>
    <a class="btn btn-mango om-go" href="{CLOVER}" target="_blank" rel="noopener">See the full menu and order</a>
    <p class="om-note">Opens our secure Clover checkout in a new tab. Pick up at the counter inside Animal Paradise Gyms, {ADDR1}.</p>
    <div class="om-alt"><span>Prefer delivery?</span>{ext(UBER,"Uber Eats")}{ext(DOOR,"DoorDash")}{ext(GRUB,"Grubhub")}</div>
    <p class="om-alt"><span>Smoothie or shake?</span><a href="{TEL}">Call {PHONE}</a></p>
  </div>
</div>'''

def footer():
    cols = "".join(f'<li><a href="{href(s)}">{t}</a></li>' for s, t in PAGES if s != "home")
    return f'''<footer class="site-foot"><div class="wrap foot-in">
  <div class="foot-brand"><a class="brand" href="{href("home")}"><img class="foot-logo" src="{IMG["logo_full"]}" alt="Animal Cafe" width="110" height="129" loading="lazy"></a>
    <p>Açaí bowls, smoothies and protein shakes, made with real, simple ingredients inside Animal Paradise Gyms.</p>
    <div class="socials">{ext(IG,"Instagram")}{ext(FB,"Facebook")}</div></div>
  <div><h2>Menu</h2><ul>{cols}</ul></div>
  <div><h2>Order</h2><ul><li>{ext(CLOVER,"Pickup menu")}</li><li>{ext(UBER,"Uber Eats")}</li><li>{ext(DOOR,"DoorDash")}</li><li>{ext(GRUB,"Grubhub")}</li><li>{ext(APG,"Animal Paradise Gyms")}</li><li>{ext(SUPPS,"Animal Supps")}</li></ul></div>
  <div><h2>Visit</h2><ul class="plain"><li>{ADDR1}</li><li>Cumberland Mall, {ADDR2}</li><li>Every day 4AM to 12AM</li><li><a href="{TEL}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>{ext(MAPS,"Get directions")}</li></ul></div>
</div><div class="wrap foot-base"><span>© 2026 Animal Cafe · Vineland, NJ</span><span>Website and marketing by Leads Magnets</span></div></footer>
<a class="mobile-order" href="#order" data-order aria-haspopup="dialog">Order for pickup</a>
{order_modal()}'''

def render(slug):
    title, desc, fn = META[slug]
    res = fn()
    body, schemas = (res if isinstance(res, tuple) else (res, []))
    schemas = [BUSINESS] + schemas if slug in ("home", "contact", "about-us") else schemas
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    can = canon(slug) if slug != "404" else SITE + "/404"
    seo = f'''<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="canonical" href="{can}"><meta property="og:type" content="website"><meta property="og:site_name" content="Animal Cafe">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{can}">
<meta property="og:image" content="{ABS("og")}"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0c0b09">
<link rel="icon" href="{IMG["logo_png"]}">'''
    if slug == "404":
        seo += '<meta name="robots" content="noindex">'
    if MODE == "prod":
        assets = '<link rel="stylesheet" href="/assets/site.css">'
        script = '<script src="/assets/site.js" defer></script>'
        pixel = f'''<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{META_PIXEL}');fbq('track','PageView');</script>'''
    else:
        assets = f"<style>{CSS}</style>"
        script = f"<script>{JS}</script>"
        pixel = ""
    inner = f'''{header(slug)}<main id="main">{body}</main>{footer()}{script}'''
    skip = '<a class="skip" href="#main">Skip to content</a>'
    if MODE == "preview" and slug == "home":
        return f"{seo}{FONTS}{assets}{ld}{skip}{inner}"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{seo}{FONTS}{assets}{ld}{pixel}</head><body>{skip}{inner}</body></html>'''

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for slug in list(META):
        htmlout = render(slug)
        if MODE == "prod":
            if slug == "home": path = os.path.join(OUT, "index.html")
            elif slug == "404": path = os.path.join(OUT, "404.html")
            else:
                os.makedirs(os.path.join(OUT, slug)); path = os.path.join(OUT, slug, "index.html")
        else:
            path = os.path.join(OUT, ("index" if slug == "home" else slug) + ".html")
        open(path, "w").write(htmlout)
    shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "img"), os.path.join(OUT, "img"))
    if MODE == "prod":
        os.makedirs(os.path.join(OUT, "assets"))
        open(os.path.join(OUT, "assets/site.css"), "w").write(CSS)
        open(os.path.join(OUT, "assets/site.js"), "w").write(JS)
        urls = "".join(f"<url><loc>{canon(s)}</loc><changefreq>monthly</changefreq><priority>{'1.0' if s=='home' else '0.8'}</priority></url>" for s, _ in PAGES)
        open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
        open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
        open(os.path.join(OUT, "_redirects"), "w").write(
            "/our-menu /smoothies/ 301\n/our-menu/ /smoothies/ 301\n/order-pickup /order/ 301\n/order-pickup/ /order/ 301\n"
            "/cart /order/ 301\n/cart/ /order/ 301\n/checkout /order/ 301\n/checkout/ /order/ 301\n/shop /menu/ 301\n/shop/ /menu/ 301\n")
        lines = [f"# Animal Cafe", "", "> Açaí bowls, smoothies and protein shakes inside Animal Paradise Gyms, "
                 f"{ADDR1}, {ADDR2}. Open every day 4AM to 12AM. Phone {PHONE}.", "",
                 "## Pages"] + [f"- [{t}]({canon(s)})" for s, t in PAGES] + ["", "## Ordering",
                 f"- Pickup (bowls): {CLOVER}", f"- Uber Eats: {UBER}", f"- DoorDash: {DOOR}", f"- Grubhub: {GRUB}",
                 "", "## Menu"] + [f"- {i['name']}: ${i['price']} ({', '.join(i['desc'])})" for i in ALL] + ["",
                 "- Build your own bowl: $10.49 single base, $11.99 split base", "", "## Related",
                 f"- Animal Paradise Gyms: {APG}", f"- Animal Supps: {SUPPS}"]
        open(os.path.join(OUT, "llms.txt"), "w").write("\n".join(lines) + "\n")
    print("built", OUT, len(os.listdir(OUT)))

main()
