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

* `social.instagram` and `social.facebook`, an empty string hides that icon
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

* Phone number, currently the placeholder `050-000-0000`. Until it is real, the
  call and WhatsApp buttons all dial a number that is not yours.
* Instagram and Facebook links, currently empty so the icons are hidden
* Kosher certification authority, currently `null` so no kosher line shows
* Saturday hours, confirm whether closed
* Confirm the four "good to know" facts: parking, seating, payment, pre-ordering
* Accessibility, deliberately not claimed on the page until someone confirms it
* A vector version of the logo, SVG or AI or PDF
* The real domain, to replace `example.com` in the `og:image` and `og:url` tags

## Photographs that must be replaced

Every photograph on the site right now is a temporary stand-in from a free stock
library, chosen to hold the right shape and mood. None of them is La Farina.
Twelve photographs, all inside `SITE.images`:

| Slot | Shape | What to shoot |
|---|---|---|
| `hero` | wide, dark | The truck at dusk with the lights on, or a hero pastry shot. Needs a dark, quiet area on one side for the wordmark to sit over. |
| `about` | portrait | Coffee being poured, hands in frame |
| `strip` (3) | 4:3 each | Croissants, the truck itself, a sandwich. These three sit butted together above the menu, exactly like the printed menu sheet. |
| `boardRail` (2) | 4:5 each | A shake and a pastry, both against a dark ground. The second one is hidden on phones. |
| `events` | wide | The truck set up at an event, people around it |
| `film` (4) | 4:5 each | Cold coffee, pizza, bread, sandwiches. Full width band above the footer. |

Two notes on the current stand-ins. The truck in the middle of the strip is
somebody else's truck and carries Japanese signage, so it is cropped to hide
most of it. Replace that one first. All the photos also run through one shared
warm grade in CSS (`.ph img`), which is what makes a dozen different sources
read as a single set. Your own photos will pick that up automatically.

## Publishing it later

The site is static, so it can be hosted free on Netlify, Cloudflare Pages,
Vercel or GitHub Pages. Drag the `site` folder onto their upload page and it is
live. The only recurring cost is the domain name, roughly 10 to 40 dollars a
year depending on whether you choose `.com` or `.co.il`.

Before going live, replace `example.com` in the `og:image` and `og:url` tags at
the top of `index.html` with the real domain, so the correct photo appears when
someone shares the link on WhatsApp.
