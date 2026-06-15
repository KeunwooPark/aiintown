# Glossary

> **TL;DR** — Definitions of the Jekyll and GitHub Pages terms used across this wiki.

## Jekyll

**Jekyll** — A Ruby static-site generator that turns markdown/HTML source plus layouts into a static website. Used here as the site engine.

**Front matter** — The YAML block fenced by `---` at the top of a content file (e.g. `index.md`). It sets per-page variables such as `layout` and `title` that the theme reads. A file with no front matter is copied verbatim instead of being processed.

**`minima`** — Jekyll's default theme, providing the layouts and styling for this otherwise-empty site. Selected via `theme: minima` in `_config.yml`.

**`_config.yml`** — Jekyll's site-wide configuration file, read once at build time.

**`_site/`** — The generated output directory Jekyll writes the built static site into. Gitignored; GitHub regenerates it server-side.

## GitHub Pages

**GitHub Pages** — GitHub's static-site hosting. Here it uses the *native build*: GitHub runs Jekyll for us on push, so no CI workflow is needed.

**`github-pages` gem** — A meta-gem pinning the exact versions of Jekyll, plugins, and dependencies that GitHub Pages runs in production. Pinned in the `Gemfile` so local builds match the deployed build.

**Project site** — A GitHub Pages site served under a repository path, e.g. `https://keunwoopark.github.io/aiintown/`. Contrast with a *user/organization site* served at the domain root (`https://keunwoopark.github.io/`), which requires a repo named `keunwoopark.github.io`.

**`baseurl`** — The path prefix a project site is served under (`/aiintown` here). Internal links must respect it, or they 404. A user/organization site uses an empty `baseurl`.

**Deploy from a branch** — The GitHub Pages source mode used here: GitHub builds and serves from a chosen branch (`main`) and folder (`/ (root)`). Enabled manually in Settings → Pages.
