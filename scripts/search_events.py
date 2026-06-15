import json, hashlib, datetime, pathlib, yaml

MODEL = "claude-sonnet-4-5"
DATA = pathlib.Path("_data")
EVENTS_DIR = DATA / "events"
RUN_DATE = datetime.date.today()
RUN_DATE_STR = RUN_DATE.isoformat()

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
        f"date (YYYY-MM-DD if known), venue, url, source, description."
    )
    hints = city.get("query_hints", [])
    if hints:
        prompt += f" If you find relevant events, focus on topics: {', '.join(hints)}."
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return parse_json_array(text)


def merge(city, found):
    path = EVENTS_DIR / f"{city['id']}.json"
    existing = json.loads(path.read_text()) if path.exists() else []
    by_id = {e["id"]: e for e in existing}

    for raw in found:
        if not is_upcoming(raw.get("date")):
            continue
        e = {**raw, "city": city["id"]}
        e["id"] = event_id(e)
        _apply_date_status(e)
        if e["id"] in by_id:
            by_id[e["id"]]["last_seen"] = RUN_DATE_STR
        else:
            e["first_seen"] = e["last_seen"] = RUN_DATE_STR
            by_id[e["id"]] = e

    records = sorted(
        by_id.values(),
        key=lambda x: (x.get("date") or "9999", x["title"]),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")


# --- helpers ---

def event_id(e):
    key = f"{e['title'].strip().lower()}|{e.get('date', '')}|{e['city']}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def is_upcoming(date_str):
    if not date_str:
        return True
    try:
        return datetime.date.fromisoformat(date_str[:10]) >= RUN_DATE
    except ValueError:
        return True


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
