"""Command line: python -m autosite <command>."""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from .builder import build
from .config import load_config
from .content import Article, load_all
from .generator import generate, pending_topics
from .products import build_all
from .shop import catalog_for


def cmd_generate(config, args):
    generate(config, count=args.count)


def cmd_build(config, args):
    out = build(config)
    published = sum(1 for a in load_all(config.content_dir) if not a.draft)
    print(f"built {published} articles into {out}")


def cmd_run(config, args):
    cmd_generate(config, args)
    cmd_build(config, args)


def cmd_status(config, args):
    today = dt.date.today().isoformat()
    articles = load_all(config.content_dir)
    drafts = [a for a in articles if a.draft]
    live = [a for a in articles if a.is_live(today)]
    scheduled = sorted((a for a in articles if not a.draft and not a.is_live(today)), key=lambda a: a.date)
    print(f"live: {len(live)}, scheduled: {len(scheduled)}, drafts: {len(drafts)}, "
          f"topics left: {len(pending_topics(config))}")
    if scheduled:
        print(f"  next: {scheduled[0].date} {scheduled[0].slug}; last: {scheduled[-1].date}")
    for a in drafts:
        note = f"  <- {'; '.join(a.issues)}" if a.issues else ""
        print(f"  draft: {a.slug}{note}")


def cmd_publish(config, args):
    slugs = [a.slug for a in load_all(config.content_dir) if a.draft] if args.all else args.slugs
    for slug in slugs:
        path = config.content_dir / f"{slug}.md"
        if not path.exists():
            sys.exit(f"no such article: {slug}")
        article = Article.load(path)
        article.draft = False
        article.issues = []
        article.save(config.content_dir)
        print(f"published: {slug}")


def cmd_products(config, args):
    out = config.root / "dist" / "products"
    for path in build_all(catalog_for(config), out):
        print(f"built {path.relative_to(config.root)}")
    print("Upload the paid files to your payment platform and put the links into products.yaml.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="autosite", description="Autonomous affiliate content site")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, func, help_text in [
        ("generate", cmd_generate, "write new articles from topics.txt"),
        ("run", cmd_run, "generate, then build"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--count", type=int, help="number of articles (default from site.yaml)")
        p.set_defaults(func=func)

    sub.add_parser("build", help="render the site into public/").set_defaults(func=cmd_build)
    sub.add_parser("status", help="show drafts and the topic queue").set_defaults(func=cmd_status)
    sub.add_parser("products", help="build template files into dist/products/").set_defaults(func=cmd_products)

    p = sub.add_parser("publish", help="approve drafts for publishing")
    p.add_argument("slugs", nargs="*")
    p.add_argument("--all", action="store_true", help="publish every draft")
    p.set_defaults(func=cmd_publish)

    args = parser.parse_args(argv)
    args.func(load_config(), args)


if __name__ == "__main__":
    main()
