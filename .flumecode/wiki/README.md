<!-- wiki-synced-to: db930f262c3faefb16c6ab8358ca61b9b1966239 -->

# aiintown wiki

> **TL;DR** — `aiintown` (product name "AI in Town") is a minimal Jekyll site built and served natively by GitHub Pages whose homepage lists upcoming AI events grouped by city, plus a scheduled GitHub Actions job that uses Claude web search to collect those events into committed per-city JSON data files.

This repository is a static website, presented to users as **AI in Town** — a site that collects and shows local offline meetups across various cities. It uses [Jekyll](https://jekyllrb.com/) with its **own custom theme** — committed `_layouts/`, `_includes/`, and `_sass/` giving a botanic-garden / organic look with a Google Fonts type pairing (`Fraunces` display serif headlines + `Nunito Sans` body), a gradient hero, and botanical SVG accents (`minima` stays configured only as a fallback) — and is published through GitHub Pages' native build (the `github-pages` gem), deployed from the `main` branch root. There is no application backend or JavaScript build tooling. A daily GitHub Actions workflow plus a Python script searches the web (via Claude) for upcoming offline AI events per city and commits the results under `_data/events/`; the homepage then renders that data at build time as a card list grouped by city.

## Navigation map

| Component   | What it does                       | Wiki page                                | Key paths                            |
| ----------- | ---------------------------------- | ---------------------------------------- | ------------------------------------ |
| Jekyll site | Custom-themed site rendering events by city, with client-side city search | [components/site.md](components/site.md) | `index.md`, `_layouts/`, `_includes/`, `_sass/`, `assets/css/main.scss`, `assets/js/search.js`, `_config.yml` |
| AI event search | Daily Claude search → per-city event JSON | [components/event-search.md](components/event-search.md) | `_data/cities.yml`, `scripts/search_events.py`, `.github/workflows/search-ai-events.yml` |
| UI Preview  | How sessions screenshot UI changes | [components/ui-preview.md](components/ui-preview.md) | `.flumecode/plugins/ui-preview.json`, `Gemfile` |

See also [architecture.md](architecture.md) for the build-and-deploy flow and [glossary.md](glossary.md) for Jekyll / GitHub Pages terms.

## For agents

This is the index. Start here, follow the link in the navigation map to the page you need, then open the cited source paths. The entire system is small enough that [components/site.md](components/site.md) covers nearly everything.
