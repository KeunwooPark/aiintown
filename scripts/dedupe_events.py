"""One-time/manual cleanup: collapse duplicate event records in _data/events/*.json
using the same merge()/event_id() logic as the daily run.

Usage: python scripts/dedupe_events.py
"""
import json
import yaml
from scripts import search_events as se


def main():
    cities = yaml.safe_load((se.DATA / "cities.yml").read_text())
    for city in cities:
        path = se.EVENTS_DIR / f"{city['id']}.json"
        if not path.exists():
            continue
        before = len(json.loads(path.read_text()))
        se.merge(city, [])          # re-index + collapse existing, no new events
        after = len(json.loads(path.read_text()))
        print(f"{city['id']}: {before} -> {after}")


if __name__ == "__main__":
    main()
