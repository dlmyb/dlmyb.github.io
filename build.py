from __future__ import annotations

import datetime as dt
import re
import shutil
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - used by Python < 3.11
    import tomli as tomllib


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
DIST_DIR = ROOT / "dist"


def load_toml(path: Path) -> dict:
    with path.open("rb") as file:
        return tomllib.load(file)


def render_markdown(value: str | None) -> str:
    if not value:
        return ""
    html = markdown.markdown(value, extensions=["extra", "sane_lists"])
    return re.sub(r"<a href=", '<a target="_blank" rel="noopener noreferrer" href=', html)


def render_inline_markdown(value: str | None) -> str:
    html = render_markdown(value)
    if html.startswith("<p>") and html.endswith("</p>"):
        return html[3:-4]
    return html


def localize_value(value, suffix: str):
    if isinstance(value, list):
        localized = []
        hidden_key = f"hidden{suffix}"
        for item in value:
            if isinstance(item, dict) and item.get(hidden_key):
                continue
            localized.append(localize_value(item, suffix))
        return localized
    if isinstance(value, dict):
        return localize_dict(value, suffix)
    return value


def localize_dict(data: dict, suffix: str) -> dict:
    localized = {}
    for key, value in data.items():
        if key == "pages" or key.endswith("_zh") or key.startswith("hidden"):
            continue
        localized[key] = localize_value(data.get(f"{key}{suffix}", value), suffix)
    if suffix:
        for key, value in data.items():
            if key.endswith(suffix):
                base_key = key[: -len(suffix)]
                localized.setdefault(base_key, localize_value(value, suffix))
    return localized


def clean_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()


def copy_static_files() -> None:
    shutil.copytree(STATIC_DIR, DIST_DIR / "static")
    for filename in ("CNAME", ".nojekyll"):
        source = ROOT / filename
        if source.exists():
            shutil.copy2(source, DIST_DIR / filename)


def render_pages(site: dict) -> list[dict]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["markdown"] = render_markdown
    env.filters["markdown_inline"] = render_inline_markdown

    template = env.get_template("page.html.j2")
    pages = []
    content = load_toml(DATA_DIR / "content.toml")

    for page_config in content["pages"]:
        suffix = page_config.get("suffix", "")
        page = localize_dict(content, suffix)
        page.update(page_config)
        page.pop("suffix", None)
        html = template.render(site=site, page=page)
        output = DIST_DIR / page["output"]
        output.write_text(html, encoding="utf-8")
        pages.append(page)

    return pages


def write_sitemap(site: dict, pages: list[dict]) -> None:
    base_url = site["base_url"].rstrip("/")
    today = dt.date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for page in pages:
        output = page["output"]
        path = "" if output == "index.html" else output
        loc = f"{base_url}/{path}"
        lines.extend(
            [
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{today}</lastmod>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    (DIST_DIR / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    site = load_toml(DATA_DIR / "site.toml")
    clean_dist()
    copy_static_files()
    pages = render_pages(site)
    write_sitemap(site, pages)


if __name__ == "__main__":
    main()
