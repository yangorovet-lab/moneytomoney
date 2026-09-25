"""Rendering the published articles into a static website."""

from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .affiliate import insert_links, used_product_ids
from .config import Config
from .content import Article, load_all

PACKAGE_DIR = Path(__file__).resolve().parent

STATIC_PAGES = {
    "about": "About",
    "disclosure": "Affiliate disclosure",
    "privacy": "Privacy policy",
}


def render_markdown(text: str, config: Config) -> str:
    return markdown.markdown(insert_links(text, config), extensions=["extra", "sane_lists", "toc"])


def build(config: Config) -> Path:
    out = config.output_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(PACKAGE_DIR / "static", out / "static")

    base_url = config.site["base_url"].rstrip("/")
    env = Environment(
        loader=FileSystemLoader(PACKAGE_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    env.globals.update(
        site=config.site,
        base=urlparse(base_url).path.rstrip("/"),
        base_url=base_url,
        year=dt.date.today().year,
        static_pages=STATIC_PAGES,
        reviewed=not config.generation["auto_publish"],
    )

    articles = [a for a in load_all(config.content_dir) if not a.draft]

    def write(rel: str, html: str) -> None:
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    write("index.html", env.get_template("index.html").render(articles=articles))
    for article in articles:
        write(
            f"{article.slug}/index.html",
            env.get_template("article.html").render(
                article=article,
                body=render_markdown(article.body, config),
                has_affiliate_links=bool(used_product_ids(article.body)),
            ),
        )
    for slug, title in STATIC_PAGES.items():
        write(f"{slug}/index.html", env.get_template(f"{slug}.html").render(title=title))
    write("404.html", env.get_template("404.html").render())
    write("sitemap.xml", sitemap(base_url, articles))
    write("feed.xml", feed(config, base_url, articles))
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n")
    return out


def sitemap(base_url: str, articles: list[Article]) -> str:
    urls = [f"<url><loc>{base_url}/</loc></url>"]
    urls += [
        f"<url><loc>{base_url}/{a.slug}/</loc><lastmod>{a.date}</lastmod></url>" for a in articles
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def feed(config: Config, base_url: str, articles: list[Article]) -> str:
    items = "".join(
        f"<item><title>{escape(a.title)}</title><link>{base_url}/{a.slug}/</link>"
        f"<guid>{base_url}/{a.slug}/</guid><description>{escape(a.description)}</description></item>"
        for a in articles[:20]
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
        f"<title>{escape(config.site['name'])}</title><link>{base_url}/</link>"
        f"<description>{escape(config.site.get('tagline', ''))}</description>"
        f"{items}</channel></rss>\n"
    )
