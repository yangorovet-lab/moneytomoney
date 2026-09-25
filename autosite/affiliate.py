"""Turning product placeholders into disclosed affiliate links."""

from __future__ import annotations

import html
import re

from .config import Config

# The model marks product mentions as [[product-id]] or [[product-id|link text]].
PLACEHOLDER = re.compile(r"\[\[([a-z0-9-]+)(?:\|([^\]]+))?\]\]")


def used_product_ids(markdown_text: str) -> set[str]:
    return {m.group(1) for m in PLACEHOLDER.finditer(markdown_text)}


def has_links(markdown_text: str, config: Config) -> bool:
    products = (config.product(pid) for pid in used_product_ids(markdown_text))
    return any(p and config.product_url(p) for p in products)


def insert_links(markdown_text: str, config: Config) -> str:
    """Replace placeholders with sponsored links.

    Unknown ids and products whose affiliate IDs are not configured yet become plain text.
    """

    def replace(match: re.Match) -> str:
        product = config.product(match.group(1))
        text = match.group(2) or (product.name if product else match.group(1))
        url = product and config.product_url(product)
        if not url:
            return html.escape(text)
        return (
            f'<a href="{html.escape(url, quote=True)}" '
            f'rel="sponsored nofollow noopener" target="_blank">{html.escape(text)}</a>'
        )

    return PLACEHOLDER.sub(replace, markdown_text)
