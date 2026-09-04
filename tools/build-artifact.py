"""Turns index.html into the file that gets published as the live link.

index.html is the real, deployable website and stays the single source of
truth. The Claude Artifact viewer is a stricter place than a normal web host:
it supplies its own <!doctype>/<html>/<head>/<body>, it blocks iframes, and it
blocks images loaded from any outside host. So this script rewrites four things
and nothing else:

  1. keeps only the part from <title> to </body>, then re-adds the favicon link
     (it sits above <title> in the real file) and restores lang="he" dir="rtl"
  2. swaps the Google Maps iframe for a Leaflet map whose OpenStreetMap tiles,
     four zoom levels of them, are baked into the file and served from memory
  3. inlines every photograph in SITE.images as a data URI
  4. drops srcset, which a data URI makes pointless

Downloads, re-encoded photos and map tiles are cached in build/.cache, keyed by
the URL or by the content of the file on disk, so replacing a photograph or
moving the pin invalidates only what it touches and a rebuild needs no network.

Usage:  py tools/build-artifact.py
Output: build/artifact.html
"""

import base64
import hashlib
import io
import json
import math
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
OUT = ROOT / "build" / "artifact.html"
CACHE = ROOT / "build" / ".cache"

# photographs kept on disk are re-encoded, so a 3 MB camera file does not land
# in the page at full size. Anything already fetched at a chosen width is used
# exactly as downloaded.
LOCAL_MAX_WIDTH = 1200
LOCAL_QUALITY = 80

DIR_SHIM = """<script>/* the artifact host supplies its own <html>; restore the direction */
document.documentElement.setAttribute("lang","he");
document.documentElement.setAttribute("dir","rtl");</script>"""

# the map. Tiles come from OpenStreetMap once, at build time, and live in the
# page from then on. Four zoom levels, and the pan box is what maxBounds allows,
# so the map can never be dragged to a corner that was never fetched.
LEAFLET = "1.9.4"
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE_AGENT = "la-farina-site-build/1.0 (static site for one food truck)"
MAP_ZOOMS = (15, 16, 17, 18)
MAP_START = 17
MAP_VIEW = (620, 400)   # the box is never drawn much larger than this
# how far past the truck the map may be dragged. It has to beat the width of
# the box at the zoom the map opens at, or maxBounds pins the centre and the
# map refuses to drag at all.
MAP_PAN_M = 420

MAP_CSS = """/* the link that stands in if Leaflet does not load */
.mapout{
  position:absolute; inset:0; display:flex; flex-direction:column;
  align-items:center; justify-content:center; gap:.55rem;
  background:var(--paper-2); text-decoration:none; text-align:center; padding:1rem;
}
.mapout__pin{font-size:1.75rem; line-height:1; color:var(--ember-deep)}
.mapout__cta{
  font-family:var(--sans); font-size:var(--t-fine); letter-spacing:.04em;
  color:var(--ember-deep); border-bottom:1px solid currentColor; padding-bottom:2px;
}
.mapout:hover .mapout__cta{color:var(--ink)}
.mapout:focus-visible{outline:2px solid var(--ember-deep); outline-offset:-3px}
#map{position:absolute; inset:0; direction:ltr}
.leaflet-container{font-family:var(--sans); background:var(--paper-2)}
/* the same warm grade the photographs carry, so the map belongs to the page */
.leaflet-tile-pane{filter:grayscale(.3) contrast(1.03) sepia(.12)}
.leaflet-bar{border:none; box-shadow:none}
.leaflet-bar a{
  width:30px; height:30px; line-height:30px; border-radius:0;
  background:var(--paper); color:var(--ink-2); border:1px solid var(--rule);
  font-family:var(--sans); font-size:1.1rem; font-weight:600;
}
.leaflet-bar a:first-child{border-bottom:none}
.leaflet-bar a:hover{background:var(--ink); color:var(--cream); border-color:var(--ink)}
.leaflet-bar a.leaflet-disabled,
.leaflet-bar a.leaflet-disabled:hover{
  background:var(--paper-2); color:var(--ink-3); border-color:var(--rule);
}
.leaflet-control-attribution{
  background:rgba(224,216,200,.88); color:var(--ink-3);
  font-family:var(--sans); font-size:10px; padding:1px 6px;
}
.leaflet-control-attribution a{color:var(--ink-2)}
/* the pin is the one loud thing on a deliberately quiet map */
.pin svg .pin__body{fill:var(--ember); stroke:var(--ink); stroke-width:2; stroke-linejoin:round}
.pin svg .pin__eye{fill:var(--paper)}
.pinlabel{
  background:var(--ink); color:var(--cream); border:none; border-radius:0;
  box-shadow:none; padding:.22rem .5rem;
  font-family:var(--sans); font-weight:700; font-size:9px;
  letter-spacing:.18em; text-transform:uppercase; white-space:nowrap;
}
.pinlabel::before{display:none}"""

MAP_JS = """/* The map. An artifact may not open an iframe or reach a tile server, so every
   tile around the truck was fetched at build time and lives in this file. Zoom
   and the pin work exactly as they should, the map simply stops at the edge of
   the neighbourhood instead of pretending the rest of the world is loadable. */
(function () {
  var el = document.getElementById("map");
  var link = document.getElementById("map-link");
  if (!el || !window.L) return;            /* the link underneath stays, and works */

  var TILES = __TILES__;
  var HERE = __HERE__, BOUNDS = __BOUNDS__;
  var BLANK = "data:image/gif;base64,R0lGODlhAQABAIAAAOXi2gAAACH5BAEAAAEALAAAAAABAAEAAAICTAEAOw==";
  var quiet = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var Baked = L.TileLayer.extend({
    getTileUrl: function (c) { return TILES[c.z + "/" + c.x + "/" + c.y] || BLANK; }
  });

  var map = L.map(el, {
    center: HERE, zoom: __START__, minZoom: __MINZ__, maxZoom: __MAXZ__,
    maxBounds: BOUNDS, maxBoundsViscosity: 1,
    zoomControl: false, scrollWheelZoom: false,
    zoomAnimation: !quiet, fadeAnimation: !quiet, markerZoomAnimation: !quiet
  });

  new Baked("", {
    minZoom: __MINZ__, maxZoom: __MAXZ__, noWrap: true,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  map.attributionControl.setPrefix("");
  L.control.zoom({
    position: "topright", zoomInTitle: "התקרבות", zoomOutTitle: "התרחקות"
  }).addTo(map);

  L.marker(HERE, {
    title: "La Farina Food Truck",
    icon: L.divIcon({
      className: "pin", iconSize: [30, 38], iconAnchor: [15, 37], tooltipAnchor: [0, -34],
      html: '<svg width="30" height="38" viewBox="0 0 30 38" aria-hidden="true">'
          + '<path class="pin__body" d="M15 36.5C15 36.5 27 22.6 27 14.5A12 12 0 1 0 3 14.5C3 22.6 15 36.5 15 36.5Z"/>'
          + '<circle class="pin__eye" cx="15" cy="14.4" r="4.3"/></svg>'
    })
  }).addTo(map).bindTooltip("La Farina", {
    permanent: true, direction: "top", className: "pinlabel", offset: [0, 0]
  });

  /* the wheel belongs to the page until someone actually reaches for the map */
  map.on("click", function () { map.scrollWheelZoom.enable(); });
  map.on("mouseout", function () { map.scrollWheelZoom.disable(); });

  if (link) link.remove();
})();"""

MAP_MARKUP = """      <div class="map">
        <a id="map-link" class="mapout" href="#" target="_blank" rel="noopener"><span class="mapout__pin" aria-hidden="true">◎</span><span class="mapout__cta">פתיחת המפה בגוגל</span></a>
        <div id="map" role="application" aria-label="מפה: מיקום הפוד טראק במרכז לידר, גני תקווה"></div>
      </div>"""


def cached(key, produce):
    """Return a data URI for `key`, running `produce` only on a cache miss."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(key.encode("utf-8")).hexdigest() + ".txt")
    if path.exists():
        return path.read_text(encoding="ascii")
    uri = produce()
    path.write_text(uri, encoding="ascii")
    return uri


def as_data_uri(raw, mime):
    return "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")


def fetch_remote(url):
    req = urllib.request.Request(url, headers={"User-Agent": "la-farina-build"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        mime = r.headers.get_content_type()
    return as_data_uri(raw, mime)


def encode_local(raw):
    from PIL import Image

    im = Image.open(io.BytesIO(raw))
    im = im.convert("RGB")
    if im.width > LOCAL_MAX_WIDTH:
        h = round(im.height * LOCAL_MAX_WIDTH / im.width)
        im = im.resize((LOCAL_MAX_WIDTH, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=LOCAL_QUALITY, optimize=True, progressive=True)
    return as_data_uri(buf.getvalue(), "image/jpeg")


def inline(src):
    if src.startswith("http://") or src.startswith("https://"):
        return cached(src, lambda: fetch_remote(src))
    path = (SRC.parent / src).resolve()
    if not path.exists():
        raise SystemExit("photo not found: " + src)
    raw = path.read_bytes()
    return cached("sha1:" + hashlib.sha1(raw).hexdigest(), lambda: encode_local(raw))


def leaflet_css():
    """Leaflet's stylesheet, fetched once. Only scripts may come from a CDN."""
    url = ("https://cdnjs.cloudflare.com/ajax/libs/leaflet/"
           + LEAFLET + "/leaflet.css")

    def get():
        req = urllib.request.Request(url, headers={"User-Agent": TILE_AGENT})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8")

    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".css")
    if not path.exists():
        # newline="" throughout: the stylesheet ships with CRLF, and letting
        # Windows translate it again doubles every line break in the page
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(get())
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n").strip()


def mercator_px(lat, lon, z):
    """Where a coordinate lands on the world image at zoom z, in pixels."""
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return ((lon + 180.0) / 360.0 * n,
            (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n)


def fetch_tile(key):
    from PIL import Image

    z, x, y = key.split("/")
    req = urllib.request.Request(
        TILE_URL.format(z=z, x=x, y=y), headers={"User-Agent": TILE_AGENT}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    time.sleep(0.12)  # a courtesy to a tile server that costs us nothing
    buf = io.BytesIO()
    # lossless, because a soft street name on a map is worse than a bigger file
    Image.open(io.BytesIO(raw)).convert("RGB").save(
        buf, "WEBP", lossless=True, method=6
    )
    return as_data_uri(buf.getvalue(), "image/webp")


def map_tiles(lat, lon):
    """Every tile the map can reach, keyed "z/x/y"."""
    tiles = {}
    for z in MAP_ZOOMS:
        per_px = 156543.033924 * math.cos(math.radians(lat)) / 2 ** z
        pan = MAP_PAN_M / per_px
        cx, cy = mercator_px(lat, lon, z)
        edge = 2 ** z
        xs = range(int((cx - MAP_VIEW[0] / 2 - pan) // 256),
                   int((cx + MAP_VIEW[0] / 2 + pan) // 256) + 1)
        ys = range(int((cy - MAP_VIEW[1] / 2 - pan) // 256),
                   int((cy + MAP_VIEW[1] / 2 + pan) // 256) + 1)
        for tx in xs:
            for ty in ys:
                if not (0 <= tx < edge and 0 <= ty < edge):
                    continue
                key = "%d/%d/%d" % (z, tx, ty)
                tiles[key] = cached("tile:" + key, lambda k=key: fetch_tile(k))
        sys.stdout.write("  zoom %d: %d tiles\n" % (z, len(xs) * len(ys)))
    return tiles


def map_script(lat, lon):
    """Leaflet, the baked tiles and the pin, as two script tags."""
    tiles = map_tiles(lat, lon)
    weight = sum(len(v) for v in tiles.values())
    print("  %d map tiles, %.1f MB inlined" % (len(tiles), weight / 1e6))

    dlat = MAP_PAN_M / 111320.0
    dlon = MAP_PAN_M / (111320.0 * math.cos(math.radians(lat)))
    bounds = [[lat - dlat, lon - dlon], [lat + dlat, lon + dlon]]

    return (
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/'
        + LEAFLET
        + '/leaflet.js"></script>\n<script>\n'
        + MAP_JS.replace("__TILES__", json.dumps(tiles, separators=(",", ":")))
        .replace("__HERE__", json.dumps([lat, lon]))
        .replace("__BOUNDS__", json.dumps(bounds))
        .replace("__MINZ__", str(min(MAP_ZOOMS)))
        .replace("__MAXZ__", str(max(MAP_ZOOMS)))
        .replace("__START__", str(MAP_START))
        + "\n</script>\n"
    )


def cut(text, opening, closing):
    a = text.index(opening)
    b = text.index(closing, a)
    return a, b


def build():
    src = SRC.read_text(encoding="utf-8")

    icon = re.search(r'<link rel="icon" href="[^"]+">', src)
    if not icon:
        raise SystemExit('index.html has no <link rel="icon">')

    head = src[src.index("<title>"): src.index("</head>")].rstrip()
    body = src[src.index("<body>") + len("<body>"): src.rindex("</body>")]

    # the favicon lives above <title>, which the artifact head does not keep
    head = head.replace(
        "</title>", "</title>\n" + icon.group(0) + "\n" + DIR_SHIM, 1
    )

    # an iframe never renders inside an artifact, so the Google map becomes a
    # Leaflet map with the tiles around the truck baked in
    coords = re.search(
        r'coords:\s*\{\s*lat:\s*(-?[\d.]+),\s*lon:\s*(-?[\d.]+)\s*\}', src
    )
    if not coords:
        raise SystemExit("SITE.coords is missing from index.html")
    lat, lon = float(coords.group(1)), float(coords.group(2))

    anchor = ".map iframe{"
    line_end = head.index("\n", head.index(anchor))
    head = (head[:line_end + 1]
            + "/* Leaflet " + LEAFLET + ", inlined: the artifact blocks outside "
            + "stylesheets */\n" + leaflet_css() + "\n"
            + MAP_CSS + "\n"
            + head[line_end + 1:])

    old_map = re.search(r'^ *<div class="map"><iframe .*?</iframe></div>$', body, re.M)
    if not old_map:
        raise SystemExit("the map markup in index.html changed shape")
    body = body[:old_map.start()] + MAP_MARKUP + body[old_map.end():]

    old_js = re.search(
        r'  \$\("#map"\)\.src = "https://www\.google\.com/maps\?q="'
        r'.*?output=embed";\n',
        body,
        re.S,
    )
    if not old_js:
        raise SystemExit("the map wiring in index.html changed shape")
    body = (body[:old_js.start()] + '  $("#map-link").href = gmaps;\n'
            + body[old_js.end():])
    body = body.rstrip() + "\n\n" + map_script(lat, lon)

    # every photograph, inlined
    ia, ib = cut(body, "  images: {", "\n  }\n};")
    block = body[ia:ib]
    block = re.sub(r'\n\s*srcset:"[^"]*",?', "", block)
    count = 0

    def swap(m):
        nonlocal count
        count += 1
        sys.stdout.write("  inlining %d: %s\n" % (count, m.group(1)[:70]))
        return 'src:"' + inline(m.group(1)) + '"'

    block = re.sub(r'src:"([^"]+)"', swap, block)
    body = body[:ia] + block + body[ib:]

    out = head + "\n" + body
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out, encoding="utf-8")
    print("built %s  (%d photos, %.1f MB)" % (OUT, count, len(out.encode()) / 1e6))


if __name__ == "__main__":
    build()
