# Animal Cafe website (animalcafe.net)

Static site hosted on Vercel (animalcafe.net DNS is at Hostinger, registrar Namecheap). A Cloudflare Workers config is also kept for a future move.

## Folders
- `public/` is the live website. Cloudflare serves this folder as is.
- `build.py` holds all page content: menu, prices, links, copy. `site.css` is the styling, `site.js` the behaviour (order popup, bowl builder, menu filter).
- `img/` holds the source images. The build copies them into `public/img/`.

## Change something
Edit `build.py` (or css/js), then run `python3 build.py prod` and commit. Cloudflare redeploys automatically on every push to `main`.

## Cloudflare settings
- Build command: none (leave empty)
- Deploy command: `npx wrangler deploy`
- Config: `wrangler.jsonc` (serves `public/`, uses `public/404.html`, applies `public/_redirects` and `public/_headers`)

## Vercel settings
- Framework: Other. Build command: none. Output directory: `public` (all set in `vercel.json`).
- Redirects and caching live in `vercel.json` (Vercel ignores `public/_redirects`).
- Every push to `main` redeploys automatically.
