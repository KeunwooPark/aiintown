<!-- preview-plugin-synced-to: 2d6ff4d133ed1717fa627cc0654e15f8ce52b5cb -->

# UI Preview

> **TL;DR** — Boot this Jekyll site headlessly with `bundle exec jekyll serve` and screenshot a temporary showcase page mounted at `/aiintown/__flumecode_preview/`.

## Detected stack
- Static Jekyll site, `minima` theme, built via the `github-pages` gem (Ruby/Bundler).
- `baseurl: /aiintown` in `_config.yml`, so everything is served under `/aiintown/`.

## How previews run
- Install step 1: `bundle install`.
- Install step 2: pre-install the Playwright Chromium browser. Playwright ships browser binaries separately from its npm package, so a Playwright install or update can leave `~/Library/Caches/ms-playwright/` without the headless-shell build that the screenshot step launches; this step self-heals that gap. It resolves the runner's own Playwright via `$(npm root -g)/@flumecode/runner` and runs `npx playwright install chromium` from inside that directory, so the downloaded build matches the exact Playwright version the runner uses. If that directory is absent it falls back to `npx --yes playwright install chromium`. The step ends in `|| true` so it is non-fatal and never blocks the Jekyll preview.
- Serve: `bundle exec jekyll serve --host 127.0.0.1 --port {PORT} --no-watch`.
- Readiness/showcase URLs include the `/aiintown` baseurl prefix.
- `webrick` is pinned in the `Gemfile` because Ruby 3.0+ dropped it from the stdlib.

## Showcase
A per-session agent creates `flumecode_preview.html` (front matter `permalink: /__flumecode_preview/`, so it is served at `/aiintown/__flumecode_preview/`) that renders the REAL changed layout/include/page with hard-coded fake data — no DB/backend is reachable. The file name must not begin with `_`/`__`, which Jekyll excludes from the build. Recipe details live in `.flumecode/plugins/ui-preview.json`.
