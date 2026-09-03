# La Farina Food Truck, website

Everything for the website lives in this folder.

## Folder layout

```
La-farina/
  site/
    index.html        The entire website. One self contained file.
  assets/
    logo/             Brand logo files
    manu/             Photo of the printed menu
    brand/            Cups, stickers, business cards, signage
    photos/           Photography, sorted by subject
      01-hero/        Wide shots of the truck for the main image
      02-cart/        The truck from several angles
      03-drinks/      Coffee and cold drinks
      04-food/        Croissants, sandwiches, pastries
      05-atmosphere/  People, the location, morning light
      06-team/        Staff photos
  tools/
    build-preview.ps1 Helper that produces the phone preview link
  README.md           This file
```

## The website itself

`site/index.html` is the whole thing. No database, no build step, no dependencies.
Open it by double clicking and it runs in your browser. The logo is embedded
directly inside the file, so it works even with no internet connection except
for the fonts.

## Changing prices, hours, photos or the phone number

Open `site/index.html` in any text editor and search for this line:

```
const SITE = {
```

Everything a business owner needs to change sits in the block underneath it:
phone number, WhatsApp message, social links, address, kosher authority,
opening hours, the full menu with every price, the "good to know" facts, and
every photograph. Nothing else in the file needs to be touched. Save, refresh
the browser, done.

Three fields behave as switches. Leave them empty and the thing simply does not
appear, so the site never shows a dead link or a bracketed placeholder:

* `social.instagram`, `social.tiktok` and `social.facebook`, an empty string
  hides that icon. Instagram drives two icons, one in the header and one in the
  footer. TikTok and Facebook are footer only.
* `kosher`, `null` hides the kosher line entirely

In the menu, a category can carry `feature: true`, which sets it in larger type
on the board. That is reserved for `קפה` and `מאפים`, the two things the truck
is actually for.

## Replacing the photographs

Every image on the page is one line in `SITE.images`. To swap one in:

1. Replace `src` with a local path, for example `../assets/photos/01-hero/truck.jpg`
2. Delete the `srcset` line if that image has one
3. Update `alt` to describe the new photo in Hebrew
4. Optionally add `pos: "70% 40%"` to choose which part of the photo stays in frame

Nothing else moves. Every image sits in a frame with a fixed aspect ratio, so a
replacement of any shape drops straight in without changing the layout.

## Style rule

No em dashes and no en dashes anywhere in the site copy. Use commas, colons,
periods or parentheses instead. Time ranges use a plain hyphen, for example
`07:30-21:00`.

## Still to add

* Facebook link, currently empty so that icon stays hidden. Instagram
  (`lafarina_foodtruck_leader`) and TikTok (`@lafarinafoodtruckleader`) are live.
* Kosher certification authority, currently `null` so no kosher line shows
* Saturday hours, confirm whether closed
* Confirm the four "good to know" facts: parking, seating, payment, pre-ordering
* Accessibility, deliberately not claimed on the page until someone confirms it
* A vector version of the logo, SVG or AI or PDF
* The real domain, to replace `example.com` in the `og:image` and `og:url` tags

## Photographs that must be replaced

Nine photographs, all inside `SITE.images`. Three are real: the truck in the
events band, the shakshuka in the middle of the strip, and the bowl in the
closing band. The other six are temporary stand-ins from a free stock library,
chosen to hold the right shape and mood.

`assets/photos/02-cart/truck-front.jpg` is a second truck shot, cropped to 3:2
and unused. It is the same truck with nobody in it.

| Slot | Shape | What to shoot |
|---|---|---|
| `hero` | wide, dark | The truck at dusk with the lights on, or a hero pastry shot. Needs a dark, quiet area on one side for the wordmark to sit over. |
| `strip` (3) | 3:2, 4:3 on narrow | Croissants, shakshuka, a sandwich. These three sit butted together above the menu, exactly like the printed menu sheet. The shakshuka is done. |
| `events` | wide, bleeds off the edge | Done. The truck with customers at the counter. Fills half the page from 900px and stretches to the copy, so a wide shot suits it and a portrait one does not. |
| `film` (4) | 4:5, 3:2 on narrow | Cold coffee, a bowl, bread, sandwiches. Full width band above the footer. The bowl is done. |

One note on the stand-ins. All the photos run through one shared
warm grade in CSS (`.ph img`), which is what makes a dozen different sources
read as a single set. Your own photos will pick that up automatically.

## The live preview link

The site is already live as a private link you can open on a phone:

```
https://claude.ai/code/artifact/12ac7ac1-d31e-439a-b213-3d8c0a88e3a6
```

That page is built from `site/index.html`, it is not the same file. The viewer
supplies its own page shell, blocks iframes and blocks images from any outside
host, so `tools/build-artifact.py` rewrites four things and nothing else:

1. keeps the part from `<title>` to `</body>` and re-adds the favicon and the
   right to left direction
2. swaps the Google Maps iframe for a Leaflet map whose OpenStreetMap tiles are
   baked into the file, four zoom levels of them
3. inlines all nine photographs into the file itself
4. drops `srcset`, which an inlined photo makes pointless

The map is the one place where the preview link and the real site genuinely
differ. On a real host the Google Maps iframe is the better map and stays. In
the preview nothing may load from outside, so the tiles around the truck are
fetched once at build time and travel inside the page. Zoom runs from 15 to 18
and the map can be dragged about 400 metres each way, which is where the tiles
stop. That is what makes the preview file about 4 MB.

The pin sits at `coords` in the config block, next to the address. It was
geocoded from the address, so if it is not exactly on the truck, move it:

```
coords:    { lat: 32.0563087, lon: 34.8759125 },
```

then rebuild. Tiles for the new spot are fetched automatically.

To push a change up:

```
py tools/build-artifact.py
```

then publish `build/artifact.html` to that same link. Downloads and re-encoded
photos are cached in `build/.cache`, so a rebuild needs no internet and only a
photo you actually changed is processed again. `build/` is not committed.

One thing to know when you check the link on a phone. The phone button and the
Instagram icon in the top bar only appear from 900 pixels wide and up. On a
narrow screen the top bar deliberately carries the wordmark alone, and the ways
to call are the buttons in the opening screen and in the footer.

## Publishing it later

The site is static, so it can be hosted free on Netlify, Cloudflare Pages,
Vercel or GitHub Pages. Drag the `site` folder onto their upload page and it is
live. The only recurring cost is the domain name, roughly 10 to 40 dollars a
year depending on whether you choose `.com` or `.co.il`.

Before going live, replace `example.com` in the `og:image` and `og:url` tags at
the top of `index.html` with the real domain, so the correct photo appears when
someone shares the link on WhatsApp.
