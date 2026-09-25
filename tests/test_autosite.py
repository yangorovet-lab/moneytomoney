import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from autosite.affiliate import insert_links
from autosite.builder import build
from autosite.config import load_config, slugify
from autosite.content import Article, load_all
from autosite.generator import generate, parse_response, pending_topics

ROOT = Path(__file__).resolve().parent.parent

GOOD_BODY = "Intro paragraph about chairs.\n\n## Picking a chair\n\n" + "word " * 950 + (
    "\n\nA solid option is [[ergo-chair|this adjustable chair]]."
)


class FakeStream:
    def __init__(self, text, stop_reason="end_turn"):
        self.message = SimpleNamespace(
            stop_reason=stop_reason,
            content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        )

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class FakeClient:
    def __init__(self, text, stop_reason="end_turn"):
        self.calls = []
        self.text, self.stop_reason = text, stop_reason
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeStream(self.text, self.stop_reason)


@pytest.fixture
def config(tmp_path):
    shutil.copy(ROOT / "site.yaml", tmp_path / "site.yaml")
    (tmp_path / "topics.txt").write_text("# comment\nHow to choose a chair\nBest desk lamp\n")
    return load_config(tmp_path / "site.yaml")


def response(body=GOOD_BODY):
    return f"TITLE: How to Choose a Chair\nDESCRIPTION: A short guide.\n---\n{body}"


def test_slugify():
    assert slugify("How to choose: an office chair?") == "how-to-choose-an-office-chair"


def test_parse_response():
    title, description, body = parse_response(response("Hello"))
    assert (title, description, body) == ("How to Choose a Chair", "A short guide.", "Hello")


def test_parse_response_rejects_missing_separator():
    with pytest.raises(ValueError):
        parse_response("TITLE: x\nno separator")


def test_generate_saves_draft_and_consumes_topic(config):
    client = FakeClient(response())
    [article] = generate(config, count=1, client=client)

    assert article.slug == "how-to-choose-a-chair"
    assert article.draft  # auto_publish is off in site.yaml
    assert article.issues == []
    assert pending_topics(config) == ["Best desk lamp"]
    call = client.calls[0]
    assert call["model"] == "claude-opus-5"
    assert call["fallbacks"] == "default"
    assert "How to choose a chair" in call["messages"][0]["content"]


def test_quality_issues_force_draft(config):
    config.generation["auto_publish"] = True
    body = "We tested this chair for a month. [[made-up-id]] See https://example.com"
    [article] = generate(config, count=1, client=FakeClient(response(body)))

    assert article.draft
    assert any("too short" in i for i in article.issues)
    assert "claims first-hand testing" in article.issues
    assert any("made-up-id" in i for i in article.issues)
    assert "contains raw URLs" in article.issues


def test_refusal_is_skipped(config):
    assert generate(config, count=1, client=FakeClient("", stop_reason="refusal")) == []
    assert list(config.content_dir.glob("*.md")) == []


def test_insert_links(config):
    html = insert_links("Try [[ergo-chair]] or [[nope|this]].", config)
    assert 'rel="sponsored nofollow noopener"' in html
    assert "YOUR-AFFILIATE-ID" in html
    assert "Example Ergonomic Chair</a>" in html
    assert html.endswith("or this.")


def test_article_round_trip(tmp_path):
    article = Article(slug="a", title="T: colon", description="D", body="Body", date="2026-01-01", draft=False)
    article.save(tmp_path)
    assert load_all(tmp_path)[0] == article


def test_build_publishes_only_approved(config):
    Article(slug="live", title="Live", description="d", body="See [[ergo-chair]].", date="2026-01-02",
            draft=False).save(config.content_dir)
    Article(slug="hidden", title="Hidden", description="d", body="x", date="2026-01-01").save(config.content_dir)

    out = build(config)

    page = (out / "live" / "index.html").read_text()
    assert "This article contains affiliate links" in page
    assert 'rel="sponsored nofollow noopener"' in page
    assert not (out / "hidden").exists()
    assert "/live/" in (out / "sitemap.xml").read_text()
    assert "hidden" not in (out / "index.html").read_text()
    for extra in ["robots.txt", "feed.xml", "404.html", "disclosure/index.html", "static/style.css"]:
        assert (out / extra).exists()
