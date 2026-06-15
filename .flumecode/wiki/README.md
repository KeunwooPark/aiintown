<!-- wiki-synced-to: 793cb21e5f299c4b326a4945b0f1fb9642f29906 -->

# aiintown wiki

> **TL;DR** — `aiintown` is a minimal Jekyll site built and served natively by GitHub Pages, plus a scheduled GitHub Actions job that uses Claude web search to collect upcoming AI events into committed per-city JSON data files.

This repository is a static website. It uses [Jekyll](https://jekyllrb.com/) with the default `minima` theme and is published through GitHub Pages' native build (the `github-pages` gem), deployed from the `main` branch root. There is no application backend or JavaScript build tooling. A separate, data-only subsystem — a daily GitHub Actions workflow plus a Python script — searches the web (via Claude) for upcoming offline AI events per city and commits the results under `_data/events/` for a future template to render.

## Navigation map

| Component   | What it does                       | Wiki page                                | Key paths                            |
| ----------- | ---------------------------------- | ---------------------------------------- | ------------------------------------ |
| Jekyll site | The whole static site + its config | [components/site.md](components/site.md) | `_config.yml`, `index.md`, `Gemfile` |
| AI event search | Daily Claude search → per-city event JSON | [components/event-search.md](components/event-search.md) | `_data/cities.yml`, `scripts/search_events.py`, `.github/workflows/search-ai-events.yml` |
| UI Preview  | How sessions screenshot UI changes | [components/ui-preview.md](components/ui-preview.md) | `.flumecode/plugins/ui-preview.json`, `Gemfile` |

See also [architecture.md](architecture.md) for the build-and-deploy flow and [glossary.md](glossary.md) for Jekyll / GitHub Pages terms.

## For agents

This is the index. Start here, follow the link in the navigation map to the page you need, then open the cited source paths. The entire system is small enough that [components/site.md](components/site.md) covers nearly everything.
