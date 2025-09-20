import json
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional
from unittest import mock

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

if "tweepy" not in sys.modules:
    sys.modules["tweepy"] = mock.MagicMock()

if "eventregistry" not in sys.modules:
    sys.modules["eventregistry"] = mock.MagicMock()

google_module = mock.MagicMock()
google_genai_module = mock.MagicMock()
google_types_module = mock.MagicMock()
google_module.genai = google_genai_module
google_genai_module.types = google_types_module

sys.modules.setdefault("google", google_module)
sys.modules.setdefault("google.genai", google_genai_module)
sys.modules.setdefault("google.genai.types", google_types_module)

from bot import BitcoinMiningNewsBot
from gemini_client import ArticleContentManager, ReportGenerator


class DummyGeminiClient:
    def __init__(self, article_response: Dict[str, object], analysis_response: Optional[Dict[str, object]] = None):
        self.article_response = article_response
        self.analysis_response = analysis_response or {}

    def generate_article(self, article: Dict[str, object]):
        return self.article_response

    def analyze_article(self, article: Dict[str, object]):
        return self.analysis_response


@pytest.fixture()
def sample_article() -> Dict[str, str]:
    return {
        "title": "Bitcoin miners expand operations amid price surge",
        "summary": "Operators respond to market signals with new investments.",
        "body": "Bitcoin miners are expanding operations...",
        "url": "https://example.com/miners-expand",
    }


@pytest.fixture()
def generated_article() -> Dict[str, object]:
    return {
        "headline": "Bitcoin Miners Accelerate Expansion",
        "subhead": "Infrastructure upgrades aim to capitalise on higher BTC prices.",
        "sections": [
            {"title": "Background", "content": "The mining sector has seen renewed interest."},
            {"title": "Hashrate Impact", "content": "Hashrate projections point to sustained growth."},
            {"title": "Regulatory Outlook", "content": "Policy makers remain cautious but open to innovation."},
        ],
    }


@pytest.fixture()
def analysis_result(sample_article: Dict[str, str]) -> Dict[str, object]:
    return {
        "article_title": sample_article["title"],
        "article_url": sample_article["url"],
        "analysis_text": "Key themes, risks, and opportunities for miners.",
        "analysis_timestamp": "2024-01-01T00:00:00",
        "model_used": "gemini-test",
    }


def _parse_front_matter(markdown: str) -> Tuple[Dict[str, object], str]:
    assert markdown.startswith("---"), "Generated file is missing YAML front matter"
    parts = markdown.split("---", 2)
    if len(parts) < 3:
        raise AssertionError("Front matter block not terminated correctly")

    front_matter_block = parts[1].strip()
    body = parts[2].lstrip()

    metadata: Dict[str, object] = {}
    for line in front_matter_block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        metadata[key.strip()] = json.loads(raw_value.strip())

    return metadata, body


def test_generated_article_saved_with_structure(tmp_path: Path, sample_article: Dict[str, str], generated_article: Dict[str, object]):
    bot = BitcoinMiningNewsBot(safe_mode=True)
    articles_dir = tmp_path / "docs" / "articles"
    bot.article_content_manager = ArticleContentManager(content_dir=str(articles_dir))

    dummy_gemini = DummyGeminiClient(generated_article)
    bot.api_manager.gemini_client = dummy_gemini

    bot._generate_and_save_article(sample_article)

    files = list(articles_dir.glob("*.md"))
    assert len(files) == 1, "Expected one generated article file"

    content = files[0].read_text(encoding="utf-8")
    metadata, body = _parse_front_matter(content)

    assert metadata["layout"] == "article"
    assert metadata["permalink"].startswith("/articles/")
    assert metadata["source_url"] == sample_article["url"]
    assert metadata["title"].startswith("Bitcoin Miners")

    lines = [line for line in body.splitlines() if line.strip()]
    assert lines[0].startswith("# ")
    assert any(line.startswith("## ") for line in lines[1:]), "Subhead missing"
    section_headers = [line for line in lines if line.startswith("### ")]
    assert len(section_headers) >= 3, "Expected at least three body sections"

    # Ensure original metadata is preserved for traceability
    assert "Source URL" in body


def test_analysis_report_saved_with_front_matter(tmp_path: Path, analysis_result: Dict[str, object]):
    reports_dir = tmp_path / "docs" / "reports"
    report_generator = ReportGenerator(reports_dir=str(reports_dir))

    path = report_generator.save_analysis_report(analysis_result)

    assert path is not None
    content = Path(path).read_text(encoding="utf-8")
    metadata, body = _parse_front_matter(content)

    assert metadata["layout"] == "report"
    assert metadata["permalink"].startswith("/reports/")
    assert metadata["model_used"] == analysis_result["model_used"]

    assert "## Article Information" in body
    assert analysis_result["article_title"] in body


def test_bot_pipeline_writes_site_artifacts(
    tmp_path: Path,
    sample_article: Dict[str, str],
    generated_article: Dict[str, object],
    analysis_result: Dict[str, object],
):
    site_root = tmp_path / "site"
    articles_dir = site_root / "docs" / "articles"
    reports_dir = site_root / "docs" / "reports"

    bot = BitcoinMiningNewsBot(safe_mode=True)
    bot.article_content_manager = ArticleContentManager(content_dir=str(articles_dir))
    bot.report_generator = ReportGenerator(reports_dir=str(reports_dir))

    dummy_gemini = DummyGeminiClient(generated_article, analysis_result)
    bot.api_manager.gemini_client = dummy_gemini

    bot._generate_and_save_article(sample_article)
    bot._analyze_and_save_report(sample_article)

    article_files = list(articles_dir.glob("*.md"))
    report_files = list(reports_dir.glob("*.md"))

    assert len(article_files) == 1, "Generated article missing from site tree"
    assert len(report_files) == 1, "Generated report missing from site tree"

    article_metadata, _ = _parse_front_matter(article_files[0].read_text(encoding="utf-8"))
    report_metadata, _ = _parse_front_matter(report_files[0].read_text(encoding="utf-8"))

    assert article_metadata["permalink"].startswith("/articles/")
    assert report_metadata["permalink"].startswith("/reports/")
