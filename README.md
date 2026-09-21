# superbits.in

The SuperBits company site. One static page, no build step, no dependencies —
`index.html` is the whole thing. Fonts come from Google Fonts; everything else
is inline.

## Files

| | |
|---|---|
| `index.html` | the site. Edit this and nothing else. |
| `build-artifact.py` | regenerates `dist/artifact.html`, the body-only copy used for the Claude preview link. Run it after editing. |
| `dist/` | generated. Not the thing you deploy. |

## Deploy

Copy the page to the server and point nginx at it.

```bash
scp index.html <user>@<server>:/var/www/superbits.in/index.html
```

nginx server block (same box that already serves `app.superspace.superbits.in`):

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

## What is claimed on this page

Everything on it is true and checkable today:

- **India, engineering company.** Stated, not embellished.
- **SuperSpace, shipped, on Google Play.** Linked to the real listing.
- **Own signaling and TURN servers, Postgres, transactional billing, an API
  contract guard.** All of it is in the `samsaram-backend` repo.
- **31 ms p95 ring-to-device at 1,000 concurrent sockets.** From our own load
  test (`signaling-server/test/load.js`), single node. The page says so.

Nothing about team size, funding, customer counts, awards or offices appears,
because none of it could be substantiated. Add those when they are true.

## Still to add

- **Privacy policy and terms.** Google Play requires a privacy policy URL, and
  this site is where it belongs — `superbits.in/privacy`. Currently missing
  from the release checklist too.
- **A company email.** The page uses `info.super.bits@gmail.com` because that
  is the address already published in the app. `hello@superbits.in` on the
  domain would read considerably better.
- **A careers page**, once there is a role to name. The contact section stands
  in for it.
- **An OG image** at `/og.png` (1200×630) so shared links preview properly. The
  meta tags are in place and pointing at nothing yet.
