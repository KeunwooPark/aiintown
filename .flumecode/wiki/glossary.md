# Glossary

> **TL;DR** — Definitions of the Jekyll and GitHub Pages terms used across this wiki.

## Jekyll

**Jekyll** — A Ruby static-site generator that turns markdown/HTML source plus layouts into a static website. Used here as the site engine.

**Front matter** — The YAML block fenced by `---` at the top of a content file (e.g. `index.md`). It sets per-page variables such as `layout` and `title` that the theme reads. A file with no front matter is copied verbatim instead of being processed.

**`minima`** — Jekyll's default theme. Still named via `theme: minima` in `_config.yml`, but only as a **fallback**: the repo ships its own theme (`_layouts/`, `_includes/`, `_sass/`) whose `_layouts/default.html` takes precedence, so no `minima` chrome actually renders.

**Layout** — A template under `_layouts/` that wraps a page's content. A page's front matter picks one with `layout:`, and a layout can itself nest in another (`home` → `default` here). The site's custom layouts replace `minima`'s.

**Include (partial)** — A reusable snippet under `_includes/` pulled into a page or layout with `{% include file.html %}`, optionally with parameters (e.g. `{% include event-card.html event=event city=city %}`, read inside as `include.event` / `include.city`). The site uses `header.html`, `footer.html`, and `event-card.html`.

**`_sass/` and SCSS compilation** — SCSS partials (`_variables`, `_base`, `_layout`, `_event-card`) live under `_sass/`. `assets/css/main.scss` carries an empty front-matter fence so `jekyll-sass-converter` (bundled with `github-pages`) compiles its `@import`s into `assets/css/main.css`.

**`relative_url`** — A Liquid filter that prefixes a path with the site's `baseurl` (`/aiintown`). Asset and internal links use it so they resolve correctly under the project-site path.

**`site.data`** — The Liquid object exposing everything under `_data/`. A file `_data/foo.json` is reachable as `site.data.foo`; the home layout indexes events dynamically as `site.data.events[city.id]`.

**`_config.yml`** — Jekyll's site-wide configuration file, read once at build time.

**`_site/`** — The generated output directory Jekyll writes the built static site into. Gitignored; GitHub regenerates it server-side.

## GitHub Pages

**GitHub Pages** — GitHub's static-site hosting. Here it uses the *native build*: GitHub runs Jekyll for us on push, so no CI workflow is needed.

**`github-pages` gem** — A meta-gem pinning the exact versions of Jekyll, plugins, and dependencies that GitHub Pages runs in production. Pinned in the `Gemfile` so local builds match the deployed build.

**Project site** — A GitHub Pages site served under a repository path, e.g. `https://keunwoopark.github.io/aiintown/`. Contrast with a *user/organization site* served at the domain root (`https://keunwoopark.github.io/`), which requires a repo named `keunwoopark.github.io`.

**`baseurl`** — The path prefix a project site is served under (`/aiintown` here). Internal links must respect it, or they 404. A user/organization site uses an empty `baseurl`.

**Deploy from a branch** — The GitHub Pages source mode used here: GitHub builds and serves from a chosen branch (`main`) and folder (`/ (root)`). Enabled manually in Settings → Pages.

## AI event search

**`_data/`** — Jekyll's data directory. Any YAML/JSON file here is auto-loaded and exposed to templates as `site.data.<filename>`. The event subsystem reads `_data/cities.yml` and writes `_data/events/<city>.json` into it.

**Web search tool** — Anthropic's server-side `web_search_20250305` tool. When enabled in a Messages API request, Claude can browse the live web to ground its answers. It is a **billed** tool — usage counts toward API cost. Without it the model would hallucinate events.

**`ANTHROPIC_API_KEY`** — The Anthropic API credential. Supplied as a GitHub Actions repository secret and read from the environment by the `Anthropic()` client; required for the workflow to run.

**Upcoming event** — An event whose date is on or after the run date. The script keeps these and drops events with a parseable past date. Events with a missing/unparseable date are kept too (they may be upcoming) and flagged `date_status: "unknown"`.

**Stable `id`** — A 16-character SHA-1 fingerprint of an event's normalized `title|date|city`. It is the dedupe key across runs, so the same event is updated rather than duplicated.

**`first_seen` / `last_seen`** — ISO dates recording when an event was first discovered and most recently re-seen. `first_seen` is preserved on updates; `last_seen` advances each run that returns the event, giving an accumulating history.

**`workflow_dispatch`** — A GitHub Actions trigger that lets a workflow be started manually from the Actions UI, alongside its scheduled `cron` trigger.
