# Dispatch

A local-first news desk. RSS feeds, filtered your way, with on-device summaries.
No accounts, no paid keys, nothing leaves your device except the feed requests.

## Hosting (GitHub + Cloudflare Pages, free)

GitHub Pages alone will NOT work, because it can't run the feed proxy.
Host on Cloudflare Pages instead and connect it to your GitHub repo.

1. Put this folder in a GitHub repo (see below).
2. In the Cloudflare dashboard: Workers & Pages -> Create -> Pages ->
   Connect to Git -> pick the repo.
3. Framework preset: None. Build command: `exit 0` (this is what lets the
   proxy function deploy). Build output directory: `.` (repo root). The
   included `wrangler.toml` already sets the output dir, so defaults are fine.
4. Save and Deploy. You get a URL like `https://dispatch-xxx.pages.dev`.

The `functions/proxy.js` file is auto-served at `/proxy`, which is the path the
app tries first, so feeds fetch server-side with no CORS problems.

### Put the code on GitHub (terminal)

    cd dispatch
    git init
    git add .
    git commit -m "Dispatch"
    git branch -M main
    git remote add origin https://github.com/YOU/dispatch.git
    git push -u origin main

No terminal? On github.com create a new repo, then use
"Add file -> Upload files" and drag everything in this folder in.

## Install on a phone

- iOS: open the pages.dev URL in Safari -> Share -> Add to Home Screen.
- Android: open it in Chrome -> menu -> Install app.

## Run locally on a computer (optional)

    python3 serve.py

then open http://localhost:8000. This runs the same proxy locally.

## Updating

Push to GitHub (`git push`) or re-upload files. Cloudflare redeploys on its own.
