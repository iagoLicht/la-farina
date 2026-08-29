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

## Changing prices, hours or the phone number

Open `site/index.html` in any text editor and search for this line:

```
const SITE = {
```

Everything a business owner needs to change sits in the block underneath it:
phone number, WhatsApp message, address, opening hours, and the full menu with
every price. Nothing else in the file needs to be touched. Save, refresh the
browser, done.

## Style rule

No em dashes and no en dashes anywhere in the site copy. Use commas, colons,
periods or parentheses instead. Time ranges use a plain hyphen, for example
`07:30-21:00`.

## Still to add

* Phone number, currently a placeholder
* Instagram and Facebook links
* Kosher certification authority
* Saturday hours, confirm whether closed
* Parking, seating and payment details
* Real photographs, every image is a labelled placeholder right now
* A vector version of the logo, SVG or AI or PDF

## Publishing it later

The site is static, so it can be hosted free on Netlify, Cloudflare Pages,
Vercel or GitHub Pages. Drag the `site` folder onto their upload page and it is
live. The only recurring cost is the domain name, roughly 10 to 40 dollars a
year depending on whether you choose `.com` or `.co.il`.

Before going live, replace `example.com` in the `og:image` and `og:url` tags at
the top of `index.html` with the real domain, so the correct photo appears when
someone shares the link on WhatsApp.
