"""Articles stored as Markdown files with a YAML front matter header."""

from __future__ import annotations

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

    @property
    def word_count(self) -> int:
        return len(self.body.split())

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


def load_all(directory: Path) -> list[Article]:
    if not directory.exists():
        return []
    articles = [Article.load(p) for p in sorted(directory.glob("*.md"))]
    return sorted(articles, key=lambda a: a.date, reverse=True)
