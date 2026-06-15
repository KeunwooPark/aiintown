# Jekyll site

> **TL;DR** — A minimal Jekyll site whose homepage renders the collected AI events grouped by city, built on the `minima` theme with a couple of small custom includes and a stylesheet.

> **Purpose** — Document each source file of the site and what it controls.
> **Key files** — `_config.yml`, `index.md`, `_includes/events.html`, `_includes/event-card.html`, `assets/main.scss`, `Gemfile`.
> **Depends on** — Jekyll + the `minima` theme via the `github-pages` gem; the event data under `_data/` (see [components/event-search.md](components/event-search.md)). **Used by** — GitHub Pages' build.
> **Related** — [architecture.md](architecture.md) for the build/deploy flow, [glossary.md](glossary.md) for terms.

## Layout

The site is small. Content and config sit at the repo root (`_config.yml`, `index.md`); a thin rendering layer extends the `minima` theme with two `_includes/` partials and a single `assets/main.scss`. There are no `_layouts/` or `_posts/` — page chrome still comes from the theme; the includes only add the events list to the homepage body.

## Source files

### `_config.yml`

Site-wide settings read by Jekyll at build time. It sets:

- `title` and `description` — site metadata surfaced by the theme.
- `theme: minima` — uses the default Jekyll theme, so no layouts are committed here.
- `url` and `baseurl` — configured for a **project site** at `https://keunwoopark.github.io/aiintown/`. The `/aiintown` path is the `baseurl`; see [architecture.md](architecture.md) for why this matters and what breaks if the repo becomes a user/organization site.

Changing `_config.yml` requires a build restart locally (Jekyll does not hot-reload config).

### `index.md`

The homepage. Its front matter uses `layout: page` (not `minima`'s `home`, which would inject a blog-post list) so the page renders its own body inside the theme's header/footer chrome. The body is a one-line intro plus `{% include events.html %}`, which delegates all event rendering to the partial below.

### `_includes/events.html`

The events listing partial. It loops over the **enabled** cities — `site.data.cities | where: "enabled", true` — and for each one indexes the matching event array as `site.data.events[city.id]` (the data file is `_data/events/<city.id>.json`, exposed by Jekyll under that key). Each city becomes a `<section>` with an `<h2>` heading (`name`, plus `, country` when present). When a city's array is non-empty it renders an `<ul>` of cards via `{% include event-card.html event=event %}`; when empty or missing it shows a `No upcoming events found yet.` message instead of erroring. The loop is fully data-driven: adding a city to `_data/cities.yml` needs no template edit.

### `_includes/event-card.html`

Renders one event passed in as `include.event`. The title links to `event.url` when present, else plain text. The date line formats `event.date` with Liquid's `date` filter, **except** when `date_status == "unknown"` or `date` is blank — those route to a literal `Date TBD` and never reach the filter (which would choke on an unparseable string). `venue`, `description`, and `source` each render only when present, guarded by `{% if %}` so missing optional fields produce no empty markup. Field names mirror the schema written by `scripts/search_events.py` (see [components/event-search.md](components/event-search.md)).

### `assets/main.scss`

Light custom styling layered on the theme. The empty front-matter block (`---` / `---`) makes Jekyll process the file into CSS; `@import "minima";` keeps all the theme's styles, after which a handful of rules style the event cards (list bullets removed, muted meta text, spacing). Non-essential — the page renders correctly without it.

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

- **Add a city** by editing `_data/cities.yml` only — the events partial picks it up with no template change.
- **Change how an event displays** by editing `_includes/event-card.html`; restyle via `assets/main.scss`.
- **Add pages** by creating more `.md` / `.html` files with front matter at the root or in subfolders.
- **Add a plugin** only from GitHub Pages' [supported plugin list](https://pages.github.com/versions/); anything outside it requires switching to a GitHub Actions build workflow.
