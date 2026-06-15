# aiintown

A site served with GitHub Pages using Jekyll and the Minima theme.

## Enabling GitHub Pages

GitHub Pages must be turned on manually once in the repository settings — there is no code or config that does this automatically.

1. Go to **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment**, set Source to **Deploy from a branch**.
3. Set the branch to `main` and the folder to `/ (root)`, then click **Save**.

The site will not publish until this step is completed.

## Local preview

Install dependencies (requires [Bundler](https://bundler.io/)):

```
bundle install
```

Start a local server:

```
bundle exec jekyll serve
```

Because `baseurl` is set to `/aiintown`, the local site is available at:

```
http://localhost:4000/aiintown/
```

## AI event search

A GitHub Actions workflow (`search-ai-events`) runs `scripts/search_events.py` daily at 03:17 UTC and commits the results back to `_data/events/`.

### Secret requirement

The workflow calls the Anthropic API. Add `ANTHROPIC_API_KEY` as a repository secret under **Settings → Secrets and variables → Actions** before enabling the workflow. Web search is a billed Anthropic tool — each workflow run consumes API credits.

### Configuring cities

Edit `_data/cities.yml` to control which cities are searched. Each entry supports:

| Field | Description |
|-------|-------------|
| `id` | Short slug used as the output filename (e.g. `seoul` → `_data/events/seoul.json`) |
| `name` | City display name passed to the model |
| `country` | Country name passed to the model |
| `enabled` | Set to `false` to skip a city without removing it |
| `query_hints` | Keywords injected into the search prompt |

### Per-city event data shape

Results are stored in `_data/events/<city-id>.json` as a JSON array. Each record contains:

| Field | Description |
|-------|-------------|
| `id` | 16-character SHA-1 fingerprint of title + date + city |
| `title` | Event title |
| `date` | Date in `YYYY-MM-DD` format, if known |
| `city` | City `id` from `cities.yml` |
| `venue` | Venue name or address |
| `url` | Event URL |
| `source` | Where the information was found |
| `description` | Short event description |
| `first_seen` | ISO date of the run that first found this event |
| `last_seen` | ISO date of the most recent run that returned this event |
| `date_status` | `"unknown"` when the date is missing or unparseable; absent otherwise |

Search is scoped to upcoming events only — the script discards anything dated before the run date.

### Rendering events on the site

Displaying events on the Jekyll site is intentionally out of scope for now. The workflow is data-only; the JSON files are committed to the repository so a future template can consume them.
