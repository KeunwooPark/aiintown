import json, hashlib, datetime, pathlib, yaml
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

MODEL = "claude-sonnet-4-5"
DATA = pathlib.Path("_data")
EVENTS_DIR = DATA / "events"
RUN_DATE = datetime.date.today()
RUN_DATE_STR = RUN_DATE.isoformat()

GLOBAL_EVENT_PLATFORMS = ["Luma", "Eventbrite", "Meetup"]
EXISTING_TITLE_LIMIT = 50

# Instantiated lazily in main() so test imports don't require ANTHROPIC_API_KEY.
client = None


def main():
    global client
    from anthropic import Anthropic
    client = Anthropic()

    cities = yaml.safe_load((DATA / "cities.yml").read_text())
    for city in cities:
        if city.get("enabled", True):
            merge(city, search_city(city))


def search_city(city):
    prompt = (
        f"Today's date is {RUN_DATE_STR}. Find ONLY UPCOMING in-person/offline AI "
        f"events (meetups, conferences, talks) in {city['name']}, {city['country']} "
        f"happening on or after {RUN_DATE_STR}. Use web search. Do NOT include events "
        f"that have already finished. Return ONLY a JSON array; each item: title, "
        f"date (YYYY-MM-DD if known), venue, url, source, description, title_local, description_local."
    )
    language = city.get("language")
    if language:
        prompt += (
            f" Search the web in {language} as well as English, and read "
            f"{language}-language sources, so you also catch locally-indexed events."
            f" For title_local and description_local, give the title and description"
            f" written in {language} (copy them verbatim if the event is already in {language})."
        )
    prompt += (
        " Include small, grassroots and community events (university clubs, "
        "coworking spaces, local meetup/community sites and venues), in addition "
        "to — not instead of — larger conferences and international events."
    )
    local = city.get("event_platforms", [])
    platforms = GLOBAL_EVENT_PLATFORMS + local
    prompt += (
        " In addition to general web search, also check dedicated event-listing "
        f"platforms such as {', '.join(platforms)} for matching events."
    )
    hints = city.get("query_hints", [])
    if hints:
        prompt += f" If you find relevant events, focus on topics: {', '.join(hints)}."
    prompt += (
        " Return each DISTINCT event only ONCE: do not list the same event multiple"
        " times under different title phrasings or from different sources. Use the"
        " event's primary/official page as `url`; if several sources describe the same"
        " event, merge them into a single item with the best title and that canonical URL."
    )
    known = _existing_event_entries(city)
    if known:
        listing = "; ".join(f"{t} — {u}" if u else t for t, u in known)
        prompt += (
            " We already have these events on file (title — url): " + listing +
            ". Prioritize discovering ADDITIONAL upcoming events that are NOT already"
            " in this list (match by URL as well as title); focus on new, smaller, or"
            " recently-announced events beyond the ones above."
        )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8000,  # was 4000 — avoid truncating large JSON arrays into parse failures
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],  # was max_uses: 5
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return parse_json_array(text)


def _combine(a, b):
    """Pick the canonical record when a and b collide; keep widest seen-window."""
    def known(r):
        return r.get("date_status") != "unknown" and bool(r.get("date"))
    if known(a) != known(b):
        keep = a if known(a) else b
    elif len(a.get("description", "")) != len(b.get("description", "")):
        keep = a if len(a.get("description", "")) > len(b.get("description", "")) else b
    else:
        keep = a if a.get("title", "") <= b.get("title", "") else b
    keep = dict(keep)
    fs = [r.get("first_seen") for r in (a, b) if r.get("first_seen")]
    ls = [r.get("last_seen") for r in (a, b) if r.get("last_seen")]
    if fs:
        keep["first_seen"] = min(fs)
    if ls:
        keep["last_seen"] = max(ls)
    return keep


def merge(city, found):
    path = EVENTS_DIR / f"{city['id']}.json"
    existing = json.loads(path.read_text()) if path.exists() else []

    by_id = {}
    for e in existing:
        e = {**e, "city": e.get("city", city["id"])}
        eid = event_id(e)
        by_id[eid] = _combine(by_id[eid], e) if eid in by_id else e

    for raw in found:
        if not is_upcoming(raw.get("date")):
            continue
        e = {**raw, "city": city["id"]}
        _apply_date_status(e)
        eid = event_id(e)
        if eid in by_id:
            prev = by_id[eid]
            survivor = _combine(prev, {**e, "first_seen": prev.get("first_seen", RUN_DATE_STR),
                                       "last_seen": RUN_DATE_STR})
            survivor["first_seen"] = min(prev.get("first_seen", RUN_DATE_STR), RUN_DATE_STR)
            survivor["last_seen"] = RUN_DATE_STR
            by_id[eid] = survivor
        else:
            e["first_seen"] = e["last_seen"] = RUN_DATE_STR
            by_id[eid] = e

    records = sorted(by_id.values(), key=lambda x: (x.get("date") or "9999", x["title"]))
    # The rendered site and downstream data files key on `id`, so every written record must carry it.
    for eid, rec in by_id.items():
        rec["id"] = eid
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")


# --- helpers ---

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src",
}


def normalize_url(url):
    """Canonical, comparable form of a URL, or '' if there is no usable URL.
    Collapses http/https, leading www., trailing slash, fragment, tracking params."""
    if not url or not isinstance(url, str):
        return ""
    u = url.strip()
    if not u:
        return ""
    if "://" not in u:
        u = "https://" + u
    parts = urlsplit(u)
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path.rstrip("/")
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if k.lower() not in TRACKING_PARAMS]
    query = urlencode(sorted(kept))
    if not host:
        return ""
    # scheme intentionally dropped so http/https compare equal
    return urlunsplit(("", host, path, query, ""))


def event_id(e):
    url = normalize_url(e.get("url"))
    if url:
        key = f"url|{url}|{e['city']}"
    else:
        key = f"{e['title'].strip().lower()}|{e.get('date', '')}|{e['city']}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def is_upcoming(date_str):
    if not date_str:
        return True
    try:
        return datetime.date.fromisoformat(date_str[:10]) >= RUN_DATE
    except ValueError:
        return True


def _existing_event_entries(city, limit=EXISTING_TITLE_LIMIT):
    """Return up to `limit` (title, url) pairs for upcoming events already stored for this city."""
    city_id = city.get("id")
    if not city_id:
        return []
    path = EVENTS_DIR / f"{city_id}.json"
    if not path.exists():
        return []
    try:
        records = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    out = [(r["title"], r.get("url", "")) for r in records
           if isinstance(r, dict) and r.get("title") and is_upcoming(r.get("date"))]
    return out[:limit]


def _apply_date_status(e):
    """Mark events whose date cannot be parsed so consumers can surface uncertainty."""
    date_str = e.get("date")
    if not date_str:
        e["date_status"] = "unknown"
        return
    try:
        datetime.date.fromisoformat(date_str[:10])
        # Valid date — no date_status annotation needed.
    except ValueError:
        e["date_status"] = "unknown"


def parse_json_array(text):
    """Extract a JSON array from model output that may contain prose or fenced blocks.

    Returns [] rather than raising when the text cannot be parsed as an array.
    Items missing a 'title' key are silently dropped.
    """
    candidate = _extract_json_candidate(text)
    if candidate is None:
        return []
    try:
        result = json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        return []
    if not isinstance(result, list):
        return []
    return [item for item in result if isinstance(item, dict) and "title" in item]


def _extract_json_candidate(text):
    """Return the best JSON array substring from text, or None."""
    # Prefer content inside a fenced ```json ... ``` block.
    fenced = _extract_fenced_block(text)
    if fenced is not None:
        return fenced

    # Fall back to the first '[' ... last ']' span in the raw text.
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end > start:
        return text[start : end + 1]

    return None


def _extract_fenced_block(text):
    """Return the content of the first ```json ... ``` block, or None."""
    fence_open = text.find("```json")
    if fence_open == -1:
        fence_open = text.find("```")
    if fence_open == -1:
        return None
    content_start = text.find("\n", fence_open)
    if content_start == -1:
        return None
    fence_close = text.find("```", content_start)
    if fence_close == -1:
        return None
    return text[content_start:fence_close].strip()


if __name__ == "__main__":
    main()
