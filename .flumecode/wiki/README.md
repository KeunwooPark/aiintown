<!-- wiki-synced-to: 6862c532a25728ecab24810bcd2809c3454970ea -->

# aiintown wiki

> **TL;DR** — `aiintown` is a minimal, empty Jekyll site built and served natively by GitHub Pages, with no JavaScript framework and no CI workflow.

This repository is a single static website. It uses [Jekyll](https://jekyllrb.com/) with the default `minima` theme and is published through GitHub Pages' native build (the `github-pages` gem), deployed from the `main` branch root. There is intentionally no application backend, no JavaScript build tooling, and no GitHub Actions deploy workflow.

## Navigation map

| Component   | What it does                       | Wiki page                                | Key paths                            |
| ----------- | ---------------------------------- | ---------------------------------------- | ------------------------------------ |
| Jekyll site | The whole static site + its config | [components/site.md](components/site.md) | `_config.yml`, `index.md`, `Gemfile` |

See also [architecture.md](architecture.md) for the build-and-deploy flow and [glossary.md](glossary.md) for Jekyll / GitHub Pages terms.

## For agents

This is the index. Start here, follow the link in the navigation map to the page you need, then open the cited source paths. The entire system is small enough that [components/site.md](components/site.md) covers nearly everything.
