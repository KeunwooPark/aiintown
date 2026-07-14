# aiintown

'AI in Town' is a website that collects and shows local offline meetups in various cities.

A site served with GitHub Pages using Jekyll and the Minima theme.

## How to contribute

If you want to add cities or ask for features, you can add sketches in the [FlumeCode repository](https://www.flumecode.work/repositories/26c6aa50-ba00-4b22-b371-fb4ccfe0fe0b) — sketches are lightweight proposals for new cities and feature ideas.

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
| `event_platforms` | Optional list of local/regional event-listing platforms for that city (added to the built-in global list of Luma, Eventbrite, Meetup that applies to every city) |

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

The committed JSON is consumed two ways:

- **Per-city pages** (`/cities/<id>/`) render the events as cards, sorted by date.
- **The home page** is an "Ask about AI events" interface (see below) that answers natural-language questions from the same data.

## Ask about AI events (question interface)

The home page lets visitors ask questions in plain language ("Any AI meetups in Seoul this summer?") and get an answer grounded in the committed events data. There is **no database and no embeddings** — the whole dataset is small enough to hand to Claude in one call ("context stuffing"), which is simpler and more accurate than RAG at this scale.

Because GitHub Pages is static and can't safely hold an API key, the Claude call runs in a small **Cloudflare Worker** (`worker/`). The browser POSTs the question to the Worker; the Worker loads the events JSON from GitHub, calls the Anthropic API, and returns a grounded answer plus the events it cited.

### Deploying the Worker

Prerequisites: a [Cloudflare account](https://dash.cloudflare.com/) and [Wrangler](https://developers.cloudflare.com/workers/wrangler/) (`npm install -g wrangler`, then `wrangler login`).

```
cd worker
npm install
wrangler secret put ANTHROPIC_API_KEY   # paste your Anthropic API key when prompted
wrangler deploy
```

`wrangler deploy` prints the Worker URL (e.g. `https://aiintown-ask.<subdomain>.workers.dev`). Then wire the site to it:

1. In `_config.yml`, set `ask_endpoint` to that URL **plus `/api/ask`**, e.g.
   `ask_endpoint: "https://aiintown-ask.<subdomain>.workers.dev/api/ask"`
2. Commit and push so GitHub Pages rebuilds. Until `ask_endpoint` is set, the ask box shows a "not configured yet" message.

### Worker configuration (`worker/wrangler.toml`)

| Setting | Purpose |
|---------|---------|
| `ANTHROPIC_API_KEY` | **Secret** (set via `wrangler secret put`, never committed). Each question is one billed Claude call. |
| `ALLOWED_ORIGIN` | Site origin allowed to call the Worker via CORS. Defaults to `https://keunwoopark.github.io`. |
| `CITIES` | Comma-separated city ids to load (e.g. `berlin,seoul`). Add a city here after its JSON exists. |
| `EVENTS_BASE_URL` | Raw GitHub base URL for the events JSON. The Worker always fetches live data (edge-cached ~1h), so the daily pipeline stays untouched — no Worker redeploy needed when events change. |
| `MODEL` | Claude model id (default `claude-sonnet-5`). |
| `[[unsafe.bindings]]` RATE_LIMITER | Per-IP rate limit (default 20 requests / 60s). Remove the block to disable. |

### Cost

Each question is a single Anthropic API call that includes the full events dataset (~35k tokens) as input. On `claude-sonnet-5` that is inexpensive per call, but it is a public endpoint — keep the rate limiter enabled and monitor usage.

This project was made by [FlumeCode](https://www.flumecode.work).
