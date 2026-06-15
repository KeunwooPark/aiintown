<!-- wiki-synced-to: 415850996d5a09c181ba18f4297211c0739ca767 -->

# aiintown wiki

> **TL;DR** — `aiintown` is a minimal Jekyll site built and served natively by GitHub Pages whose homepage lists upcoming AI events grouped by city, plus a scheduled GitHub Actions job that uses Claude web search to collect those events into committed per-city JSON data files.

This repository is a static website. It uses [Jekyll](https://jekyllrb.com/) with the default `minima` theme and is published through GitHub Pages' native build (the `github-pages` gem), deployed from the `main` branch root. There is no application backend or JavaScript build tooling. A daily GitHub Actions workflow plus a Python script searches the web (via Claude) for upcoming offline AI events per city and commits the results under `_data/events/`; the homepage then renders that data at build time through a small set of `_includes/` partials.

## Navigation map

| Component   | What it does                       | Wiki page                                | Key paths                            |
| ----------- | ---------------------------------- | ---------------------------------------- | ------------------------------------ |
| Jekyll site | Static site that renders events by city | [components/site.md](components/site.md) | `index.md`, `_includes/`, `assets/main.scss`, `_config.yml` |
| AI event search | Daily Claude search → per-city event JSON | [components/event-search.md](components/event-search.md) | `_data/cities.yml`, `scripts/search_events.py`, `.github/workflows/search-ai-events.yml` |
| UI Preview  | How sessions screenshot UI changes | [components/ui-preview.md](components/ui-preview.md) | `.flumecode/plugins/ui-preview.json`, `Gemfile` |

See also [architecture.md](architecture.md) for the build-and-deploy flow and [glossary.md](glossary.md) for Jekyll / GitHub Pages terms.

## For agents

This is the index. Start here, follow the link in the navigation map to the page you need, then open the cited source paths. The entire system is small enough that [components/site.md](components/site.md) covers nearly everything.
