/**
 * Tests for stripMarkdown — uses Node's built-in node:test runner (no extra
 * test dependencies). Run with: npm test  (-> node --test src/strip-markdown.test.js)
 *
 * The citedEvents case imports the real function from index.js to confirm the
 * Worker's citation matching still works on the stripped answer end-to-end.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { stripMarkdown } from "./strip-markdown.js";
import { citedEvents } from "./index.js";

test("bold/italic/strikethrough emphasis is removed, text kept", () => {
  assert.strictEqual(
    stripMarkdown("**bold** and *italic* and ***both***"),
    "bold and italic and both"
  );
  assert.strictEqual(stripMarkdown("__bold__ and _italic_"), "bold and italic");
  assert.strictEqual(stripMarkdown("~~struck~~"), "struck");
});

test("headings become plain text", () => {
  assert.strictEqual(stripMarkdown("# Heading"), "Heading");
  assert.strictEqual(stripMarkdown("### Sub heading"), "Sub heading");
  assert.strictEqual(
    stripMarkdown("# Heading\n\nBody text"),
    "Heading\n\nBody text"
  );
});

test("unordered list markers are removed, items kept on their own lines", () => {
  assert.strictEqual(stripMarkdown("- one\n- two\n- three"), "one\ntwo\nthree");
  assert.strictEqual(stripMarkdown("* a\n* b"), "a\nb");
});

test("ordered list markers are removed", () => {
  assert.strictEqual(stripMarkdown("1. first\n2. second"), "first\nsecond");
});

test("link keeps label only and drops the URL", () => {
  assert.strictEqual(
    stripMarkdown("Visit [the site](https://example.com) now."),
    "Visit the site now."
  );
  assert.strictEqual(
    stripMarkdown("- [AI Summit](https://x.com)\n- [ML Meetup](https://y.com)"),
    "AI Summit\nML Meetup"
  );
});

test("inline code and code fences keep their text, drop backticks/fence", () => {
  assert.strictEqual(
    stripMarkdown("Use `npm install` to add it."),
    "Use npm install to add it."
  );
  assert.strictEqual(
    stripMarkdown("```python\nx = 1\nprint(x)\n```"),
    "x = 1\nprint(x)"
  );
});

test("blockquotes drop the > marker", () => {
  assert.strictEqual(
    stripMarkdown("> quoted text\n> second line"),
    "quoted text\nsecond line"
  );
});

test("hard line breaks are preserved as newlines", () => {
  assert.strictEqual(stripMarkdown("Line one  \nLine two"), "Line one\nLine two");
});

test("image keeps alt text and drops the URL", () => {
  assert.strictEqual(stripMarkdown("![alt text](img.png)"), "alt text");
});

test("table becomes space-separated plain rows", () => {
  assert.strictEqual(
    stripMarkdown("| A | B |\n|---|---|\n| 1 | 2 |"),
    "A  B\n1  2"
  );
});

test("plain text without markdown passes through unchanged", () => {
  assert.strictEqual(stripMarkdown("plain text no markdown"), "plain text no markdown");
});

test("empty / nullish input returns an empty string", () => {
  assert.strictEqual(stripMarkdown(""), "");
  assert.strictEqual(stripMarkdown(null), "");
});

test("raw < > & are preserved (no HTML entity round-trip)", () => {
  assert.strictEqual(
    stripMarkdown("A > B and C < D and AT&T"),
    "A > B and C < D and AT&T"
  );
});

test("paragraphs stay separated by a blank line", () => {
  assert.strictEqual(
    stripMarkdown("First paragraph.\n\nSecond paragraph."),
    "First paragraph.\n\nSecond paragraph."
  );
});

test("citedEvents still matches event titles on the stripped answer", () => {
  const events = [
    { id: "1", title: "AI Summit 2024", date: "2024-06-01", venue: "Hall", url: "https://x", city: "berlin" },
    { id: "2", title: "ML Meetup", date: "2024-07-01", venue: "Cafe", url: "https://y", city: "seoul" },
  ];
  const stripped = stripMarkdown(
    "Check out **AI Summit 2024** and [ML Meetup](https://y)."
  );
  const cited = citedEvents(stripped, events);
  assert.deepEqual(
    cited.map((e) => e.title),
    ["AI Summit 2024", "ML Meetup"]
  );
});
