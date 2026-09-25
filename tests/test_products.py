import shutil
import zipfile
from pathlib import Path

import openpyxl
import pymupdf
import pytest

from autosite.builder import build
from autosite.config import load_config
from autosite.content import Article
from autosite.products import best_match, build_all, load_catalog

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def config(tmp_path):
    for name in ("site.yaml", "products.yaml"):
        shutil.copy(ROOT / name, tmp_path / name)
    return load_config(tmp_path / "site.yaml")


@pytest.fixture
def catalog():
    return load_catalog(ROOT / "products.yaml")


def test_every_product_builds(tmp_path, catalog):
    paths = {p.name: p for p in build_all(catalog, tmp_path)}

    assert len(pymupdf.open(paths["ergonomic-setup-checklist.pdf"])) == 2
    assert len(pymupdf.open(paths["remote-work-planner.pdf"])) == 4
    assert len(pymupdf.open(paths["desk-stretch-routine.pdf"])) == 2
    wb = openpyxl.load_workbook(paths["home-office-planner.xlsx"])
    assert wb.sheetnames == ["Start here", "Ergonomic calculator", "Gear budget", "Setup audit"]
    assert wb["Ergonomic calculator"]["B5"].value == '=IF(B3="in",B4*2.54,B4)'
    with zipfile.ZipFile(paths["home-office-bundle.zip"]) as zf:
        assert sorted(zf.namelist()) == sorted([
            "home-office-planner.xlsx", "remote-work-planner.pdf", "desk-stretch-routine.pdf", "README.txt"])


def test_paid_files_are_never_published(config):
    out = build(config)

    published = {p.name for p in out.rglob("*") if p.is_file()}
    assert "ergonomic-setup-checklist.pdf" in published
    for paid in ["home-office-planner.xlsx", "remote-work-planner.pdf", "desk-stretch-routine.pdf",
                 "home-office-bundle.zip"]:
        assert paid not in published


def test_product_pages(config):
    out = build(config)

    shop = (out / "templates" / "index.html").read_text()
    assert "Home Office Planner" in shop and "coming soon" in shop
    free = (out / "templates" / "ergonomic-setup-checklist" / "index.html").read_text()
    assert "/downloads/ergonomic-setup-checklist.pdf" in free
    paid = (out / "templates" / "home-office-planner" / "index.html").read_text()
    assert "Coming soon" in paid and "Buy now" not in paid
    assert "/templates/home-office-planner/" in (out / "sitemap.xml").read_text()
    assert (out / "static" / "previews" / "home-office-bundle.png").exists()


def test_checkout_link_turns_on_sales(config):
    text = (config.root / "products.yaml").read_text()
    text = text.replace('checkout_url: ""', 'checkout_url: "https://pay.example/buy"')
    (config.root / "products.yaml").write_text(text)
    Article(slug="neck", title="How to stop neck pain on a laptop", description="d",
            keyword="neck pain laptop", body="Stretches and breaks help neck pain.", date="2026-01-01",
            draft=False).save(config.content_dir)

    out = build(config)

    paid = (out / "templates" / "home-office-planner" / "index.html").read_text()
    assert 'href="https://pay.example/buy"' in paid and "Coming soon" not in paid
    article = (out / "neck" / "index.html").read_text()
    assert "5-Minute Desk Stretch Routine" in article


def test_best_match_falls_back_to_free(catalog):
    assert best_match(catalog, "standing desk budget", "standing desk").id == "ergonomic-setup-checklist"
    for p in catalog:
        p.checkout_url = "https://pay.example"
    assert best_match(catalog, "standing desk budget", "standing desk").id == "home-office-planner"
    assert best_match(catalog, "nothing relevant here").id == "ergonomic-setup-checklist"
