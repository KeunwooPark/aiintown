# AI event search

> **TL;DR** — A scheduled GitHub Actions job runs a Python script that asks Claude (with web search) for upcoming offline AI events per city and commits the results as per-city JSON under `_data/events/`.

> **Purpose** — Periodically discover upcoming in-person AI events for a configurable list of cities and store them as committed data files.
> **Key files** — `_data/cities.yml`, `scripts/search_events.py`, `scripts/requirements.txt`, `.github/workflows/search-ai-events.yml`, `scripts/test_search_events.py`.
> **Depends on** — the Anthropic Messages API + its server-side `web_search` tool (`ANTHROPIC_API_KEY` secret); GitHub Actions. **Used by** — the Jekyll site, which renders the JSON on the homepage (see [components/site.md](components/site.md)).
> **Related** — [architecture.md](architecture.md) for how this sits beside the Pages build, [glossary.md](glossary.md) for terms.

## The one core idea

This subsystem **generates data, not pages**. A daily job collects events with an LLM and commits them into the repo as `_data/events/<city-id>.json`. Because the files live in Jekyll's `_data/` directory, the site renders them at build time via `_layouts/home.html` (see [components/site.md](components/site.md)) — this subsystem stays focused on producing clean data. The search is deliberately scoped to *upcoming* events; finished events are never written.

## The four parts

### `_data/cities.yml` — the input

The single human-editable source of truth for which cities to search. It is a YAML list; each entry has `id` (slug used as the output filename), `name`, `country`, `enabled`, an optional `language` (a human-readable name like `Korean` or `German`, no locale codes), and optional `query_hints` (keywords injected into the prompt). Adding or removing a city is a pure data edit — no code change — and the script iterates every entry where `enabled` is not `false`.

`language` drives a local-language search instruction in the prompt (see the worker below), and `query_hints` mixes English topic/format terms with local-language general keywords (e.g. Seoul carries `밋업`/`세미나`, Berlin carries `Treffen`/`Vortrag`) so coverage broadens rather than shifts. The hints stay topic-/format-focused; language selection lives in the dedicated `language` field, not in `query_hints`.

### `scripts/search_events.py` — the worker

For each enabled city the script builds a prompt, calls Claude, parses the response, filters, and merges into the city's JSON file. The important design points:

- **Web search is mandatory.** The request passes the `web_search_20250305` server-side tool (name `web_search`, `max_uses: 5`). Without it Claude cannot browse and would hallucinate events. `MODEL` is pinned in one constant (`claude-sonnet-4-5`).
- **Run-date-scoped prompt.** `RUN_DATE` (today) is interpolated into the prompt, which instructs Claude to return *only* upcoming, in-person AI events on or after that date as a JSON array of `title`, `date`, `venue`, `url`, `source`, `description`.
- **Localized, community-aware prompt.** When a city defines `language`, `search_city` appends a sentence telling Claude to also search the web and read sources in that language (in addition to English) to catch locally-indexed events; the sentence is skipped when `language` is absent, keeping the prompt back-compatible. A further sentence — added for every city — tells Claude to include small, grassroots, and community events (university clubs, coworking spaces, local meetup/community sites and venues) *in addition to, not instead of,* larger conferences and international events. The output schema, `web_search` config, and `parse_json_array` handling are unchanged, so non-ASCII titles still round-trip via the `ensure_ascii=False` write path.
- **Lazy client.** The `Anthropic()` client is created inside `main()`, not at import, so the test suite can import the module without `ANTHROPIC_API_KEY`.
- **Defensive parsing.** `parse_json_array` extracts the array from possibly-prose output — preferring a fenced ```` ```json ```` block, else the first `[` … last `]` span — and returns `[]` (never raises) on malformed output, dropping any item lacking a `title`. This is what keeps a bad LLM response from corrupting the data files.
- **Code-level upcoming guard.** `is_upcoming` drops events whose parseable `date` is strictly before `RUN_DATE`, but *keeps* events with missing/unparseable dates (they could still be upcoming). `_apply_date_status` tags those kept-but-undated events with `date_status: "unknown"` so consumers can surface the uncertainty.
- **Dedupe + history merge.** `event_id` is a 16-char SHA-1 of normalized `title|date|city`. `merge` loads the existing file, keys records by `id`, updates `last_seen` on a hit and sets `first_seen`/`last_seen` on a new record, then writes the array sorted by `(date, title)`. Re-running with identical results produces no duplicates and preserves the original `first_seen`.

`scripts/requirements.txt` pins the two runtime deps (`anthropic`, `PyYAML`). `scripts/test_search_events.py` unit-tests the pure helpers (`is_upcoming`, parsing, merge) without network or API key.

### `.github/workflows/search-ai-events.yml` — the schedule

A GitHub Actions workflow triggered daily by `schedule` (cron `17 3 * * *`) and on demand via `workflow_dispatch`. It checks out the repo, sets up Python 3.12, installs `scripts/requirements.txt`, runs the script with `ANTHROPIC_API_KEY` from `secrets`, then commits any change under `_data/events/` back to `main` (the commit is skipped when `git diff --cached --quiet` finds no diff). The job needs `permissions: contents: write` to push.

### `_data/events/<city-id>.json` — the output

One JSON array per city, generated by the script. Each record's shape is documented in the repo `README.md`. These files are the deliverable, and the site's `_includes/event-card.html` reads exactly these field names (`title`, `date`, `venue`, `url`, `source`, `description`, `date_status`).

## Gotchas and constraints

- **Web search is billed.** Every daily run consumes Anthropic API credits; the tool counts toward usage.
- **Undated noise persists.** Keeping events with vague/missing dates avoids losing real ones but means some non-upcoming clutter (flagged `date_status: "unknown"`) can remain.
- **No retroactive pruning.** Only *new* past events are filtered at write time; events already stored stay as accumulated history even after their date passes.
- **Push to `main` needs write access.** If branch protection is enabled on `main`, the commit step fails and the workflow/permissions must be adjusted.
- **Cron is best-effort.** GitHub Actions `schedule` can be delayed under load and is auto-disabled after ~60 days of repo inactivity.

## Extension points

- **Add/remove cities** by editing `_data/cities.yml` only.
- **Change the model or search budget** via the `MODEL` constant and the tool's `max_uses`.
- **Adjust how events render** in the Jekyll layer — `_layouts/home.html` / `_includes/event-card.html` (see [components/site.md](components/site.md)).
