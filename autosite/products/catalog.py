"""The product catalog defined in products.yaml."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Product:
    id: str
    name: str
    price: float
    format: str
    file: str
    summary: str
    includes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    checkout_url: str = ""
    bundle: list[str] = field(default_factory=list)

    @property
    def is_free(self) -> bool:
        return not self.price

    @property
    def available(self) -> bool:
        """Free products can always be downloaded; paid ones need a checkout link."""
        return self.is_free or bool(self.checkout_url.strip())

    @property
    def price_label(self) -> str:
        return "Free" if self.is_free else f"${self.price:g}"

    def relevance(self, text: str) -> int:
        text = text.lower()
        return sum(1 for k in self.keywords if re.search(rf"\b{re.escape(k.lower())}\b", text))


def load_catalog(path: Path) -> list[Product]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [Product(**p) for p in data.get("products") or []]


def best_match(products: list[Product], text: str, headline: str = "", min_score: int = 2) -> Product | None:
    """The most relevant paid product on sale, or else the free lead magnet.

    Keywords found in the headline (title and target query) count double.
    """
    candidates = [p for p in products if p.available and not p.bundle]
    paid = [p for p in candidates if not p.is_free]

    def score(p: Product) -> int:
        return p.relevance(text) + 2 * p.relevance(headline)

    if paid:
        best = max(paid, key=score)
        if score(best) >= min_score:
            return best
    return next((p for p in candidates if p.is_free), None)
