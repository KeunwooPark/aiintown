# Jekyll site

> **TL;DR** — A Jekyll site with its **own custom theme** (own layouts, includes, and SCSS) whose homepage is a monospace airport-departure-board list of cities that each link to a per-city page listing that city's collected AI events, all in a stark two-ink lithograph print-shop visual style.

> **Purpose** — Document each source file of the site and what it controls.
> **Key files** — `_config.yml`, `index.md`, `cities/<id>.html`, `_layouts/default.html`, `_layouts/home.html`, `_layouts/city.html`, `_includes/event-card.html`, `_sass/`, `assets/css/main.scss`, `Gemfile`.
> **Depends on** — Jekyll via the `github-pages` gem; the event data under `_data/` (see [components/event-search.md](components/event-search.md)). `minima` remains configured only as a fallback. **Used by** — GitHub Pages' build.
> **Related** — [architecture.md](architecture.md) for the build/deploy flow, [glossary.md](glossary.md) for terms.

## Layout

The site ships its **own theme** rather than leaning on `minima`'s chrome. Content and config sit at the repo root (`_config.yml`, `index.md`); the presentation layer is fully committed: `_layouts/` (page skeletons), `_includes/` (header, footer, event card), and `_sass/` partials compiled through `assets/css/main.scss`. `theme: minima` stays in `_config.yml` purely as a fallback for anything not overridden — but the committed `_layouts/default.html` takes precedence, so no `minima` chrome renders. There are no `_posts/`.

### Theme structure

The render tree is layered so styling and structure each have one home:

- **`_layouts/default.html`** — the HTML skeleton (`<head>` + stylesheet link, then header → page `content` → footer).
- **`_layouts/home.html`** — wraps `default` and renders the **departure-board** city list (the landing page; no event cards).
- **`_layouts/city.html`** — wraps `default` and renders **one city's** events as cards; one rendered page per city.
- **`cities/<id>.html`** — tiny per-city stub pages (front matter only) that bind a `city_id` to `_layouts/city.html` at a `/cities/<id>/` permalink.
- **`_includes/`** — `header.html` (hero), `footer.html` (attribution), `event-card.html` (one event), `search-bar.html` (the city search input + autocomplete `<datalist>`).
- **`_sass/`** — SCSS partials (`_variables`, `_base`, `_layout`, `_event-card`, `_search`, `_departure-board`) imported by `assets/css/main.scss`.

## Source files

### `_config.yml`

Site-wide settings read by Jekyll at build time. It sets:

- `title` and `description` — site metadata surfaced by the theme. `title` is the **user-facing brand name** (`AI in Town`), rendered in the header and used as the default browser-tab title; it is deliberately distinct from the `aiintown` repo/URL slug below.
- `theme: minima` — uses the default Jekyll theme, so no layouts are committed here.
- `url` and `baseurl` — configured for a **project site** at `https://keunwoopark.github.io/aiintown/`. The `/aiintown` path is the `baseurl`; see [architecture.md](architecture.md) for why this matters and what breaks if the repo becomes a user/organization site.

Changing `_config.yml` requires a build restart locally (Jekyll does not hot-reload config).

### `index.md`

The homepage. Its front matter is now just `layout: home` plus a `title` (`AI in Town`, which overrides `site.title` for the homepage `<title>` via `page.title | default: site.title`); the body is intentionally empty (a comment) because `_layouts/home.html` renders the entire departure-board city list from `site.data`. This replaces the earlier under-construction placeholder and the `{% include events.html %}` approach.

### `_layouts/default.html`

The base HTML skeleton every page wraps. The `<head>` sets charset/viewport, the page title (`page.title | default: site.title`), preconnects to and loads the **Google Fonts** web typefaces (`Fraunces` display serif + `Nunito Sans` humanist sans + `Space Mono` monospace for the departure board, with `display=swap`, all in one combined stylesheet request), then links the compiled stylesheet via `{{ '/assets/css/main.css' | relative_url }}` — `relative_url` is required because the site is served under `baseurl: /aiintown`. The font `<link>` precedes `main.css` so the `$font-serif` / `$font-sans` / `$font-mono` stacks resolve against loaded fonts. Google Fonts is the one external runtime dependency; self-host under `assets/` if fully-offline rendering is ever required. The `<body>` pulls in `header.html`, then the page `content` inside `<main class="container">`, then `footer.html`. This override is what suppresses `minima`'s default chrome.

### `_layouts/home.html`

The **departure-board** landing layout (`layout: default`). It renders one scannable airport-departure-sign row per city instead of listing any events. It loops over `site.data.cities`, **skipping disabled cities** with `{% unless city.enabled == false %}` (so a city is enabled unless explicitly `enabled: false`). The board opens with a `.board-head` header row whose column labels carry `data-i18n` keys (`board_destination`, `board_country`, `board_next`), then each city becomes an `<a class="board-row">` anchor linking to its page via `{{ '/cities/' | append: city.id | append: '/' | relative_url }}` (`relative_url` keeps the `/aiintown` baseurl).

Each row maps the airport metaphor onto the data: a `.dest` column of `city.name` (the "destination"), a `.country` column, and a `.when` "time/status" column computed from `site.data.events[city.id] | sort: 'date'` — it shows the first event's date (`%b %-d`), or a `Date TBD` span when that event has `date_status: unknown` / blank `date`, or a `No upcoming events found yet.` fallback when the city has no events. A `.gate` `►` glyph closes the row.

Every row keeps the same `data-city-section` / `data-city-id` / `data-city-name` / `data-city-locale` attributes the old layout used, and the hidden `.no-results` line stays at the end. These are the hooks the client-side script reuses **unchanged**: `data-city-name`/`data-city-id` drive the city filter (toggling each row's `hidden` attribute and showing `.no-results` when nothing matches), and `data-city-locale` lets the language switcher localize the row's i18n spans. The loop is fully data-driven, but note the new requirement: a city also needs a matching `cities/<id>.html` stub (below) for its row's link to resolve.

### `_layouts/city.html`

The per-city event-listing layout (`layout: default`) — this is where the event cards moved off the homepage. It resolves its city with `{% assign city = site.data.cities | where: 'id', page.city_id | first %}` (the stub page supplies `page.city_id`), renders a `.back-link` to the homepage (`data-i18n="back_to_cities"`), then emits the same `.city-section` markup the old `_layouts/home.html` used: `data-city-section` with `data-city-id` / `data-city-name` / `data-city-locale`, an `<h2>` of `name, country`, and `site.data.events[city.id] | sort: 'date'` rendered as an `.event-list` of cards via `{% include event-card.html event=event city=city %}`, with the verbatim `No upcoming events found yet.` empty state. Because the section keeps `data-city-locale`, the language switcher still localizes the event text on these pages exactly as before.

### `cities/<id>.html`

One tiny **stub page per city** under `cities/`, each carrying only front matter: `layout: city`, `city_id: <id>` (must match an `id` in `_data/cities.yml`), `permalink: /cities/<id>/`, and a `title`. Jekyll builds each into `_site/cities/<id>/index.html`. Stubs exist for the two current cities (`cities/seoul.html`, `cities/berlin.html`).

These stubs are needed because GitHub Pages' native build forbids generator plugins, so per-city pages cannot be auto-generated — they are materialized as files. **Adding a city therefore requires two edits**: a `_data/cities.yml` entry *and* a matching `cities/<id>.html` stub. Forget the stub and the board row links to a 404. Keep the stub a ~5-line file; all rendering logic lives in the shared `_layouts/city.html`.

### `_data/i18n.yml`

Holds all UI chrome strings for each supported locale (`en`, `ko`, `de`). Each key is a locale code whose value is a map of string keys (`name` for the switcher option label, plus `language_label`, `tagline`, `search_label`, `search_placeholder`, `no_events`, `no_cities`, `date_tbd`, and the departure-board / per-city chrome keys `board_destination`, `board_country`, `board_next`, `back_to_cities`). Jekyll's `site.data.i18n` makes this available to templates at build time and to JavaScript via `window.SITE_I18N` (injected in `_layouts/default.html`); every locale block must define the same key set.

### `_includes/header.html` and `_includes/footer.html`

`header.html` is the flat two-ink hero banner — `site.title`, a tagline (with `data-i18n="tagline"` for runtime localization), a `<label class="lang-switch">` containing a `<select id="lang-switcher">` built from `site.data.i18n`, and the search bar via `{% include search-bar.html %}`. `footer.html` is the attribution strip showing `site.description`. Both override `minima`'s equivalents.

### `_includes/event-card.html`

Renders one event passed in as `include.event` (aliased to `e`), plus `include.city` for the `data-city="{{ city.id }}"` and `data-title` attributes (hooks for the future filter, and the Booking.com-style result-card structure). The title links to `e.url` when present, else plain text. The date line formats `e.date` with Liquid's `date` filter, **except** when `date_status == "unknown"` or `date` is blank — those route to a literal `Date TBD` and never reach the filter (which would choke on an unparseable string). `venue`, `description`, and `source` each render only when present, guarded by `{% if %}`. Field names mirror the schema written by `scripts/search_events.py` (see [components/event-search.md](components/event-search.md)).

**English + localized text.** The title and description each carry two spans: the always-rendered English text (`.t-en` / `.d-en`) and, *only when* `e.title_local` / `e.description_local` exists, a hidden localized span (`.t-local` / `.d-local`) tagged `data-locale="{{ include.city.locale }}"`. The English span is visible by default, so the card is correct before JS runs and whenever no localized variant exists; the language switcher unhides the localized span (and hides the English one) for cities whose locale matches the active UI locale (see below). Both `*_local` fields render **unescaped**, matching the pre-existing treatment of `description` — escaping/sanitizing is deliberately out of scope.

### Client-side city search and language switching

`_includes/search-bar.html` renders a `<form class="city-search">` containing an `<input id="city-search" data-i18n-placeholder="search_placeholder">` and a `<datalist id="city-options">` whose `<option>` elements are built from `site.data.cities` at build time. `assets/js/search.js` is linked from `_layouts/default.html` with `relative_url` and `defer`; it handles two concerns:

1. **Language switching** — reads `window.SITE_I18N` (injected by `_layouts/default.html` from `site.data.i18n`). `applyLang(lang)` sets `document.documentElement.lang`, then updates `textContent` for every `[data-i18n]` element and `placeholder` for every `[data-i18n-placeholder]` element using the locale dict. After swapping that chrome it also **toggles event text by locale**: it walks every `[data-city-section]` and, via `applyLocaleToSection`, computes `useLocal = section's data-city-locale === lang`; for matching sections it hides `.t-en`/`.d-en` and unhides `.t-local`/`.d-local`, and does the reverse for non-matching sections. Sections/events without a `.t-local` span simply keep English. The active locale is persisted to `localStorage` and restored on page load. The `<select id="lang-switcher">` (in `header.html`) drives the switcher.

2. **City filtering** — on each `input` event it reads the query, matches it case-insensitively against each `[data-city-section]` element's `data-city-name` and `data-city-id` attributes, toggles that element's `hidden` attribute accordingly, and reveals the `.no-results` element when nothing matches. The script targets the `[data-city-section]` attribute (not a class), so it works unchanged whether the matched elements are the homepage's `.board-row` anchors or a per-city page's single `.city-section` — no JS change was needed for the departure-board redesign.

No backend or build tooling is involved beyond the static datalist generation; the search header still renders on per-city pages (where it filters only the single section), which is harmless. Styling lives in `_sass/_search.scss`.

### `_sass/` partials and `assets/css/main.scss`

The custom design system. `assets/css/main.scss` carries the empty front-matter fence (`---` / `---`) that makes `jekyll-sass-converter` compile it to `assets/css/main.css`; it `@import`s the partials in order. The partials are:

- **`_variables.scss`** — the single source of truth for the look: a **two-ink lithograph palette** — cream paper `$color-bg`, near-black `$color-ink`, and a single bold vermilion `$color-accent` (the second ink) — plus flat tokens (`$radius: 0` for square corners, `$shadow: none`, and a `$border: 2px solid $color-ink` hard ink-frame token) and the type stacks: an **elegant display serif** `'Fraunces'` (`$font-serif`, loaded from Google Fonts) for headlines, a **warm humanist sans** `'Nunito Sans'` (`$font-sans`) for body, and a **monospace** `'Space Mono'` (`$font-mono`) for the departure board, each followed by system fallbacks. The old green/earth tokens (`$color-leaf`, `$color-leaf-light`, `$color-earth`) were removed — partials now reference `$color-ink`/`$color-accent` directly.
- **`_base.scss`** — element resets and typography: serif headlines colored ink-black, sans body, and links in the vermilion accent (ink on hover).
- **`_layout.scss`** — `.container`, the `.site-header` hero, `.city-section`, and `.site-footer`. The hero is **flat**: a solid cream `$color-bg` field with a hard ink `border-bottom`, no gradient — ink headline + vermilion tagline. Decoration is **geometric primitives** (data-URI SVGs, no raster assets): a vermilion `<circle>` in the hero corner via `.site-header::after`, and a small vermilion `<rect>` (filled square) marker before each city heading via `.city-section > h2::before`. Section headings and the footer use the hard `$border` ink rule.
- **`_event-card.scss`** — the `.event-card` is **flat with a hard ink border** (`$border`) and square corners (no shadow); the `:hover` swaps the border to the vermilion accent and adds a faint warm tint (no `translateY` lift, no shadow). The `.source` badge is a square ink-outlined tag (replacing the old rounded green pill); `time` is uppercase vermilion.
- **`_search.scss`** — the `.city-search` form (a square, hard-ink-bordered input with a vermilion focus outline) and the `.sr-only` screen-reader utility.
- **`_departure-board.scss`** — the homepage board. It **inverts the palette** to evoke a dark split-flap departure sign while staying on-brand: a `$color-ink` panel with `$color-bg` (cream) text, square corners, and the hard `$border` ink frame, all set in `$font-mono`. `.board-head` and `.board-row` are CSS grid (`destination | country | when | gate`); the `.when` "time/status" column, the `.gate` glyph, and `:hover` use the `$color-accent` vermilion. Imported **last** in `assets/css/main.scss` (after `search`).

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

- **Add a city** with **two** edits: a `_data/cities.yml` entry (the board row is data-driven) **and** a matching `cities/<id>.html` stub so the per-city page exists. Skip the stub and the board row links to a 404 — per-city pages cannot be auto-generated on GitHub Pages' native build.
- **Change how an event displays** by editing `_includes/event-card.html` (shared by the per-city pages).
- **Retune the departure board** in `_sass/_departure-board.scss` (e.g. revert it to the light cream palette) and the `$font-mono` token in `_sass/_variables.scss`.
- **Retune the look** — colors, spacing, and fonts live in `_sass/_variables.scss`; structural rules in the other `_sass/` partials.
- **Add pages** by creating more `.md` / `.html` files with front matter at the root or in subfolders (use `layout: default` to inherit the theme).
- **Add a plugin** only from GitHub Pages' [supported plugin list](https://pages.github.com/versions/); anything outside it requires switching to a GitHub Actions build workflow.
