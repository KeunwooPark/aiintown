# Glossary

> **TL;DR** — Definitions of the Jekyll and GitHub Pages terms used across this wiki.

## Jekyll

**Jekyll** — A Ruby static-site generator that turns markdown/HTML source plus layouts into a static website. Used here as the site engine.

**Front matter** — The YAML block fenced by `---` at the top of a content file (e.g. `index.md`). It sets per-page variables such as `layout` and `title` that the theme reads. A file with no front matter is copied verbatim instead of being processed.

**`minima`** — Jekyll's default theme. Still named via `theme: minima` in `_config.yml`, but only as a **fallback**: the repo ships its own theme (`_layouts/`, `_includes/`, `_sass/`) whose `_layouts/default.html` takes precedence, so no `minima` chrome actually renders.

**Layout** — A template under `_layouts/` that wraps a page's content. A page's front matter picks one with `layout:`, and a layout can itself nest in another (`home` → `default` here). The site's custom layouts replace `minima`'s.

**Include (partial)** — A reusable snippet under `_includes/` pulled into a page or layout with `{% include file.html %}`, optionally with parameters (e.g. `{% include event-card.html event=event city=city %}`, read inside as `include.event` / `include.city`). The site uses `header.html`, `footer.html`, `event-card.html`, and `search-bar.html`.

**`_sass/` and SCSS compilation** — SCSS partials (`_variables`, `_base`, `_layout`, `_event-card`, `_search`, `_departure-board`) live under `_sass/`. `assets/css/main.scss` carries an empty front-matter fence so `jekyll-sass-converter` (bundled with `github-pages`) compiles its `@import`s into `assets/css/main.css`.

**Departure board** — The homepage's airport-departure-sign metaphor: `_layouts/home.html` renders the cities as a monospace, dark-panel grid (`.departure-board` / `.board-row`, styled in `_sass/_departure-board.scss`) instead of listing events. Each row's columns map onto the data (destination = city, then country, then a "next event" time/status column) and link to that city's page.

**Per-city page / stub** — Each city's events live on a dedicated page at `/cities/<id>/`, rendered by `_layouts/city.html`. Because GitHub Pages' native build allows no generator plugin, the page is materialized by a tiny front-matter-only **stub** file `cities/<id>.html` that binds `city_id` to the layout. Adding a city needs both a `_data/cities.yml` entry and a matching stub.

**`relative_url`** — A Liquid filter that prefixes a path with the site's `baseurl` (`/aiintown`). Asset and internal links use it so they resolve correctly under the project-site path.

**`site.data`** — The Liquid object exposing everything under `_data/`. A file `_data/foo.json` is reachable as `site.data.foo`; the home layout indexes events dynamically as `site.data.events[city.id]`.

**Client-side city search / `<datalist>`** — The search bar (`_includes/search-bar.html` + `assets/js/search.js`) filters events entirely in the browser, with no reload or backend. A native HTML `<datalist>` of city names is generated from `site.data.cities` at build time for autocomplete, and a vanilla-JS `input` handler toggles each city section's `hidden` attribute. No JS build tooling is involved.

**UI chrome localization / `_data/i18n.yml`** — A client-side translation mechanism for the site's fixed UI strings (tagline, search labels, empty-state messages, `Date TBD`). `_data/i18n.yml` holds one entry per locale (`en`, `ko`, `de`); the table is serialized into the page as `window.SITE_I18N` and applied by `assets/js/search.js`. Templates tag translatable elements with `data-i18n="<key>"` (text) or `data-i18n-placeholder="<key>"` (attribute), keeping the English literal as a pre-JS / crawler fallback. The `<select id="lang-switcher">` lets a visitor pick a locale; the choice is persisted in `localStorage` under `lang` and restored on reload. Localized **event text** (below) rides on the same switcher.

**Localized event text / `title_local` / `description_local`** — Per-event title and description rendered in a city's own language, distinct from the fixed UI chrome above. `scripts/search_events.py` asks Claude to return `title_local`/`description_local` (in the city's `language`) alongside the English fields, and `_includes/event-card.html` emits them as hidden `.t-local`/`.d-local` spans beside the visible `.t-en`/`.d-en` English spans. When the active UI locale equals a city's `locale` code (matched via the section's `data-city-locale`), `applyLang` in `search.js` swaps that city's events to the localized spans; otherwise — or when an event lacks the `*_local` fields — English shows. Cost stays linear: one localized variant per city, not every locale.

**City `locale` vs `language`** — Two fields on each `_data/cities.yml` entry. `language` is a human-readable name (`Korean`, `German`) that feeds the search prompt; `locale` is a short code (`ko`, `de`) matching the `_data/i18n.yml` keys, used only by the Jekyll/JS layer to match a city's events against the active UI locale.

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
