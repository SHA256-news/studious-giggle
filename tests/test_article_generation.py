import sys
from pathlib import Path
from typing import Dict
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
from gemini_client import ArticleContentManager


class DummyGeminiClient:
    def __init__(self, article_response: Dict[str, object]):
        self.article_response = article_response

    def generate_article(self, article: Dict[str, object]):
        return self.article_response


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


def test_generated_article_saved_with_structure(tmp_path: Path, sample_article: Dict[str, str], generated_article: Dict[str, object]):
    bot = BitcoinMiningNewsBot(safe_mode=True)
    bot.article_content_manager = ArticleContentManager(content_dir=str(tmp_path))

    dummy_gemini = DummyGeminiClient(generated_article)
    bot.api_manager.gemini_client = dummy_gemini

    bot._generate_and_save_article(sample_article)

    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1, "Expected one generated article file"

    content = files[0].read_text(encoding="utf-8")

    lines = [line for line in content.splitlines() if line.strip()]
    assert lines[0].startswith("# ")
    assert any(line.startswith("## ") for line in lines[1:]), "Subhead missing"
    section_headers = [line for line in lines if line.startswith("### ")]
    assert len(section_headers) >= 3, "Expected at least three body sections"

    # Ensure original metadata is preserved for traceability
    assert "Source URL" in content
