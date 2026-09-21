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

## Logo

`logo/` holds the SuperBits mark — the same one in the site header.

| | |
|---|---|
| `superbits-mark.svg` | the brand version: `#282D38` squares, `#FF2D6F` centre, transparent ground. Works on light and dark. |
| `superbits-mark-mono.svg` | single colour via `currentColor` — inherits whatever colour you set, for stamps, favicons and one-colour print. |
| `superbits-mark-512.png` | 512×512 raster with alpha, for anywhere SVG isn't accepted. |
| `superspace-icon.png` | the SuperSpace app icon, inlined into the page as a data URI. |

The mark is drawn edge to edge with no padding. Anywhere it needs breathing
room — an app icon, a favicon, a profile picture — add roughly 15% around it
rather than scaling it down inside the frame.

## Play Console artwork

`python3 make-store-assets.py` regenerates the developer-page assets from the
mark. Both are RGB PNGs — 24-bit, no alpha, which is what Play asks for.

| | |
|---|---|
| `store/superbits-logo-512.png` | 512×512 developer logo, ~7 KB |
| `store/superbits-feature-4096.png` | 4096×2304 feature graphic, ~110 KB |

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

Only what can be checked today: that SuperBits is a technology company in
India, and that SuperSpace is live on Google Play. No team size, funding,
customer count, award or office appears anywhere, because none of it could be
substantiated yet. Add them when they are true.

## Still to add

- **Privacy policy and terms.** Google Play requires a privacy policy URL, and
  this domain is where it belongs — `superbits.in/privacy`. Still open on the
  SuperSpace release checklist, so this site unblocks the store listing.
- **A company email.** The page uses `info.super.bits@gmail.com`, the address
  already published in the app. `hello@superbits.in` on the domain would read
  considerably better.
- **An OG image** at `/og.png`, 1200×630. The meta tags are in place and
  currently point at nothing, so shared links preview blank.

  bigrock domain
