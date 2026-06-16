# Jekyll site

> **TL;DR** — A Jekyll site with its **own custom theme** (own layouts, includes, and SCSS) whose homepage renders the collected AI events grouped by city in a botanic-garden / organic visual style.

> **Purpose** — Document each source file of the site and what it controls.
> **Key files** — `_config.yml`, `index.md`, `_layouts/default.html`, `_layouts/home.html`, `_includes/event-card.html`, `_sass/`, `assets/css/main.scss`, `Gemfile`.
> **Depends on** — Jekyll via the `github-pages` gem; the event data under `_data/` (see [components/event-search.md](components/event-search.md)). `minima` remains configured only as a fallback. **Used by** — GitHub Pages' build.
> **Related** — [architecture.md](architecture.md) for the build/deploy flow, [glossary.md](glossary.md) for terms.

## Layout

The site ships its **own theme** rather than leaning on `minima`'s chrome. Content and config sit at the repo root (`_config.yml`, `index.md`); the presentation layer is fully committed: `_layouts/` (page skeletons), `_includes/` (header, footer, event card), and `_sass/` partials compiled through `assets/css/main.scss`. `theme: minima` stays in `_config.yml` purely as a fallback for anything not overridden — but the committed `_layouts/default.html` takes precedence, so no `minima` chrome renders. There are no `_posts/`.

### Theme structure

The render tree is layered so styling and structure each have one home:

- **`_layouts/default.html`** — the HTML skeleton (`<head>` + stylesheet link, then header → page `content` → footer).
- **`_layouts/home.html`** — wraps `default` and renders the per-city events listing (replaces the old `_includes/events.html`).
- **`_includes/`** — `header.html` (hero), `footer.html` (attribution), `event-card.html` (one event), `search-bar.html` (the city search input + autocomplete `<datalist>`).
- **`_sass/`** — SCSS partials (`_variables`, `_base`, `_layout`, `_event-card`, `_search`) imported by `assets/css/main.scss`.

## Source files

### `_config.yml`

Site-wide settings read by Jekyll at build time. It sets:

- `title` and `description` — site metadata surfaced by the theme. `title` is the **user-facing brand name** (`AI in Town`), rendered in the header and used as the default browser-tab title; it is deliberately distinct from the `aiintown` repo/URL slug below.
- `theme: minima` — uses the default Jekyll theme, so no layouts are committed here.
- `url` and `baseurl` — configured for a **project site** at `https://keunwoopark.github.io/aiintown/`. The `/aiintown` path is the `baseurl`; see [architecture.md](architecture.md) for why this matters and what breaks if the repo becomes a user/organization site.

Changing `_config.yml` requires a build restart locally (Jekyll does not hot-reload config).

### `index.md`

The homepage. Its front matter is now just `layout: home` plus a `title` (`AI in Town`, which overrides `site.title` for the homepage `<title>` via `page.title | default: site.title`); the body is intentionally empty (a comment) because `_layouts/home.html` renders the entire events listing from `site.data`. This replaces the earlier under-construction placeholder and the `{% include events.html %}` approach.

### `_layouts/default.html`

The base HTML skeleton every page wraps. The `<head>` sets charset/viewport, the page title (`page.title | default: site.title`), preconnects to and loads the **Google Fonts** web typefaces (`Fraunces` display serif + `Nunito Sans` humanist sans, with `display=swap`), then links the compiled stylesheet via `{{ '/assets/css/main.css' | relative_url }}` — `relative_url` is required because the site is served under `baseurl: /aiintown`. The font `<link>` precedes `main.css` so the `$font-serif` / `$font-sans` stacks resolve against loaded fonts. Google Fonts is the one external runtime dependency; self-host under `assets/` if fully-offline rendering is ever required. The `<body>` pulls in `header.html`, then the page `content` inside `<main class="container">`, then `footer.html`. This override is what suppresses `minima`'s default chrome.

### `_layouts/home.html`

The events listing layout (`layout: default`). It loops over `site.data.cities`, **skipping disabled cities** with `{% unless city.enabled == false %}` (so a city is enabled unless explicitly `enabled: false`). For each city it emits a `.city-section` carrying `data-city-id` / `data-city-name` / `data-city-locale` attributes (the locale code comes from the city's `locale` field in `_data/cities.yml`), an `<h2>` of `name, country`, and the events from `site.data.events[city.id] | sort: 'date'` rendered as an `.event-list` of cards via `{% include event-card.html event=event city=city %}`. Empty/missing arrays show a `No upcoming events found yet.` message instead of erroring. The hidden `.no-results` line and `data-*` attributes are the hooks the client-side scripts use: `data-city-name`/`data-city-id` drive the city filter, while `data-city-locale` lets the language switcher decide which sections show localized event text (see below). The filter toggles each `.city-section`'s `hidden` attribute (showing `.no-results` when nothing matches). The loop is fully data-driven: adding a city to `_data/cities.yml` needs no template edit.

### `_data/i18n.yml`

Holds all UI chrome strings for each supported locale (`en`, `ko`, `de`). Each key is a locale code whose value is a map of string keys (`name` for the switcher option label, plus `language_label`, `tagline`, `search_label`, `search_placeholder`, `no_events`, `no_cities`, `date_tbd`). Jekyll's `site.data.i18n` makes this available to templates at build time and to JavaScript via `window.SITE_I18N` (injected in `_layouts/default.html`).

### `_includes/header.html` and `_includes/footer.html`

`header.html` is the botanic hero banner — `site.title`, a tagline (with `data-i18n="tagline"` for runtime localization), a `<label class="lang-switch">` containing a `<select id="lang-switcher">` built from `site.data.i18n`, and the search bar via `{% include search-bar.html %}`. `footer.html` is the attribution strip showing `site.description`. Both override `minima`'s equivalents.

### `_includes/event-card.html`

Renders one event passed in as `include.event` (aliased to `e`), plus `include.city` for the `data-city="{{ city.id }}"` and `data-title` attributes (hooks for the future filter, and the Booking.com-style result-card structure). The title links to `e.url` when present, else plain text. The date line formats `e.date` with Liquid's `date` filter, **except** when `date_status == "unknown"` or `date` is blank — those route to a literal `Date TBD` and never reach the filter (which would choke on an unparseable string). `venue`, `description`, and `source` each render only when present, guarded by `{% if %}`. Field names mirror the schema written by `scripts/search_events.py` (see [components/event-search.md](components/event-search.md)).

**English + localized text.** The title and description each carry two spans: the always-rendered English text (`.t-en` / `.d-en`) and, *only when* `e.title_local` / `e.description_local` exists, a hidden localized span (`.t-local` / `.d-local`) tagged `data-locale="{{ include.city.locale }}"`. The English span is visible by default, so the card is correct before JS runs and whenever no localized variant exists; the language switcher unhides the localized span (and hides the English one) for cities whose locale matches the active UI locale (see below). Both `*_local` fields render **unescaped**, matching the pre-existing treatment of `description` — escaping/sanitizing is deliberately out of scope.

### Client-side city search and language switching

`_includes/search-bar.html` renders a `<form class="city-search">` containing an `<input id="city-search" data-i18n-placeholder="search_placeholder">` and a `<datalist id="city-options">` whose `<option>` elements are built from `site.data.cities` at build time. `assets/js/search.js` is linked from `_layouts/default.html` with `relative_url` and `defer`; it handles two concerns:

1. **Language switching** — reads `window.SITE_I18N` (injected by `_layouts/default.html` from `site.data.i18n`). `applyLang(lang)` sets `document.documentElement.lang`, then updates `textContent` for every `[data-i18n]` element and `placeholder` for every `[data-i18n-placeholder]` element using the locale dict. After swapping that chrome it also **toggles event text by locale**: it walks every `[data-city-section]` and, via `applyLocaleToSection`, computes `useLocal = section's data-city-locale === lang`; for matching sections it hides `.t-en`/`.d-en` and unhides `.t-local`/`.d-local`, and does the reverse for non-matching sections. Sections/events without a `.t-local` span simply keep English. The active locale is persisted to `localStorage` and restored on page load. The `<select id="lang-switcher">` (in `header.html`) drives the switcher.

2. **City filtering** — on each `input` event it reads the query, matches it case-insensitively against each `.city-section`'s `data-city-name` and `data-city-id` attributes, toggles the section's `hidden` attribute accordingly, and reveals the `.no-results` element when no section matches.

No backend or build tooling is involved beyond the static datalist generation; styling lives in `_sass/_search.scss`.

### `_sass/` partials and `assets/css/main.scss`

The custom design system. `assets/css/main.scss` carries the empty front-matter fence (`---` / `---`) that makes `jekyll-sass-converter` compile it to `assets/css/main.css`; it `@import`s the partials in order. The partials are:

- **`_variables.scss`** — the single source of truth for the look: a botanic palette (leafy greens, earthy brown, soft cream `$color-bg`), spacing/radius/shadow tokens, and the type stacks — an **elegant display serif** `'Fraunces'` (`$font-serif`, loaded from Google Fonts) for headlines and a **warm humanist sans** `'Nunito Sans'` (`$font-sans`) for body, each followed by the original serif / system fallbacks. The palette is unchanged; this is a typography + decoration pass.
- **`_base.scss`** — element resets and typography (serif headlines colored leaf-green, sans body).
- **`_layout.scss`** — `.container`, the `.site-header` hero, `.city-section`, and `.site-footer`. The hero uses a **layered `linear-gradient`** (explicit hex stops, avoiding deprecated `darken()`/`lighten()`) instead of a flat green, plus a low-opacity botanical leaf watermark via `.site-header::after`; city headings carry a small inline-SVG leaf marker via `.city-section > h2::before`. Both motifs are data-URI SVGs — no raster assets.
- **`_event-card.scss`** — the Booking.com-style `.event-card` (rounded corners, soft shadow, date/venue/description, source pill), now with a `transition` and a **`:hover` lift** (`translateY(-3px)` and a deeper green-tinted shadow).
- **`_search.scss`** — the `.city-search` form styling and the `.sr-only` screen-reader utility.

Tune colors or fonts in `_variables.scss` and everything downstream follows.

### `Gemfile`

Pins the `github-pages` gem in the `:jekyll_plugins` group. This is the same gem GitHub Pages runs in production, so local builds use the exact toolchain GitHub uses. A commented-out optional `webrick` line is included for platforms that need it for `jekyll serve`.

### `.gitignore`

Excludes generated and machine-specific files from version control: `_site/` (the build output GitHub regenerates server-side), `.jekyll-cache/`, `.sass-cache/`, and `Gemfile.lock`.

### `README.md` (repo root)

Human-facing instructions, distinct from this wiki. It documents the one-time **Settings → Pages** toggle needed to publish, and how to preview locally with `bundle install` then `bundle exec jekyll serve` (noting the local URL respects the `/aiintown` baseurl).

## Local preview

```
bundle install
bundle exec jekyll serve
```

The site is then served at `http://localhost:4000/aiintown/` — the path reflects `baseurl`. Running `bundle exec jekyll build` instead produces the static `_site/` directory.

## Extension points

- **Add a city** by editing `_data/cities.yml` only — `_layouts/home.html` picks it up with no template change.
- **Change how an event displays** by editing `_includes/event-card.html`.
- **Retune the look** — colors, spacing, and fonts live in `_sass/_variables.scss`; structural rules in the other `_sass/` partials.
- **Add pages** by creating more `.md` / `.html` files with front matter at the root or in subfolders (use `layout: default` to inherit the theme).
- **Add a plugin** only from GitHub Pages' [supported plugin list](https://pages.github.com/versions/); anything outside it requires switching to a GitHub Actions build workflow.
