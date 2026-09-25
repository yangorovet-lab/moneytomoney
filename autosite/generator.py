"""Writing articles with the Claude API."""

from __future__ import annotations

import datetime as dt
import re

import anthropic

from .affiliate import used_product_ids
from .config import Config, read_topics, slugify
from .content import Article

SYSTEM_PROMPT = """\
You write articles for an independent niche website. The site earns money from \
affiliate links, so it only survives if readers trust it and search engines see \
it as genuinely helpful. Every article must be the most useful answer to the \
reader's query that you can write.

Honesty rules (non-negotiable):
- Nobody on the team has personally tested products. Never claim or imply \
hands-on testing, personal experience, or anecdotes ("I tried", "we tested", \
"in my experience", "after a month of use").
- Never invent statistics, studies, prices, quotes, reviews, or ratings. When a \
general fact is well established, state it plainly without fake citations.
- Describe a product only with the facts supplied for it. If those facts are not \
enough to recommend it for the reader's situation, do not mention it.
- Health, legal, or financial topics: give general information and suggest \
seeing a professional for individual cases.

Product mentions:
- Mention a listed product only where it genuinely helps the reader, at most \
once or twice per article. Most of the value must come from the advice itself.
- Mark each mention as [[product-id]] or [[product-id|link text]] using the ids \
provided. Never write raw URLs.

Output format, exactly:
TITLE: <search-friendly title, under 65 characters>
DESCRIPTION: <meta description, under 155 characters>
---
<the article body in Markdown, starting with an intro paragraph, using ## and ### \
headings, no H1>"""


def build_prompt(config: Config, keyword: str) -> str:
    products = "\n".join(
        f"- id: {p.id}\n  name: {p.name}\n  facts: {p.facts}\n  relevant to: {', '.join(p.keywords)}"
        for p in config.products
    ) or "(none)"
    return (
        f"Site niche: {config.niche}\n"
        f"Language: {config.site.get('language', 'en')}\n"
        f"Target search query: {keyword}\n"
        f"Minimum length: {config.generation['min_words']} words.\n\n"
        f"Affiliate products you may mention:\n{products}"
    )


def parse_response(text: str) -> tuple[str, str, str]:
    """Split the model output into (title, description, body)."""
    header, sep, body = text.partition("\n---\n")
    if not sep:
        raise ValueError("response is missing the '---' separator")
    title = re.search(r"^TITLE:\s*(.+)$", header, re.MULTILINE)
    description = re.search(r"^DESCRIPTION:\s*(.+)$", header, re.MULTILINE)
    if not title:
        raise ValueError("response is missing a TITLE line")
    return (
        title.group(1).strip(),
        description.group(1).strip() if description else "",
        body.strip(),
    )


# Phrases that signal fabricated first-hand experience.
FIRST_HAND = re.compile(
    r"\b(i|we) (have )?(tested|tried|used|reviewed)\b|\bin my experience\b|"
    r"\bmy (own )?testing\b|\bмы протестировали\b|\bя (протестировал|попробовал)",
    re.IGNORECASE,
)


def quality_issues(article: Article, config: Config) -> list[str]:
    issues = []
    if article.word_count < config.generation["min_words"]:
        issues.append(f"too short: {article.word_count} words")
    if FIRST_HAND.search(article.body):
        issues.append("claims first-hand testing")
    unknown = used_product_ids(article.body) - {p.id for p in config.products}
    if unknown:
        issues.append(f"unknown product ids: {', '.join(sorted(unknown))}")
    if re.search(r"https?://", article.body):
        issues.append("contains raw URLs")
    return issues


def write_article(client: anthropic.Anthropic, config: Config, keyword: str) -> Article:
    gen = config.generation
    with client.beta.messages.stream(
        model=gen["model"],
        max_tokens=32000,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": gen["effort"]},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": build_prompt(config, keyword)}],
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        raise RuntimeError(f"model declined the topic {keyword!r}")
    if message.stop_reason == "max_tokens":
        raise RuntimeError(f"article for {keyword!r} was cut off")

    text = "".join(block.text for block in message.content if block.type == "text")
    title, description, body = parse_response(text)
    article = Article(
        slug=slugify(keyword),
        title=title,
        description=description,
        body=body,
        keyword=keyword,
        date=dt.date.today().isoformat(),
    )
    article.issues = quality_issues(article, config)
    article.draft = bool(article.issues) or not gen["auto_publish"]
    return article


def pending_topics(config: Config) -> list[str]:
    done = {p.stem for p in config.content_dir.glob("*.md")}
    return [t for t in read_topics(config.topics_file) if slugify(t) not in done]


def generate(config: Config, count: int | None = None, client: anthropic.Anthropic | None = None) -> list[Article]:
    count = count if count is not None else config.generation["articles_per_run"]
    topics = pending_topics(config)[:count]
    if not topics:
        print("Topic queue is empty: add new lines to topics.txt")
        return []

    client = client or anthropic.Anthropic()
    written = []
    for keyword in topics:
        try:
            article = write_article(client, config, keyword)
        except (RuntimeError, ValueError) as err:
            print(f"skipped {keyword!r}: {err}")
            continue
        path = article.save(config.content_dir)
        status = "draft" if article.draft else "published"
        note = f" ({'; '.join(article.issues)})" if article.issues else ""
        print(f"{status}: {path.name}{note}")
        written.append(article)
    return written
