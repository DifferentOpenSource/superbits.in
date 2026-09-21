# superbits.in

The SuperBits site. One static page — `index.html` is the whole thing. No build
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

## Deploy

```bash
scp index.html <user>@<server>:/var/www/superbits.in/index.html
```

nginx, on the same box that already serves `app.superspace.superbits.in`:

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
