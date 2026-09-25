"""Articles stored as Markdown files with a YAML front matter header."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Article:
    slug: str
    title: str
    description: str
    body: str
    keyword: str = ""
    date: str = ""
    draft: bool = True
    issues: list[str] = field(default_factory=list)

    def is_live(self, today: str) -> bool:
        """Approved and its publish date has arrived (dates are ISO strings, so they compare as text)."""
        return not self.draft and self.date <= today

    @property
    def word_count(self) -> int:
        return len(self.body.split())

    @property
    def reading_minutes(self) -> int:
        return max(1, round(self.word_count / 230))

    def to_text(self) -> str:
        meta = {
            "title": self.title,
            "description": self.description,
            "keyword": self.keyword,
            "date": self.date,
            "draft": self.draft,
        }
        if self.issues:
            meta["issues"] = self.issues
        header = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
        return f"---\n{header}---\n\n{self.body.strip()}\n"

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.slug}.md"
        path.write_text(self.to_text(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "Article":
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            raise ValueError(f"{path}: missing front matter")
        _, header, body = text.split("---\n", 2)
        meta = yaml.safe_load(header) or {}
        return cls(
            slug=path.stem,
            title=meta.get("title", path.stem),
            description=meta.get("description", ""),
            body=body.strip(),
            keyword=meta.get("keyword", ""),
            date=str(meta.get("date", "")),
            draft=bool(meta.get("draft", False)),
            issues=list(meta.get("issues") or []),
        )


STOP_WORDS = {"a", "an", "and", "at", "do", "for", "from", "how", "in", "is", "it", "of", "on", "or",
              "should", "the", "to", "vs", "what", "when", "which", "with", "you", "your", "best", "work",
              "working", "home", "office"}


def topic_words(article: Article) -> set[str]:
    text = f"{article.keyword} {article.title}".lower()
    return {w for w in re.findall(r"[a-z0-9]+", text) if w not in STOP_WORDS and len(w) > 2}


def related(article: Article, pool: list[Article], limit: int = 3) -> list[Article]:
    """The articles sharing the most topic words with this one."""
    words = topic_words(article)
    scored = [(len(words & topic_words(other)), other.date, other) for other in pool if other.slug != article.slug]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: (s[0], s[1]), reverse=True)
    return [s[2] for s in scored[:limit]]


def load_all(directory: Path) -> list[Article]:
    if not directory.exists():
        return []
    articles = [Article.load(p) for p in sorted(directory.glob("*.md"))]
    return sorted(articles, key=lambda a: a.date, reverse=True)
