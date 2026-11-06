# superbits.in

The SuperBits Labs site. One static page — `index.html` is the whole thing. No build
step, no dependencies. Fonts come from Google Fonts; everything else is inline.

It is a holding page: it says who we are, that more is coming, and points at
the product that is already live. Nothing more, on purpose.

## Files

| | |
|---|---|
| `index.html` | the site. Edit this and nothing else. |
| `build-artifact.py` | regenerates `dist/artifact.html`, the body-only copy used for a Claude preview link. Optional; run it after editing if you use that preview. |
| `dist/` | generated, git-ignored. Not what you deploy. |

## The sky

The background is a canvas starfield — three depth layers drifting slowly,
twinkling, and shifting under the cursor, with stars near the pointer
brightening. It sits behind everything at `z-index: 0` and takes no pointer
events, so it can never intercept a click.

The knobs are at the top of the script in `index.html`:

| | |
|---|---|
| `LAYERS` | per-depth `size`, `alpha`, `drift` and `twinkle`. Raise `alpha` for a louder sky. |
| `REACH` | how far from the cursor stars respond, in px |
| `SHIFT` | how far the nearest layer parallaxes, in px |
| `w * h / 5200` | star density. Smaller divisor, more stars; capped at 260. |

Three things it does deliberately: `prefers-reduced-motion` gets a still sky
rather than no sky, the cursor is ignored on touch screens because there is no
hover to speak of, and a hidden tab stops animating entirely.

`node test-sky.js` drives the script against a stub canvas and checks what it
tries to paint. The failure mode here is silent — one NaN coordinate and the
sky just doesn't draw, which looks identical to a plain black page.

## Logo

`python3 make-logo.py` regenerates every SVG in `logo/`. The wordmark is
written as outlined paths, never `<text>` — a logo has to come out identical
in Illustrator, on a printer's machine and in an email signature, and none of
those will have Archivo installed.

| | |
|---|---|
| `superbits-logo.svg` | the full lockup, mark + SUPERBITS LABS, for dark backgrounds |
| `superbits-logo-light.svg` | the same lockup in near-black, for light backgrounds |
| `superbits-tile.svg` | the mark on its own rounded ground — the app-icon form, matching the favicon |
| `superbits-mark.svg` | the mark alone, transparent |
| `superbits-mark-mono.svg` | the mark in one colour via `currentColor`, for stamps and one-colour print |
| `superbits-mark-512.png` | 512×512 raster with alpha, for anywhere SVG isn't accepted |
| `bloomlet-icon.png` | the Bloomlet app icon, inlined into the page as a data URI |

Standalone assets draw the eight grey cells at `#3D4453`. The site header
keeps `#282D38` on purpose: there the mark is small and beside the wordmark,
so it should recede, and alone that value is a black square with a pink dot.

The bare mark is drawn edge to edge. Anywhere it needs breathing room — an
app icon, a profile picture — use `superbits-tile.svg`, which already has it,
rather than shrinking the mark inside a frame.

The tab icon is an inline SVG data URI in `index.html`, the same composition
as the tile, so it costs no request and stays crisp at any size.
`apple-touch-icon.png` in the root is the one real file: iOS wants a PNG and
ignores a data URI there. It comes from `make-store-assets.py`, which shares
its drawing code with the Play logo.

## Generated artwork

`python3 make-store-assets.py` regenerates every raster asset from the mark.
All RGB PNGs — 24-bit, no alpha, which is what Play asks for.

| | |
|---|---|
| `store/superbits-logo-512.png` | 512×512 developer logo, ~7 KB |
| `store/superbits-feature-4096.png` | 4096×2304 feature graphic, ~110 KB |
| `store/superbits-youtube-banner.png` | 2560×1440 channel art, ~330 KB |
| `apple-touch-icon.png` | 180×180 iOS home-screen icon, in the root where Safari looks for it |

YouTube crops channel art differently on every surface and only the centre
**1546×423** survives on all of them — a phone sees that and nothing else. The
lockup is sized to sit inside that box with room to spare, and the starfield
is what the wider crops get. `youtube()` asserts the fit, because a banner
whose name is cut in half on mobile is the usual way this asset goes wrong.

PNG rather than JPEG on purpose: a composition this dark and this flat bands
visibly under JPEG, and lossless still comes in at a tenth of the 1 MB limit.

The eight grey cells are lighter here (`#3D4453`) than on the site
(`#282D38`). On the site the mark is small and beside the wordmark, so it
should recede; alone at 48px in a Play listing that same grey reads as a black
square with a pink dot, and the grid disappears.

## Deploy

GitHub Pages serves this repo at **superbits.in** — `CNAME` in the root is what
binds the domain, and `.nojekyll` stops Pages running the page through Jekyll.
Push to `main` and the site updates; there is nothing else to do.

Settings → Pages: source `main` / `/ (root)`, custom domain `superbits.in`,
Enforce HTTPS on.

DNS at BigRock, for the apex and `www`:

```
A     @     185.199.108.153
A     @     185.199.109.153
A     @     185.199.110.153
A     @     185.199.111.153
CNAME www   differentopensource.github.io.
```

<details>
<summary>Self-hosting instead, on the box that runs app.superspace.superbits.in</summary>

```bash
scp index.html <user>@<server>:/var/www/superbits.in/index.html
```

```nginx
server {
    listen 443 ssl http2;
    server_name superbits.in www.superbits.in;

    ssl_certificate     /etc/letsencrypt/live/superbits.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/superbits.in/privkey.pem;

    root /var/www/superbits.in;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}

server {
    listen 80;
    server_name superbits.in www.superbits.in;
    return 301 https://$host$request_uri;
}
```

Certificate: `sudo certbot --nginx -d superbits.in -d www.superbits.in`.
</details>

## What the page claims

Only what can be checked today: that SuperBits Labs is a technology company
in India, and that Bloomlet is live at bloomlet.superbits.in. No team size, funding,
customer count, award or office appears anywhere, because none of it could be
substantiated yet. Add them when they are true.

## Still to add

- **Privacy policy and terms.** Google Play requires a privacy policy URL, and
  this domain is where it belongs — `superbits.in/privacy`. Still open on the
  Bloomlet release checklist, so this site unblocks the store listing.
- **A company email.** The page uses `info.super.bits@gmail.com`, the address
  already published in the app. `hello@superbits.in` on the domain would read
  considerably better.
- **An OG image** at `/og.png`, 1200×630. The meta tags are in place and
  currently point at nothing, so shared links preview blank.

  bigrock domain
