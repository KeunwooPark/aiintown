/**
 * AI in Town — "Ask about AI events" Worker
 *
 * A single endpoint, POST /api/ask, that answers natural-language questions
 * about upcoming AI events. There is no database and no embeddings: the whole
 * events dataset (~a few hundred KB) is small enough to hand to Claude in one
 * call ("context stuffing"), which is simpler and more accurate than RAG at
 * this scale.
 *
 * Flow:
 *   1. Fetch each city's events JSON from GitHub (cached at the edge).
 *   2. Build a grounded prompt that forbids answering outside the data.
 *   3. Call the Anthropic Messages API and return the answer + cited events.
 *
 * Configuration (wrangler vars / secrets):
 *   ANTHROPIC_API_KEY  (secret, required)  — set via `wrangler secret put`
 *   ALLOWED_ORIGIN     (var)   — the site origin allowed to call this Worker
 *   CITIES             (var)   — comma-separated city ids to load
 *   EVENTS_BASE_URL    (var)   — raw base URL for the events JSON files
 *   MODEL              (var)   — Claude model id
 */

const DEFAULTS = {
  ALLOWED_ORIGIN: "https://keunwoopark.github.io",
  CITIES: "berlin,seoul",
  EVENTS_BASE_URL:
    "https://raw.githubusercontent.com/KeunwooPark/aiintown/main/_data/events",
  MODEL: "claude-sonnet-5",
};

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
const MAX_QUESTION_CHARS = 500;
const EVENTS_CACHE_TTL = 3600; // seconds

const LANG_NAMES = { en: "English", ko: "Korean", de: "German" };

export default {
  async fetch(request, env, ctx) {
    const cfg = { ...DEFAULTS, ...env };
    const cors = corsHeaders(cfg.ALLOWED_ORIGIN);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return json({ error: "Method not allowed" }, 405, cors);
    }

    const url = new URL(request.url);
    if (url.pathname !== "/api/ask") {
      return json({ error: "Not found" }, 404, cors);
    }

    // Optional per-IP rate limit (Cloudflare Rate Limiting binding).
    if (env.RATE_LIMITER) {
      const ip = request.headers.get("cf-connecting-ip") || "anon";
      const { success } = await env.RATE_LIMITER.limit({ key: ip });
      if (!success) {
        return json(
          { error: "Rate limit exceeded. Please wait a moment and try again." },
          429,
          cors
        );
      }
    }

    // Parse and validate the question.
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "Invalid JSON body" }, 400, cors);
    }
    const question = (body.question || "").toString().trim();
    const lang = LANG_NAMES[body.lang] ? body.lang : "en";
    if (!question) {
      return json({ error: "Please enter a question." }, 400, cors);
    }
    if (question.length > MAX_QUESTION_CHARS) {
      return json(
        { error: `Question is too long (max ${MAX_QUESTION_CHARS} characters).` },
        400,
        cors
      );
    }

    if (!env.ANTHROPIC_API_KEY) {
      return json({ error: "Server is not configured." }, 500, cors);
    }

    // Load events (edge-cached).
    let events;
    try {
      events = await loadEvents(cfg, ctx);
    } catch (err) {
      return json({ error: "Could not load event data." }, 502, cors);
    }

    // Ask Claude.
    try {
      const answer = await askClaude(env.ANTHROPIC_API_KEY, cfg.MODEL, {
        question,
        lang,
        events,
      });
      return json({ answer, events: citedEvents(answer, events) }, 200, cors);
    } catch (err) {
      return json(
        { error: "The assistant is unavailable right now. Please try again." },
        502,
        cors
      );
    }
  },
};

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function json(data, status, extraHeaders) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...extraHeaders },
  });
}

/**
 * Fetch and merge each city's events array from GitHub, using the Cloudflare
 * cache so we don't hit GitHub on every request. The daily pipeline keeps the
 * source JSON fresh, so nothing here needs a redeploy when events change.
 */
async function loadEvents(cfg, ctx) {
  const cities = cfg.CITIES.split(",")
    .map((c) => c.trim())
    .filter(Boolean);

  const all = [];
  for (const city of cities) {
    const src = `${cfg.EVENTS_BASE_URL}/${city}.json`;
    const cacheKey = new Request(src);
    const cache = caches.default;

    let resp = await cache.match(cacheKey);
    if (!resp) {
      resp = await fetch(src, {
        cf: { cacheTtl: EVENTS_CACHE_TTL, cacheEverything: true },
      });
      if (resp.ok) {
        const toCache = new Response(resp.clone().body, resp);
        toCache.headers.set("Cache-Control", `max-age=${EVENTS_CACHE_TTL}`);
        if (ctx) ctx.waitUntil(cache.put(cacheKey, toCache));
      }
    }
    if (!resp.ok) continue; // a missing city file shouldn't fail the whole request

    const cityEvents = await resp.json();
    if (Array.isArray(cityEvents)) all.push(...cityEvents);
  }

  if (all.length === 0) throw new Error("No events loaded");
  return all;
}

function systemPrompt(lang) {
  const langName = LANG_NAMES[lang] || "English";
  return [
    "You are the assistant for 'AI in Town', a site that lists upcoming in-person AI events by city.",
    "You answer questions using ONLY the events provided in the user's message as JSON.",
    "",
    "Rules:",
    "- Base every statement strictly on the provided events. Never invent events, dates, venues, or URLs.",
    "- If no provided event matches the question, say so plainly and, if helpful, mention what cities or event types ARE available.",
    "- When you reference an event, use its exact title. Include the event URL when one is present.",
    "- Today's date context comes from the events' dates; treat events as upcoming.",
    "- Be concise and friendly. Prefer a short intro sentence followed by a compact list when several events match.",
    `- Respond in ${langName}.`,
  ].join("\n");
}

async function askClaude(apiKey, model, { question, lang, events }) {
  const userContent = [
    "Here are the events, as a JSON array:",
    "<events>",
    JSON.stringify(events),
    "</events>",
    "",
    `Question: ${question}`,
  ].join("\n");

  const payload = {
    model,
    max_tokens: 1024,
    thinking: { type: "disabled" },
    output_config: { effort: "low" },
    system: systemPrompt(lang),
    messages: [{ role: "user", content: userContent }],
  };

  const resp = await fetch(ANTHROPIC_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": ANTHROPIC_VERSION,
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    throw new Error(`Anthropic API error: ${resp.status}`);
  }

  const data = await resp.json();
  if (data.stop_reason === "refusal") {
    return "I can't answer that one. Try asking about upcoming AI events instead.";
  }
  const text = (data.content || [])
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("")
    .trim();
  return text || "I couldn't find an answer for that.";
}

/**
 * Return the subset of events whose title appears in the model's answer, so the
 * frontend can render them as clickable cards next to the prose.
 */
function citedEvents(answer, events) {
  const lower = answer.toLowerCase();
  const seen = new Set();
  const cited = [];
  for (const e of events) {
    if (!e.title) continue;
    const key = e.id || e.title;
    if (seen.has(key)) continue;
    if (lower.includes(e.title.toLowerCase())) {
      seen.add(key);
      cited.push({
        title: e.title,
        date: e.date,
        date_status: e.date_status,
        venue: e.venue,
        url: e.url,
        city: e.city,
      });
    }
  }
  return cited;
}
