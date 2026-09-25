"""Building the downloadable template files."""

from __future__ import annotations

import zipfile
from pathlib import Path

from . import checklist, spreadsheet, stretches, weekly_planner
from .catalog import Product, best_match, load_catalog

BUILDERS = {
    "ergonomic-setup-checklist": checklist.build,
    "home-office-planner": spreadsheet.build,
    "remote-work-planner": weekly_planner.build,
    "desk-stretch-routine": stretches.build,
}

BUNDLE_README = """Complete Home Office Bundle

Thank you for your purchase!

- home-office-planner.xlsx: open in Excel, or in Google Sheets via File > Import.
- remote-work-planner.pdf: print as many pages as you need (undated).
- desk-stretch-routine.pdf: print the poster and cut out the pocket card.

These templates are general information, not medical advice.
"""

__all__ = ["Product", "best_match", "build_product", "build_all", "load_catalog", "render_preview"]


def build_product(product: Product, catalog: list[Product], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / product.file
    if product.bundle:
        parts = {p.id: p for p in catalog}
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for part_id in product.bundle:
                part_path = build_product(parts[part_id], catalog, out_dir)
                zf.write(part_path, part_path.name)
            zf.writestr("README.txt", BUNDLE_README)
        return path
    builder = BUILDERS.get(product.id)
    if builder is None:
        raise KeyError(f"no builder for product {product.id!r}")
    builder(path)
    return path


def build_all(catalog: list[Product], out_dir: Path) -> list[Path]:
    return [build_product(p, catalog, out_dir) for p in catalog]


def render_preview(pdf_path: Path, png_path: Path, width: int = 900, watermark: bool = False) -> bool:
    """Render the first page of a PDF to PNG. Returns False if PyMuPDF is unavailable.

    Paid products get a low-resolution, watermarked preview so the image can't replace the file.
    """
    try:
        import pymupdf
    except ImportError:
        return False
    with pymupdf.open(pdf_path) as doc:
        page = doc[0]
        if watermark:
            width = min(width, 520)
            rect = page.rect
            for i in range(3):
                y = rect.height * (0.3 + 0.25 * i)
                page.insert_text((rect.width * 0.18, y), "PREVIEW", fontsize=64, color=(0.1, 0.42, 0.33),
                                 fill_opacity=0.18, stroke_opacity=0.18,
                                 morph=(pymupdf.Point(rect.width / 2, y), pymupdf.Matrix(-20)))
        zoom = width / page.rect.width
        png_path.parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(png_path)
    return True
