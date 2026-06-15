<!-- wiki-synced-to: a347a938aa79cd5dc90d41fffb2a0e6d74ec32cb -->

# aiintown wiki

> **TL;DR** — `aiintown` is a minimal Jekyll site built and served natively by GitHub Pages whose homepage lists upcoming AI events grouped by city, plus a scheduled GitHub Actions job that uses Claude web search to collect those events into committed per-city JSON data files.

This repository is a static website. It uses [Jekyll](https://jekyllrb.com/) with its **own custom theme** — committed `_layouts/`, `_includes/`, and `_sass/` giving a botanic-garden / organic look with NYT-style serif headlines (`minima` stays configured only as a fallback) — and is published through GitHub Pages' native build (the `github-pages` gem), deployed from the `main` branch root. There is no application backend or JavaScript build tooling. A daily GitHub Actions workflow plus a Python script searches the web (via Claude) for upcoming offline AI events per city and commits the results under `_data/events/`; the homepage then renders that data at build time as a card list grouped by city.

## Navigation map

| Component   | What it does                       | Wiki page                                | Key paths                            |
| ----------- | ---------------------------------- | ---------------------------------------- | ------------------------------------ |
| Jekyll site | Custom-themed site rendering events by city | [components/site.md](components/site.md) | `index.md`, `_layouts/`, `_includes/`, `_sass/`, `assets/css/main.scss`, `_config.yml` |
| AI event search | Daily Claude search → per-city event JSON | [components/event-search.md](components/event-search.md) | `_data/cities.yml`, `scripts/search_events.py`, `.github/workflows/search-ai-events.yml` |
| UI Preview  | How sessions screenshot UI changes | [components/ui-preview.md](components/ui-preview.md) | `.flumecode/plugins/ui-preview.json`, `Gemfile` |

See also [architecture.md](architecture.md) for the build-and-deploy flow and [glossary.md](glossary.md) for Jekyll / GitHub Pages terms.

## For agents

This is the index. Start here, follow the link in the navigation map to the page you need, then open the cited source paths. The entire system is small enough that [components/site.md](components/site.md) covers nearly everything.
