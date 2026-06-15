# Jekyll site

> **TL;DR** — The whole repository is one minimal Jekyll site: a config file, a homepage, a Gemfile, and a gitignore.

> **Purpose** — Document each source file of the site and what it controls.
> **Key files** — `_config.yml`, `index.md`, `Gemfile`, `.gitignore`, `README.md`.
> **Depends on** — Jekyll + the `minima` theme via the `github-pages` gem. **Used by** — GitHub Pages' build.
> **Related** — [architecture.md](architecture.md) for the build/deploy flow, [glossary.md](glossary.md) for terms.

## Layout

Everything is flat at the repo root. There are no `_layouts/`, `_includes/`, `_posts/`, or asset directories — the site is intentionally empty, relying entirely on the `minima` theme's defaults.

## Source files

### `_config.yml`

Site-wide settings read by Jekyll at build time. It sets:

- `title` and `description` — site metadata surfaced by the theme.
- `theme: minima` — uses the default Jekyll theme, so no layouts are committed here.
- `url` and `baseurl` — configured for a **project site** at `https://keunwoopark.github.io/aiintown/`. The `/aiintown` path is the `baseurl`; see [architecture.md](architecture.md) for why this matters and what breaks if the repo becomes a user/organization site.

Changing `_config.yml` requires a build restart locally (Jekyll does not hot-reload config).

### `index.md`

The homepage. Its Jekyll **front matter** (`layout: home`, `title: Home`) tells the `minima` theme to wrap the body in the home layout. The body is a single placeholder line — the site is an empty starter.

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

- **Add pages** by creating more `.md` / `.html` files with front matter at the root or in subfolders.
- **Customize the theme** by overriding `minima` files (e.g. add `_layouts/`, `_includes/`, or `assets/`).
- **Add a plugin** only from GitHub Pages' [supported plugin list](https://pages.github.com/versions/); anything outside it requires switching to a GitHub Actions build workflow.
