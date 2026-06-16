# Architecture

> **TL;DR** — Source markdown lives at the repo root; GitHub Pages builds it into static HTML with Jekyll and serves it from the `main` branch — no deploy workflow. A separate scheduled Actions job generates event data but does not build or deploy the site.

> **At a glance**
> **Purpose** — Explain how a few flat files at the repo root become a published website.
> **Key files** — `_config.yml`, `index.md`, `Gemfile`, `.gitignore`.
> **Depends on** — GitHub Pages' native Jekyll build (the `github-pages` gem). **Used by** — site visitors at the published URL.
> **Related** — [components/site.md](components/site.md), [glossary.md](glossary.md).

## The one core idea

This is a **static site with no build step of our own**. We commit Jekyll source files; GitHub Pages runs the build and hosts the result. Nothing in this repo deploys the site — GitHub does, as part of its native Pages pipeline.

## Build-and-deploy flow

1. **Author.** Content and configuration are plain files at the repo root: `_config.yml` (site settings) and `index.md` (the homepage). Front matter on `index.md` selects a layout from the repo's **own custom theme** under `_layouts/` (`minima` is configured only as a fallback). The two-ink lithograph SCSS in `_sass/` is compiled to `assets/css/main.css` as part of the build.
2. **Push.** Changes are committed to the `main` branch.
3. **Build.** GitHub Pages detects the push, installs the `github-pages` gem (pinned in `Gemfile`), and runs `jekyll build`. The output is the static `_site/` directory.
4. **Serve.** GitHub serves `_site/` at `https://keunwoopark.github.io/aiintown/`.

The build artifact (`_site/`) and lockfile caches are never committed — see `.gitignore`.

## The data-generation flow (independent of the build)

A second, unrelated pipeline writes *data* into the repo. It does not build or serve anything — it only commits files that the Pages build later picks up:

1. **Schedule.** The `search-ai-events` GitHub Actions workflow fires daily (and on manual dispatch). This is the repo's only `.github/workflows` file and is **not** a deploy workflow.
2. **Search.** It runs `scripts/search_events.py`, which reads `_data/cities.yml` and, per enabled city, calls the Anthropic Messages API with the server-side `web_search` tool to find upcoming offline AI events.
3. **Store.** The script filters out past events, dedupes by a stable `id`, accumulates `first_seen`/`last_seen` history, and writes `_data/events/<city-id>.json`.
4. **Commit.** The workflow commits any change under `_data/events/` back to `main`. That push then triggers the normal Pages build above, which now renders the events: the homepage (`index.md`, `layout: home`) drives `_layouts/home.html`, which reads `site.data.events` and lists each enabled city's events as cards. So data flows end-to-end — search writes JSON, the build turns it into HTML — with no manual step in between.

See [components/event-search.md](components/event-search.md) for the details and gotchas.

## Key decisions and their rationale

- **Native GitHub Pages build, not a custom workflow.** Using the `github-pages` gem means GitHub builds the site server-side. The repo has no `.github/workflows` *deploy* file. The trade-off: only GitHub's [fixed allow-list of Jekyll plugins](https://pages.github.com/versions/) works; an unsupported plugin would force a switch to a GitHub Actions build workflow.
- **Pinning `github-pages` locally.** The `Gemfile` pins the same gem GitHub runs, so a local `bundle exec jekyll build` matches production and avoids version drift between preview and deploy.
- **Project-site URL configuration.** The repo is a *project site*, served under a path segment (`/aiintown`), not at the domain root. So `_config.yml` sets `url: https://keunwoopark.github.io` and `baseurl: /aiintown`. If the repo were ever renamed to `keunwoopark.github.io` (a user/organization site), `baseurl` must change to `""` or internal links would 404.

## Manual step that code cannot perform

Publishing requires a one-time toggle in **Settings → Pages → Deploy from a branch → `main` / `/ (root)`**. This is a repository-settings action in the GitHub UI; no file in the repo can enable it. Until it is toggled on, the site does not publish. The repo `README.md` documents this step.
