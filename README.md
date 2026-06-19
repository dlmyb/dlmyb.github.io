# Personal Website

This site is generated from Jinja2 templates and TOML content files, then deployed to GitHub Pages by GitHub Actions.

## Local Build

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 build.py
```

The generated site is written to `dist/`.

## Editing Content

- Shared site settings live in `data/site.toml`.
- Page content lives in `data/content.toml`.
- Chinese-specific values use the `_zh` suffix, for example `name_zh` overrides `name` on the Chinese page.
- If a `_zh` value does not exist, the Chinese page falls back to the base key.
- Section bodies use Markdown, so syntax like `**bold**`, `*italic*`, and `[text](https://example.com)` is supported.

## Deployment

Pushing to `master` runs `.github/workflows/pages.yml`, builds `dist/`, and deploys the artifact to GitHub Pages.

The repository's GitHub Pages source should be set to **GitHub Actions**.
