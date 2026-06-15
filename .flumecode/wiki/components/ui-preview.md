<!-- preview-plugin-synced-to: 2d6ff4d133ed1717fa627cc0654e15f8ce52b5cb -->

# UI Preview

> **TL;DR** — Boot this Jekyll site headlessly with `bundle exec jekyll serve` and screenshot a temporary showcase page mounted at `/aiintown/__flumecode_preview/`.

## Detected stack
- Static Jekyll site, `minima` theme, built via the `github-pages` gem (Ruby/Bundler).
- `baseurl: /aiintown` in `_config.yml`, so everything is served under `/aiintown/`.

## How previews run
- Install: `bundle install`.
- Serve: `bundle exec jekyll serve --host 127.0.0.1 --port {PORT} --no-watch`.
- Readiness/showcase URLs include the `/aiintown` baseurl prefix.
- `webrick` is pinned in the `Gemfile` because Ruby 3.0+ dropped it from the stdlib.

## Showcase
A per-session agent creates `flumecode_preview.html` (front matter `permalink: /__flumecode_preview/`, so it is served at `/aiintown/__flumecode_preview/`) that renders the REAL changed layout/include/page with hard-coded fake data — no DB/backend is reachable. The file name must not begin with `_`/`__`, which Jekyll excludes from the build. Recipe details live in `.flumecode/plugins/ui-preview.json`.
