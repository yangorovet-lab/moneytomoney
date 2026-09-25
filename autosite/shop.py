"""Rendering the template shop: product pages, free downloads and previews."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .products import Product, best_match, build_product, load_catalog, render_preview
from .products import spreadsheet


def catalog_for(config) -> list[Product]:
    return load_catalog(config.root / "products.yaml")


def build_assets(catalog: list[Product], out: Path) -> dict[str, str]:
    """Publish free files and preview images. Returns product id -> preview path (relative to out)."""
    previews: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for product in catalog:
            if product.bundle:
                continue
            path = build_product(product, catalog, tmp_dir)
            if product.is_free:
                (out / "downloads").mkdir(parents=True, exist_ok=True)
                shutil.copy(path, out / "downloads" / product.file)
            if path.suffix == ".pdf":
                source = path
            elif product.id == "home-office-planner":
                source = tmp_dir / "home-office-planner-preview.pdf"
                spreadsheet.build_preview(source)
            else:
                continue
            rel = f"static/previews/{product.id}.png"
            if render_preview(source, out / rel, watermark=not product.is_free):
                previews[product.id] = rel
    for product in catalog:
        parts = [out / previews[i] for i in product.bundle if i in previews]
        if parts:
            rel = f"static/previews/{product.id}.png"
            bundle_preview(parts, out / rel)
            previews[product.id] = rel
    return previews


def bundle_preview(images: list[Path], png_path: Path, width: int = 520) -> None:
    """Fan the part previews out on one card."""
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.draw_rect(page.rect, color=None, fill=(0.91, 0.95, 0.93))
    step = 70
    w = 612 - 80 - step * (len(images) - 1)
    for i, image in enumerate(images):
        x, y = 40 + i * step, 40 + i * step
        page.insert_image(pymupdf.Rect(x, y, x + w, y + w * 792 / 612), filename=str(image))
    zoom = width / 612
    page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(png_path)


def bundle_value(product: Product, catalog: list[Product]) -> float:
    parts = {p.id: p for p in catalog}
    return sum(parts[i].price for i in product.bundle if i in parts)


__all__ = ["best_match", "build_assets", "bundle_value", "catalog_for"]
