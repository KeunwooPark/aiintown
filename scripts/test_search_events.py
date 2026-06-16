"""Unit tests for search_events.py.

Importable without ANTHROPIC_API_KEY and without network access:
the module-level `client` in search_events is None until main() is called.
"""

import datetime
import json
import pathlib
import tempfile
import unittest
import unittest.mock
from types import SimpleNamespace
from unittest.mock import MagicMock

import scripts.search_events as se


class TestIsUpcoming(unittest.TestCase):
    def setUp(self):
        # Pin RUN_DATE so tests don't depend on the actual calendar day.
        self._orig = se.RUN_DATE
        se.RUN_DATE = datetime.date(2025, 6, 15)

    def tearDown(self):
        se.RUN_DATE = self._orig

    def test_future_date_is_upcoming(self):
        self.assertTrue(se.is_upcoming("2025-12-31"))

    def test_past_date_is_not_upcoming(self):
        self.assertFalse(se.is_upcoming("2025-01-01"))

    def test_empty_string_is_upcoming(self):
        self.assertTrue(se.is_upcoming(""))

    def test_none_is_upcoming(self):
        self.assertTrue(se.is_upcoming(None))

    def test_unparseable_date_is_upcoming(self):
        self.assertTrue(se.is_upcoming("not-a-date"))

    def test_same_day_is_upcoming(self):
        self.assertTrue(se.is_upcoming("2025-06-15"))


class TestNormalizeUrl(unittest.TestCase):
    def test_empty_and_none(self):
        self.assertEqual(se.normalize_url(""), "")
        self.assertEqual(se.normalize_url(None), "")

    def test_www_scheme_slash_tracking_fragment(self):
        a = se.normalize_url("http://www.Example.com/path/?utm_source=x#frag")
        b = se.normalize_url("https://example.com/path")
        self.assertEqual(a, b)


class TestEventIdUrl(unittest.TestCase):
    def test_same_url_different_title_same_id(self):
        a = {"title": "ICML 2026", "date": "2026-07-06", "city": "seoul", "url": "https://icml.cc/"}
        b = {"title": "International Conference on Machine Learning (ICML 2026)",
             "date": "2026-07-06", "city": "seoul", "url": "http://www.icml.cc"}
        self.assertEqual(se.event_id(a), se.event_id(b))

    def test_no_url_falls_back_to_title(self):
        a = {"title": "Meetup A", "date": "2025-07-01", "city": "seoul"}
        b = {"title": "Meetup B", "date": "2025-07-01", "city": "seoul"}
        self.assertNotEqual(se.event_id(a), se.event_id(b))


class TestEventId(unittest.TestCase):
    def _make(self, title, date, city):
        return {"title": title, "date": date, "city": city}

    def test_same_inputs_produce_same_hash(self):
        e = self._make("AI Meetup", "2025-07-01", "seoul")
        self.assertEqual(se.event_id(e), se.event_id(e))

    def test_different_titles_produce_different_hashes(self):
        a = self._make("Meetup A", "2025-07-01", "seoul")
        b = self._make("Meetup B", "2025-07-01", "seoul")
        self.assertNotEqual(se.event_id(a), se.event_id(b))

    def test_hash_is_16_chars(self):
        e = self._make("Test Event", "2025-08-01", "berlin")
        self.assertEqual(len(se.event_id(e)), 16)

    def test_title_stripped_and_lowercased(self):
        a = self._make("  AI Meetup  ", "2025-07-01", "seoul")
        b = self._make("ai meetup", "2025-07-01", "seoul")
        self.assertEqual(se.event_id(a), se.event_id(b))


class TestParseJsonArray(unittest.TestCase):
    def test_plain_json_array(self):
        text = '[{"title": "Foo", "date": "2025-07-01"}]'
        result = se.parse_json_array(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Foo")

    def test_fenced_json_block(self):
        text = 'Here are the events:\n```json\n[{"title": "Bar"}]\n```\nDone.'
        result = se.parse_json_array(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Bar")

    def test_surrounding_prose(self):
        text = 'Sure! Here you go: [{"title": "Baz"}] That is all.'
        result = se.parse_json_array(text)
        self.assertEqual(len(result), 1)

    def test_item_missing_title_is_skipped(self):
        text = '[{"date": "2025-07-01"}, {"title": "Good"}]'
        result = se.parse_json_array(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Good")

    def test_totally_malformed_returns_empty(self):
        self.assertEqual(se.parse_json_array("not json at all"), [])

    def test_empty_string_returns_empty(self):
        self.assertEqual(se.parse_json_array(""), [])

    def test_object_instead_of_array_returns_empty(self):
        self.assertEqual(se.parse_json_array('{"title": "Solo"}'), [])

    def test_multiple_items_all_with_title(self):
        text = '[{"title": "A"}, {"title": "B"}, {"title": "C"}]'
        result = se.parse_json_array(text)
        self.assertEqual(len(result), 3)


class TestMerge(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()

        patcher_events_dir = unittest.mock.patch.object(
            se, "EVENTS_DIR", pathlib.Path(self._tmpdir)
        )
        patcher_run_date = unittest.mock.patch.object(
            se, "RUN_DATE", datetime.date(2025, 6, 15)
        )
        patcher_run_date_str = unittest.mock.patch.object(
            se, "RUN_DATE_STR", "2025-06-15"
        )

        patcher_events_dir.start()
        patcher_run_date.start()
        patcher_run_date_str.start()

        self.addCleanup(patcher_events_dir.stop)
        self.addCleanup(patcher_run_date.stop)
        self.addCleanup(patcher_run_date_str.stop)

    def _city(self, city_id="seoul"):
        return {"id": city_id, "name": "Seoul", "country": "South Korea"}

    def _event(self, title="AI Meetup", date="2025-07-01"):
        # No URL so dedup falls back to title-based keying; use _event_url() for URL tests.
        return {"title": title, "date": date, "venue": "HQ",
                "source": "web", "description": "Great event"}

    def _load(self, city_id="seoul"):
        path = se.EVENTS_DIR / f"{city_id}.json"
        return json.loads(path.read_text())

    def test_first_run_sets_first_seen_and_last_seen(self):
        city = self._city()
        se.merge(city, [self._event()])
        records = self._load()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_seen"], "2025-06-15")
        self.assertEqual(records[0]["last_seen"], "2025-06-15")

    def test_second_run_updates_last_seen_only(self):
        city = self._city()
        se.merge(city, [self._event()])
        # Advance date for the second run.
        se.RUN_DATE = datetime.date(2025, 6, 20)
        se.RUN_DATE_STR = "2025-06-20"
        se.merge(city, [self._event()])
        records = self._load()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_seen"], "2025-06-15")
        self.assertEqual(records[0]["last_seen"], "2025-06-20")

    def test_no_duplicates_on_identical_rerun(self):
        city = self._city()
        se.merge(city, [self._event()])
        se.merge(city, [self._event()])
        records = self._load()
        self.assertEqual(len(records), 1)

    def test_past_dated_event_is_dropped(self):
        city = self._city()
        se.merge(city, [self._event(date="2025-01-01")])
        records = self._load()
        self.assertEqual(len(records), 0)

    def test_new_event_on_second_run_is_added(self):
        city = self._city()
        se.merge(city, [self._event("Event A")])
        se.merge(city, [self._event("Event B")])
        records = self._load()
        titles = {r["title"] for r in records}
        self.assertIn("Event A", titles)
        self.assertIn("Event B", titles)

    def test_date_status_unknown_when_date_missing(self):
        city = self._city()
        event = self._event()
        del event["date"]
        se.merge(city, [event])
        records = self._load()
        self.assertEqual(records[0].get("date_status"), "unknown")

    def test_date_status_unknown_when_date_unparseable(self):
        city = self._city()
        event = self._event(date="TBD")
        se.merge(city, [event])
        records = self._load()
        self.assertEqual(records[0].get("date_status"), "unknown")

    def test_date_status_not_unknown_when_date_valid(self):
        city = self._city()
        se.merge(city, [self._event(date="2025-09-01")])
        records = self._load()
        self.assertNotEqual(records[0].get("date_status"), "unknown")

    def test_records_sorted_by_date_then_title(self):
        city = self._city()
        events = [
            self._event("Zebra Event", "2025-08-01"),
            self._event("Alpha Event", "2025-08-01"),
            self._event("Early Event", "2025-07-01"),
        ]
        se.merge(city, events)
        records = self._load()
        self.assertEqual(records[0]["title"], "Early Event")
        self.assertEqual(records[1]["title"], "Alpha Event")
        self.assertEqual(records[2]["title"], "Zebra Event")

    def test_local_fields_preserved(self):
        e = self._event()
        e["title_local"] = "서울 AI 밋업"
        e["description_local"] = "훌륭한 행사"
        se.merge(self._city(), [e])
        rec = self._load()[0]
        self.assertEqual(rec["title_local"], "서울 AI 밋업")
        self.assertEqual(rec["description_local"], "훌륭한 행사")

    def _event_url(self, title, url, date="2025-07-01"):
        return {"title": title, "date": date, "venue": "HQ", "url": url,
                "source": "web", "description": "x"}

    def test_url_duplicates_collapse_in_found(self):
        city = self._city()
        se.merge(city, [self._event_url("ICML A", "https://icml.cc/"),
                        self._event_url("ICML (B)", "http://www.icml.cc")])
        self.assertEqual(len(self._load()), 1)

    def test_existing_url_duplicates_collapse_on_load(self):
        city = self._city()
        se.merge(city, [self._event_url("ICML A", "https://icml.cc/")])
        se.RUN_DATE_STR = "2025-06-20"
        se.merge(city, [self._event_url("ICML (B)", "http://www.icml.cc")])
        se.merge(city, [])
        recs = self._load()
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["first_seen"], "2025-06-15")
        self.assertEqual(recs[0]["last_seen"], "2025-06-20")

    def test_merge_returns_counts_for_new_events(self):
        counts = se.merge(self._city(), [self._event()])
        self.assertEqual(counts["fetched"], 1)
        self.assertEqual(counts["new"], 1)
        self.assertEqual(counts["duplicates"], 0)
        self.assertEqual(counts["skipped_past"], 0)

    def test_merge_counts_duplicates_on_rerun(self):
        se.merge(self._city(), [self._event()])
        counts = se.merge(self._city(), [self._event()])
        self.assertEqual(counts["new"], 0)
        self.assertEqual(counts["duplicates"], 1)

    def test_merge_counts_skipped_past(self):
        counts = se.merge(self._city(), [self._event(date="2025-01-01")])
        self.assertEqual(counts["skipped_past"], 1)
        self.assertEqual(counts["new"], 0)


class TestWriteRunLog(unittest.TestCase):
    def setUp(self):
        self._tmpdir = pathlib.Path(tempfile.mkdtemp())

        patcher_logs_dir = unittest.mock.patch.object(
            se, "LOGS_DIR", self._tmpdir
        )
        patcher_run_log = unittest.mock.patch.object(
            se, "RUN_LOG", self._tmpdir / "search_runs.jsonl"
        )
        patcher_run_date_str = unittest.mock.patch.object(
            se, "RUN_DATE_STR", "2025-06-15"
        )

        patcher_logs_dir.start()
        patcher_run_log.start()
        patcher_run_date_str.start()

        self.addCleanup(patcher_logs_dir.stop)
        self.addCleanup(patcher_run_log.stop)
        self.addCleanup(patcher_run_date_str.stop)

    def _city_counts(self, city, fetched, new, duplicates, skipped_past):
        return {
            "city": city,
            "fetched": fetched,
            "new": new,
            "duplicates": duplicates,
            "skipped_past": skipped_past,
        }

    @unittest.mock.patch("builtins.print")
    def test_success_path_writes_valid_json_line(self, _mock_print):
        per_city = [
            self._city_counts("seoul", fetched=3, new=1, duplicates=2, skipped_past=0),
            self._city_counts("berlin", fetched=5, new=3, duplicates=1, skipped_past=1),
        ]
        se.write_run_log(per_city)

        lines = se.RUN_LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)

        entry = json.loads(lines[0])
        self.assertEqual(entry["run_date"], "2025-06-15")
        self.assertEqual(entry["cities"], per_city)
        self.assertEqual(entry["totals"]["fetched"], 8)
        self.assertEqual(entry["totals"]["new"], 4)
        self.assertEqual(entry["totals"]["duplicates"], 3)
        self.assertEqual(entry["totals"]["skipped_past"], 1)

    @unittest.mock.patch("builtins.print")
    def test_append_behavior_two_calls_produce_two_lines(self, _mock_print):
        per_city = [self._city_counts("seoul", fetched=2, new=2, duplicates=0, skipped_past=0)]
        se.write_run_log(per_city)
        se.write_run_log(per_city)

        lines = se.RUN_LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        # Both lines must be valid JSON.
        for line in lines:
            json.loads(line)

    @unittest.mock.patch("builtins.print")
    def test_empty_per_city_totals_are_all_zero(self, _mock_print):
        se.write_run_log([])

        lines = se.RUN_LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)

        entry = json.loads(lines[0])
        self.assertEqual(entry["cities"], [])
        self.assertEqual(entry["totals"]["fetched"], 0)
        self.assertEqual(entry["totals"]["new"], 0)
        self.assertEqual(entry["totals"]["duplicates"], 0)
        self.assertEqual(entry["totals"]["skipped_past"], 0)


class TestSearchCity(unittest.TestCase):
    def setUp(self):
        self._orig_client = se.client
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(
            content=[SimpleNamespace(type="text", text="[]")]
        )
        se.client = mock_client

    def tearDown(self):
        se.client = self._orig_client

    def test_prompt_includes_global_and_local_platforms(self):
        city = {
            "name": "Seoul",
            "country": "South Korea",
            "event_platforms": ["Onoffmix"],
        }
        se.search_city(city)
        prompt = se.client.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Luma", prompt)
        self.assertIn("Eventbrite", prompt)
        self.assertIn("Meetup", prompt)
        self.assertIn("Onoffmix", prompt)

    def test_prompt_without_local_platforms_is_valid(self):
        city = {"name": "Berlin", "country": "Germany"}
        se.search_city(city)
        prompt = se.client.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Luma", prompt)
        self.assertIn("Eventbrite", prompt)
        self.assertIn("Meetup", prompt)

    def test_prompt_includes_existing_titles_when_file_present(self):
        tmp = tempfile.mkdtemp()
        with unittest.mock.patch.object(se, "EVENTS_DIR", pathlib.Path(tmp)):
            (pathlib.Path(tmp) / "seoul.json").write_text(json.dumps([
                {"title": "Existing Gathering", "date": "2099-01-01", "city": "seoul"}
            ]))
            se.search_city({"id": "seoul", "name": "Seoul", "country": "South Korea"})
        prompt = se.client.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Existing Gathering", prompt)
        self.assertIn("ADDITIONAL", prompt)

    def test_prompt_includes_local_fields_when_language_set(self):
        se.search_city({"name": "Seoul", "country": "South Korea", "language": "Korean"})
        prompt = se.client.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("title_local", prompt)
        self.assertIn("description_local", prompt)

    def test_prompt_instructs_single_event_per_url(self):
        se.search_city({"name": "Seoul", "country": "South Korea"})
        prompt = se.client.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("only ONCE", prompt)


if __name__ == "__main__":
    unittest.main()
