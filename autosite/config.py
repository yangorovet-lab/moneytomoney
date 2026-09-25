"""Loading site configuration and the topic queue."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Product:
    id: str
    name: str
    url: str
    facts: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class Config:
    site: dict
    niche: str
    generation: dict
    products: list[Product]
    affiliate: dict = field(default_factory=dict)
    root: Path = ROOT

    @property
    def content_dir(self) -> Path:
        return self.root / "content"

    @property
    def output_dir(self) -> Path:
        return self.root / "public"

    @property
    def topics_file(self) -> Path:
        return self.root / "topics.txt"

    def product(self, product_id: str) -> Product | None:
        return next((p for p in self.products if p.id == product_id), None)

    def product_url(self, product: Product) -> str | None:
        """The product's affiliate URL, or None while its affiliate IDs are not configured."""
        ids = {k: str(v).strip() for k, v in self.affiliate.items()}
        try:
            url = product.url.format(**ids)
        except KeyError:
            return None
        if any(f"{{{k}}}" in product.url and not v for k, v in ids.items()):
            return None
        return url


def load_config(path: Path | None = None) -> Config:
    path = path or ROOT / "site.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    generation = {
        "model": "claude-opus-5",
        "effort": "medium",
        "articles_per_run": 1,
        "min_words": 900,
        "auto_publish": False,
        **(data.get("generation") or {}),
    }
    products = [Product(**p) for p in data.get("products") or []]
    return Config(
        site=data["site"],
        niche=data["niche"].strip(),
        generation=generation,
        products=products,
        affiliate=data.get("affiliate") or {},
        root=path.resolve().parent,
    )


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:80].rstrip("-") or "article"


def read_topics(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]
