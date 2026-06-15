# aiintown

A site served with GitHub Pages using Jekyll and the Minima theme.

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
