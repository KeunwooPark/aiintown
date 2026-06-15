# Architecture

> **TL;DR** — Source markdown lives at the repo root; GitHub Pages builds it into static HTML with Jekyll and serves it from the `main` branch — no servers, no CI workflow.

> **At a glance**
> **Purpose** — Explain how a few flat files at the repo root become a published website.
> **Key files** — `_config.yml`, `index.md`, `Gemfile`, `.gitignore`.
> **Depends on** — GitHub Pages' native Jekyll build (the `github-pages` gem). **Used by** — site visitors at the published URL.
> **Related** — [components/site.md](components/site.md), [glossary.md](glossary.md).

## The one core idea

This is a **static site with no build step of our own**. We commit Jekyll source files; GitHub Pages runs the build and hosts the result. Nothing in this repo deploys the site — GitHub does, as part of its native Pages pipeline.

## Build-and-deploy flow

1. **Author.** Content and configuration are plain files at the repo root: `_config.yml` (site settings) and `index.md` (the homepage). Front matter on `index.md` selects a theme layout.
2. **Push.** Changes are committed to the `main` branch.
3. **Build.** GitHub Pages detects the push, installs the `github-pages` gem (pinned in `Gemfile`), and runs `jekyll build`. The output is the static `_site/` directory.
4. **Serve.** GitHub serves `_site/` at `https://keunwoopark.github.io/aiintown/`.

The build artifact (`_site/`) and lockfile caches are never committed — see `.gitignore`.

## Key decisions and their rationale

- **Native GitHub Pages build, not a custom workflow.** Using the `github-pages` gem means GitHub builds the site server-side. This keeps the repo free of any `.github/workflows` deploy file. The trade-off: only GitHub's [fixed allow-list of Jekyll plugins](https://pages.github.com/versions/) works; an unsupported plugin would force a switch to a GitHub Actions workflow.
- **Pinning `github-pages` locally.** The `Gemfile` pins the same gem GitHub runs, so a local `bundle exec jekyll build` matches production and avoids version drift between preview and deploy.
- **Project-site URL configuration.** The repo is a *project site*, served under a path segment (`/aiintown`), not at the domain root. So `_config.yml` sets `url: https://keunwoopark.github.io` and `baseurl: /aiintown`. If the repo were ever renamed to `keunwoopark.github.io` (a user/organization site), `baseurl` must change to `""` or internal links would 404.

## Manual step that code cannot perform

Publishing requires a one-time toggle in **Settings → Pages → Deploy from a branch → `main` / `/ (root)`**. This is a repository-settings action in the GitHub UI; no file in the repo can enable it. Until it is toggled on, the site does not publish. The repo `README.md` documents this step.
