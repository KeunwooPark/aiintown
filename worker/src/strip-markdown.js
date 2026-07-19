/**
 * @file Convert a markdown string to plain text by stripping all styling.
 *
 * Why strip on the backend (Worker), not the frontend: the frontend already
 * renders the answer safely as plain text via textContent, so literal markdown
 * punctuation (**bold**, # headings, - lists, [link](url)) shows up in the UI.
 * Stripping in the Worker gives a clean "plain text" API contract for every
 * consumer and leaves the frontend's XSS-safe render path untouched. The raw
 * markdown answer is still logged to copyeval for evaluation fidelity; only the
 * HTTP response carries the stripped text.
 *
 * Why a custom marked Renderer instead of marked.parse() -> strip-HTML: parsing
 * to HTML and then stripping tags would require an HTML entity round-trip
 * (decoding &lt; &amp; &gt; …) and would still risk mangling text such as
 * "A > B" or "AT&T". A Renderer subclass emits plain text directly from the
 * parsed token tree, so no HTML is ever produced — raw <, >, & characters pass
 * through unchanged and no entity decoding is needed. marked's lexer/parser
 * still does the robust markdown-grammar parsing; only the output shape changes.
 */
import { marked, Renderer } from "marked";

/**
 * marked Renderer that emits plain text instead of HTML.
 *
 * Block methods return their text followed by a blank-line separator; inline
 * methods drop emphasis/quote markers and keep the readable text. Links keep
 * only their label (the URL is dropped — the event cards render clickable
 * links separately), and images keep only their alt text.
 */
class PlainTextRenderer extends Renderer {
  // --- Block-level tokens ---
  space() {
    return "";
  }
  code({ text }) {
    return text.replace(/\n+$/, "") + "\n\n";
  }
  blockquote({ tokens }) {
    return this.parser.parse(tokens).trim() + "\n\n";
  }
  heading({ tokens }) {
    return this.parser.parseInline(tokens).trim() + "\n\n";
  }
  hr() {
    return "\n\n";
  }
  html({ text }) {
    return text.replace(/<[^>]+>/g, "").trim() + "\n\n";
  }
  def() {
    return "";
  }
  paragraph({ tokens }) {
    return this.parser.parseInline(tokens).trim() + "\n\n";
  }
  checkbox() {
    return "";
  }
  list(token) {
    const items = token.items
      .map((item) => this.listitem(item).trim())
      .filter(Boolean);
    return items.join("\n") + "\n\n";
  }
  listitem(item) {
    return this.parser.parse(item.tokens).trim();
  }
  table(token) {
    const row = (cells) =>
      cells.map((c) => this.tablecell(c).trim()).join("  ");
    return [row(token.header), ...token.rows.map(row)].join("\n") + "\n\n";
  }
  tablecell(cell) {
    return this.parser.parseInline(cell.tokens);
  }

  // --- Inline tokens (parseInline dispatches these on this.renderer) ---
  strong({ tokens }) {
    return this.parser.parseInline(tokens);
  }
  em({ tokens }) {
    return this.parser.parseInline(tokens);
  }
  del({ tokens }) {
    return this.parser.parseInline(tokens);
  }
  codespan({ text }) {
    return text;
  }
  br() {
    return "\n";
  }
  link({ tokens }) {
    // Keep only the link label; drop the URL (event cards link separately).
    return this.parser.parseInline(tokens);
  }
  image({ text }) {
    return text; // alt text
  }
  text(token) {
    return token.tokens ? this.parser.parseInline(token.tokens) : token.text;
  }
}

/**
 * Strip all markdown styling from a string, returning plain text.
 *
 * Bold/italic/strikethrough emphasis, headings, list markers, blockquotes,
 * code fences, horizontal rules, and link/image syntax are removed while the
 * readable text is kept. Paragraphs stay separated by a blank line and list
 * items / hard line breaks stay on their own lines, so a plain-text renderer
 * that splits on newlines (e.g. the site's renderAnswer) still shows structure.
 *
 * @param {string} md - Markdown text to convert (e.g. a model's answer).
 * @returns {string} The input as plain text, with no markdown punctuation.
 */
export function stripMarkdown(md) {
  if (!md) return "";
  const out = marked.parse(md, { renderer: new PlainTextRenderer() });
  return out
    .replace(/[ \t]+\n/g, "\n") // trim trailing whitespace on each line
    .replace(/\n{3,}/g, "\n\n") // collapse runs of blank lines
    .trim();
}
