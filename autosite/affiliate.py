"""Turning product placeholders into disclosed affiliate links."""

from __future__ import annotations

import html
import re

from .config import Config

# The model marks product mentions as [[product-id]] or [[product-id|link text]].
PLACEHOLDER = re.compile(r"\[\[([a-z0-9-]+)(?:\|([^\]]+))?\]\]")


def used_product_ids(markdown_text: str) -> set[str]:
    return {m.group(1) for m in PLACEHOLDER.finditer(markdown_text)}


def insert_links(markdown_text: str, config: Config) -> str:
    """Replace placeholders with sponsored links; unknown ids become plain text."""

    def replace(match: re.Match) -> str:
        product = config.product(match.group(1))
        text = match.group(2) or (product.name if product else match.group(1))
        if product is None:
            return text
        return (
            f'<a href="{html.escape(product.url, quote=True)}" '
            f'rel="sponsored nofollow noopener" target="_blank">{html.escape(text)}</a>'
        )

    return PLACEHOLDER.sub(replace, markdown_text)
